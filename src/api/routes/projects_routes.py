from datetime import datetime
import os
from typing import List
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File
from pydantic import BaseModel

from src.api.utils import verify_token
from src.models.base_models import Project, ProductBase, ProjectDTO, VideoConfiguration, ProjectStatus, Asset, ActorBase, VoiceBase
from src.services.script_generation.generate_script import generate_script_with_llm
from src.supabase_tools.handle_project_tb_updates import get_all_projects_from_db, get_project_from_db, project_to_dto
from src.supabase_tools.handle_product_tb_updates import get_product_from_db
from src.supabase_tools.handle_actor_tb_updates import get_actor_from_db
from src.supabase_tools.handle_voice_tb_updates import get_voice_from_db
from src.utils.util_functions import determine_asset_type, save_file_locally
from src.config.constants import Constants
from src.utils.logger import logger
from src.models.shared_state import projects_in_memory

projects_router = APIRouter()

class CreateProjectRequest(BaseModel):
    product_id: UUID

@projects_router.get("/api/projects")
async def get_all_project_dtos(user_id: UUID = Depends(verify_token)) -> List[ProjectDTO]:
    try:
        projects = await get_all_projects_from_db(user_id)
        return [project_to_dto(project) for project in projects]
    except Exception as e:
        logger.error(f"An error occurred while converting projects to DTOs: {e}")
        raise Exception(f"An error occurred while converting projects to DTOs: {e}")

@projects_router.get("/api/projects/{project_id}")
async def get_project(project_id: UUID):
    try:
        project = await get_project_from_db(project_id)
        project_dto = project_to_dto(project)
        return project_dto
    except Exception as e:
        logger.error(f"An error occurred while fetching the project: {e}")
        raise Exception(f"An error occurred while fetching the project: {e}")

@projects_router.post("/api/projects/create-project")
async def create_project(request: CreateProjectRequest, user_id: UUID = Depends(verify_token)):
    try:
        project_id = uuid4()

        product = await get_product_from_db(request.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        product_base = ProductBase(
            name=product.name,
            description=product.description,
            product_link=product.product_link,
            thumbnail_url=product.thumbnail_url,
            logo_url=product.logo_url,
        )

        project = Project(
            id=project_id,
            user_id=user_id,
            product_id=request.product_id,
            product_base=product_base,
            status=ProjectStatus.CREATED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        projects_in_memory[project_id] = project
        logger.info(f"Project created in memory: {project}")
        logger.info(f"Projects in memory size: {len(projects_in_memory)}")

        return {"project_id": project_id}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

