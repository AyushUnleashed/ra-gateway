from src.models.base_models import Project
from src.supabase_tools.supabase_client import SUPABASE_CLIENT

async def update_project_in_db(project: Project) -> Project:
    response = SUPABASE_CLIENT.table("projects").update(project.dict()).eq("id", str(project.id)).execute()
    if not response.data:
        raise Exception("Failed to update project in the database")
    updated_project_data = response.data[0]
    return Project(**updated_project_data)