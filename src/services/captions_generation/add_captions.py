import cv2
import numpy as np
import whisper
from typing import List, Tuple
import os
import pickle
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
from src.utils.logger import logger

roboto_font_path = "src/fonts/Roboto-Black.ttf"

class CaptionType:
    def __init__(self, name: str, font_path: str, font_size: int = 32,
                 thickness: int = 2, line_type: int = cv2.LINE_AA, outline_thickness: int = 2):
        self.name = name
        self.font = ImageFont.truetype(font_path, font_size)
        self.thickness = thickness
        self.line_type = line_type
        self.outline_thickness = outline_thickness
        logger.debug(f"Initialized CaptionType: {self.name}")

    def render(self, frame: np.ndarray, text: str, position: Tuple[int, int]) -> np.ndarray:
        raise NotImplementedError("Subclasses must implement the render method")

    def get_text_size(self, text: str) -> Tuple[int, int]:
        bbox = self.font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

class HighlightedWordsCaption(CaptionType):
    def __init__(self, font_path: str, font_size: int = 32, default_color: Tuple[int, int, int] = (255, 255, 255),
                 highlight_color: Tuple[int, int, int] = (0, 255, 0),
                 outline_color: Tuple[int, int, int] = (0, 0, 0), outline_thickness: int = 2):
        super().__init__("HighlightedWords", font_path, font_size, outline_thickness=outline_thickness)
        self.default_color = default_color
        self.highlight_color = highlight_color
        self.outline_color = outline_color
        logger.debug("Initialized HighlightedWordsCaption")

    def render(self, frame: np.ndarray, words: List[str], current_word_index: int, position: Tuple[int, int]) -> np.ndarray:
        logger.debug("Rendering HighlightedWordsCaption")
        frame_height, frame_width = frame.shape[:2]
        x, y = position
        max_width = int(frame_width * 0.9)  # Use 90% of frame width
        lines = []
        current_line = []
        current_line_width = 0

        for i, word in enumerate(words):
            word_size = self.get_text_size(word + " ")
            if current_line_width + word_size[0] > max_width:
                lines.append((current_line, current_line_width))
                current_line = []
                current_line_width = 0
            current_line.append((word, i))
            current_line_width += word_size[0]
        
        if current_line:
            lines.append((current_line, current_line_width))

        total_height = len(lines) * word_size[1] * 1.5  # 1.5 for line spacing
        start_y = max(word_size[1], int(y - total_height / 2))

        # Create a transparent overlay
        overlay = Image.new('RGBA', (frame_width, frame_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        for line, line_width in lines:
            x = int((frame_width - line_width) / 2)  # Center each line
            for word, word_index in line:
                color = self.highlight_color if word_index == current_word_index else self.default_color
                
                # Draw outline
                for dx, dy in [(-self.outline_thickness, -self.outline_thickness), (-self.outline_thickness, self.outline_thickness), 
                               (self.outline_thickness, -self.outline_thickness), (self.outline_thickness, self.outline_thickness)]:
                    draw.text((x+dx, start_y+dy), word, font=self.font, fill=self.outline_color)
                
                # Draw text
                draw.text((x, start_y), word, font=self.font, fill=color)
                
                word_width, _ = self.get_text_size(word + " ")
                x += word_width

            start_y += int(word_size[1] * 1.5)  # Move to next line

        # Combine the overlay with the frame
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame_with_text = Image.alpha_composite(frame_pil.convert('RGBA'), overlay)
        return cv2.cvtColor(np.array(frame_with_text), cv2.COLOR_RGB2BGR)

class BoxedHighlightCaption(CaptionType):
    def __init__(self, font_path: str = "src/fonts/Roboto-Black.ttf", font_size: int = 64,
                 default_color: Tuple[int, int, int] = (255, 255, 0),
                 highlight_color: Tuple[int, int, int] = (255, 0, 0),
                 outline_color: Tuple[int, int, int] = (0, 0, 0),
                 outline_thickness: int = 3,
                 background_color: Tuple[int, int, int, int] = (0, 0, 0, 128),
                 background_padding: int = 20,
                 max_lines: int = 1):  # New parameter to control the number of lines
        super().__init__("BoxedHighlight", font_path, font_size, outline_thickness=outline_thickness)
        self.default_color = default_color
        self.highlight_color = highlight_color
        self.outline_color = outline_color
        self.background_color = background_color
        self.background_padding = background_padding
        self.max_lines = max_lines  # Store the max_lines parameter
        logger.debug("Initialized BoxedHighlightCaption")

    def render(self, frame: np.ndarray, words: List[str], current_word_index: int, position: Tuple[int, int]) -> np.ndarray:
        logger.debug("Rendering BoxedHighlightCaption")
        frame_height, frame_width = frame.shape[:2]
        x, y = position
        max_width = int(frame_width * 0.9)  # Use 90% of frame width

        # Split words into lines
        lines = []
        current_line = []
        current_line_width = 0

        for i, word in enumerate(words):
            word_size = self.get_text_size(word + " ")
            if current_line_width + word_size[0] > max_width:
                lines.append((current_line, current_line_width))
                current_line = []
                current_line_width = 0
            current_line.append((word, i))
            current_line_width += word_size[0]
        
        if current_line:
            lines.append((current_line, current_line_width))

        # Determine which line contains the current word
        current_line_index = 0
        for i, (line, _) in enumerate(lines):
            if any(word_index == current_word_index for _, word_index in line):
                current_line_index = i
                break

        # Only render the current line
        start_index = max(0, current_line_index - self.max_lines + 1)
        end_index = start_index + self.max_lines
        lines_to_render = lines[start_index:end_index]

        total_height = len(lines_to_render) * self.font.size * 1.5  # 1.5 for line spacing
        start_y = max(self.font.size, int(y - total_height / 2))

        # Create a transparent overlay
        overlay = Image.new('RGBA', (frame_width, frame_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Add a semi-transparent background for the entire text area
        background_height = int(total_height + 2 * self.background_padding)
        background_y = start_y - self.background_padding
        draw.rectangle([0, background_y, frame_width, background_y + background_height],
                       fill=self.background_color)

        for line, line_width in lines_to_render:
            x = int((frame_width - line_width) / 2)  # Center each line
            for word, word_index in line:
                word_width, word_height = self.get_text_size(word + " ")
                if word_index == current_word_index:
                    # Calculate centered position for highlight box
                    box_width = word_width + self.font.size // 2  # Add some padding
                    box_height = self.font.size + self.font.size // 4  # Add some padding
                    box_x = x - (box_width - word_width) // 2
                    box_y = start_y - (box_height - self.font.size) // 2
                    
                    # Draw centered box around the word
                    draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height], 
                                   fill=self.highlight_color)
                
                # Draw outline
                for dx, dy in [(-self.outline_thickness, -self.outline_thickness), (-self.outline_thickness, self.outline_thickness), 
                               (self.outline_thickness, -self.outline_thickness), (self.outline_thickness, self.outline_thickness)]:
                    draw.text((x+dx, start_y+dy), word, font=self.font, fill=self.outline_color)
                
                # Draw text
                draw.text((x, start_y), word, font=self.font, fill=self.default_color)
                
                x += word_width

            start_y += int(self.font.size * 1.5)  # Move to next line

        # Combine the overlay with the frame
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame_with_text = Image.alpha_composite(frame_pil.convert('RGBA'), overlay)
        return cv2.cvtColor(np.array(frame_with_text), cv2.COLOR_RGB2BGR)


def transcribe_video(video_path: str, model: whisper.Whisper) -> List[List]:
    cache_file = f"{video_path}_transcription_cache.pkl"
    
    if os.path.exists(cache_file):
        logger.info("Loading transcription from cache")
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    logger.info('Transcribing video')
    result = model.transcribe(video_path)

    text_array = []
    for segment in result["segments"]:
        start_time = segment["start"]
        end_time = segment["end"]
        words = segment["text"].strip().split()
        
        for word in words:
            text_array.append([word, start_time, end_time])
            start_time += (end_time - start_time) / len(words)

    logger.info('Transcription complete')
    
    # Cache the transcription
    with open(cache_file, 'wb') as f:
        pickle.dump(text_array, f)
    
    return text_array

def process_video_for_captions(input_video: str, output_video: str, caption_type: CaptionType, font_path: str, font_size: int = 32):
    logger.info(f"Loading Whisper model")
    model = whisper.load_model("base")

    # Load the video using moviepy
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

    # Transcribe video (now with caching)
    text_array = transcribe_video(input_video, model)

    logger.info("Processing video...")
    frame_number = 0
    word_index = 0
    sentence_index = 0
    current_sentence = []
    current_sentence_start_time = 0
    current_sentence_end_time = 0

    # Pre-compute sentences based on Whisper's segments
    sentences = []
    for segment in model.transcribe(input_video)["segments"]:
        words = segment["text"].strip().split()
        start_time = segment["start"]
        end_time = segment["end"]
        sentences.append((words, start_time, end_time))

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

        # Find the current word based on timestamp
        while word_index < len(current_sentence) and current_sentence_start_time + (word_index * (current_sentence_end_time - current_sentence_start_time) / len(current_sentence)) <= current_time:
            word_index += 1

        if current_sentence:
            current_word_index = min(word_index, len(current_sentence) - 1)
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

if __name__ == "__main__":
    input_video = "src/temp_storage/a34b03d2-7190-45cc-b2e7-01e347b18675/working/final_video.mp4"
    output_video = "src/temp_storage/working/finalvideo_w_captions.NINE_SIXTEEN.mp4"
    # Path to your Roboto font file
    roboto_font_path = "src/fonts/Roboto-Black.ttf"
    
    # Use HighlightedWordsCaption with Roboto font:
    # caption_type = HighlightedWordsCaption(
    #     font_path=roboto_font_path,
    #     font_size=32,
    #     default_color=(255, 255, 255),  # White
    #     highlight_color=(160, 32, 250),  # Purple
    #     outline_color=(0, 0, 0),         # Black
    #     outline_thickness=2              # Outline thickness
    # )

    # Alternatively, you can use BoxedHighlightCaption:
    caption_type = BoxedHighlightCaption(
        font_path=roboto_font_path,
        font_size=72,
        default_color=(255, 255, 255),  # White text
        highlight_color=(255, 0, 0),    # Red highlight
        outline_color=(0, 0, 0),        # Black outline
        outline_thickness=3,
        background_color=(0, 0, 0, 0),  # Transparent background
        background_padding=5,
        max_lines=1  # Set to 1 to display only one line at a time
    )
    process_video_for_captions(input_video, output_video, caption_type, font_path=roboto_font_path, font_size=32)