from src.models.base_models import Project
from src.supabase_tools.supabase_client import SUPABASE_CLIENT

def update_project_in_db(project: Project) -> Project:
    response = SUPABASE_CLIENT.table("projects").update(project.dict()).eq("id", str(project.id)).execute()
    if response.status_code != 200:
        raise Exception("Failed to update project in the database")
    updated_project_data = response.data
    return Project(**updated_project_data)