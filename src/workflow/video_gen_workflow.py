import asyncio
from datetime import datetime
import os
from uuid import UUID

import cv2
from src.utils.logger import logger
from fastapi import HTTPException
from src.api.routes.video_layouts_routes import get_video_layout_base
from src.config.settings import Settings
from src.config.constants import Constants
from src.models.base_models import AspectRatio, Project, ProjectStatus, VideoLayoutType
from src.models.shared_state import projects_in_memory
from src.notification.async_slack_bot import RA_SLACK_BOT
from src.notification.gmail_service import send_video_ready_alert_by_email
from src.services.captions_generation.add_captions import BoxedHighlightCaption, process_video_for_captions
from src.services.lipsync_generation.muse_talk_lipsync import create_muste_talk_prediction
from src.services.video_editing.combine_videos import combine_videos_vertically
from src.services.video_editing.edit_asset_video import generate_asset_video
from src.services.voice_over_generation.generate_t2s import generate_t2s_audio
from src.supabase_tools.handle_bucket_updates import upload_file_to_projects
from src.supabase_tools.handle_project_tb_updates import update_project_in_db
from src.supabase_tools.handle_users_tb_updates import get_user_from_db
from src.utils.file_handling import get_local_path
from src.utils.util_functions import download_video
from src.workflow.wrokflow_utils import download_lipsync_video, handle_error, send_video_ready_notification, upload_final_video, handle_success

async def start_lipsync_gen_with_audio(project: Project):
    try:
        # Generate T2S audio
        t2s_audio_url, audio_duration = await generate_t2s_audio(project.id, project.final_script, project.voice_base)
        project.t2s_audio_url = t2s_audio_url
        project.final_video_duration = audio_duration
        project.status = ProjectStatus.VOICE_OVER_READY
        await update_project_in_db(project)
        await handle_success(project, "T2S audio generation")
    except Exception as e:
        await handle_error(project, e, ProjectStatus.VOICE_OVER_GENERATION_FAILED, "T2S audio generation")
        return

    try:
        prediction_id = await create_muste_talk_prediction(
            video_input_url=project.actor_base.full_video_link,
            audio_input_url=project.t2s_audio_url
        )
        project.lipsync_prediction_id = prediction_id
        project.status = ProjectStatus.ACTOR_GENERATION_STARTED
        await update_project_in_db(project)
        await handle_success(project, "starting lipsync generation")
    except Exception as e:
        await handle_error(project, e, ProjectStatus.ACTOR_GENERATION_COULD_NOT_START, "starting lipsync generation")
        return

async def start_assets_video_generation(project: Project):
    try:
        # Update project status to indicate asset video generation has started
        project.status = ProjectStatus.ASSETS_VIDEO_GENERATION_STARTED
        await update_project_in_db(project)

        # Generate Asset Video
        logger.info(f"Starting asset video generation for project {project.id}")
        assets_video_local_path = await generate_asset_video_async(project)
        project.assets_video_local_path = assets_video_local_path
        await update_project_in_db(project)
        await handle_success(project, "asset video generation")
    except Exception as e:
        await handle_error(project, e, ProjectStatus.ASSETS_VIDEO_GENERATION_FAILED, "asset video generation")
        return

async def video_post_processing(project: Project):
    try:
        logger.info(f"Starting video post-processing for project {project.id}")

        # Download lipsync video
        try:
            lipsync_video_local_path = await download_lipsync_video(project)
            project.status = ProjectStatus.ACTOR_GENERATION_COMPLETED
            await update_project_in_db(project)
            await handle_success(project, "downloading lipsync video")
        except Exception as e:
            await handle_error(project, e, ProjectStatus.ACTOR_GENERATION_FAILED, "downloading lipsync video")
            return

        # Retrieve video layout base
        try:
            video_layout_base = await get_video_layout_base(project.video_layout_id)
            project.video_layout_base = video_layout_base
        except Exception as e:
            await handle_error(project, e, ProjectStatus.LAYOUT_RETRIEVAL_FAILED, "retrieving video layout base")
            return

        # Combine videos
        try:
            final_video_local_path = await combine_videos(project, lipsync_video_local_path, project.assets_video_local_path)
            await handle_success(project, "combining videos")
        except Exception as e:
            await handle_error(project, e, ProjectStatus.VIDEO_EDITING_FAILED, "combining videos")
            return

        # Add captions to final video
        try:
            final_video_with_captions_local_path = await add_captions_to_video(project, final_video_local_path)
            await handle_success(project, "adding captions to video")
        except Exception as e:
            await handle_error(project, e, ProjectStatus.CAPTIONS_ADDITION_FAILED, "adding captions to video")
            return

        # Upload final video
        try:
            logger.info(f"final_video_with_captions_local_path: {final_video_with_captions_local_path}")
            final_video_url = await upload_final_video(project, final_video_with_captions_local_path)
            project.final_video_url = final_video_url
            project.status = ProjectStatus.COMPLETED
            project.updated_at = datetime.now()
            await update_project_in_db(project)
            await handle_success(project, "uploading final video")
        except Exception as e:
            await handle_error(project, e, ProjectStatus.UPLOAD_FAILED, "uploading final video")
            return

        await send_video_ready_notification(project.id, project.user_id, final_video_url)

        return project

    except Exception as e:
        await handle_error(project, e, ProjectStatus.POST_PROCESSING_FAILED, "video post-processing")


