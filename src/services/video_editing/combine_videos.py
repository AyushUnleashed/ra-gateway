import moviepy.editor as mp

def combine_videos_vertically(video1_path, video2_path, output_path):
    # Load the videos
    video1 = mp.VideoFileClip(video1_path)
    video2 = mp.VideoFileClip(video2_path)

    # Calculate the dimensions for the final video
    final_width = max(video1.w, video2.w)
    final_height = final_width * 9 // 16

    # Function to crop and resize a video
    def crop_and_resize(video):
        # Calculate the crop height
        crop_height = video.h * 8 // 9  # This maintains the 16:9 ratio
        # Crop from the center
        y1 = (video.h - crop_height) // 2
        cropped = video.crop(y1=y1, height=crop_height)
        # Resize to half the final height
        return cropped.resize(height=final_height // 2)

    # Crop and resize both videos
    video1_processed = crop_and_resize(video1)
    video2_processed = crop_and_resize(video2)

    # Combine the videos vertically
    final_video = mp.CompositeVideoClip([
        video1_processed.set_position((0, 0)),
        video2_processed.set_position((0, final_height // 2))
    ], size=(final_width, final_height))

    # Write the result to a file
    final_video.write_videofile(output_path)

    # Close the video clips
    video1.close()
    video2.close()

if __name__ == "__main__":
# Example usage
    combine_videos_vertically("video1.mp4", "video2.mp4", "combined_output.mp4")