import asyncio
from fastapi import UploadFile, File, HTTPException
from uuid import uuid4, UUID
from typing import Optional
from datetime import datetime
from fastapi import APIRouter
import os
from src.services.captions_generation.add_captions import BoxedHighlightCaption, roboto_font_path, process_video_for_captions
from src.services.lipsync_generation.muse_talk_lipsync import create_muste_talk_prediction
from src.services.video_editing.edit_video import edit_final_video
from src.supabase_tools.handle_project_tb_updates import update_project_in_db
from src.utils.util_functions import determine_asset_type, save_file_locally
main_router = APIRouter()

from src.services.lipsync_generation.generate_lipsync import generate_lipsync_video
from src.utils.constants import Constants
from src.utils.util_functions import save_file_locally,download_video
from src.utils.file_handling import get_local_path

from src.models.base_models import Project, Product, VideoConfiguration, ProductBase, AssetType ,Asset, Actor, ActorBase,Voice, VoiceBase, VideoLayoutBase,VideoLayout, ProjectStatus
from src.models.shared_state import projects_in_memory


from src.services.script_generation.generate_script import generate_script_with_llm
from src.services.voice_over_generation.generate_t2s import generate_t2s_audio

# DB functions
from src.supabase_tools.handle_product_tb_updates import add_product_to_db, get_product_from_db, get_all_products_from_db, update_product_in_db
from src.supabase_tools.handle_actor_tb_updates import get_actors_from_db, get_actor_from_db
from src.supabase_tools.handle_voice_tb_updates import get_voices_from_db, get_voice_from_db
from src.supabase_tools.handle_layout_tb_updates import get_layout_from_db, get_layouts_from_db
from src.supabase_tools.handle_bucket_updates import upload_file_to_projects


from pydantic import BaseModel

class CreateProductRequest(BaseModel):
    name: str
    description: str
    product_link: Optional[str]  = None

    # logo: Optional[UploadFile] = None

# add a product
@main_router.post("/api/products/create-product")
async def create_product(
    request: CreateProductRequest
):
    product_id = uuid4()
    logo_url = None
    # if request.logo:
    #     logo_url = upload_to_supabase(f"products/{product_id}/logo.png", logo)

    # Create product (dummy function)
    product = Product(
        id=product_id,
        name=request.name,
        description=request.description,
        product_link=request.product_link,
        logo_url=logo_url,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    add_product_to_db(product)

    return {"product_id": product_id}


@main_router.get("/api/products/get-all-products")
async def get_all_products():
    products = await get_all_products_from_db()
    return products

@main_router.get("/api/products/{product_id}")
async def get_product(product_id: UUID):
    product = await get_product_from_db(product_id)
    return product.model_dump()

@main_router.put("/api/products/{product_id}")
async def update_product(product_id: UUID, request: CreateProductRequest):
    # Retrieve the existing product from the database
    existing_product = await get_product_from_db(product_id)
    
    # Update the product fields with the new data from the request
    updated_product = existing_product.copy(update={
        "name": request.name,
        "description": request.description,
        "product_link": request.product_link,
        "updated_at": datetime.now()
    })
    
    # Call the relevant function to update the product in the database
    updated_product_in_db = await update_product_in_db(updated_product)
    
    return updated_product_in_db.model_dump()




class CreateProjectRequest(BaseModel):
    product_id: UUID

# create a project
@main_router.post("/api/projects/create-project")
async def create_project(request: CreateProjectRequest):
    project_id = uuid4()

    # retrieve product from db
    product = await get_product_from_db(request.product_id)
    product_base = ProductBase(
        name=product.name,
        description=product.description,
        product_link=product.product_link,
        thumbnail_url=product.thumbnail_url,
        logo_url=product.logo_url,
    )
    # Create project in memory
    project = Project(
        id=project_id,
        product_id=request.product_id,
        product_base=product_base,
        status=ProjectStatus.CREATED,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    projects_in_memory[project_id] = project
    print(projects_in_memory)

    return {"project_id": project_id}


# Add video configuration to project

@main_router.post("/api/projects/{project_id}/video-configuration")
async def configure_video(project_id: UUID, config: VideoConfiguration):
    if project_id not in projects_in_memory:
        print("Project not found")
        #print(projects_in_memory[project_id])
        print(projects_in_memory)
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]
    project.video_configuration = config
    project.status = ProjectStatus.DRAFT
    project.updated_at = datetime.now()

    return {"config_added": True, "message": "Video configuration added successfully"}

# Create a script for a project

@main_router.post("/api/projects/{project_id}/generate-script")
async def generate_script(project_id: UUID):
    if project_id not in projects_in_memory:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]

    # Dummy function to generate script
    script_object = await generate_script_with_llm(project.product_base, project.video_configuration)

    project.script = script_object
    project.updated_at = datetime.now()

    return {"script_generated": True, "message": "Script generated successfully", "script": script_object.dict()}

