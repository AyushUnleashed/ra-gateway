ReelsAI.pro gateway backend

# TODO:

## Database and Storage
- [x] Design data models
- [x] Decide what to save on VM vs what to save on bucket & where
- [x] Decide which tables need to be created vs what to keep in memory
- [x] Create full endpoint flow with dummy functions
- [x] Create tables on Supabase
- [x] Add sample data to tables on Supabase
- [ ] Write code to get data from Supabase DB
- [ ] Write code to upload files to Supabase bucket

## Misc
- [x] Create Config
- [x] Decide on paths & create variables for them

## Core Features
- [x] Implement script generation module
- [x] Implement T2S generation module
- [ ] Implement lip sync generation module
- [ ] Implement video editing module v1
- [ ] Implement caption generation module









## Things to save in pipeline & Where to save them :
1. T2s audio file for a particular project, particular voice
2. Lipsync video generated for a particular project, particular actor, particular voice
3. Asset Images or Videos
4. Asset Bg video generated using those assets.
5. Combined Edited video of asset + Actor lipsync video 
6. Caption added version of last video 



## Storage

- tree
    - Supabase Bucket (Persistent Storage):
        - `/actors/{actor_id}/`
            - `portrait_video.mp4`: The original actor portrait video
            - `portrait_matted_video.mp4`: The original actor portrait video bg removed
            - `squared_video.mpy`: Squared actor video
            - `squared_matted_video`: Sqaured actor video with bg removed.
            - `thumbnail.png`: Thumbnail image for the actor
        - `/products/{product_id}/`
            - `logo.png`: Product logo (if applicable)
        - `/voices/{voice_id}/`
            - `sample.mp3`: Voice sample audio (if applicable)
        - `/projects/{project_id}/`
            - `t2s_audio_{voice.voice_identifier}.mp3`: Text-to-speech generated audio
            - `final_video_w_captions.mp4`: Final edited video with captions


    - Local VM Storage (Temporary Storage):
        - `/temp_storage/{project_id}/`
            - `assets/`: Folder for uploaded user assets
                - `image1.jpg`, `video1.mp4`, etc.
            - `working/`: Folder for temporary files during processing
                - `t2s_audio_{voice.voice_identifier}.mp3`: Text-to-speech generated audio
                - `lipsync_video_{actor.name}.mp4`: Generated lipsync video
                - `bg_video.mp4` : Generated bg video from the assets provided
                - `composite_video.mp4`: Generated composite video combining bg_video & lipsync video
                - `final_video_w_captions.mp4`: Final edited video with captions
                