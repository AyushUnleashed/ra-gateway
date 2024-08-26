from moviepy.editor import ImageClip, concatenate_videoclips
from src.models.base_models import VideoAssets, AssetType

def generate_background_video_using_assets(video_assets: VideoAssets, video_length: int):
    image_clips = []
    num_assets = len(video_assets.assets)
    time_per_image = video_length / num_assets

    for asset in video_assets.assets:
        if asset.asset_type == AssetType.IMAGE:
            image_clip = ImageClip(str(asset.asset_local_path)).set_duration(time_per_image)
            image_clips.append(image_clip)

    background_video = concatenate_videoclips(image_clips, method="compose")
    output_path = "assets/background_video.mp4"
    background_video.write_videofile(output_path, codec="libx264")

    return output_path