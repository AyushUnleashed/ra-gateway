from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, ColorClip
from enum import Enum
from typing import List
from src.models.base_models import Asset
from src.utils.constants import Constants
from src.models.base_models import AspectRatio, AssetType
import os
import numpy as np
from PIL import Image, ImageDraw

def create_rounded_corner_mask(size, radius):
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), size], radius, fill=255)
    return mask

def apply_rounded_corners(clip, radius):
    mask = create_rounded_corner_mask((clip.w, clip.h), radius)
    return clip.set_mask(ImageClip(np.array(mask), ismask=True))

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

    # Create the background clip (off-white color)
    background_color = (245, 243, 242)
    background = ColorClip(size=(width, height), color=background_color, duration=asset_duration)

    clips = []
    for index, asset in enumerate(assets):
        try:
            if asset.type == AssetType.VIDEO:
                clip = VideoFileClip(asset.local_path).without_audio()
                if clip.duration < asset_duration:
                    clip = clip.loop(duration=asset_duration)
                else:
                    clip = clip.subclip(0, asset_duration)
            elif asset.type == AssetType.IMAGE:
                clip = ImageClip(asset.local_path).set_duration(asset_duration)
            else:
                print(f"Warning: Unsupported asset type: {asset.type}. Skipping this asset.")
                continue

            # Resize the clip to fit within the frame while maintaining aspect ratio
            clip_aspect_ratio = clip.w / clip.h
            if clip_aspect_ratio > width / height:
                new_width = width
                new_height = int(width / clip_aspect_ratio)
            else:
                new_height = height
                new_width = int(height * clip_aspect_ratio)

            clip = clip.resize(newsize=(new_width, new_height))
            
            # Apply rounded corners to the resized clip
            clip = apply_rounded_corners(clip, radius=20)

            # Center the clip
            clip = clip.set_position(("center", "center"))

            # Create a composite clip with the background and the rounded asset clip
            composite_clip = CompositeVideoClip([background.copy(), clip], size=(width, height))
            composite_clip = composite_clip.set_duration(asset_duration)
            
            clips.append(composite_clip)
        except Exception as e:
            print(f"Error processing asset {index}: {str(e)}")
            import traceback
            print(traceback.format_exc())
            continue

    if not clips:
        raise ValueError("No valid clips to concatenate")

    # Concatenate all the clips
    final_clip = concatenate_videoclips(clips, method="compose")

    # Define the output path
    asset_edited_video_path = str(os.path.join(Constants.LOCAL_STORAGE_BASE_PATH, "working", f"asset_edited_video_{aspect_ratio}.mp4"))

    # Ensure the folder exists
    os.makedirs(os.path.dirname(asset_edited_video_path), exist_ok=True)

    # Write the final video to a file
    final_clip.write_videofile(asset_edited_video_path, codec="libx264", fps=25)

    # Close all clips
    final_clip.close()
    for clip in clips:
        clip.close()
    background.close()

    return asset_edited_video_path

if __name__ == "__main__":
    import asyncio
    from src.models.base_models import Asset, AspectRatio, AssetType

    # Create example assets
    assets_folder = "src/temp_storage/0da6b88d-a06e-4741-adcb-75ef1a67ef6c/assets"
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
    final_video_length = 26  # seconds
    aspect_ratio = AspectRatio.SQUARE

    # Run the edit_asset_video function
    edited_video_path = asyncio.run(edit_asset_video(assets, final_video_length, aspect_ratio))
    print(f"Edited video saved at: {edited_video_path}")