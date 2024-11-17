from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.models.shared_state import projects_in_memory
from src.models.base_models import ActorBase, VoiceBase
from src.utils.logger import logger
from src.supabase_tools.handle_actor_tb_updates import get_actor_from_db, get_actors_from_db
from src.supabase_tools.handle_voice_tb_updates import get_voice_from_db, get_voices_from_db

actors_router = APIRouter()

# Get Actor & Voices

@actors_router.get("/api/actors-and-voices")
async def get_actors_and_voices():
    # Retrieve actors and voices from the database
    actors = [actor for actor in get_actors_from_db() if actor.is_visible]
    voices = [voice for voice in get_voices_from_db() if voice.is_visible]

    logger.info("Actors and voices retrieved")

    return {"actors": actors, "voices": voices}

# Select Actor & Voice
class SelectActorVoiceRequest(BaseModel):
    actor_id: UUID
    voice_id: UUID
    
@actors_router.post("/api/projects/{project_id}/select-actor-voice")
async def select_actor_voice(project_id: UUID, request: SelectActorVoiceRequest):
    if project_id not in projects_in_memory:
        logger.warning(f"Project not found: {project_id}")
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_in_memory[project_id]
    project.actor_id = request.actor_id
    actor = get_actor_from_db(request.actor_id)

    actor_base = ActorBase(
        name=actor.name,
        gender=actor.gender,
        full_video_link=actor.full_video_link,
        thumbnail_image_url=actor.thumbnail_image_url,
        default_voice_id=actor.default_voice_id,
        is_visible=actor.is_visible
    )

    project.actor_base = actor_base

    project.voice_id = request.voice_id
    voice = get_voice_from_db(request.voice_id)

    voice_base = VoiceBase(
        name=voice.name,
        gender=voice.gender,
        voice_identifier=voice.voice_identifier,
        is_visible=voice.is_visible,
        provider=voice.provider
    )

    project.voice_base = voice_base
    project.updated_at = datetime.now()

    logger.info(f"Actor and voice selected for project {project_id}: Actor ID {request.actor_id}, Voice ID {request.voice_id}")

    return {"selection_successful": True, "message": "Actor and voice selected successfully"}
