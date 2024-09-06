from src.models.base_models import Voice
from typing import List
from uuid import UUID
from src.supabase_tools.supabase_client import SUPABASE_CLIENT

def get_voices_from_db() -> List[Voice]:
    response = SUPABASE_CLIENT.table("voices").select("*").execute()
    if response.status_code != 200:
        raise Exception("Failed to retrieve voices from the database")
    voices_data = response.data
    return [Voice(**voice) for voice in voices_data]

def get_voice_from_db(voice_id: UUID) -> Voice:
    response = SUPABASE_CLIENT.table("voices").select("*").eq("id", str(voice_id)).single().execute()
    if response.status_code != 200:
        raise Exception("Failed to retrieve voice from the database")
    voice_data = response.data
    return Voice(**voice_data)