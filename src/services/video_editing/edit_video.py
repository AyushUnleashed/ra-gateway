from uuid import UUID
import requests
from typing import List
from src.models.base_models import Asset, VideoLayoutType, AspectRatio
from src.utils.constants import Constants
from src.utils.util_functions import download_video
import os
from src.services.video_editing.combine_videos import combine_videos_vertically

from src.services.video_editing.edit_asset_video import edit_asset_video


from src.utils.file_handling import get_local_path
# def process_assets(assets: List[Asset]) -> List[str]:
#     return [asset.local_path for asset in assets if asset.local_path]

async def edit_final_video(lipsync_video_local_path: str, final_video_path: str, layout_type: VideoLayoutType, assets: List[Asset], final_video_duration: int, project_id:UUID) -> str:
    try:
        # Verify paths are not null
        if not lipsync_video_local_path or not os.path.exists(lipsync_video_local_path) or os.path.getsize(lipsync_video_local_path) < 1024:
            raise ValueError("Lipsync video local path is null, empty, or the file is too small (possibly corrupt)")
        if not final_video_path:
            raise ValueError("Final video path is null or empty")

        aspect_ratio = AspectRatio.NINE_SIXTEEN.value
        asset_edited_video_path  = get_local_path(project_id,"working", f"asset_edited_video_{AspectRatio.NINE_SIXTEEN}.mp4")

        # Call function to edit the video
        asset_video_path = await edit_asset_video(
            assets=assets,
            final_video_length=final_video_duration, 
            aspect_ratio=aspect_ratio,
            asset_edited_video_path =asset_edited_video_path
        )

        if layout_type == VideoLayoutType.TOP_BOTTOM.value:
            combine_videos_vertically(
                top_video_path=asset_video_path,
                bottom_video_path=lipsync_video_local_path,
                output_path=final_video_path,
            )
            return final_video_path
        else:
            raise Exception("Unsupported layout type")
    except Exception as e:
        raise Exception(f"An error occurred while editing the final video: {e}")
