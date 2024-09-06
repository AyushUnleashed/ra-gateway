from fastapi import UploadFile, File, HTTPException
from uuid import uuid4, UUID
from pydantic import HttpUrl
from typing import Optional
from datetime import datetime
from fastapi import APIRouter

from src.services.video_editing.edit_video import edit_final_video
from src.supabase_tools.handle_project_tb_updates import update_project_in_db
from src.utils.util_functions import determine_asset_type, save_file_locally
main_router = APIRouter()

from src.services.lipsync_generation.generate_wav2lip import generate_lipsync_video
from src.utils.constants import Constants

from src.models.base_models import Project, Product, VideoConfiguration, ProductBase, AssetType ,Asset, Actor, ActorBase,Voice, VoiceBase, VideoLayoutBase,VideoLayout
from src.models.shared_state import projects_in_memory


from src.services.script_generation.generate_script import generate_script_with_llm
from src.services.voice_over_generation.generate_t2s import generate_t2s_audio

# DB functions
from src.supabase_tools.handle_product_tb_updates import add_product_to_db, get_product_from_db
from src.supabase_tools.handle_actor_tb_updates import get_actors_from_db, get_actor_from_db
from src.supabase_tools.handle_voice_tb_updates import get_voices_from_db, get_voice_from_db
from src.supabase_tools.handle_layout_tb_updates import get_layouts_from_db

# add a product
@main_router.post("/api/products/create-product")
async def create_product(
    name: str,
    description: str,
    product_link: Optional[HttpUrl] = None,
    logo: Optional[UploadFile] = File(None)
):
    product_id = uuid4()

    logo_url = None
    # if logo:
    #     logo_url = upload_to_supabase(f"products/{product_id}/logo.png", logo)

    # Create product (dummy function)
    product = Product(
        id=product_id,
        name=name,
        description=description,
        product_link=product_link,
        logo_url=logo_url,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    add_product_to_db(product)

    return {"product_id": product_id}

# create a project
@main_router.post("/api/projects/create-project")
async def create_project(product_id: UUID):
    project_id = uuid4()

    # retrieve product from db
    product = get_product_from_db(product_id)
    product_base = ProductBase(
        name=product.name,
        description=product.description,
        product_link=product.product_link,
        logo_url=product.logo_url,
    )
    # Create project in memory
    project = Project(
        id=project_id,
        product_id=product_id,
        product_base=product_base,
    )

    projects_in_memory[project_id] = project

    return {"project_id": project_id}


# Add video configuration to project

@main_router.put("/api/projects/{project_id}/video-configuration")
async def configure_video(project_id: UUID, config: VideoConfiguration):
    if project_id not in projects_in_memory:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]
    project.video_configuration = config
    project.updated_at = datetime.now()

    return {"config_added": True, "message": "Video configuration added successfully"}

# Create a script for a project

@main_router.post("/api/projects/{project_id}/generate-script")
async def generate_script(project_id: UUID):
    if project_id not in projects_in_memory:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]

    # Dummy function to generate script
    script_object = generate_script_with_llm(project.product_base, project.video_configuration)

    project.script = script_object
    project.updated_at = datetime.now()

    return {"script_generated": True, "message": "Script generated successfully", "script": script_object.dict()}

# Get Actor & Voices

@main_router.get("/api/get-actors-and-voices")
async def get_actors_and_voices():
    # Dummy functions to get actors and voices
    actors = get_actors_from_db()
    voices = get_voices_from_db()

    return {"actors": actors, "voices": voices}


# Select Actor & Voice
@main_router.post("/api/projects/{project_id}/select-actor-voice")
async def select_actor_voice(project_id: UUID, actor_id: UUID, voice_id: UUID):
    if project_id not in projects_in_memory:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]
    project.actor_id = actor_id
    actor = get_actor_from_db(actor_id)

    actor_base = ActorBase(
        name=actor.name,
        gender=actor.gender,
        full_video_link=actor.full_video_link,
        thumbnail_image_url=actor.thumbnail_image_url,
        default_voice_id=actor.default_voice_id
    )

    project.actor_base = actor_base

    project.voice_id = voice_id
    voice = get_voice_from_db(voice_id)

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
    local_path = save_file_locally(f"{Constants.LOCAL_STORAGE_BASE_PATH}/{project_id}/assets/{file.filename}", file)

    asset = Asset(type=determine_asset_type(file.filename), local_path=local_path)
    project.assets.append(asset)
    project.updated_at = datetime.now()

    return {"asset_uploaded": True, "message": "Asset uploaded successfully", "asset_id": str(len(project.assets) - 1)}


# Get Video Layouts
#     
@main_router.get("/api/video-layouts")
async def get_video_layouts():
    # Dummy function to get video layouts
    layouts = get_layouts_from_db()

    return {"layouts": layouts}


# select layout
@main_router.post("/api/projects/{project_id}/select-layout")
async def select_layout(project_id: UUID, layout_id: UUID):
    if project_id not in projects_in_memory:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]

    # Call db to get VideoLayout
    video_layout = get_layouts_from_db(layout_id)
    if not video_layout:
        raise HTTPException(status_code=404, detail="Layout not found")

    # Create VideoLayoutBase
    video_layout_base = VideoLayoutBase(
        name=video_layout.name,
        description=video_layout.description,
        thumbnail_url=video_layout.thumbnail_url
    )

    # Attach VideoLayoutBase to the project
    project.video_layout_id = layout_id
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
    project.status = "processing"

    background_tasks.add_task(process_video, project_id)

    return {"generation_started": True, "message": "Video generation process started"}

async def process_video(project_id: UUID):
    project = projects_in_memory[project_id]

    # Generate T2S audio
    t2s_audio_url, audio_duration = generate_t2s_audio(project.id,project.script.content, project.voice_base.voice_identifier)
    project.t2s_audio_url = t2s_audio_url
    project.final_video_duration = audio_duration

    # Generate lipsync video
    lipsync_video_url = generate_lipsync_video(project.actor_base.full_video_link, project.t2s_audio_url)
    project.lipsync_video_url = lipsync_video_url

    # Edit final video
    final_video_url = edit_final_video(
        project.lipsync_video_url,
        project.video_layout_id,
        project.assets,
        project.final_video_duration
    )

    project.final_video_url = final_video_url

    project.status = "completed"
    project.updated_at = datetime.now()

    # Update project in database
    update_project_in_db(project)



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
        response["final_video_url"] = str(project.final_video_url)

    return response
