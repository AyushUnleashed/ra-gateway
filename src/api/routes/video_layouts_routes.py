from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from src.supabase_tools.handle_layout_tb_updates import get_layout_from_db, get_layouts_from_db
from src.models.base_models import VideoLayoutBase
from src.models.shared_state import projects_in_memory
from src.utils.logger import logger

video_layouts_router = APIRouter()

class SelectLayoutRequest(BaseModel):
    layout_id: UUID

# Get Video Layouts
@video_layouts_router.get("/api/video-layouts")
async def get_video_layouts():
    # Dummy function to get video layouts
    layouts = get_layouts_from_db()

    logger.info("Video layouts retrieved")

    return {"layouts": layouts}


async def get_video_layout_base(layout_id: UUID):
    video_layout = get_layout_from_db(layout_id)
    if not video_layout:
        logger.warning(f"Layout not found: {layout_id}")
        raise HTTPException(status_code=404, detail="Layout not found")

    video_layout_base = VideoLayoutBase(
        name=video_layout.name,
        description=video_layout.description,
        thumbnail_url=video_layout.thumbnail_url
    )

    logger.info(f"Video layout base retrieved: {layout_id}")

    return video_layout_base

# select layout
@video_layouts_router.post("/api/projects/{project_id}/select-layout")
async def select_layout(project_id: UUID, selectLayoutRequest: SelectLayoutRequest):
    if project_id not in projects_in_memory:
        logger.warning(f"Project not found: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]

    video_layout_base = await get_video_layout_base(selectLayoutRequest.layout_id)
    # Attach VideoLayoutBase to the project
    project.video_layout_id = selectLayoutRequest.layout_id
    project.video_layout_base = video_layout_base
    project.updated_at = datetime.now()

    logger.info(f"Layout selected for project {project_id}: {selectLayoutRequest.layout_id}")

    return {"layout_selected": True, "message": "Layout selected successfully"}
