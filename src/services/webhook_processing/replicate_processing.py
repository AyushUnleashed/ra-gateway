import asyncio
from uuid import UUID
from fastapi import HTTPException
from src.config.settings import Settings
from src.models.base_models import ProjectStatus
from src.models.shared_state import projects_in_memory

from src.notification.async_slack_bot import RA_SLACK_BOT
from src.supabase_tools.handle_project_tb_updates import get_project_from_db, get_project_id_from_prediction_id, update_project_in_db 
from src.utils.logger import logger
from src.workflow.video_gen_workflow import video_post_processing
from fastapi import HTTPException
from src.config.settings import Settings


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
