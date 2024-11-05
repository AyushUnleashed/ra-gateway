# src/services/voice_over_generation/elevenlabs_t2s.py
import aiohttp
from pathlib import Path
from fastapi import HTTPException
from src.utils.logger import logger
from src.config import Config

async def elevenlabs_text_to_speech(script: str, voice_id: str, output_file_path: str):
    logger.info("Starting Eleven Labs text-to-speech conversion.")
    
    speech_file_path = Path(output_file_path)
    speech_file_path.parent.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Output file path set to: {speech_file_path}")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": Config.ELEVEN_LABS_API_KEY
    }
    
    data = {
        "text": script,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.0,
            "similarity_boost": 1.0,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    logger.info("Received successful response from Eleven Labs API.")
                    with open(speech_file_path, 'wb') as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                    logger.info(f"Audio file written to: {output_file_path}")
                    return output_file_path
                else:
                    error_message = await response.text()
                    if response.status == 503:
                        logger.error("Eleven Labs API service unavailable")
                        raise HTTPException(
                            status_code=503,
                            detail={
                                "error": "service_unavailable",
                                "message": "Service temporarily unavailable",
                                "retry_after": "3600"
                            }
                        )
                    logger.error(f"Failed to generate text-to-speech audio: {error_message}")
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Failed to generate text-to-speech audio: {error_message}"
                    )
    except Exception as e:
        logger.error(f"Failed to generate text-to-speech audio with Eleven Labs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate text-to-speech audio: {str(e)}"
        )