@main_router.get("/api/projects/{project_id}/scripts")
async def get_script(project_id: UUID):
    if project_id not in projects_in_memory:
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
        raise HTTPException(status_code=404, detail="Script not found")

    return [project.script.dict()]

@main_router.post("/api/projects/{project_id}/script")
async def finalize_script(project_id: UUID):
    if project_id not in projects_in_memory:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]

    if not project.script:
        raise HTTPException(status_code=404, detail="Script not found")

    project.final_script = project.script.content
    project.updated_at = datetime.now()

    return {"final_script_set": True, "message": "Script has been set as final script for the project"}


# Get Actor & Voices

@main_router.get("/api/actors-and-voices")
async def get_actors_and_voices():
    # Dummy functions to get actors and voices
    actors = get_actors_from_db()
    voices = get_voices_from_db()

    return {"actors": actors, "voices": voices}


# Select Actor & Voice
class SelectActorVoiceRequest(BaseModel):
    actor_id: UUID
    voice_id: UUID

@main_router.post("/api/projects/{project_id}/select-actor-voice")
async def select_actor_voice(project_id: UUID, request: SelectActorVoiceRequest):
    if project_id not in projects_in_memory:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]
    project.actor_id = request.actor_id
    actor = get_actor_from_db(request.actor_id)

    actor_base = ActorBase(
        name=actor.name,
        gender=actor.gender,
        full_video_link=actor.full_video_link,
        thumbnail_image_url=actor.thumbnail_image_url,
        default_voice_id=actor.default_voice_id
    )

    project.actor_base = actor_base

    project.voice_id = request.voice_id
    voice = get_voice_from_db(request.voice_id)

    voice_base = VoiceBase(
        name=voice.name,
        gender=voice.gender,
        voice_identifier=voice.voice_identifier
    )

    project.voice_base = voice_base
    project.updated_at = datetime.now()

    return {"selection_successful": True, "message": "Actor and voice selected successfully"}


# Upload Assets for Project
@main_router.post("/api/projects/{project_id}/assets")
async def upload_asset(project_id: UUID,file: UploadFile = File(...)):
    if project_id not in projects_in_memory:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]

    # Dummy function to save file locally
    local_path = save_file_locally(os.path.join(Constants.LOCAL_STORAGE_BASE_PATH, str(project_id), "assets", file.filename), file)

    asset = Asset(type=determine_asset_type(file.filename), local_path=local_path)
    project.assets.append(asset)
    project.updated_at = datetime.now()

    return {"asset_uploaded": True, "message": "Asset uploaded successfully", "asset_id": str(len(project.assets) - 1)}


# Get Video Layouts
@main_router.get("/api/video-layouts")
async def get_video_layouts():
    # Dummy function to get video layouts
    layouts = get_layouts_from_db()

    return {"layouts": layouts}

class SelectLayoutRequest(BaseModel):
    layout_id: UUID

