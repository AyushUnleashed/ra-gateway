import moviepy.editor as mp
from src.utils.logger import logger

def validate_video(video_clip, video_path):
    """Validate video dimensions and properties"""
    if video_clip.w <= 0 or video_clip.h <= 0:
        raise ValueError(f"Invalid video dimensions for {video_path}. Width: {video_clip.w}, Height: {video_clip.h}")
    return True

def combine_videos_vertically(top_video_path, bottom_video_path, output_path, shift_top_video=(0, 0), shift_bottom_video=(0, -100)):
    """
    Combines two videos vertically with specific requirements:
    - Input videos should have valid dimensions (width and height > 0)
    - Videos will be cropped to 9:8 aspect ratio
    - Final output will be 16:9 aspect ratio
    
    Args:
        top_video_path (str): Path to the top video
        bottom_video_path (str): Path to the bottom video
        output_path (str): Path for the output video
        shift_top_video (tuple): (x, y) shift for top video positioning
        shift_bottom_video (tuple): (x, y) shift for bottom video positioning
    """
    logger.info("Starting the process to combine videos vertically.")
    logger.debug(f"Top video path: {top_video_path}, Bottom video path: {bottom_video_path}")
    
    try:
        # Load the videos
        top_video = mp.VideoFileClip(top_video_path)
        bottom_video = mp.VideoFileClip(bottom_video_path)
        
        # Validate videos
        validate_video(top_video, top_video_path)
        validate_video(bottom_video, bottom_video_path)
        
        logger.info(f"Loaded videos - Top: {top_video.w}x{top_video.h}, Bottom: {bottom_video.w}x{bottom_video.h}")

        # Function to center crop the video to 9:8 aspect ratio with shift
        def center_crop_to_9_8(video, shift, video_name=""):
            if video.w <= 0 or video.h <= 0:
                raise ValueError(f"Invalid dimensions for {video_name}: {video.w}x{video.h}")
                
            target_aspect_ratio = 9 / 8
            video_aspect_ratio = video.w / video.h
            logger.debug(f"{video_name} aspect ratio: {video_aspect_ratio:.2f}, Target: {target_aspect_ratio:.2f}")

            if video_aspect_ratio > target_aspect_ratio:
                # Video is wider than 9:8, crop width
                new_width = int(video.h * target_aspect_ratio)
                x_center = video.w // 2 + shift[0]
                return video.crop(x1=max(0, x_center - new_width//2), 
                                x2=min(video.w, x_center + new_width//2))
            else:
                # Video is taller than 9:8 or equal, crop height
                new_height = int(video.w / target_aspect_ratio)
                y_center = video.h // 2 + shift[1]
                return video.crop(y1=max(0, y_center - new_height//2),
                                y2=min(video.h, y_center + new_height//2))

        # Center crop both videos to make them 9:8 with shifts
        video1_cropped = center_crop_to_9_8(top_video, shift_top_video, "Top video")
        video2_cropped = center_crop_to_9_8(bottom_video, shift_bottom_video, "Bottom video")
        
        # Verify cropped dimensions
        if video1_cropped.w <= 0 or video1_cropped.h <= 0 or video2_cropped.w <= 0 or video2_cropped.h <= 0:
            raise ValueError("Invalid dimensions after cropping")

        # Calculate the dimensions for the final video (16:9 aspect ratio)
        final_width = max(video1_cropped.w, video2_cropped.w)
        final_height = final_width * 16 // 9
        logger.info(f"Final video dimensions: {final_width}x{final_height}")

        # Resize both videos to fit half of the final height
        half_height = final_height // 2
        video1_resized = video1_cropped.resize(height=half_height)
        video2_resized = video2_cropped.resize(height=half_height)

        # Combine the videos vertically
        final_video = mp.CompositeVideoClip([
            video1_resized.set_position(("center", 0)),
            video2_resized.set_position(("center", half_height))
        ], size=(final_width, final_height))

        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the result to a file
        final_video.write_videofile(output_path, codec="libx264", fps=25)
        logger.info(f"Final video written to: {output_path}")

    except Exception as e:
        logger.error(f"Error processing videos: {str(e)}")
        raise
    
    finally:
        # Clean up resources
        if 'top_video' in locals(): top_video.close()
        if 'bottom_video' in locals(): bottom_video.close()
        logger.debug("Video clips closed.")

if __name__ == "__main__":
    # Example usage
    try:
        combine_videos_vertically(
            "src/temp_storage/1aa538b0-3502-43e5-9ba9-fc30964cb8b4/working/asset_edited_video_AspectRatio.NINE_SIXTEEN.mp4",
            "src/lipsync_lifestyle_reelsai.mp4",
            "src/final_video.mp4",
            shift_top_video=(0, 0),
            shift_bottom_video=(0, -100)
        )
    except Exception as e:
        logger.error(f"Failed to combine videos: {str(e)}")