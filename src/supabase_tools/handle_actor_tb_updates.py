from src.models.base_models import Actor
from typing import List
from uuid import UUID
from src.supabase_tools.supabase_client import SUPABASE_CLIENT
from src.config.constants import TableNames

def get_actors_from_db() -> List[Actor]:
    response = SUPABASE_CLIENT.table(TableNames.ACTORS).select("*").execute()
    actors_data = response.data
    return [Actor(**actor) for actor in actors_data]

def get_actor_from_db(actor_id: UUID) -> Actor:
    response = SUPABASE_CLIENT.table(TableNames.ACTORS).select("*").eq("id", str(actor_id)).single().execute()
    actor_data = response.data
    return Actor(**actor_data)

if __name__ == "__main__":
    actors = get_actors_from_db()
    print(f"Retrieved {len(actors)} actors from the database.")
    
    if actors:
        actor_id = actors[0].id
        actor = get_actor_from_db(actor_id)
        print(f"Retrieved actor with ID {actor_id}: {actor}")