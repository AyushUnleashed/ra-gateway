import asyncio
from uuid import UUID
from fastapi import BackgroundTasks, Request, HTTPException
from fastapi import APIRouter
from src.config.settings import Settings
from src.models.base_models import Project, ProjectStatus
from src.models.shared_state import projects_in_memory

from src.notification.async_slack_bot import RA_SLACK_BOT
from src.supabase_tools.handle_project_tb_updates import get_project_from_db, get_project_id_from_prediction_id, update_project_in_db 
from src.utils.logger import logger
from src.workflow.video_gen_workflow import video_post_processing

webhook_router = APIRouter()

def save_to_file(data, filename):
    import json
    from pathlib import Path

    sample_responses_folder = Path("src/sample_responses")
    sample_responses_folder.mkdir(parents=True, exist_ok=True)
    with open(sample_responses_folder / filename, "w") as f:
        json.dump(data, f, indent=4)

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
async def process_replicate_webhook(data):
    try:
        prediction_id = data.get("id")
        lipsync_video_url = data.get("output")
        if not lipsync_video_url or not prediction_id:
            logger.error("Missing required data in webhook payload.")
            raise ValueError("Missing required data in webhook payload")

        logger.info(f"Processing prediction ID: {prediction_id}")
        project_id = await get_project_id_from_prediction_id(prediction_id)
        
        # Attempt to get and update the project, retrying if the asset video local path is empty
        for attempt in range(5):
            project = await get_and_update_project(project_id, lipsync_video_url)
            if project.assets_video_local_path:
                logger.info(f"Project {project_id} updated with lipsync video URL.")
                return await video_post_processing(project)
            else:
                logger.warning(f"Assets video local path is empty for project {project_id}. Retrying in 1 minute... (Attempt {attempt + 1}/5)")
                await asyncio.sleep(60)  # Wait for 1 minute before retrying

        # If after 5 attempts the asset video local path is still empty, log an error
        logger.error(f"Assets video local path is still empty after 5 attempts for project {project_id}.")
        raise ValueError("Assets video local path is not updated after multiple attempts")

    except Exception as e:
        logger.error(f"Error in process_replicate_webhook: {str(e)}")
        return await handle_webhook_error(data, str(e))

async def get_and_update_project(project_id, lipsync_video_url):
    logger.info(f"Fetching project {project_id} from database.")
    project = await get_project_from_db(project_id)
    project.lipsync_video_url = lipsync_video_url
    projects_in_memory[project_id] = project
    logger.info(f"Project {project_id} updated in memory.")
    return project

async def update_project_status(prediction_id, status):
    if prediction_id:
        project_id = await get_project_id_from_prediction_id(prediction_id)
        if project_id in projects_in_memory:
            project = projects_in_memory[project_id]
            project.status = status
            await update_project_in_db(project)
            logger.info(f"Project {project_id} status updated to {status}.")

async def handle_webhook_error(data, error_message):
    logger.error(f"An error occurred: {error_message}")
    prediction_id = data.get("id")
    await update_project_status(prediction_id, ProjectStatus.ACTOR_GENERATION_FAILED)
    await RA_SLACK_BOT.send_message(f" env:{Settings.APP_ENV} \n prediction_id:{prediction_id} An error occurred during video processing: {error_message} for {prediction_id}")
    raise HTTPException(status_code=500, detail=error_message)
