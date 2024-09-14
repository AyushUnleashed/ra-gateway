from src.supabase_tools.supabase_client import SUPABASE_CLIENT
from supabase import StorageException
from typing import Optional
import asyncio
import os

BUCKET_NAME = "prod-bucket"

def upload_file(local_path: str, supabase_path: str, content_type: Optional[str] = None) -> str:
    """
    Upload a single file to Supabase storage.
    
    :param local_path: Local path of the file to upload
    :param supabase_path: Path where the file will be stored in Supabase
    :param content_type: MIME type of the file (optional)
    :return: Public URL of the uploaded file
    """
    with open(local_path, 'rb') as file:
        file_options = {"content-type": content_type} if content_type else None
        try:
            SUPABASE_CLIENT.storage.from_(BUCKET_NAME).upload(
                path=supabase_path,
                file=file,
                file_options=file_options
            )
        except StorageException as e:
            if e.args[0].get('statusCode') == 400 and e.args[0].get('error') == 'Duplicate':
                print(f"File already exists at {supabase_path}, updating...")
                SUPABASE_CLIENT.storage.from_(BUCKET_NAME).update(
                    path=supabase_path,
                    file=file,
                    file_options=file_options
                )
            else:
                raise e
    
    return get_public_url(supabase_path)

def upload_file_to_projects(project_id: str, local_path: str, content_type: Optional[str] = None) -> str:
    """
    Upload a file to the 'projects' directory in Supabase storage.
    
    :param project_id: ID of the project
    :param local_path: Local path of the file to upload
    :param content_type: MIME type of the file (optional)
    :return: Public URL of the uploaded file
    """
     # Ensure forward slashes and no double slashes
    supabase_path = f"projects/{str(project_id)}/{os.path.basename(local_path)}"
    supabase_path = supabase_path.replace("\\", "/").replace("//", "/")
    
    print(f"Uploading to Supabase path: {supabase_path}")  # Debug print
    
    return upload_file(local_path, supabase_path, content_type)


def get_public_url(file_path: str) -> str:
    """
    Get the public URL of a file in Supabase storage.
    
    :param file_path: Path of the file in Supabase storage
    :return: Public URL of the file
    """
    try:
        return SUPABASE_CLIENT.storage.from_(BUCKET_NAME).get_public_url(file_path)
    except Exception as e:
        print(f"Error getting public URL for {file_path}: {str(e)}")
        return ""


# if __name__ == '__main__':
#     user_id = "123_1"
#     asyncio.run(handle_supabase_upload('free-user-images',f'image_generator/user_content/image_id_{user_id}/face_swap_{user_id}/fs_{user_id}.png',f'user_{user_id}/user_image.png'))


if __name__ == '__main__':
    project_id = "9b4d6fe4-b6cd-4175-8b9d-8202e863a448"
    local_file_path = "src/temp_storage/9b4d6fe4-b6cd-4175-8b9d-8202e863a448/working/lipsync_video_Sara.mp4"
    content_type = "video/mp4"
    
    public_url = upload_file_to_projects(project_id, local_file_path, content_type)
    print(f"Uploaded file is accessible at: {public_url}")
