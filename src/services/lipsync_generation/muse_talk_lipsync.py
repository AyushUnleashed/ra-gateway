import aiohttp
from src.utils.logger import logger
from src.config import Config
from pydantic import BaseModel
from typing import Optional, Dict, Any

class MuseTalkPredictionResponse(BaseModel):
    id: str
    model: str
    version: str
    input: Dict[str, str]
    logs: str
    output: Optional[Any]
    data_removed: bool
    error: Optional[Any]
    status: str
    created_at: str
    urls: Dict[str, str]

async def create_muste_talk_prediction(video_input_url: str, audio_input_url: str) -> str:
    logger.info("Starting MuseTalk video generation.")
    try:
        logger.debug(f"Preparing input data for video generation with audio_input_url: {audio_input_url}, video_input_url: {video_input_url}")

        input_data = {
            "version": "5501004e78525e4bbd9fa20d1e75ad51fddce5a274bec07b9b16d685e34eeaf8",
            "input": {
                "audio_input": audio_input_url,
                "video_input": video_input_url
            },
            "webhook": f"{Config.RAI_GATEWAY_BACKEND_URL}/webhook/replicate",
            "webhook_events_filter": ["completed"]
        }

        logger.debug(f"Input data prepared: {input_data}")

        async with aiohttp.ClientSession() as session:
            logger.debug("Opened aiohttp ClientSession.")
            async with session.post(
                "https://api.replicate.com/v1/predictions",
                json=input_data,
                headers={
                    "Authorization": f"Bearer {Config.REPLICATE_API_TOKEN}",
                    "Content-Type": "application/json"
                }
            ) as response:
                logger.debug(f"Received response with status code: {response.status}")
                if response.status not in (200, 201):
                    logger.error(f"Failed to generate MuseTalk video. Status code: {response.status}")
                    raise Exception(f"Failed to generate MuseTalk video. Status code: {response.status}")
                output = await response.json()
                logger.info(f"MuseTalk video generation successful. Output: {output}")

    except Exception as e:
        logger.error(f"Failed to generate MuseTalk video. Error: {e}")
        raise

    return output["id"]

import asyncio
import httpx
import os
from typing import Optional

async def poll_for_lipsync_video(prediction_id: str, max_retries: int = 60, retry_interval: int = 20) -> Optional[str]:
    """
    Poll Replicate API for the lipsync video result.
    
    :param prediction_id: The ID of the prediction to get.
    :param max_retries: Maximum number of retries before giving up.
    :param retry_interval: Time in seconds between retries.
    :return: The URL of the generated lipsync video, or None if failed.
    """
    logger.info(f"Polling for lipsync video with prediction_id: {prediction_id}")
    api_token = Config.REPLICATE_API_TOKEN
    if not api_token:
        logger.error("REPLICATE_API_TOKEN is not set in the Config")
        raise ValueError("REPLICATE_API_TOKEN is not set in the Config")

    headers = {
        "Authorization": f"Token {api_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        logger.debug("Opened httpx AsyncClient.")
        for attempt in range(max_retries):
            logger.debug(f"Attempt {attempt + 1} of {max_retries}.")
            response = await client.get(f"https://api.replicate.com/v1/predictions/{prediction_id}", headers=headers)
            
            logger.debug(f"Received response with status code: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Error: Received status code {response.status_code}")
                return None

            data = response.json()
            status = data.get("status")
            logger.debug(f"Current prediction status: {status}")

            if status == "succeeded":
                output = data.get("output")
                if output and isinstance(output, str):
                    logger.info("Lipsync video generation succeeded.")
                    return output
                else:
                    logger.error("Error: Unexpected output format")
                    return None
            elif status in ["failed", "canceled"]:
                logger.error(f"Error: Prediction {status}")
                return None
            elif status in ["starting", "processing"]:
                logger.info(f"Status: {status}. Retrying in {retry_interval} seconds...")
                await asyncio.sleep(retry_interval)
            else:
                logger.error(f"Error: Unknown status '{status}'")
                return None

    logger.error(f"Error: Max retries ({max_retries}) reached")
    return None

if __name__ == "__main__":

    async def main():
        logger.info("Starting main function for MuseTalk prediction.")
        prediction_id = await create_muste_talk_prediction(
            video_input_url="https://reels-ai-pro-bucket.s3.ap-south-1.amazonaws.com/prod-bucket/actors/4e4a6cc7-f044-4445-9548-f0933b0cbe0e/portrait_video.mp4",
            audio_input_url="https://reels-ai-pro-bucket.s3.ap-south-1.amazonaws.com/prod-bucket/voices/a059382e-5d8d-49ec-96d1-eb7e46c04e31/t2s_nova.wav"
        )
        logger.info(f"Prediction ID obtained: {prediction_id}")

    import asyncio
    asyncio.run(main())