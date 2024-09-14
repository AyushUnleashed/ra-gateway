import replicate
import logging as logger

def generate_actor_video_mt(video_input_url: str,audio_input_url: str):
    logger.info("Starting MuseTalk video generation.")
    try:
        logger.info(f"audio_input_url: {audio_input_url}, video_input_url: {video_input_url}")

        input = {
            "audio_input": audio_input_url,
            "video_input": video_input_url
        }

        output = replicate.run(
            "douwantech/musetalk:5501004e78525e4bbd9fa20d1e75ad51fddce5a274bec07b9b16d685e34eeaf8",
            input=input
        )
        logger.info(f"MuseTalk video generation successful. Output: {output}")
    except Exception as e:
        logger.error(f"Failed to generate MuseTalk video. Error: {e}")
        raise
    return output
