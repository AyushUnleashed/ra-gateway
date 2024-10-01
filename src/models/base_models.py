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
    ACTOR_GENERATION_STARTED = "actor_generation_started"
    ACTOR_GENERATION_FAILED = "actor_generation_failed"
    ACTOR_GENERATION_COMPLETED = "actor_generation_completed"
    ACTOR_GENERATION_CANCELLED= "actor_generation_cancelled"
    
    COMPLETED = "completed"
    FAILED = "failed"
    TEST = "test"

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
    local_path: Optional[Union[str, None]] = None
    description: Optional[Union[str, None]] = None

    def serialize_for_db(self) -> Dict[str, Any]:
        data = self.model_dump(exclude={"local_path"})
        # Convert enum to its value
        data['type'] = data['type'].value
        return data


class VideoConfiguration(BaseModel):
    duration: int
    target_audience: str
    cta: str
    direction: str

    def serialize_for_db(self) -> Dict[str, Any]:
        return self.model_dump()

class Script(BaseModel):
    id: UUID
    title: str
    content: str

    def serialize_for_db(self) -> Dict[str, Any]:
        data = self.model_dump()
        # Convert UUID to string
        data['id'] = str(data['id'])
        return data



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
    user_id: UUID
    created_at: datetime
    updated_at: datetime
  
    def serialize_for_db(self) -> Dict[str, Any]:
        data = self.model_dump()
        # Convert UUID to string
        data['id'] = str(data['id'])
        data['user_id'] = str(data['user_id'])
        
        # Convert datetime objects to ISO format strings
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()
        
        return data

# Actor
class ActorBase(BaseModel):
    name: str
    gender: str
    full_video_link: str
    thumbnail_image_url: Optional[str]
    default_voice_id: UUID

class Actor(ActorBase):
    id: UUID

    def serialize_for_db(self) -> Dict[str, Any]:
        data = self.model_dump()
        # Convert UUID to string
        data['id'] = str(data['id'])
        data['default_voice_id'] = str(data['default_voice_id'])
        return data


# Voice
class VoiceBase(BaseModel):
    name: str
    gender: str
    voice_identifier: OpenAIVoiceIdentifier
    sample_audio_url: Optional[str] = None

class Voice(VoiceBase):
    id: UUID

    def serialize_for_db(self) -> Dict[str, Any]:
        data = self.model_dump()
        # Convert UUID to string
        data['id'] = str(data['id'])
        # Convert Enum to string
        data['voice_identifier'] = data['voice_identifier'].value
        return data

# VideoLayout
class VideoLayoutBase(BaseModel):
    name: str
    description: Optional[str]
    thumbnail_url: Optional[str]

class VideoLayout(VideoLayoutBase):
    id: UUID

    def serialize_for_db(self) -> Dict[str, Any]:
        data = self.model_dump()
        # Convert UUID to string
        data['id'] = str(data['id'])
        return data
    

class ProjectDTO(BaseModel):
    id: UUID
    user_id: UUID
    product_id: UUID
    status: ProjectStatus

    created_at: datetime
    updated_at: datetime
    final_video_url: Optional[str] = None
    
class Project(ProjectDTO):
    actor_id: Optional[UUID] = None
    voice_id: Optional[UUID] = None
    video_layout_id: Optional[UUID] = None

    assets: List[Asset] = []
    video_configuration: Optional[VideoConfiguration] = None
    script: Optional[Script] = None

    # cache
    product_base: Optional[ProductBase] = None
    actor_base: Optional[ActorBase] = None
    voice_base: Optional[VoiceBase] = None
    video_layout_base: Optional[VideoLayoutBase] = None

    # final data 
    final_script: Optional[str] = None
    t2s_audio_url: Optional[str] = None
    lipsync_prediction_id: Optional[str] = None
    lipsync_video_url: Optional[str] = None
    final_video_duration: Optional[float] = None
    

    def serialize_for_db(self) -> Dict[str, Any]:
        data = self.model_dump(exclude={"product_base", "actor_base", "voice_base","video_layout_base","script"})
        print(data)

        # Convert UUID to string
        data['id'] = str(data['id'])
        data['product_id'] = str(data['product_id'])
        data['user_id'] = str(data['user_id'])
        if data['actor_id'] is not None:
            data['actor_id'] = str(data['actor_id'])
        if data['voice_id'] is not None:
            data['voice_id'] = str(data['voice_id'])
        if data['video_layout_id'] is not None:
            data['video_layout_id'] = str(data['video_layout_id'])
        
        # Convert datetime objects to ISO format strings
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()
        
        return data

    
 
class User(BaseModel):
    id: UUID
    full_name: str
    email: str
    avatar_url: Optional[str] = None
    credits: int

    def serialize_for_db(self) -> Dict[str, Any]:
        data = self.model_dump()
        # Convert UUID to string
        data['id'] = str(data['id'])
        return data