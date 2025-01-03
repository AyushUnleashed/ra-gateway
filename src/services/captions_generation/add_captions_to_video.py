import cv2
import numpy as np
import os
from typing import List, Tuple
from moviepy.editor import VideoFileClip
from captions import CaptionType
from src.utils.logger import logger

def process_video_for_captions(input_video: str, output_video: str, caption_type: CaptionType, 
                               sentences: List[Tuple[List[str], float, float]]) -> str:
    try:
        logger.info(f"Loading video: {input_video}")
        video = VideoFileClip(input_video)
        
        # Extract audio from the input video
        audio = video.audio

        cap = cv2.VideoCapture(input_video)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        temp_output = 'temp_output.mp4'
        out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))

        logger.info("Processing video...")
        frame_number = 0
        word_index = 0
        sentence_index = 0
        current_sentence = []
        current_sentence_start_time = 0
        current_sentence_end_time = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            current_time = frame_number / fps

            # Move to the next sentence if the current one has ended
            if current_time > current_sentence_end_time and sentence_index < len(sentences):
                current_sentence, current_sentence_start_time, current_sentence_end_time = sentences[sentence_index]
                sentence_index += 1
                word_index = 0

            # Determine the current word index based on the timing
            if current_sentence_end_time > current_sentence_start_time and current_sentence:
                word_duration = (current_sentence_end_time - current_sentence_start_time) / len(current_sentence)
                word_index = int((current_time - current_sentence_start_time) / word_duration)
                word_index = min(word_index, len(current_sentence) - 1)
            else:
                word_index = 0

            if current_sentence:
                current_word_index = word_index
                text_y = height // 2  # Vertically center the captions
                frame = caption_type.render(frame, current_sentence, current_word_index, (0, text_y))

            out.write(frame)
            frame_number += 1

            if frame_number % 100 == 0:
                logger.info(f"Processed {frame_number} frames")

        cap.release()
        out.release()
        cv2.destroyAllWindows()

        # Load the processed video (without audio)
        processed_video = VideoFileClip(temp_output)

        # Combine the processed video with the original audio
        final_video = processed_video.set_audio(audio)

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_video), exist_ok=True)

        # Write the final video with audio
        final_video.write_videofile(output_video, codec='libx264', audio_codec='aac')

        # Clean up temporary files
        os.remove(temp_output)

        logger.info(f"Video processing complete. Output saved to {output_video}")

        return output_video

    except Exception as e:
        logger.error(f"An error occurred during captions video processing: {e}")
    finally:
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        if os.path.exists(temp_output):
            os.remove(temp_output)