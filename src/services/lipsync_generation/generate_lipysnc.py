from src.services.lipsync_generation.wav2lip_lipsync import generate_actor_video
from pydantic import HttpUrl

def generate_lipsync_video(original_video_url,t2s_audio_url) -> HttpUrl:
    # Generate lipsync video
    lipsync_video_url = generate_actor_video(original_video_url,t2s_audio_url)
    return lipsync_video_url
