from pathlib import Path
import aiohttp
import aiofiles
from src.models.base_models import AssetType
from src.utils.file_handling import get_local_path
from src.utils.logger import logger
import os

async def download_video(url: str, output_path: str) -> str:
    try:
        logger.info(f"Starting download of video from {url} to {output_path}")
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_content = await response.read()
                async with aiofiles.open(output_path, 'wb') as file:
                    await file.write(response_content)
        logger.info(f"Video successfully downloaded to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"An error occurred while downloading the video: {e}")
        raise Exception(f"An error occurred while downloading the video: {e}")
        

def save_file_locally(path, file):
    logger.info(f"Saving file locally at {path}")
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wb") as buffer:
        buffer.write(file.file.read())
    logger.info(f"File successfully saved at {path}")
    return path

def determine_asset_type(filename):
    logger.info(f"Determining asset type for file: {filename}")
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
        logger.info(f"File {filename} determined to be of type IMAGE")
        return AssetType.IMAGE
    elif filename.lower().endswith(('.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv')):
        logger.info(f"File {filename} determined to be of type VIDEO")
        return AssetType.VIDEO
    else:
        logger.error(f"Unsupported file type for file: {filename}")
        raise ValueError("Unsupported file type")
    

if __name__ == "__main__":
    import asyncio
    lipsync_video_url = "https://replicate.delivery/pbxt/gtZYuSgzVP4cLlJN4UbNQPeMidXGmxfjflfcLBm9KVbN1czNB/tmpf3393cj9portrait_video_tmpt8saro19t2s_nova.mp4"
    lipsync_video_local_path = get_local_path("1234", "working", f"lipsync_video_sara.mp4")
    lipsync_video_local_path = asyncio.run(download_video(lipsync_video_url, output_path=lipsync_video_local_path))