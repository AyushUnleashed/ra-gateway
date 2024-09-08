import requests
from typing import List
from src.models.base_models import Asset, VideoLayoutType, AspectRatio
from src.utils.constants import Constants
from src.utils.util_functions import download_video

from src.services.video_editing.combine_videos import combine_videos_vertically

from src.services.video_editing.edit_asset_video import edit_asset_video


from src.utils.file_handling import get_local_path
# def process_assets(assets: List[Asset]) -> List[str]:
#     return [asset.local_path for asset in assets if asset.local_path]

async def edit_final_video(lipsync_video_local_path: str, layout_type: VideoLayoutType, assets: List[Asset], final_video_duration:int) -> None:
    
    # Call function to edit the video (assuming a function named `edit_video` exists)
    asset_video_path = edit_asset_video(
        assets=assets,
        final_video_length=final_video_duration, 
        aspect_ratio=AspectRatio.NINE_SIXTEEN
    )

    final_video_path = f"{Constants.LOCAL_STORAGE_BASE_PATH}/working/final_video.mp4"
    combine_videos_vertically(
        video1=lipsync_video_local_path,
        video2=asset_video_path,
        output_path=final_video_path,
    )

    return final_video_path
