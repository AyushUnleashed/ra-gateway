from src.models.base_models import Actor
from typing import List
from uuid import UUID
from src.supabase_tools.supabase_client import SUPABASE_CLIENT
from src.utils.constants import TableNames

def get_actors_from_db() -> List[Actor]:
    response = SUPABASE_CLIENT.table(TableNames.ACTORS).select("*").execute()
    actors_data = response.data
    return [Actor(**actor) for actor in actors_data]

def get_actor_from_db(actor_id: UUID) -> Actor:
    response = SUPABASE_CLIENT.table(TableNames.ACTORS).select("*").eq("id", str(actor_id)).single().execute()
    actor_data = response.data
    return Actor(**actor_data)