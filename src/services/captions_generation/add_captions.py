import cv2
import numpy as np
import whisper
from typing import List, Tuple

class CaptionType:
    def __init__(self, name: str, font: int = cv2.FONT_HERSHEY_SIMPLEX, font_scale: float = 4.0,
                 thickness: int = 8, line_type: int = cv2.LINE_AA):
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

def process_video(input_video: str, output_video: str, caption_type: CaptionType,
                  font_name: str = cv2.FONT_HERSHEY_SIMPLEX, font_scale: float = 1.0):
    model = whisper.load_model("base")

    cap = cv2.VideoCapture(input_video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    # Transcribe video
    text_array = transcribe_video(input_video, model)

    # Calculate max words per line
    max_words = get_max_words_per_line(width, font_name, font_scale, caption_type.thickness)

    print("Processing video...")
    frame_number = 0
    word_index = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = frame_number / fps
        current_words = []
        current_word_index = -1

        # Find the current word based on timestamp
        while word_index < len(text_array) and text_array[word_index][1] <= current_time:
            word_index += 1

        # Collect words for display
        for i in range(max(0, word_index - max_words // 2), min(len(text_array), word_index + max_words // 2)):
            word, start_time, end_time = text_array[i]
            if start_time <= current_time < end_time:
                current_word_index = len(current_words)
            current_words.append(word)

        if current_words:
            text_y = height // 2  # Vertically center the captions
            frame = caption_type.render(frame, current_words, current_word_index, (0, text_y))

        out.write(frame)
        frame_number += 1

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Video processing complete. Output saved to {output_video}")


def transcribe_video(video_path: str, model: whisper.Whisper) -> List[List]:
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
    return text_array

if __name__ == "__main__":
    input_video = "assets/video_retalking_full_output.mp4"
    output_video = "assets/output_video_with_captions.mp4"
    
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