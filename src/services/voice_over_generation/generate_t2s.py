import os
from pathlib import Path
from typing import Tuple
import replicate
from dotenv import load_dotenv
import os
from src.aws_tools.upload_to_s3 import upload_to_s3
from src.supabase_tools.handle_bucket_updates import upload_file_to_projects
from src.utils.constants import Constants
from src.models.base_models import OpenAIVoiceIdentifier
import logging as logger
from src.config import Config
import asyncio
load_dotenv()

# voice = "nova"
import aiohttp

async def openai_text_to_speech(script: str, voice: OpenAIVoiceIdentifier, output_file_path: str):
    logger.info("Starting OpenAI text-to-speech conversion.")
    
    speech_file_path = Path(output_file_path)
    speech_file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "tts-1",
        "input": script,
        "voice": voice.value
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    with open(speech_file_path, 'wb') as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                    return output_file_path
                else:
                    error_message = await response.text()
                    logger.error(f"Failed to generate text-to-speech audio: {error_message}")
                    raise Exception(f"Failed to generate text-to-speech audio: {error_message}")
    except Exception as e:
        logger.error(f"Failed to generate text-to-speech audio: {e}")
        raise

# def get_audio_duration(audio_file_path: str) -> float:
#     import wave

#     try:
#         with wave.open(audio_file_path, 'rb') as audio_file:
#             frames = audio_file.getnframes()
#             rate = audio_file.getframerate()
#             duration = frames / float(rate)
#             logger.info(f"Audio duration: {duration} seconds")
#         return duration
#     except wave.Error as e:
#         logger.error(f"Failed to get audio duration: {e}")
#         raise

async def get_audio_duration_librosa(audio_file_path: str) -> float:
    import librosa
    try:
        duration = await asyncio.to_thread(librosa.get_duration, path=audio_file_path)
        print("Duration:", duration)
        return duration
    except Exception as e:
        logger.error(f"Failed to get audio duration using librosa: {e}")
        raise



async def generate_t2s_audio(project_id: str, script: str, voice_identifier: OpenAIVoiceIdentifier) -> Tuple[str, float]:
    logger.info(f"Generating audio from script for voice: {voice_identifier}")

    cache = False
    if cache == True:
        return "https://kooaoegvtnxgrxbyuwvu.supabase.co/storage/v1/object/public/prod-bucket/projects/test_project_id/t2s_nova.wav",22.368

    t2s_output_audio_path = f"{Constants.LOCAL_STORAGE_BASE_PATH}/{project_id}/working/t2s_{voice_identifier.value}.wav"
    # Generate text to speech audio
    await openai_text_to_speech(script, voice_identifier, t2s_output_audio_path)
    
    # Read the audio file and get its duration
    duration = await get_audio_duration_librosa(t2s_output_audio_path)
    #duration = 0.0

    try:
        t2s_output_audio_file_url = upload_file_to_projects(
            local_path=t2s_output_audio_path,
            project_id=project_id,
            content_type="audio/wav"
        )
        logger.info(f"OpenAI T2S file uploaded successfully at path: {t2s_output_audio_file_url}")
    except Exception as e:
        logger.error(f"Failed to upload T2S file to Supabase: {e}")
        raise

    return t2s_output_audio_file_url, duration

if __name__ == "__main__":
    # from src.utils.constants import DEMO_SCRIPT
    async def main():
        DEMO_SCRIPT = "Tired of AI-generated content that sounds robotic? Meet Longshot AI, your AI co-pilot for creating content that ranks and resonates. With features like one-click SEO blogs, fact-checking, and real-time content optimization, Longshot AI revolutionizes your content strategy. Say goodbye to confusion and hello to unbeatable results. Plan, generate, and optimize with ease. Visit longshot.ai and transform your content game today."
        url, duration = await generate_t2s_audio(
            project_id="test_project_id",
            script=DEMO_SCRIPT,
            voice_identifier=OpenAIVoiceIdentifier.NOVA
        )
        print("URL: ", url)
        

    asyncio.run(main())

if __name__ == "__main__":
    # from src.utils.constants import DEMO_SCRIPT
    async def main():
        await get_audio_duration_librosa(audio_file_path="src/temp_storage/be41c076-2813-4160-a8bc-67169a04cefa/working/t2s_nova.wav")
        
    import asyncio
    asyncio.run(main())
