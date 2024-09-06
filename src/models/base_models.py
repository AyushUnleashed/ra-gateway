from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime
from enum import Enum

# enums
   
class AssetType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DurationOption(int,Enum):
    SHORT = 15
    MEDIUM = 30

class OpenAIVoiceIdentifier(str, Enum):
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"

class VideoLayoutType(str, Enum):
    TOP_BOTTOM = "TOP_BOTTOM"
    AVATAR_BUBBLE = "AVATAR_BUBBLE"

class AspectRatio(str, Enum):
    SQUARE = "1:1"
    NINE_SIXTEEN = "9:16"

# temporary entites.
class Asset(BaseModel):
    type: AssetType
    url: Optional[HttpUrl]
    local_path: Optional[str]
    description: Optional[str]


class VideoConfiguration(BaseModel):
    duration: int
    target_audience: str
    cta: str
    direction: str

class Script(BaseModel):
    title: str
    content: str



 # Reusable entities   

# Product
class ProductBase(BaseModel):
    name: str
    description: str
    product_link: Optional[HttpUrl]
    logo_url: Optional[HttpUrl]

class Product(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

# Actor
class ActorBase(BaseModel):
    name: str
    gender:str
    full_video_link: HttpUrl
    thumbnail_image_url: HttpUrl
    default_voice_id: UUID

class Actor(ActorBase):
    id: UUID


# Voice
class VoiceBase(BaseModel):
    name: str
    gender: str
    voice_identifier: OpenAIVoiceIdentifier

class Voice(VoiceBase):
    id: UUID

# VideoLayout
class VideoLayoutBase(BaseModel):
    name: str
    description: Optional[str]
    thumbnail_url: Optional[HttpUrl]

class VideoLayout(VideoLayoutBase):
    id: UUID
    
    
class Project(BaseModel):
    id: UUID
    product_id: UUID
    product_base: ProductBase
    video_configuration: Optional[VideoConfiguration]
    script: Optional[Script]
    actor_id: Optional[UUID]
    actor_base: Optional[ActorBase]
    voice_id: Optional[UUID]
    voice_base: Optional[VoiceBase]
    video_layout_id: Optional[UUID]
    video_layout_base: Optional[VideoLayoutBase]
    lipsync_video_url: Optional[HttpUrl]
    final_video_duration: Optional[float]
    final_video_url: Optional[HttpUrl]
    status: ProjectStatus
    assets: List[Asset] = []
    created_at: datetime
    updated_at: datetime
    
 