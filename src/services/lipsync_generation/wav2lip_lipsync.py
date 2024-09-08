import replicate
from dotenv import load_dotenv
import os
from utils.logger import get_logger
logger = get_logger(__name__)

load_dotenv()
def generate_actor_video(original_actor_video_link, audio_file_link):
    logger.info(f"Starting video generation for actor")
    try:
        logger.info(f"original_actor_video_link: {original_actor_video_link}, audio_file_link: {audio_file_link}")

        output = replicate.run(
            "devxpy/cog-wav2lip:8d65e3f4f4298520e079198b493c25adfc43c058ffec924f2aefc8010ed25eef",
            input={
                "face": original_actor_video_link,
                "audio": audio_file_link,
                "fps": 25,
                "pads": "0 10 0 0",
                "smooth": True,
                "resize_factor": 1
            }
        )
        logger.info(f"Video generation successful for actor. Output: {output}")
    except Exception as e:
        logger.error(f"Failed to generate video for. Error: {e}")
        raise
    return output

    # upsacle the video using codeformer
    # Return the path of the generated video
    # pass

if __name__ == "__main__":
    original_actor_video_link = "https://test-bucket-aws-mine.s3.ap-south-1.amazonaws.com/input_video.mp4?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEBwaCmFwLXNvdXRoLTEiSDBGAiEAlskgi8v0oLlWk0oYrsKseXHHugP0glaAxwlBhy9taUQCIQC4y2O2kDit7rNA4mTIsTzoxDOClh8%2F3MiFzoHQXGTS3irtAgjV%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDYwNjQwNDAxNjU0NiIMFGv6xgvcnokNUkJvKsECk4mJhYptBcRHGuwN0SCNF%2FjEDtIIZDd4mepSutGgkLRu2swJzT4blQYoKBhO30nie2aQHmO9%2FjNO6G20nA3wKby4GwFsR%2B470LYH%2BW35DfoGIRT0HjdBfNFfa%2BZa0pp6LFcKsRxsSivRaKbPczYGnq9DSIAyyB%2BEgBa9wtuG6pzQXS7A0iOdvbN7QdA%2BXlNz8La%2B%2BSrWeQg0ia3tvvo8enKyk%2BVxQM5COhgYJBcWgWqsEnaurEYmto6SVJHrmBigHH%2BOZDts4qCq1H%2F05YHLSO5fKm%2Fytr1VTRnAADBZSJs5HzDuyGPQrtxnB%2BMDP%2Fofpm%2FSMV6xf%2BIL%2BWEavVex0B32xm7gJVQ13Un8H4Lovu5X42fgkNlloOLb%2FXataEN1Img2jeT69qw0JreDNAqAN3jAJxRatuRd%2Fos3zrYrwkQZMJnepLQGOrICyxEDKiHVWvF5vMF1WcQw3rmypefQRiJ%2FlyxUavIF0l9Mqh81qrfZHMdoLrdU82ZgYkHrGsOLowHXFUz%2FFCopIKUJBUtl713sy1RbNGjRQuXAJkpjaWKt%2B6B27dXxpV5sJ14SgnL3KL1v%2Bacx1U74cxD0dgh5VvAZ0ryIbVVd6K5CFyVsmtWbOsH0LEDvXGLOT5vX5fgloYKRwBQF70jrqBYjfwe5g9%2FgLVIvcPaaX%2Bg4o5zX%2BS7aNnPLS1kjhe9B1QrrcxC3dUMrIJy3tc2xfLMmqFebQ4TYUF%2Bkj3qOJQ0ozvmotuElkANy1RdCZ6WdWnP%2BkhacYlLRIzUMHL3JtaBCqNSL8VJm6MsUPnvA7FjeRpqUcCQK6pD%2FRhN%2BEOJ5oFGDG2Rq0zcahbwG%2FOR8Z1pV&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240706T141113Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIAY2MD67GRBOVVCTW2%2F20240706%2Fap-south-1%2Fs3%2Faws4_request&X-Amz-Signature=c0bd8cc5f1081a60fcb78aab92e2d257a3100047a59ebbc331cb1671da694cf4"
    audio_file_link = "https://test-bucket-aws-mine.s3.ap-south-1.amazonaws.com/Alekhyaa%20Demo%20%20SIH%2023%20%20Text%20to%20Video%20%20Generative%20AI%20%28mp3cut.net%29%20%28enhanced%29.wav?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEBwaCmFwLXNvdXRoLTEiSDBGAiEAlskgi8v0oLlWk0oYrsKseXHHugP0glaAxwlBhy9taUQCIQC4y2O2kDit7rNA4mTIsTzoxDOClh8%2F3MiFzoHQXGTS3irtAgjV%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDYwNjQwNDAxNjU0NiIMFGv6xgvcnokNUkJvKsECk4mJhYptBcRHGuwN0SCNF%2FjEDtIIZDd4mepSutGgkLRu2swJzT4blQYoKBhO30nie2aQHmO9%2FjNO6G20nA3wKby4GwFsR%2B470LYH%2BW35DfoGIRT0HjdBfNFfa%2BZa0pp6LFcKsRxsSivRaKbPczYGnq9DSIAyyB%2BEgBa9wtuG6pzQXS7A0iOdvbN7QdA%2BXlNz8La%2B%2BSrWeQg0ia3tvvo8enKyk%2BVxQM5COhgYJBcWgWqsEnaurEYmto6SVJHrmBigHH%2BOZDts4qCq1H%2F05YHLSO5fKm%2Fytr1VTRnAADBZSJs5HzDuyGPQrtxnB%2BMDP%2Fofpm%2FSMV6xf%2BIL%2BWEavVex0B32xm7gJVQ13Un8H4Lovu5X42fgkNlloOLb%2FXataEN1Img2jeT69qw0JreDNAqAN3jAJxRatuRd%2Fos3zrYrwkQZMJnepLQGOrICyxEDKiHVWvF5vMF1WcQw3rmypefQRiJ%2FlyxUavIF0l9Mqh81qrfZHMdoLrdU82ZgYkHrGsOLowHXFUz%2FFCopIKUJBUtl713sy1RbNGjRQuXAJkpjaWKt%2B6B27dXxpV5sJ14SgnL3KL1v%2Bacx1U74cxD0dgh5VvAZ0ryIbVVd6K5CFyVsmtWbOsH0LEDvXGLOT5vX5fgloYKRwBQF70jrqBYjfwe5g9%2FgLVIvcPaaX%2Bg4o5zX%2BS7aNnPLS1kjhe9B1QrrcxC3dUMrIJy3tc2xfLMmqFebQ4TYUF%2Bkj3qOJQ0ozvmotuElkANy1RdCZ6WdWnP%2BkhacYlLRIzUMHL3JtaBCqNSL8VJm6MsUPnvA7FjeRpqUcCQK6pD%2FRhN%2BEOJ5oFGDG2Rq0zcahbwG%2FOR8Z1pV&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240706T141152Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIAY2MD67GRBOVVCTW2%2F20240706%2Fap-south-1%2Fs3%2Faws4_request&X-Amz-Signature=76b30583eb2a8668bc5093841017c1e872d01ef78152f4cb4438d2d02d1ae259"
    generate_actor_video("0",original_actor_video_link, audio_file_link)