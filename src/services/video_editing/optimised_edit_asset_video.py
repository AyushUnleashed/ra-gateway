import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List
from functools import partial
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, ColorClip
from moviepy.video.io.ffmpeg_writer import FFMPEG_VideoWriter
from src.models.base_models import AspectRatio, Asset, AssetType

# Thread pool for CPU-bound tasks
thread_pool = ThreadPoolExecutor()

async def edit_asset_video(assets: List[Asset], final_video_length: int, aspect_ratio: AspectRatio, asset_edited_video_path: str) -> str:
    try:
        if aspect_ratio == AspectRatio.SQUARE.value:
            width, height = 1080, 1080
        elif aspect_ratio == AspectRatio.NINE_SIXTEEN.value:
            width, height = 1080, 1920
        else:
            raise ValueError("Unsupported aspect ratio")

        asset_duration = final_video_length / len(assets)
        background_color = (245, 243, 242)

        # Process assets concurrently using asyncio
        clip_params_list = await asyncio.gather(*[
            process_asset(asset, asset_duration, width, height)
            for asset in assets
        ])

        clip_params_list = [params for params in clip_params_list if params is not None]

        if not clip_params_list:
            raise ValueError("No valid clips to concatenate")

        # Create clips using thread pool for CPU-bound tasks
        background = ColorClip(size=(width, height), color=background_color, duration=asset_duration)
        clips = await asyncio.gather(*[
            asyncio.to_thread(create_composite_clip, params, background, width, height)
            for params in clip_params_list
        ])

        # Concatenate clips (CPU-bound task)
        final_clip = await asyncio.to_thread(concatenate_videoclips, clips, method="compose")

        # Use FFMPEG_VideoWriter for faster encoding
        os.makedirs(os.path.dirname(asset_edited_video_path), exist_ok=True)
        writer = FFMPEG_VideoWriter(asset_edited_video_path, final_clip.size, final_clip.fps, codec="libx264", preset="faster", bitrate="2000k")

        # Write frames using thread pool
        await asyncio.to_thread(write_frames, writer, final_clip)

        writer.close()

        # Clean up resources
        await asyncio.gather(*[asyncio.to_thread(clip.close) for clip in clips])
        await asyncio.to_thread(final_clip.close)
        await asyncio.to_thread(background.close)

        return asset_edited_video_path
    except Exception as e:
        print(f"An error occurred while editing the asset video: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise

async def process_asset(asset: Asset, asset_duration: float, width: int, height: int) -> dict:
    try:
        if asset.type == AssetType.VIDEO:
            clip = await asyncio.to_thread(VideoFileClip, asset.local_path, audio=False)
            if clip.duration < asset_duration:
                clip = await asyncio.to_thread(clip.loop, duration=asset_duration)
            else:
                clip = await asyncio.to_thread(clip.subclip, 0, asset_duration)
        elif asset.type == AssetType.IMAGE:
            clip = await asyncio.to_thread(ImageClip, asset.local_path)
            clip = await asyncio.to_thread(clip.set_duration, asset_duration)
        else:
            print(f"Warning: Unsupported asset type: {asset.type}. Skipping this asset.")
            return None

        clip_aspect_ratio = clip.w / clip.h
        if clip_aspect_ratio > width / height:
            new_width = width
            new_height = int(width / clip_aspect_ratio)
        else:
            new_height = height
            new_width = int(height * clip_aspect_ratio)

        clip_params = {
            'clip': clip,
            'resize': (new_width, new_height),
            'position': ("center", "center"),
            'duration': asset_duration
        }

        return clip_params
    except Exception as e:
        print(f"Error processing asset {asset.id}: {str(e)}")
        return None

def create_composite_clip(clip_params: dict, background: ColorClip, width: int, height: int) -> CompositeVideoClip:
    clip = clip_params['clip']
    clip = clip.resize(newsize=clip_params['resize'])
    clip = clip.set_position(clip_params['position'])

    composite_clip = CompositeVideoClip([background.copy(), clip], size=(width, height))
    composite_clip = composite_clip.set_duration(clip_params['duration'])

    return composite_clip

def write_frames(writer, clip):
    for frame in clip.iter_frames(fps=clip.fps, dtype="uint8"):
        writer.write_frame(frame)