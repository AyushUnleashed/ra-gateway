
from typing import Any, Dict
from src.supabase_tools.handle_profiles_tb_updates import update_user_credits, get_user_id_from_email
from src.utils.logger import logger
from src.payments.payments_utils import get_credit_amount_from_pack_type, get_pack_type_from_product_id
from src.config.settings import Settings

async def process_credits_addition(data) -> bool:
    try:
        customer = data["customer"]
        product_id = data["product_cart"][0]["product_id"]
        email = customer['email']
        
        # is_test_mode = is_payment_test_mode(data["payment_link"])  
        pack_type = get_pack_type_from_product_id(product_id)

        user_id = await get_user_id_from_email(email)

        additional_credits = get_credit_amount_from_pack_type(pack_type)

        # if is_test_mode == Settings.IS_PRODUCTION:
        #     logger.error(f"Payment mode mismatch: Test mode={is_test_mode}, Production mode={Settings.IS_PRODUCTION}")
        #     return False
        # Add credits to user account here
        await update_user_credits(user_id, additional_credits)
        
        return True
    except Exception as e:
        logger.error(f"Error processing credits addition: {str(e)}")
        return False
        
async def handle_payment_event(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle different payment-related events
    """
    if event_type == "payment.succeeded":
        # Process successful payment
        payment_id = data["payment_id"]
        amount = data["total_amount"]
        currency = data["currency"]
        
        # Add your business logic here
        logger.debug(f"Processing successful payment: ID={payment_id}, Amount={amount}, Currency={currency}")

        
        # # Process credits addition
        success = await process_credits_addition(data)
        
        return {
            "status": "processed",
            "message": f"Successfully processed payment {payment_id}"
        }
        
    elif event_type == "payment.failed":
        # Handle failed payment
        payment_id = data["payment_id"]
        # Add your failure handling logic here
        return {
            "status": "processed",
            "message": f"Recorded failed payment {payment_id}"
        }
    
    return {"status": "unhandled", "message": f"Unhandled payment event type: {event_type}"}

def handle_refund_event(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle refund-related events
    """
    if event_type == "refund.succeeded":
        refund = data["refunds"][0]  # Get the first refund
        refund_id = refund["refund_id"]
        amount = refund["amount"]
        
        # Add your refund processing logic here
        return {
            "status": "processed",
            "message": f"Successfully processed refund {refund_id}"
        }
    
    return {"status": "unhandled", "message": f"Unhandled refund event type: {event_type}"}

def handle_dispute_event(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle dispute-related events
    """
    if data.get("disputes"):
        dispute = data["disputes"][0]  # Get the first dispute
        dispute_id = dispute["dispute_id"]
        
        if event_type == "dispute.opened":
            # Handle new dispute
            return {
                "status": "processed",
                "message": f"New dispute recorded: {dispute_id}"
            }
        elif event_type == "dispute.won":
            # Handle won dispute
            return {
                "status": "processed",
                "message": f"Dispute won: {dispute_id}"
            }
    
    return {"status": "unhandled", "message": f"Unhandled dispute event type: {event_type}"}
