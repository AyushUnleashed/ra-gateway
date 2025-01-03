import cv2
import numpy as np
from typing import List, Tuple
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