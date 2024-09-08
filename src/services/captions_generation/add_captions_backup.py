import cv2
import numpy as np
import whisper
from typing import List, Tuple
import os
import pickle
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
class CaptionType:
    def __init__(self, name: str, font: int = cv2.FONT_HERSHEY_SIMPLEX, font_scale: float = 2.5,
                 thickness: int = 12, line_type: int = cv2.LINE_AA):
        self.name = name
        self.font = font
        self.font_scale = font_scale
        self.thickness = thickness
        self.line_type = line_type

    def render(self, frame: np.ndarray, text: str, position: Tuple[int, int]) -> np.ndarray:
        raise NotImplementedError("Subclasses must implement the render method")

class StandardCaption(CaptionType):
    def __init__(self, text_color: Tuple[int, int, int] = (255, 255, 255),
                 highlight_color: Tuple[int, int, int] = (255, 255, 255),
                 outline_color: Tuple[int, int, int] = (0, 0, 0)):
        super().__init__("Standard")
        self.text_color = text_color
        self.highlight_color = highlight_color
        self.outline_color = outline_color

    def render(self, frame: np.ndarray, words: List[str], current_word_index: int, position: Tuple[int, int]) -> np.ndarray:
        x, y = position
        text = " ".join(words)
        cv2.putText(frame, text, (x, y), self.font, self.font_scale, self.text_color, self.thickness, self.line_type)
        return frame

class OutlinedCaption(CaptionType):
    def __init__(self, text_color: Tuple[int, int, int] = (255, 255, 255),
                 highlight_color: Tuple[int, int, int] = (255, 255, 255),
                 outline_color: Tuple[int, int, int] = (0, 0, 0)):
        super().__init__("Outlined")
        self.text_color = text_color
        self.highlight_color = highlight_color
        self.outline_color = outline_color

    def render(self, frame: np.ndarray, words: List[str], current_word_index: int, position: Tuple[int, int]) -> np.ndarray:
        x, y = position
        text = " ".join(words)
        
        # Draw outline
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            cv2.putText(frame, text, (x+dx, y+dy), self.font, self.font_scale, self.outline_color, self.thickness+1, self.line_type)
        
        # Draw text
        cv2.putText(frame, text, (x, y), self.font, self.font_scale, self.text_color, self.thickness, self.line_type)
        return frame


class HighlightedWordsCaption(CaptionType):
    def __init__(self, default_color: Tuple[int, int, int] = (255, 255, 255),
                 highlight_color: Tuple[int, int, int] = (0, 255, 0),
                 outline_color: Tuple[int, int, int] = (0, 0, 0)):
        super().__init__("HighlightedWords")
        self.default_color = default_color
        self.highlight_color = highlight_color
        self.outline_color = outline_color

    def render(self, frame: np.ndarray, words: List[str], current_word_index: int, position: Tuple[int, int]) -> np.ndarray:
        frame_height, frame_width = frame.shape[:2]
        x, y = position
        max_width = int(frame_width * 0.9)  # Use 90% of frame width
        lines = []
        current_line = []
        current_line_width = 0

        for i, word in enumerate(words):
            word_size, _ = cv2.getTextSize(word + " ", self.font, self.font_scale, self.thickness)
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

        for line, line_width in lines:
            x = int((frame_width - line_width) / 2)  # Center each line
            for word, word_index in line:
                color = self.highlight_color if word_index == current_word_index else self.default_color
                
                # Draw outline
                for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    cv2.putText(frame, word, (x+dx, start_y+dy), self.font, self.font_scale, self.outline_color, self.thickness+1, self.line_type)
                
                # Draw text
                cv2.putText(frame, word, (x, start_y), self.font, self.font_scale, color, self.thickness, self.line_type)
                
                word_width, _ = cv2.getTextSize(word + " ", self.font, self.font_scale, self.thickness)[0]
                x += word_width

            start_y += int(word_size[1] * 1.5)  # Move to next line

        return frame

