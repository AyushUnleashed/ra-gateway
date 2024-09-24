from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime
from enum import Enum

# enums
   
class AssetType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"

class ProjectStatus(str, Enum):
    CREATED = "created"
    DRAFT = "draft"
    PROCESSING = "processing"
    AUDIO_READY = "audio_ready"
    LIPSYNC_READY = "lipsync_ready"
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
    url: Optional[Union[str, None]] = None
    squared_video_url: Optional[Union[str,None]] = None
    local_path: Optional[Union[str, None]] = None
    squared_video_local_path: Optional[Union[str,None]] = None
    description: Optional[Union[str, None]] = None


class VideoConfiguration(BaseModel):
    duration: int
    target_audience: str
    cta: str
    direction: str

class Script(BaseModel):
    id: UUID
    title: str
    content: str



 # Reusable entities   

# Product
class ProductBase(BaseModel):
    name: str
    description: str
    product_link: Optional[str] = None
    logo_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class Product(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
  
    def serialize_for_db(self) -> Dict[str, Any]:
        data = self.model_dump()
        # Convert str objects to strings
        for field in ['product_link', 'thumbnail_url', 'logo_url']:
            if data[field] is not None:
                data[field] = str(data[field])
        
        # Convert UUID to string
        data['id'] = str(data['id'])
        
        # Convert datetime objects to ISO format strings
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()
        
        return data

# Actor
class ActorBase(BaseModel):
    name: str
    gender:str
    full_video_link: str
    thumbnail_image_url: Optional[str]
    default_voice_id: UUID

class Actor(ActorBase):
    id: UUID


# Voice
class VoiceBase(BaseModel):
    name: str
    gender: str
    voice_identifier: OpenAIVoiceIdentifier
    sample_audio_url: Optional[str]=None

class Voice(VoiceBase):
    id: UUID

# VideoLayout
class VideoLayoutBase(BaseModel):
    name: str
    description: Optional[str]
    thumbnail_url: Optional[str]

class VideoLayout(VideoLayoutBase):
    id: UUID
    
    
class Project(BaseModel):
    id: UUID
    product_id: UUID
    user_id: UUID
    product_base: ProductBase
    status: ProjectStatus
    assets: List[Asset] = []
    created_at: datetime
    updated_at: datetime
    final_script: Optional[str] = None
    video_configuration: Optional[VideoConfiguration] = None
    script: Optional[Script] = None
    actor_id: Optional[UUID] = None
    actor_base: Optional[ActorBase] = None
    voice_id: Optional[UUID] = None
    voice_base: Optional[VoiceBase] = None
    video_layout_id: Optional[UUID] = None
    video_layout_base: Optional[VideoLayoutBase] = None
    t2s_audio_url: Optional[str] = None
    lipsync_prediction_id: Optional[str] = None
    lipsync_video_url: Optional[str] = None
    final_video_duration: Optional[float] = None
    final_video_url: Optional[str] = None

    def serialize_for_db(self) -> Dict[str, Any]:
        data = self.dict()
        
        # Convert UUID to string
        data['id'] = str(data['id'])
        data['product_id'] = str(data['product_id'])
        if data['actor_id'] is not None:
            data['actor_id'] = str(data['actor_id'])
        if data['voice_id'] is not None:
            data['voice_id'] = str(data['voice_id'])
        if data['video_layout_id'] is not None:
            data['video_layout_id'] = str(data['video_layout_id'])
        
        # Convert datetime objects to ISO format strings
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()
        
        # Convert str objects to strings
        if data['lipsync_video_url'] is not None:
            data['lipsync_video_url'] = str(data['lipsync_video_url'])
        if data['final_video_url'] is not None:
            data['final_video_url'] = str(data['final_video_url'])
        
        # Convert nested objects to JSON serializable dictionaries
        if data['product_base'] is not None:
            data['product_base'] = data['product_base'].dict()
        if data['video_configuration'] is not None:
            data['video_configuration'] = data['video_configuration'].dict()
        if data['script'] is not None:
            data['script'] = data['script'].dict()
        if data['actor_base'] is not None:
            data['actor_base'] = data['actor_base'].dict()
        if data['voice_base'] is not None:
            data['voice_base'] = data['voice_base'].dict()
        if data['video_layout_base'] is not None:
            data['video_layout_base'] = data['video_layout_base'].dict()
        
        return data

    
 