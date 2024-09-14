from src.services.lipsync_generation.muse_talk_lipsync import generate_actor_video_mt
from pydantic import HttpUrl

def generate_lipsync_video(original_video_url,t2s_audio_url) -> HttpUrl:

    cache = False
    if cache == True:
        return "https://replicate.delivery/pbxt/gtZYuSgzVP4cLlJN4UbNQPeMidXGmxfjflfcLBm9KVbN1czNB/tmpf3393cj9portrait_video_tmpt8saro19t2s_nova.mp4"
    # Generate lipsync video
    lipsync_video_url = generate_actor_video_mt(
        video_input_url=str(original_video_url),
        audio_input_url=str(t2s_audio_url)
    )
    
    return lipsync_video_url

if __name__ == "__main__":
    lipsync_video_url = generate_lipsync_video(
        original_video_url="https://kooaoegvtnxgrxbyuwvu.supabase.co/storage/v1/object/public/prod-bucket/actors/4e4a6cc7-f044-4445-9548-f0933b0cbe0e/portrait_video.mp4",
        t2s_audio_url="https://kooaoegvtnxgrxbyuwvu.supabase.co/storage/v1/object/public/prod-bucket/projects/test_project_id/t2s_nova.wav"
    )
    print("Lipsync video URL:", lipsync_video_url)