from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, ColorClip
from enum import Enum
from typing import List
from src.models.base_models import Asset
from src.utils.constants import Constants
from src.models.base_models import AspectRatio, AssetType
import os
import numpy as np
from PIL import Image, ImageDraw
from src.utils.logger import logger

# def create_rounded_corner_mask(size, radius):
#     mask = Image.new('L', size, 255)  # Start with a white (fully opaque) background
#     draw = ImageDraw.Draw(mask)
#     draw.rounded_rectangle([(0, 0), size], radius, fill=0)  # Draw black (transparent) rounded corners
#     return ImageClip(np.array(mask), ismask=True)  # Convert to MoviePy ImageClip directly

# def apply_rounded_corners(clip, radius):
#     mask = create_rounded_corner_mask((clip.w, clip.h), radius)
#     return clip.set_mask(mask)

def save_intermediate_clip(clip, filename, fps=25):
    output_path = os.path.join(Constants.LOCAL_STORAGE_BASE_PATH, "debug", filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    logger.debug(f"Saving intermediate clip to {output_path}")
    clip.write_videofile(output_path, codec="libx264", fps=fps)

async def edit_asset_video(assets: List[Asset], final_video_length: int, aspect_ratio: AspectRatio, asset_edited_video_path: str) -> str:
    try:
        logger.info("Starting asset editing process")
        if aspect_ratio == AspectRatio.SQUARE.value:
            width, height = 1080, 1080
        elif aspect_ratio == AspectRatio.NINE_SIXTEEN.value:
            width, height = 1080, 1920
        else:
            logger.error("Unsupported aspect ratio")
            raise ValueError("Unsupported aspect ratio")

        asset_duration = final_video_length / len(assets)
        background_color = (245, 243, 242)
        background = ColorClip(size=(width, height), color=background_color, duration=asset_duration)

        clips = []
        for index, asset in enumerate(assets):
            try:
                logger.debug(f"Processing asset {index}: {asset.local_path}")
                if asset.type == AssetType.VIDEO:
                    clip = VideoFileClip(asset.local_path).without_audio()
                    if clip.duration < asset_duration:
                        clip = clip.loop(duration=asset_duration)
                    else:
                        clip = clip.subclip(0, asset_duration)

                elif asset.type == AssetType.IMAGE:
                    clip = ImageClip(asset.local_path).set_duration(asset_duration)
                else:
                    logger.warning(f"Unsupported asset type: {asset.type}. Skipping this asset.")
                    continue

                clip_aspect_ratio = clip.w / clip.h
                if clip_aspect_ratio > width / height:
                    new_width = width
                    new_height = int(width / clip_aspect_ratio)
                else:
                    new_height = height
                    new_width = int(height * clip_aspect_ratio)

                clip = clip.resize(newsize=(new_width, new_height))
        
                
                clip = clip.set_position(("center", "center"))
            

                composite_clip = CompositeVideoClip([background.copy(), clip], size=(width, height))
                composite_clip = composite_clip.set_duration(asset_duration)
                clips.append(composite_clip)
            except Exception as e:
                logger.error(f"Error processing asset {index}: {str(e)}")
                import traceback
                logger.debug(traceback.format_exc())
                continue

        if not clips:
            logger.error("No valid clips to concatenate")
            raise ValueError("No valid clips to concatenate")

        final_clip = concatenate_videoclips(clips, method="compose")
        os.makedirs(os.path.dirname(asset_edited_video_path), exist_ok=True)
        logger.info(f"Writing final video to {asset_edited_video_path}")
        final_clip.write_videofile(asset_edited_video_path, codec="libx264", fps=25)

        final_clip.close()
        for clip in clips:
            clip.close()
        background.close()

        logger.info("Video editing process completed successfully")
        return asset_edited_video_path
    except Exception as e:
        logger.error(f"An error occurred while editing the asset video: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        raise

if __name__ == "__main__":
    import asyncio
    from src.models.base_models import Asset, AspectRatio, AssetType

    # Create example assets
    assets_folder = "src/temp_storage/a34b03d2-7190-45cc-b2e7-01e347b18675/assets"
    assets = []

    for filename in os.listdir(assets_folder):
        if filename.endswith((".jpg", ".jpeg", ".png", ".mp4", ".mov")):
            local_path = os.path.join(assets_folder, filename)
            if filename.endswith((".jpg", ".jpeg", ".png")):
                asset_type = AssetType.IMAGE
                description = f"{filename.split('.')[0]} image"
            else:
                asset_type = AssetType.VIDEO
                description = f"{filename.split('.')[0]} video"
            
            asset = Asset(
                type=asset_type,
                local_path=local_path,
                url=f"http://example.com/{filename}",
                description=description
            )
            assets.append(asset)

    # Define final video length and aspect ratio
    final_video_length = 19  # seconds
    aspect_ratio = AspectRatio.SQUARE

    # Run the edit_asset_video function
    logger.info("Running the edit_asset_video function")
    edited_video_path = asyncio.run(edit_asset_video(assets, final_video_length, aspect_ratio))
    logger.info(f"Edited video saved at: {edited_video_path}")