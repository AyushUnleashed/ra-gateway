import json
from fastapi import BackgroundTasks, Request, HTTPException
from fastapi import APIRouter
from src.services.webhook_processing.replicate_processing import handle_webhook_error, process_replicate_webhook, update_project_status
from src.models.base_models import  ProjectStatus
from src.payments.dodo_payments_helper import verify_signature
from src.payments.handle_payment_scenarios import handle_dispute_event, handle_payment_event, handle_refund_event
from src.payments.payments_utils import is_payment_test_mode
from src.supabase_tools.handle_dodo_webhook_tb_updates import check_existing_webhook, insert_new_webhook
from src.supabase_tools.handle_profiles_tb_updates import get_user_id_from_email
from src.utils.logger import logger
from fastapi import Request, HTTPException
from src.models.base_models import DoDoWebhook

webhook_router = APIRouter()

def save_to_file(data, filename):
    import json
    from pathlib import Path

    sample_responses_folder = Path("src/sample_responses")
    sample_responses_folder.mkdir(parents=True, exist_ok=True)
    with open(sample_responses_folder / filename, "w") as f:
        json.dump(data, f, indent=4)

@webhook_router.post("/api/webhook/videoaiditor")
async def videoaiditor_webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received videoaiditor webhook data: {data}")

        event = data.get("event")
        render_data = data.get("data", {})
        render_id = render_data.get("_id")
        status = render_data.get("status")
        output_url = render_data.get("outputUrl")
        error = render_data.get("error")
        video_id = render_data.get("videoId")
        video_version = render_data.get("videoVersion")
        created_at = render_data.get("createdAt")
        updated_at = render_data.get("updatedAt")
        video_data = render_data.get("videoData")

        if event == "render.completed":
            logger.info(f"Render completed for video ID {video_id} with output URL {output_url}")
            # Process the completed render, e.g., update database, notify user, etc.
            # Example: await update_video_status(video_id, status, output_url)
            return {"status": "received", "message": "Render completed successfully"}
        elif event == "render.failed":
            logger.error(f"Render failed for video ID {video_id} with error: {error}")
            # Handle the error case, e.g., log the error, notify user, etc.
            # Example: await handle_render_error(video_id, error)
            return {"status": "failed", "message": "Render failed"}
        else:
            logger.error(f"Unexpected event type: {event}")
            raise HTTPException(status_code=400, detail="Unexpected event type")

    except Exception as e:
        logger.error(f"Error processing videoaiditor webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



@webhook_router.post("/webhook/replicate")
async def replicate_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        logger.info(f"Received webhook data: {data}")
        status = data.get("status")
        
        if status == "succeeded":
            logger.info("Prediction succeeded, processing in background.")
            background_tasks.add_task(process_replicate_webhook,data)
            return {"status": "received"}
        elif status == "failed":
            logger.warning("Prediction failed.")
            await update_project_status(data, ProjectStatus.ACTOR_GENERATION_FAILED)
            return {"status": status, "message": "The prediction failed."}
        elif status == "canceled":
            logger.info("Prediction was canceled.")
            await update_project_status(data, ProjectStatus.ACTOR_GENERATION_CANCELLED)
            return {"status": status, "message": "The prediction was canceled."}
        else:
            logger.error("Unknown prediction status received.")
            await update_project_status(data, ProjectStatus.ACTOR_GENERATION_FAILED)
            return {"status": "unknown", "message": "The prediction status is unknown."}
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return await handle_webhook_error(data, str(e))
    

@webhook_router.post("/api/webhook/dodopayments")
async def dodopayments_webhook(request: Request):
    # Get headers
    webhook_id = request.headers.get("webhook-id")
    webhook_signature = request.headers.get("webhook-signature")
    webhook_timestamp = request.headers.get("webhook-timestamp")
    
    # Validate required headers
    if not all([webhook_id, webhook_signature, webhook_timestamp]):
        raise HTTPException(status_code=400, detail="Missing required headers")
    
    # Get raw body
    raw_body = await request.body()
    
    # Save raw body and headers to file for debugging or record-keeping
    headers = {
        "webhook-id": webhook_id,
        "webhook-signature": webhook_signature,
        "webhook-timestamp": webhook_timestamp
    }
    #save_to_file({"headers": headers, "body": json.loads(raw_body)}, "dodopayments_webhook.json")
    # Verify signature
    if not verify_signature(webhook_id, webhook_timestamp, raw_body, webhook_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    try:
        # Parse the payload
        payload = json.loads(raw_body)
        event_type = payload.get("type")
        data = payload.get("data", {})

        # create webhook entry here:
        user_id =await get_user_id_from_email(data["customer"]["email"])
        dodo_webhook = DoDoWebhook(
            payment_id=data["payment_id"],
            user_id=user_id,
            product_id=data["product_cart"][0]["product_id"],
            payload_type=data["payload_type"],
            type=event_type,
            payment_method=data["payment_method"],
            email=data["customer"]["email"],
            webhook_object=raw_body,
            test_mode=is_payment_test_mode(data["payment_link"]),
            created_at= data["created_at"]
        )

        exists, _ = await check_existing_webhook(dodo_webhook.payment_id)
        if exists:
            logger.info("Payment already exists. No action taken.")
            return "Payment already exists. No action taken."
        await insert_new_webhook(dodo_webhook)
        
        
        # Handle different event types
        if event_type.startswith("payment."):
            response = await handle_payment_event(event_type, data)
        # elif event_type.startswith("refund."):
        #     response = handle_refund_event(event_type, data)
        # elif event_type.startswith("dispute."):
        #     response = handle_dispute_event(event_type, data)
        else:
            response = {
                "status": "unhandled",
                "message": f"Unhandled event type: {event_type}"
            }
        
        # Log the webhook processing (add your logging logic here)
        logger.info(f"Processed webhook: {event_type} - {response['message']}")
        
        return {
            "success": True,
            **response
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        # Log the error (add your error logging logic here)
        print(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")