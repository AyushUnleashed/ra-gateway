from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
from enum import Enum
from typing import List
from src.models.base_models import Asset
from src.utils.constants import Constants
from src.models.base_models import AspectRatio, AssetType


async def edit_asset_video(assets: List[Asset], final_video_length: int, aspect_ratio: AspectRatio) -> str:
    # Determine the dimensions based on the aspect ratio
    if aspect_ratio == AspectRatio.SQUARE:
        width, height = 1080, 1080
    elif aspect_ratio == AspectRatio.NINE_SIXTEEN:
        width, height = 1080, 1920
    else:
        raise ValueError("Unsupported aspect ratio")

    # Calculate the duration each asset should appear
    asset_duration = final_video_length / len(assets)

    clips = []
    for asset in assets:
        if asset.type == AssetType.VIDEO:
            video_clip = VideoFileClip(asset.local_path).subclip(0, asset_duration)
            video_clip = video_clip.resize(height=height).set_position(("center", "center")).margin(left=0, right=0, top=(height - video_clip.h) // 2, bottom=(height - video_clip.h) // 2, color=(0, 0, 0))
            clips.append(video_clip)
        elif asset.type == AssetType.IMAGE:
            image_clip = ImageClip(asset.local_path, duration=asset_duration)
            image_clip = image_clip.resize(height=height).set_position(("center", "center")).margin(left=0, right=0, top=(height - image_clip.h) // 2, bottom=(height - image_clip.h) // 2, color=(0, 0, 0))
            clips.append(image_clip)
        else:
            raise ValueError(f"Unsupported asset type: {asset.type}")

    # Concatenate all the clips
    final_clip = concatenate_videoclips(clips, method="compose")

    # Define the output path
    asset_edited_video_path = f"{Constants.LOCAL_STORAGE_BASE_PATH}/working/asset_edited_video_{aspect_ratio}.mp4"

    # Write the final video to a file
    final_clip.write_videofile(asset_edited_video_path, codec="libx264", fps=25)

    # Close all clips
    for clip in clips:
        clip.close()

    return asset_edited_video_path
if __name__ == "__main__":
    import asyncio
    from src.models.base_models import Asset, AspectRatio, AssetType

    # Create example assets
    assets = [
        Asset(type=AssetType.IMAGE, local_path="src/temp_storage/test_project_id/assets/hero_section.jpg", url="http://example.com/hero_section.jpg", description="Hero section image"),
        Asset(type=AssetType.IMAGE, local_path="src/temp_storage/test_project_id/assets/create.jpg", url="http://example.com/create.jpg", description="Create image"),
        Asset(type=AssetType.IMAGE, local_path="src/temp_storage/test_project_id/assets/plan.jpg", url="http://example.com/plan.jpg", description="Plan image"),
        Asset(type=AssetType.IMAGE, local_path="src/temp_storage/test_project_id/assets/optimise.jpg", url="http://example.com/optimise.jpg", description="Optimise image"),
        Asset(type=AssetType.IMAGE, local_path="src/temp_storage/test_project_id/assets/interlink.jpg", url="http://example.com/interlink.jpg", description="Interlink image"),
        Asset(type=AssetType.IMAGE, local_path="src/temp_storage/test_project_id/assets/image.jpg", url="http://example.com/image.jpg", description="Image")
    ]

    # Define final video length and aspect ratio
    final_video_length = 26  # seconds
    aspect_ratio = AspectRatio.SQUARE

    # Run the edit_asset_video function
    edited_video_path = asyncio.run(edit_asset_video(assets, final_video_length, aspect_ratio))
    print(f"Edited video saved at: {edited_video_path}")
