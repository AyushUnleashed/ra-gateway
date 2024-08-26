from pydantic import BaseModel
from typing import Optional
from src.models.base_models import ProductInfo, VideoInfo, VideoAssets

class AddProductRequest(BaseModel):
    name: str
    description: str
    logo: Optional[str] = None # New field for product logo
    product_images: Optional[str] = None # New field for product images

class SetVideoInfoRequest(BaseModel):
    video_info: VideoInfo
    video_assets: VideoAssets