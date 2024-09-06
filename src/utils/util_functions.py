import aiohttp
import aiofiles
from src.models.base_models import AssetType

async def download_video(url: str, output_path: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_content = await response.read()
            async with aiofiles.open(output_path, 'wb') as file:
                await file.write(response_content)

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