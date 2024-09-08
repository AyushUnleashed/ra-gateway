# def merge_audio_video(video_path, audio_path, output_path):
#     print("Merging audio and video...")
#     audio = ffmpeg.input(audio_path)
#     video = ffmpeg.input(video_path)
#     out = ffmpeg.output(video, audio, output_path, vcodec='libx264', acodec='aac')
#     out.run()
#     print(f"Audio and video merged successfully. Output saved to {output_path}")