# select layout
@main_router.post("/api/projects/{project_id}/select-layout")
async def select_layout(project_id: UUID,selectLayoutRequest: SelectLayoutRequest):
    if project_id not in projects_in_memory:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]

    # Call db to get VideoLayout
    video_layout = get_layout_from_db(selectLayoutRequest.layout_id)
    if not video_layout:
        raise HTTPException(status_code=404, detail="Layout not found")

    # Create VideoLayoutBase
    video_layout_base = VideoLayoutBase(
        name=video_layout.name,
        description=video_layout.description,
        thumbnail_url=video_layout.thumbnail_url
    )

    # Attach VideoLayoutBase to the project
    project.video_layout_id = selectLayoutRequest.layout_id
    project.video_layout_base = video_layout_base
    project.updated_at = datetime.now()

    return {"layout_selected": True, "message": "Layout selected successfully"}


# Generate Video

from fastapi import BackgroundTasks

@main_router.post("/api/projects/{project_id}/generate-final-video")
async def generate_final_video(project_id: UUID, background_tasks: BackgroundTasks):
    if project_id not in projects_in_memory:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]
    project.status = ProjectStatus.PROCESSING

    background_tasks.add_task(process_video, project_id)

    return {"generation_started": True, "message": "Video generation process started"}

async def process_video(project_id: UUID):
    project = projects_in_memory[project_id]

    # Generate T2S audio
    t2s_audio_url, audio_duration = await generate_t2s_audio(project.id,project.final_script, project.voice_base.voice_identifier)
    project.t2s_audio_url = t2s_audio_url
    project.final_video_duration = audio_duration
    # await asyncio.sleep(10)
    project.status = ProjectStatus.AUDIO_READY


    prediction_id = await create_muste_talk_prediction(
        video_input_url=project.actor_base.full_video_link,
        audio_input_url=project.actor_base.t2s_audio_url
    )

    project.lipsync_prediction_id = prediction_id
    project.status = ProjectStatus.LIPSYNC_STARTED

    # Update project in database
    #update_project_in_db(project)

    # Generate lipsync video
    # lipsync_video_url = await generate_lipsync_video(project.actor_base.full_video_link, project.t2s_audio_url)
    # project.lipsync_video_url = lipsync_video_url
    # await asyncio.sleep(10)



async def video_post_processing(project: Project):

    # providing already fetched project with lipsync video url

    # save lipsync video locally
    lipsync_video_local_path = get_local_path(project.id,"working",f"lipsync_video_{project.actor_base.name}.mp4")
    lipsync_video_local_path = await download_video(project.lipsync_video_url,output_path=lipsync_video_local_path)

    project.status = ProjectStatus.LIPSYNC_READY

    final_video_local_path = get_local_path(project.id, "working", "final_video.mp4")
    # Edit final video
    final_video_local_path = await edit_final_video(
        lipsync_video_local_path,
        final_video_local_path,
        project.video_layout_base.name,
        project.assets,
        project.final_video_duration
    )

        
    caption_type = BoxedHighlightCaption(
        font_path=roboto_font_path,
        font_size=72,
        default_color=(255, 255, 255),  # Yellow text
        highlight_color=(255, 0, 0),  # Opaque red highlight
        outline_color=(0, 0, 0),
        outline_thickness=3,
        background_color=(0, 0, 0, 0),  # Fully transparent background
        background_padding=5  # 20 pixels padding around text
    )

    final_video_with_captions_local_path = get_local_path(project.id, "working", "final_video_with_captions.mp4")
    process_video_for_captions(final_video_local_path, final_video_with_captions_local_path, caption_type, font_path=roboto_font_path, font_size=32)

    # Upload final video to Supabase
    final_video_url = upload_file_to_projects(
        local_path=final_video_with_captions_local_path,
        project_id=project.id,
        content_type="video/mp4"
    )

    project.final_video_url = final_video_url

    project.status = ProjectStatus.COMPLETED
    project.updated_at = datetime.now()

    # Update project in database
    #update_project_in_db(project)

    return project


@main_router.get("/health")
async def root():
    return {"message": "API is alive"}


# Polling endpoint to check project status

@main_router.get("/api/projects/{project_id}/status")
async def get_project_status(project_id: UUID):
    if project_id not in projects_in_memory:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]
    response = {
        "status": project.status,
        "message": f"Project is {project.status}"
    }

    if project.status == "completed":
        print("Final video url: ", project.final_video_url)
        response["final_video_url"] = str(project.final_video_url)
    else:
        response["final_video_url"] = None

    return response
