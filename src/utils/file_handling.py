import os
from pathlib import Path
from typing import Union
from supabase import create_client, Client

# Constants for local paths
class LocalPaths:
    TEMP_STORAGE = Path("src/temp_storage")
    ASSETS = "assets"
    WORKING = "working"

# Constants for Supabase paths
class SupabasePaths:
    ACTORS = "actors"
    PRODUCTS = "products"
    VOICES = "voices"
    PROJECTS = "projects"

def get_local_path(project_id: str, folder_type: str, filename: str) -> Path:
    """
    Generate a local file path based on the project ID and file type.
    """
    base_path = LocalPaths.TEMP_STORAGE / project_id
    if folder_type == LocalPaths.ASSETS:
        return base_path / LocalPaths.ASSETS / filename
    elif folder_type == LocalPaths.ASSETS:
        return base_path / LocalPaths.WORKING / filename
    else:
        raise ValueError(f"Invalid folder type: {folder_type}")
    
def save_local_file(project_id: str, folder_type: str, filename: str, content: Union[str, bytes]):
    """
    Save a file to the local storage.
    """
    file_path = get_local_path(project_id, folder_type, filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    mode = "wb" if isinstance(content, bytes) else "w"
    with open(file_path, mode) as f:
        f.write(content)

def get_supabase_path(category: str, id: str, filename: str) -> str:
    """
    Generate a Supabase storage path based on the category and ID.
    """
    return f"{category}/{id}/{filename}"

# def upload_to_supabase(local_path: Union[str, Path], category: str, id: str, filename: str):
#     """
#     Upload a file from local storage to Supabase bucket.
#     """
#     with open(local_path, "rb") as f:
#         file_contents = f.read()
    
#     supabase_path = get_supabase_path(category, id, filename)
#     supabase.storage.from_("main").upload(supabase_path, file_contents)