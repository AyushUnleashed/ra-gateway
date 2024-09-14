from src.config import Config

class Constants:
    S3_BUCKET_NAME = "s3_bucket_name"
    LOCAL_STORAGE_BASE_PATH = "src/temp_storage"
    SUPABASE_API_BASE_URL = f"{Config.SUPABASE_URL}/rest/v1"


class TableNames:
    ACTORS = "actors"
    VOICES = "voices"
    PROJECTS = "projects"
    VIDEO_LAYOUTS = "video_layouts"
    PRODUCTS ="products"