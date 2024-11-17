import moviepy.editor as mp
from src.utils.logger import logger

def combine_videos_vertically(top_video_path, bottom_video_path, output_path, shift_top_video=(0, 0), shift_bottom_video=(0, -100)):
    logger.info("Starting the process to combine videos vertically.")
    logger.debug(f"Top video path: {top_video_path}, Bottom video path: {bottom_video_path}, Output path: {output_path}")
    
    # Load the videos
    top_video = mp.VideoFileClip(top_video_path)
    bottom_video = mp.VideoFileClip(bottom_video_path)
    logger.debug("Videos loaded successfully.")

    # Function to center crop the video to 9:8 aspect ratio with shift
    def center_crop_to_9_8(video, shift):
        target_aspect_ratio = 9 / 8
        video_aspect_ratio = video.w / video.h
        logger.debug(f"Video aspect ratio: {video_aspect_ratio}, Target aspect ratio: {target_aspect_ratio}")

        if video_aspect_ratio > target_aspect_ratio:
            # Video is wider than 9:8, crop width
            new_width = int(video.h * target_aspect_ratio)
            x_center = video.w // 2 + shift[0]
            logger.debug(f"Cropping width to new width: {new_width}, x_center: {x_center}")
            return video.crop(x_center=x_center, width=new_width)
        elif video_aspect_ratio < target_aspect_ratio:
            # Video is taller than 9:8, crop height
            new_height = int(video.w / target_aspect_ratio)
            y_center = video.h // 2 + shift[1]
            logger.debug(f"Cropping height to new height: {new_height}, y_center: {y_center}")
            return video.crop(y_center=y_center, height=new_height)
        logger.debug("No cropping needed, video aspect ratio matches target.")
        return video

    # Center crop both videos to make them 9:8 with shifts
    video1_cropped = center_crop_to_9_8(top_video, shift_top_video)
    video2_cropped = center_crop_to_9_8(bottom_video, shift_bottom_video)
    logger.debug("Videos cropped to 9:8 aspect ratio.")

    # Calculate the dimensions for the final video
    final_width = video1_cropped.w
    final_height = final_width * 16 // 9
    logger.debug(f"Final video dimensions calculated: width={final_width}, height={final_height}")

    # Resize both videos to fit half of the final height
    video1_resized = video1_cropped.resize(height=final_height // 2)
    video2_resized = video2_cropped.resize(height=final_height // 2)
    logger.debug("Videos resized to fit half of the final height.")

    # Combine the videos vertically
    final_video = mp.CompositeVideoClip([
        video1_resized.set_position(("center", 0)),
        video2_resized.set_position(("center", final_height // 2))
    ], size=(final_width, final_height))
    logger.info("Videos combined vertically.")

    import os
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    logger.debug("Output directory ensured to exist.")

    # Write the result to a file
    final_video.write_videofile(output_path, codec="libx264", fps=25)
    logger.info(f"Final video written to file: {output_path}")

    # Close the video clips
    top_video.close()
    bottom_video.close()
    logger.debug("Video clips closed.")

if __name__ == "__main__":
    # Example usage
    combine_videos_vertically(
        "src/temp_storage/1aa538b0-3502-43e5-9ba9-fc30964cb8b4/working/asset_edited_video_AspectRatio.NINE_SIXTEEN.mp4",
        "src/lipsync_lifestyle_reelsai.mp4",
        "src/final_video.mp4",
        shift_top_video=(0, 0), shift_bottom_video=(0, -100))