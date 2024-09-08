import os
from pathlib import Path
from openai import OpenAI
from pydantic import HttpUrl
import replicate
from dotenv import load_dotenv
import os
from src.aws_tools.upload_to_s3 import upload_to_s3
from src.utils.constants import Constants
from src.models.base_models import OpenAIVoiceIdentifier
import logging as logger
from src.config import Config

load_dotenv()

# voice = "nova"
def openai_text_to_speech(script: str, voice: OpenAIVoiceIdentifier, output_file_path: str):
    logger.info("Starting OpenAI text-to-speech conversion.")
    client = OpenAI(api_key=Config.OPENAI_API_KEY)

    speech_file_path = Path(output_file_path)
    speech_file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=script,
        )

        response.stream_to_file(speech_file_path)
        return output_file_path
    except Exception as e:
        logger.error(f"Failed to generate text-to-speech audio: {e}")
        raise

def get_audio_duration(audio_file_path: str) -> float:
    import wave

    try:
        with wave.open(audio_file_path, 'rb') as audio_file:
            frames = audio_file.getnframes()
            rate = audio_file.getframerate()
            duration = frames / float(rate)
            logger.info(f"Audio duration: {duration} seconds")
        return duration
    except wave.Error as e:
        logger.error(f"Failed to get audio duration: {e}")
        raise

def generate_t2s_audio(project_id: str, script: str, voice_identifier: OpenAIVoiceIdentifier) -> HttpUrl:
    logger.info(f"Generating audio from script for voice: {voice_identifier}")

    t2s_output_audio_path = f"{Constants.LOCAL_STORAGE_BASE_PATH}/{project_id}/working/t2s_{voice_identifier}.wav"
    # Generate text to speech audio
    openai_text_to_speech(script, voice_identifier, t2s_output_audio_path)
    
    # Read the audio file and get its duration
    # duration = get_audio_duration(t2s_output_audio_path)
    duration = 0

    # try:
    #     _, s3_t2s_output_audio_file_url = upload_to_s3(file_name=t2s_output_audio_path, bucket=Constants.S3_BUCKET_NAME, s3_file_name=t2s_output_audio_path)
    #     logger.info(f"OpenAI T2S file uploaded successfully at path: {s3_t2s_output_audio_file_url}")
    # except Exception as e:
    #     logger.error(f"Failed to upload T2S file to S3: {e}")
    #     raise

    # return s3_t2s_output_audio_file_url, duration

if __name__ == "__main__":
    # from src.utils.constants import DEMO_SCRIPT
    DEMO_SCRIPT = "Tired of AI-generated content that sounds robotic? Meet Longshot AI, your AI co-pilot for creating content that ranks and resonates. With features like one-click SEO blogs, fact-checking, and real-time content optimization, Longshot AI revolutionizes your content strategy. Say goodbye to confusion and hello to unbeatable results. Plan, generate, and optimize with ease. Visit longshot.ai and transform your content game today."
    generate_t2s_audio(
        project_id="test_project_id",
        script=DEMO_SCRIPT,
        voice_identifier=OpenAIVoiceIdentifier.NOVA
    )
