from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, HTTPException, Body
from src.models.shared_state import projects_in_memory
from src.services.script_generation.generate_script import generate_script_with_llm
from src.utils.logger import logger

scripts_router = APIRouter()

@scripts_router.post("/api/projects/{project_id}/generate-script")
async def generate_script(project_id: UUID):
    if project_id not in projects_in_memory:
        logger.warning(f"Project not found: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]

    script_object = await generate_script_with_llm(project.product_base, project.video_configuration)

    project.script = script_object
    project.updated_at = datetime.now()

    logger.info(f"Script generated for project {project_id}: {script_object}")

    return {"script_generated": True, "message": "Script generated successfully", "script": script_object.dict()}

@scripts_router.get("/api/projects/{project_id}/scripts")
async def get_script(project_id: UUID):
    if project_id not in projects_in_memory:
        logger.warning(f"Project not found: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found")

    cache = False
    project = projects_in_memory[project_id]

    if cache:
        dummy_script = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Dummy Script",
            "content": "This is a dummy script content."
        }
        return [dummy_script]

    if not project.script:
        logger.warning(f"Script not found for project {project_id}")
        raise HTTPException(status_code=404, detail="Script not found")

    logger.info(f"Script retrieved for project {project_id}")

    return [project.script.dict()]

@scripts_router.put("/api/projects/{project_id}/scripts/update")
async def update_script(project_id: UUID, script_id: UUID = Body(...), content: str = Body(...)):
    if project_id not in projects_in_memory:
        logger.warning(f"Project not found: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]

    if not project.script or project.script.id != script_id:
        logger.warning(f" Project Script: {project.script} Script ID: {script_id} & project script id: {project.script.id}")
        logger.error(f"Script not found for project {project_id} with script id {script_id}")
        raise HTTPException(status_code=404, detail="Script not found")

    project.script.content = content
    project.updated_at = datetime.now()

    logger.info(f"Script content updated for project {project_id}, script {script_id}: {project.script.content}")

    return {"script_updated": True, "message": "Script content updated successfully"}

@scripts_router.put("/api/projects/{project_id}/scripts/finalize")
async def finalize_script(project_id: UUID, body: dict):
    is_custom = body.get('is_custom', False)
    content = body.get('content')

    if project_id not in projects_in_memory:
        logger.warning(f"Project not found: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]

    if is_custom:
        project.final_script = content
        logger.info(f"Final script set for project {project_id} with custom content: {project.final_script}")
    else:
        script_id = UUID(body.get('script_id'))
        if not project.script or project.script.id != script_id:
            logger.warning(f"Script not found for project {project_id} with script id {script_id}")
            raise HTTPException(status_code=404, detail="Script not found")
        project.final_script = project.script.content
        logger.info(f"Final script set for project {project_id} with script id {script_id}: {project.final_script}")

    project.updated_at = datetime.now()


    return {"final_script_set": True, "message": "Script has been set as final script for the project"}