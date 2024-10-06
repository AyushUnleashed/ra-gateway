from src.config import Config
import os

class Constants:
    S3_BUCKET_NAME = "s3_bucket_name"
    LOCAL_STORAGE_BASE_PATH = os.path.join("src", "temp_storage")
    SUPABASE_API_BASE_URL = f"{Config.SUPABASE_URL}/rest/v1"
    SENDER_EMAIL = "support@reelsai.pro"


class TableNames:
    ACTORS = "actors"
    VOICES = "voices"
    PROJECTS = "projects"
    VIDEO_LAYOUTS = "video_layouts"
    PRODUCTS ="products"
    PROJECTS = "projects"
    PROFILES = "profiles"