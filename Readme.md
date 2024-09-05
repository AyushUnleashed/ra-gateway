ReelsAI.pro gateway backend

## Storage

- tree
    - Supabase Bucket (Persistent Storage):
        - `/actors/{actor_id}/`
            - `full_video.mp4`: The original actor video
            - `thumbnail.png`: Thumbnail image for the actor
        - `/products/{product_id}/`
            - `logo.png`: Product logo (if applicable)
        - `/voices/{voice_id}/`
            - `sample.mp3`: Voice sample audio (if applicable)
        - `/projects/{project_id}/`
            - `t2s_audio.mp3`: Text-to-speech generated audio
            - `lipsync_video.mp4`: Generated lipsync video
            - `final_video.mp4`: Final edited video
    - Local VM Storage (Temporary Storage):
        - `/temp_storage/{project_id}/`
            - `assets/`: Folder for uploaded user assets
                - `image1.jpg`, `video1.mp4`, etc.
            - `working/`: Folder for temporary files during processing
                - `temp_audio.mp3`, `temp_video.mp4`, etc.