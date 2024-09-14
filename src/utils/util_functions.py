from pathlib import Path
import aiohttp
import aiofiles
from src.models.base_models import AssetType
from src.utils.file_handling import get_local_path

async def download_video(url: str, output_path: str) -> None:
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_content = await response.read()
            async with aiofiles.open(output_path, 'wb') as file:
                await file.write(response_content)
    return output_path

def save_file_locally(path, file):
    with open(path, "wb") as buffer:
        buffer.write(file.file.read())
    return path

def determine_asset_type(filename):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
        return  AssetType.IMAGE
    elif filename.lower().endswith(('.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv')):
        return AssetType.VIDEO
    else:
        raise ValueError("Unsupported file type")
    

if __name__ == "__main__":
    import asyncio
    lipsync_video_url ="https://replicate.delivery/pbxt/gtZYuSgzVP4cLlJN4UbNQPeMidXGmxfjflfcLBm9KVbN1czNB/tmpf3393cj9portrait_video_tmpt8saro19t2s_nova.mp4"
    lipsync_video_local_path = get_local_path("1234","working",f"lipsync_video_sara.mp4")
    lipsync_video_local_path =asyncio.run(download_video(lipsync_video_url,output_path=lipsync_video_local_path))