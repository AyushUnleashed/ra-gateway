import moviepy.editor as mp
def combine_videos_vertically(video1_path, video2_path, output_path, shift_video1=(0, 0), shift_video2=(0, 0)):
    # Load the videos
    video1 = mp.VideoFileClip(video1_path)
    video2 = mp.VideoFileClip(video2_path)

    # Function to center crop the video to 9:8 aspect ratio with shift
    def center_crop_to_9_8(video, shift):
        target_aspect_ratio = 9 / 8
        video_aspect_ratio = video.w / video.h

        if video_aspect_ratio > target_aspect_ratio:
            # Video is wider than 9:8, crop width
            new_width = int(video.h * target_aspect_ratio)
            x_center = video.w // 2 + shift[0]
            return video.crop(x_center=x_center, width=new_width)
        elif video_aspect_ratio < target_aspect_ratio:
            # Video is taller than 9:8, crop height
            new_height = int(video.w / target_aspect_ratio)
            y_center = video.h // 2 + shift[1]
            return video.crop(y_center=y_center, height=new_height)
        return video

    # Center crop both videos to make them 9:8 with shifts
    video1_cropped = center_crop_to_9_8(video1, shift_video1)
    video2_cropped = center_crop_to_9_8(video2, shift_video2)

    # Calculate the dimensions for the final video
    final_width = video1_cropped.w
    final_height = final_width * 16 // 9

    # Resize both videos to fit half of the final height
    video1_resized = video1_cropped.resize(height=final_height // 2)
    video2_resized = video2_cropped.resize(height=final_height // 2)

    # Combine the videos vertically
    final_video = mp.CompositeVideoClip([
        video1_resized.set_position(("center", 0)),
        video2_resized.set_position(("center", final_height // 2))
    ], size=(final_width, final_height))

    # Write the result to a file
    final_video.write_videofile(output_path, codec="libx264", fps=25)

    # Close the video clips
    video1.close()
    video2.close()

if __name__ == "__main__":
    # Example usage
    combine_videos_vertically(
        "src/temp_storage/working/asset_edited_video_AspectRatio.SQUARE.mp4",
        "src/temp_storage/working/sara_longshotat_ai_nova.mp4", 
        "src/temp_storage/working/combined_output.mp4",
        shift_video1=(0, 0), shift_video2=(0, -100))