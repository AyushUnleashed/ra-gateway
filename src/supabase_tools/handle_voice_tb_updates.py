from src.models.base_models import Voice
from typing import List
from uuid import UUID
from src.supabase_tools.supabase_client import SUPABASE_CLIENT
from src.config.constants import TableNames

class DatabaseError(Exception):
    pass

def get_voices_from_db() -> List[Voice]:
    response = SUPABASE_CLIENT.table(TableNames.VOICES).select("*").execute()
    voices_data = response.data
    return [Voice(**voice) for voice in voices_data]

def get_voice_from_db(voice_id: UUID) -> Voice:
    response = SUPABASE_CLIENT.table(TableNames.VOICES).select("*").eq("id", str(voice_id)).single().execute()
    voice_data = response.data
    return Voice(**voice_data)

if __name__ == "__main__":
    voices = get_voices_from_db()
    print(f"Retrieved {len(voices)} voices from the database.")
    
    if voices:
        voice_id = voices[0].id
        voice = get_voice_from_db(voice_id)
        print(f"Retrieved voice with ID {voice_id}: {voice}")