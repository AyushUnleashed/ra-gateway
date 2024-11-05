# src/services/voice_over_generation/generate_t2s.py
import os
from pathlib import Path
from typing import Tuple
from uuid import UUID
from fastapi import HTTPException
import asyncio
from src.models.base_models import VoiceBase, TTSProvider
from src.services.voice_over_generation.openai_t2s import openai_text_to_speech
from src.services.voice_over_generation.elevenlabs_t2s import elevenlabs_text_to_speech
from src.supabase_tools.handle_bucket_updates import upload_file_to_projects
from src.utils.constants import Constants
from src.utils.logger import logger

async def generate_t2s_audio(project_id: str, script: str, voice: VoiceBase) -> Tuple[str, float]:
    logger.info(f"Generating audio from script for voice: {voice.name}")

    cache = False
    if cache:
        logger.info("Returning cached audio file URL and duration.")
        return "https://reels-ai-pro-bucket.s3.ap-south-1.amazonaws.com/prod-bucket/voices/FGY2WhTYpPnrIDTdsKH5/laura_reelsai_ad_sample.wav", 32.00

    t2s_output_audio_path = f"{Constants.LOCAL_STORAGE_BASE_PATH}/{project_id}/working/t2s_{voice.voice_identifier}.wav"
    logger.debug(f"Output audio path set to: {t2s_output_audio_path}")

    # Choose TTS provider based on voice configuration
    try:
        if voice.provider == TTSProvider.OPENAI:
            await openai_text_to_speech(script, voice.voice_identifier, t2s_output_audio_path)
        elif voice.provider == TTSProvider.ELEVEN_LABS:
            await elevenlabs_text_to_speech(script, voice.voice_identifier, t2s_output_audio_path)
        else:
            raise ValueError(f"Unsupported TTS provider: {voice.provider}")
    except HTTPException as e:
        logger.error(f"TTS API error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during TTS generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during TTS generation")

    # Get audio duration
    try:
        duration = await get_audio_duration_librosa(t2s_output_audio_path)
    except Exception as e:
        logger.error(f"Failed to get audio duration: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process generated audio")

    try:
        t2s_output_audio_file_url = upload_file_to_projects(
            local_path=t2s_output_audio_path,
            project_id=project_id,
            content_type="audio/wav"
        )
        logger.info(f"T2S file uploaded successfully at path: {t2s_output_audio_file_url}")
    except Exception as e:
        logger.error(f"Failed to upload T2S file to storage: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to store generated audio")

    return t2s_output_audio_file_url, duration

async def get_audio_duration_librosa(audio_file_path: str) -> float:
    import librosa
    logger.info(f"Calculating audio duration for file: {audio_file_path}")
    try:
        duration = await asyncio.to_thread(librosa.get_duration, path=audio_file_path)
        logger.info(f"Audio duration calculated: {duration} seconds")
        return duration
    except Exception as e:
        logger.error(f"Failed to get audio duration using librosa: {e}")
        raise

if __name__ == "__main__":



    
    async def main():
        DEMO_SCRIPT = "Tired of AI-generated content that sounds robotic? Meet Longshot AI..."
        
        # Test with OpenAI voice
        openai_test_voice = VoiceBase(
            id=UUID('12345678-1234-5678-1234-567812345678'),
            name="Nova",
            gender="female",
            provider=TTSProvider.OPENAI,
            voice_identifier="nova",
            is_visible=True
        )
        
        # Test with Eleven Labs voice
        eleven_labs_test_voice = VoiceBase(
            id=UUID('87654321-4321-8765-4321-876543210987'),
            name="Adam",
            gender="male",
            provider=TTSProvider.ELEVEN_LABS,
            voice_identifier="pNInz6obpgDQGcFmaJgB",
            is_visible=True
        )

        # Test OpenAI
        # logger.info("Testing OpenAI TTS...")
        # url1, duration1 = await generate_t2s_audio(
        #     project_id="test_project_id",
        #     script=DEMO_SCRIPT,
        #     voice=openai_test_voice
        # )
        # logger.info(f"Generated OpenAI T2S audio URL: {url1}, Duration: {duration1}")

        # Test Eleven Labs
        logger.info("Testing Eleven Labs TTS...")
        url2, duration2 = await generate_t2s_audio(
            project_id="test_project_id",
            script=DEMO_SCRIPT,
            voice=eleven_labs_test_voice
        )
        logger.info(f"Generated Eleven Labs T2S audio URL: {url2}, Duration: {duration2}")

    asyncio.run(main())