async def generate_asset_video_async(project: Project) -> str:
    logger.info(f"Generating asset video for project {project.id}")
    aspect_ratio = AspectRatio.NINE_SIXTEEN.value
    asset_edited_video_path = get_local_path(project.id, "working", f"asset_edited_video_{AspectRatio.NINE_SIXTEEN}.mp4")
    return await asyncio.to_thread(
        generate_asset_video,
        project.assets,
        project.final_video_duration,
        aspect_ratio,
        asset_edited_video_path
    )

async def combine_videos(project: Project, lipsync_video_local_path: str, asset_video_path: str) -> str:
    logger.info(f"Combining videos for project {project.id}")
    final_video_local_path = get_local_path(project.id, "working", "final_video.mp4")
    
    # Verify paths are not empty and exist or raise exception
    if not lipsync_video_local_path or not os.path.exists(lipsync_video_local_path):
        logger.error(f"Lipsync video path is invalid or does not exist: {lipsync_video_local_path}")
        raise FileNotFoundError(f"Lipsync video path is invalid or does not exist: {lipsync_video_local_path}")
    
    if not asset_video_path or not os.path.exists(asset_video_path):
        logger.error(f"Asset video path is invalid or does not exist: {asset_video_path}")
        raise FileNotFoundError(f"Asset video path is invalid or does not exist: {asset_video_path}")

    if project.video_layout_base.name == VideoLayoutType.TOP_BOTTOM.value:
        await asyncio.to_thread(
            combine_videos_vertically,
            asset_video_path,
            lipsync_video_local_path,
            final_video_local_path
        )
    else:
        logger.error("Unsupported layout type")
        raise Exception("Unsupported layout type")
    return final_video_local_path


async def add_captions_to_video(project: Project, final_video_local_path: str) -> str:
    logger.info(f"Adding captions to final video for project {project.id}")

    # Verify input video exists
    if not os.path.exists(final_video_local_path):
        raise FileNotFoundError(f"Input video not found at: {final_video_local_path}. Cannot proceed with adding captions.")
    
    caption_type = BoxedHighlightCaption(
        font_path=Constants.ROBOTO_FONT_PATH,
        font_size=72,
        default_color=(255, 255, 255),
        highlight_color=(255, 0, 0),
        outline_color=(0, 0, 0),
        outline_thickness=3,
        background_color=(0, 0, 0, 0),
        background_padding=5
    )
    
    # Ensure output directory exists
    final_video_with_captions_local_path = get_local_path(project.id, "working", "final_video_with_captions.mp4")
    os.makedirs(os.path.dirname(final_video_with_captions_local_path), exist_ok=True)

    await asyncio.to_thread(
        process_video_for_captions,
        final_video_local_path,
        final_video_with_captions_local_path,
        caption_type
    )
    return final_video_with_captions_local_path

# async def add_captions_to_video(project: Project, final_video_local_path: str) -> str:
#     """Add captions to video with enhanced debug logging."""
#     logger.info(f"Starting caption addition for project {project.id}")
#     logger.info(f"Input video path: {final_video_local_path}")
    
#     # Check if file exists and is accessible
#     if not os.path.exists(final_video_local_path):
#         logger.error(f"Input video file does not exist: {final_video_local_path}")
#         raise FileNotFoundError(f"Input video not found: {final_video_local_path}")
    
#     try:
#         # Log file size and permissions
#         file_stats = os.stat(final_video_local_path)
#         logger.info(f"Input video file size: {file_stats.st_size} bytes")
#         logger.info(f"Input video file permissions: {oct(file_stats.st_mode)}")
        
#         # Try to open file for reading to verify access
#         with open(final_video_local_path, 'rb') as f:
#             logger.info("Successfully opened input video file for reading")
            
#         # Verify video can be opened with cv2
#         cap = cv2.VideoCapture(final_video_local_path)
#         if not cap.isOpened():
#             logger.error("Failed to open video with OpenCV")
#             raise ValueError("Cannot open video with OpenCV")
#         logger.info("Successfully opened video with OpenCV")
#         cap.release()
        
#         # Continue with existing caption logic...
#         caption_type = BoxedHighlightCaption(
#             font_path=Constants.ROBOTO_FONT_PATH,
#             font_size=72,
#             default_color=(255, 255, 255),
#             highlight_color=(255, 0, 0),
#             outline_color=(0, 0, 0),
#             outline_thickness=3,
#             background_color=(0, 0, 0, 0),
#             background_padding=5
#         )
        
#         final_video_with_captions_local_path = get_local_path(project.id, "working", "final_video_with_captions.mp4")
#         logger.info(f"Output video will be written to: {final_video_with_captions_local_path}")
        
#         # Create output directory if it doesn't exist
#         os.makedirs(os.path.dirname(final_video_with_captions_local_path), exist_ok=True)
        
#         return await asyncio.to_thread(
#             process_video_for_captions,
#             final_video_local_path,
#             final_video_with_captions_local_path,
#             caption_type
#         )
        
#     except Exception as e:
#         logger.error(f"Error in add_captions_to_video: {str(e)}", exc_info=True)
#         raise

# if __name__ == "__main__":
#     asyncio.run(send_video_ready_notification("46b8cc8a-70bd-4b60-8fc2-9e8bdbffdd4a","814f3aa0-421b-475f-9489-38aea444f364","final_video_url"))