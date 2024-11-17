from pathlib import Path
from typing import Tuple
from fastapi import HTTPException
from dotenv import load_dotenv
from src.models.base_models import OpenAIVoiceIdentifier
from src.utils.logger import logger
from src.config.settings import Settings
import asyncio
load_dotenv()




# voice = "nova"
import aiohttp

async def openai_text_to_speech(script: str, voice: OpenAIVoiceIdentifier, output_file_path: str):
    logger.info("Starting OpenAI text-to-speech conversion.")
    
    speech_file_path = Path(output_file_path)
    speech_file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    logger.debug(f"Output file path set to: {speech_file_path}")
    
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {Settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "tts-1-hd",
        "input": script,
        "voice": voice.value
    }
    logger.debug(f"Sending request to OpenAI API with data: {data}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    logger.info("Received successful response from OpenAI API.")
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
                        logger.error("OpenAI API service unavailable")
                        raise HTTPException(
                            status_code=503,
                            detail={
                                "error": "service_unavailable",
                                "message": "Service temporarily unavailable",
                                "retry_after": "3600"  # Suggest retry after 1 hour
                            }
                        )
                    logger.error(f"Failed to generate text-to-speech audio: {error_message}")
                    raise Exception(f"Failed to generate text-to-speech audio: {error_message}")
    except Exception as e:
        logger.error(f"Failed to generate text-to-speech audio: {e}")
        raise
