from src.models.base_models import VideoLayout
from typing import List
from uuid import UUID
from src.supabase_tools.supabase_client import SUPABASE_CLIENT
from src.utils.constants import TableNames
from src.utils.logger import logger

def get_layouts_from_db() -> List[VideoLayout]:
    response = SUPABASE_CLIENT.table(TableNames.VIDEO_LAYOUTS).select("*").execute()
    layouts_data = response.data
    return [VideoLayout(**layout) for layout in layouts_data]

def get_layout_from_db(layout_id: UUID) -> VideoLayout:
    response = SUPABASE_CLIENT.table(TableNames.VIDEO_LAYOUTS).select("*").eq("id", str(layout_id)).single().execute()
    layout_data = response.data
    return VideoLayout(**layout_data)

if __name__ == "__main__":
    layouts = get_layouts_from_db()
    logger.info(f"Retrieved {len(layouts)} layouts from the database.")
    
    if layouts:
        layout_id = layouts[0].id
        layout = get_layout_from_db(layout_id)
        logger.info(f"Retrieved layout with ID {layout_id}: {layout}")