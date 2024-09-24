from fastapi import BackgroundTasks, Request, HTTPException
from fastapi import APIRouter
from src.models.shared_state import projects_in_memory
from src.api.main_routes import video_post_processing
webhook_router = APIRouter()

@webhook_router.post("/webhook/replicate")
async def replicate_webhook(request: Request, background_tasks: BackgroundTasks):
    # Asynchronously get JSON data from request
    data = await request.json()
    # # Print the JSON data for debugging purposes
    # print("Received JSON data:", data)
    background_tasks.add_task(process_replicate_webhook, data)
    # Respond to the webhook
    return {"status": "received"}

async def get_project_id_from_prediction_id(prediction_id):
    pass

async def update_project_with_lip_sync_video_url(project_id, lip_sync_video_url):
    pass

async def get_project_with_project_id(project_id):
    pass

async def process_replicate_webhook(data):
    # get prediction id, sd image link from the webhook payload

    prediction_id = data.get("id")
    lip_sync_video_url = data.get("output")

    # get project id from prediction id. 
    project_id = get_project_id_from_prediction_id(prediction_id)

    # update the project with the lip sync video url
    projects_in_memory[project_id] = await get_project_with_project_id(project_id)
    project = projects_in_memory[project_id]

    project.lip_sync_video_url = lip_sync_video_url

    project = video_post_processing(project)

    # save the project to the database
    # await update_project_in_db(project)










