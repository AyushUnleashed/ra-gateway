from src.models.base_models import VideoLayout
from typing import List
from uuid import UUID
from src.supabase_tools.supabase_client import SUPABASE_CLIENT

def get_layouts_from_db() -> List[VideoLayout]:
    response = SUPABASE_CLIENT.table("layouts").select("*").execute()
    layouts_data = response.data
    return [VideoLayout(**layout) for layout in layouts_data]

def get_layout_from_db(layout_id: UUID) -> VideoLayout:
    response = SUPABASE_CLIENT.table("layouts").select("*").eq("id", str(layout_id)).single().execute()
    layout_data = response.data
    return VideoLayout(**layout_data)