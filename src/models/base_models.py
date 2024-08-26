from pydantic import BaseModel, HttpUrl
from typing import List, Optional, enum
from pathlib import Path

class ProductInfo(BaseModel):
    product_id: str
    description: str
    name: str
    # logo: Optional[HttpUrl] = None  # New field for product logo

class DurationOption(enum):
    SHORT = 15
    MEDIUM = 30


class AssetType(enum):
    IMAGE = "image"
    VIDEO = "video"

class Asset(BaseModel):
    asset_url: str
    asset_type: AssetType
    asset_local_path: Optional[Path]

class VideoAssets(BaseModel):
    assets: List[Asset]

class VideoInfo(BaseModel):
    video_id: str
    product_id: str
    duration_limit: DurationOption
    cta: Optional[str] 
    target_audience: Optional[str] 
    script: Optional[str]
    assets: Optional[VideoAssets]
    actual_video_length: Optional[int]


class Actor(BaseModel):
    actor_id: str
    actor_name: str
    original_video_url: str

class Voice(BaseModel):
    voice_id: str
    voice_name: str


# class ReelRequest(BaseModel):
#     product_info: ProductInfo
#     assets: ReelAssets
#     ad_duration: int
#     additional_params: Optional[dict] = None  # For future expansions