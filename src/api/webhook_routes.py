from uuid import UUID
from fastapi import BackgroundTasks, Request, HTTPException
from fastapi import APIRouter
from src.models.base_models import Project, ProjectStatus
from src.models.shared_state import projects_in_memory
from src.api.main_routes import video_post_processing
webhook_router = APIRouter()
from src.supabase_tools.handle_project_tb_updates import get_project_from_db, get_project_id_from_prediction_id, update_project_in_db 


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
        status = data.get("status")
        
        if status == "succeeded":
            background_tasks.add_task(process_replicate_webhook, data)
            return {"status": "received"}
        elif status == "failed":
            await update_project_status(data, ProjectStatus.ACTOR_GENERATION_FAILED)
            return {"status": status, "message": "The prediction failed."}
        elif status == "canceled":
            await update_project_status(data, ProjectStatus.ACTOR_GENERATION_CANCELLED)
            return {"status": status, "message": "The prediction was canceled."}
        else:
            await update_project_status(data, ProjectStatus.ACTOR_GENERATION_FAILED)
            return {"status": "unknown", "message": "The prediction status is unknown."}
    except Exception as e:
        return handle_webhook_error(data, str(e))

async def process_replicate_webhook(data):
    try:
        prediction_id = data.get("id")
        lipsync_video_url = data.get("output")
        if not lipsync_video_url or not prediction_id:
            raise ValueError("Missing required data in webhook payload")

        project_id = await get_project_id_from_prediction_id(prediction_id)
        project = await get_and_update_project(project_id, lipsync_video_url)
        return await video_post_processing(project)
    except Exception as e:
        return await handle_webhook_error(data, str(e))

async def get_and_update_project(project_id, lipsync_video_url):
    project = await get_project_from_db(project_id)
    project.lipsync_video_url = lipsync_video_url
    projects_in_memory[project_id] = project
    return project

async def update_project_status(data, status):
    prediction_id = data.get("id")
    if prediction_id:
        project_id = await get_project_id_from_prediction_id(prediction_id)
        if project_id in projects_in_memory:
            project = projects_in_memory[project_id]
            project.status = status
            await update_project_in_db(project)

async def handle_webhook_error(data, error_message):
    print(f"An error occurred: {error_message}")
    await update_project_status(data, ProjectStatus.ACTOR_GENERATION_FAILED)
    raise HTTPException(status_code=500, detail=error_message)








