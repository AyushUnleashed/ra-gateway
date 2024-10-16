from moviepy.editor import ImageClip, concatenate_videoclips
from src.models.base_models import VideoAssets, AssetType
from src.utils.logger import logger

def generate_background_video_using_assets(video_assets: VideoAssets, video_length: int):
    logger.info("Starting background video generation using assets.")
    image_clips = []
    num_assets = len(video_assets.assets)
    time_per_image = video_length / num_assets
    logger.debug(f"Number of assets: {num_assets}, Time per image: {time_per_image}")

    for asset in video_assets.assets:
        if asset.asset_type == AssetType.IMAGE:
            logger.debug(f"Processing image asset: {asset.asset_local_path}")
            image_clip = ImageClip(str(asset.asset_local_path)).set_duration(time_per_image)
            image_clips.append(image_clip)

    logger.info("Concatenating image clips to create background video.")
    background_video = concatenate_videoclips(image_clips, method="compose")
    output_path = "assets/background_video.mp4"
    logger.info(f"Writing background video to file: {output_path}")
    background_video.write_videofile(output_path, codec="libx264")

    logger.info("Background video generation completed successfully.")
    return output_path