
import whisper
from captions import BoxedHighlightCaption
from transcriptions import transcribe_video_whisper, transcribe_video_assembly
from add_captions_to_video import process_video_for_captions
from src.utils.logger import logger

if __name__ == "__main__":
    input_video = "src/temp_storage/4c6c84ca-9a42-4618-b590-3cb866b7e4b2/assets/000_675f3f6f371f91c3d8aa055f_with_audio.mp4"
    output_video = "src/temp_storage/4c6c84ca-9a42-4618-b590-3cb866b7e4b2/assets/finalvideo_w_captions.NINE_SIXTEEN_assembly.mp4"
    roboto_font_path = "src/fonts/Roboto-Black.ttf"
    
    # Initialize the caption type
    caption_type = BoxedHighlightCaption(
        font_path=roboto_font_path,
        font_size=72,
        default_color=(255, 255, 255),  # White text
        highlight_color=(255, 0, 0),    # Red highlight
        outline_color=(0, 0, 0),        # Black outline
        outline_thickness=3,
        background_color=(0, 0, 0, 0),  # Transparent background
        background_padding=5,
        max_lines=1  # Display only one line at a time
    )

    logger.info("Loading Whisper model")
    # model = whisper.load_model("base")
    sentences= transcribe_video_assembly(input_video)

    # Process the video to add captions
    ouptut_video = process_video_for_captions(input_video, output_video, caption_type, sentences)
    print("Output video:", output_video)