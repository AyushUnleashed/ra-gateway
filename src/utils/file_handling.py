import os
from pathlib import Path
from typing import Union
from supabase import create_client, Client
from src.utils.logger import logger  # Import the logger

# Constants for local paths
class LocalPaths:
    TEMP_STORAGE = os.path.join("src", "temp_storage")
    ASSETS = "assets"
    WORKING = "working"

# Constants for Supabase paths
class SupabasePaths:
    ACTORS = "actors"
    PRODUCTS = "products"
    VOICES = "voices"
    PROJECTS = "projects"

def get_local_path(project_id: str, folder_type: str, filename: str) -> str:
    """
    Generate a local file path based on the project ID and file type.
    """
    logger.info(f"Generating local path for project_id: {project_id}, folder_type: {folder_type}, filename: {filename}")
    base_path = os.path.join(LocalPaths.TEMP_STORAGE, str(project_id))
    if folder_type == LocalPaths.ASSETS:
        path = str(os.path.join(base_path, LocalPaths.ASSETS, filename))
    elif folder_type == LocalPaths.WORKING:
        path = str(os.path.join(base_path, LocalPaths.WORKING, filename))
    else:
        logger.error(f"Invalid folder type: {folder_type}")
        raise ValueError(f"Invalid folder type: {folder_type}")
    logger.info(f"Generated local path: {path}")
    return path
    
def save_local_file(project_id: str, folder_type: str, filename: str, content: Union[str, bytes]):
    """
    Save a file to the local storage.
    """
    logger.info(f"Saving file locally for project_id: {project_id}, folder_type: {folder_type}, filename: {filename}")
    file_path = get_local_path(project_id, folder_type, filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    mode = "wb" if isinstance(content, bytes) else "w"
    with open(file_path, mode) as f:
        f.write(content)
    logger.info(f"File saved locally at: {file_path}")

def get_supabase_path(category: str, id: str, filename: str) -> str:
    """
    Generate a Supabase storage path based on the category and ID.
    """
    logger.info(f"Generating Supabase path for category: {category}, id: {id}, filename: {filename}")
    path = f"{category}/{id}/{filename}"
    logger.info(f"Generated Supabase path: {path}")
    return path

# def upload_to_supabase(local_path: Union[str, Path], category: str, id: str, filename: str):
#     """
#     Upload a file from local storage to Supabase bucket.
#     """
#     with open(local_path, "rb") as f:
#         file_contents = f.read()
    
#     supabase_path = get_supabase_path(category, id, filename)
#     supabase.storage.from_("main").upload(supabase_path, file_contents)