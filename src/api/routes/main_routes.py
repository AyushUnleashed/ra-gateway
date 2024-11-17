import asyncio
from fastapi import Body, Depends, UploadFile, File, HTTPException
from uuid import uuid4, UUID
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter
import os
from src.api.routes.users_routes import reduce_credit
from src.api.utils import verify_token
from src.config.constants import Constants
from src.models.base_models import Asset, ProjectStatus, VideoConfiguration
from src.models.shared_state import projects_in_memory
from src.notification.async_slack_bot import RA_SLACK_BOT

# DB functions

from src.supabase_tools.handle_project_tb_updates import add_project_to_db
from src.utils.logger import logger
from src.utils.util_functions import determine_asset_type, save_file_locally
from src.workflow.video_gen_workflow import start_assets_video_generation, start_lipsync_gen_with_audio


main_router = APIRouter()


@main_router.get("/health")
async def root():
    return {"message": "API is alive"}

@main_router.head("/health")
async def root():
    return {"message": "API is alive | Head"}

# Add video configuration to project

@main_router.post("/api/projects/{project_id}/video-configuration")
async def configure_video(project_id: UUID, config: VideoConfiguration):
    if project_id not in projects_in_memory:
        logger.warning(f"Project not found: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]
    project.video_configuration = config
    project.status = ProjectStatus.DRAFT
    project.updated_at = datetime.now()

    logger.info(f"Video configuration added to project {project_id}: {config}")

    return {"config_added": True, "message": "Video configuration added successfully"}


# Upload Assets for Project
@main_router.post("/api/projects/{project_id}/assets")
async def upload_asset(project_id: UUID,file: UploadFile = File(...)):
    if project_id not in projects_in_memory:
        logger.warning(f"Project not found: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]

    # Dummy function to save file locally
    local_path = save_file_locally(os.path.join(Constants.LOCAL_STORAGE_BASE_PATH, str(project_id), "assets", file.filename), file)

    asset = Asset(type=determine_asset_type(file.filename), local_path=local_path)
    project.assets.append(asset)
    project.updated_at = datetime.now()

    logger.info(f"Asset uploaded for project {project_id}: {file.filename}")

    return {"asset_uploaded": True, "message": "Asset uploaded successfully", "asset_id": str(len(project.assets) - 1)}

# Generate Video
from fastapi import BackgroundTasks
@main_router.post("/api/projects/{project_id}/generate-final-video")
async def generate_final_video(project_id: UUID, background_tasks: BackgroundTasks, user_id: UUID = Depends(verify_token)):
    try:
        if project_id not in projects_in_memory:
            logger.warning(f"Project not found: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")

        project = projects_in_memory[project_id]
        project.user_id = user_id
        project.status = ProjectStatus.PROCESSING

        reduced, _ = await reduce_credit(user_id)

        if reduced:

            # add project to db with status processing with user_id
            await add_project_to_db(project)

            background_tasks.add_task(start_lipsync_gen_with_audio, project)
            background_tasks.add_task(start_assets_video_generation, project)

            logger.info(f"Video generation process started for project {project_id}")
            await RA_SLACK_BOT.send_message(f"Video generation started for project {project_id}")
            return {"generation_started": True, "message": "Video generation process started"}
        else:
            logger.warning(f"No credits available for user {user_id}")
            raise HTTPException(status_code=403, detail="No credits available")
    except HTTPException as e:
        raise e
    except Exception as e:
        error_message = str(e)
        logger.error(f"An error occurred while starting video generation: {error_message}")
        await RA_SLACK_BOT.send_message(
            f"An error occurred: Video generation could not be started for project {project_id}. Error: {error_message}"
        )
        raise HTTPException(status_code=500, detail=error_message)




# Polling endpoint to check project status

# @main_router.get("/api/projects/{project_id}/status")
# async def get_project_status(project_id: UUID):
#     if project_id not in projects_in_memory:
#         raise HTTPException(status_code=404, detail="Project not found")

#     project = projects_in_memory[project_id]
#     response = {
#         "status": project.status,
#         "message": f"Project is {project.status}"
#     }

#     if project.status == "completed":
#         print("Final video url: ", project.final_video_url)
#         response["final_video_url"] = str(project.final_video_url)
#     else:
#         response["final_video_url"] = None

#     return response

