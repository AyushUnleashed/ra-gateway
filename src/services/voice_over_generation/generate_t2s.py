import os
from pathlib import Path
from openai import OpenAI
import replicate
from dotenv import load_dotenv
import os
from aws_tools.upload_to_s3 import upload_to_s3
from src.utils.constants import Constants
from utils.logger import get_logger

from src.supabase_tools.handle_voice_tb_updates import get_voice_from_db

logger = get_logger(__name__)

load_dotenv()

voice = "nova"
def openai_text_to_speech(script: str,voice:str, output_file_path: str):
    logger.info("Starting OpenAI text-to-speech conversion.")
    client = OpenAI()

    speech_file_path = Path(output_file_path)
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=script
        )
        response.stream_to_file(speech_file_path)
        logger.info(f"Text-to-speech audio saved to {speech_file_path}")
        return output_file_path
    except Exception as e:
        logger.error(f"Failed to generate text-to-speech audio: {e}")
        raise


def generate_t2s_audio(project_id, script, voice_id):
    logger.info(f"Generating audio from script for voice: {voice}")

    voice = get_voice_from_db(voice_id)

    t2s_output_audio_path = f"{Constants.LOCAL_STORAGE_BASE_PATH}/{project_id}/working/t2s_{voice.voice_identifier}.wav"
    # Generate text to speech audio
    openai_text_to_speech(script, voice.voice_identifier, t2s_output_audio_path)

    try:
        _, s3_t2s_output_audio_file_url = upload_to_s3(file_name=t2s_output_audio_path, bucket=Constants.S3_BUCKET_NAME, s3_file_name=t2s_output_audio_path)
        logger.info(f"OpenAI T2S file uploaded successfully at path: {s3_t2s_output_audio_file_url}")
    except Exception as e:
        logger.error(f"Failed to upload T2S file to S3: {e}")
        raise

    return s3_t2s_output_audio_file_url

# if __name__ == "__main__":
#     from constants import DEMO_SCRIPT
#     from models.input_models import ActorType
#     rvc_audio_link = generate_audio_from_script(DEMO_SCRIPT, ActorType.SAM_ALTMAN.value)
#     print(rvc_audio_link)