def get_max_words_per_line(frame_width: int, font, font_scale: float, thickness: int) -> int:
    avg_char_width = cv2.getTextSize("A", font, font_scale, thickness)[0][0]
    max_text_width = int(frame_width * 0.9)  # Use 90% of frame width
    return max(1, int(max_text_width / (avg_char_width * 5)))  # Assume average word length of 5 characters

def transcribe_video(video_path: str, model: whisper.Whisper) -> List[List]:
    cache_file = f"{video_path}_transcription_cache.pkl"
    
    if os.path.exists(cache_file):
        print("Loading transcription from cache")
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    print('Transcribing video')
    result = model.transcribe(video_path)

    text_array = []
    for segment in result["segments"]:
        start_time = segment["start"]
        end_time = segment["end"]
        words = segment["text"].strip().split()
        
        for word in words:
            text_array.append([word, start_time, end_time])
            start_time += (end_time - start_time) / len(words)

    print('Transcription complete')
    
    # Cache the transcription
    with open(cache_file, 'wb') as f:
        pickle.dump(text_array, f)
    
    return text_array

def process_video(input_video: str, output_video: str, caption_type: CaptionType,
                  font_name: int = cv2.FONT_HERSHEY_SIMPLEX, font_scale: float = 1.0):
    model = whisper.load_model("base")

    # Load the video using moviepy
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

    # Calculate max words per line
    max_words = get_max_words_per_line(width, font_name, font_scale, caption_type.thickness)

    print("Processing video...")
    frame_number = 0
    word_index = 0
    
    # Pre-compute text positions and sizes
    text_positions = []
    for i in range(len(text_array)):
        words = [text_array[j][0] for j in range(max(0, i - max_words // 2), min(len(text_array), i + max_words // 2))]
        current_word_index = min(max_words // 2, i)
        text_positions.append((words, current_word_index))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = frame_number / fps

        # Find the current word based on timestamp
        while word_index < len(text_array) and text_array[word_index][1] <= current_time:
            word_index += 1

        if word_index < len(text_positions):
            words, current_word_index = text_positions[word_index]
            if words:
                text_y = height // 2  # Vertically center the captions
                frame = caption_type.render(frame, words, current_word_index, (0, text_y))

        out.write(frame)
        frame_number += 1

        if frame_number % 100 == 0:
            print(f"Processed {frame_number} frames")

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # Load the processed video (without audio)
    processed_video = VideoFileClip(temp_output)

    # Combine the processed video with the original audio
    final_video = processed_video.set_audio(audio)

    # Write the final video with audio
    final_video.write_videofile(output_video, codec='libx264', audio_codec='aac')

    # Clean up temporary files
    os.remove(temp_output)

    print(f"Video processing complete. Output saved to {output_video}")


if __name__ == "__main__":
    input_video = "src/temp_storage/working/combined_output.mp4"
    output_video = "src/temp_storage/working/output_video_with_captions.mp4"
    # Choose one of the caption types:
    # caption_type = StandardCaption()
    #caption_type = OutlinedCaption()
    

    # caption_type = StandardCaption(
    #     text_color=(255, 255, 255),  # White
    #     highlight_color=(0, 255, 0),  # Green (not used in Standard, but included for consistency)
    #     outline_color=(0, 0, 0)  # Black (not used in Standard, but included for consistency)
    # )
    
    # Or use OutlinedCaption:
    # caption_type = OutlinedCaption(
    #     text_color=(255, 255, 255),  # White
    #     highlight_color=(0, 255, 0),  # Green (not used in Outlined, but included for consistency)
    #     outline_color=(0, 0, 0)  # Black
    # )
    
    # Or use HighlightedWordsCaption:
    caption_type = HighlightedWordsCaption(
        default_color=(255, 255, 255),  # White
        highlight_color=(0, 255, 0),    # Green
        outline_color=(0, 0, 0)         # Black
    )

    process_video(input_video, output_video, caption_type, font_name=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1.0)