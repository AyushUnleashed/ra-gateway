from fastapi import HTTPException
from src.config.settings import Settings
from src.notification.gmail_service import send_video_ready_alert_by_email
from src.supabase_tools.handle_project_tb_updates import update_project_in_db
from src.supabase_tools.handle_users_tb_updates import get_user_from_db
from src.utils.file_handling import get_local_path
from src.utils.logger import logger
from src.models.base_models import Project, ProjectStatus
from src.notification.async_slack_bot import RA_SLACK_BOT
from src.supabase_tools.handle_bucket_updates import upload_file_to_projects
from src.utils.util_functions import download_video

async def download_lipsync_video(project: Project) -> str:
    logger.info(f"Downloading lipsync video for project {project.id}")
    lipsync_video_local_path = get_local_path(project.id, "working", f"lipsync_video_{project.id}.mp4")
    return await download_video(project.lipsync_video_url, output_path=lipsync_video_local_path)

async def upload_final_video(project: Project, final_video_with_captions_local_path: str) -> str:
    logger.info(f"Uploading final video to Supabase for project {project.id}")
    return upload_file_to_projects(
        local_path=final_video_with_captions_local_path,
        project_id=project.id,
        content_type="video/mp4"
    )


async def handle_error(project: Project, e: Exception, status: ProjectStatus, stage: str):
    error_message = str(e)
    logger.error(f"An error occurred during {stage}: {error_message}")
    project.status = status
    await update_project_in_db(project)
    await RA_SLACK_BOT.send_message(
        f"Environment: {Settings.APP_ENV}\n"
        f"Project ID: {project.id}\n"
        f"Error: An error occurred during {stage}\n"
        f"Details: {error_message}"
    )
    raise HTTPException(status_code=500, detail=error_message)

async def send_video_ready_notification(project_id, user_id, final_video_url):
    try:
        await notify_via_slack(project_id, final_video_url)
        user = await get_user_from_db(user_id)
        user_email = user.email
        logger.info(f"Sending video ready notification for project {project_id} to user {user_email}")
        await send_video_ready_alert_by_email(user_email, project_id)
    except Exception as e:
        logger.error(f"An error occurred while sending video ready notification: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while sending video ready notification")

async def notify_via_slack(project_id, final_video_url):
    message = (
        f"Environment: {Settings.APP_ENV}\n"
        f"Project ID: {project_id}\n"
        "Status: Video processing completed\n"
        f"Final Video URL: {final_video_url}"
    )
    await RA_SLACK_BOT.send_message(message)

async def handle_success(project: Project, stage: str):
    logger.info(f"Successfully completed {stage} for project {project.id}")
    await update_project_in_db(project)
    await RA_SLACK_BOT.send_message(
        f"Environment: {Settings.APP_ENV}\n"
        f"Project ID: {project.id}\n"
        f"Status: Successfully completed {stage}"
    )
