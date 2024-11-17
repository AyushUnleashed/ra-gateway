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
                
----------------


# ReelsAI.pro Gateway Backend

This repository contains the backend code for the ReelsAI.pro gateway, which is responsible for generating video ads using various AI-driven modules. The backend is built using FastAPI and integrates with Supabase for database management, as well as other services for video processing and notifications.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [API Routes](#api-routes)
- [Database](#database)
- [Services](#services)
- [Types and Models](#types-and-models)
- [Storage](#storage)
- [Monitoring and Notifications](#monitoring-and-notifications)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [Setup and Installation](#setup-and-installation)

## Features

- **Script Generation**: Generate ad scripts using LLMs.
- **Text-to-Speech (T2S) Generation**: Convert scripts to audio.
- **Lip Sync Generation**: Create lip-synced videos.
- **Video Editing**: Combine assets and generate final videos.
- **Caption Generation**: Add captions to videos.
- **User Management**: Handle user credits and profiles.
- **Product Management**: Manage products and their details.

## Architecture

The backend is structured into several modules, each responsible for a specific part of the video generation pipeline. The main components include:

- **API**: FastAPI-based endpoints for handling requests.
- **Services**: Business logic for script generation, T2S, lip sync, and video editing.
- **Supabase Tools**: Interactions with the Supabase database.
- **Notification**: Sending notifications via Slack and email.

## API Routes

The API is organized into several routes, each handling different aspects of the application:

- **Main Routes**: Handles video generation and project management.
  - `POST /api/projects/{project_id}/generate-final-video`: Initiates the video generation process.
  - `GET /health`: Health check endpoint.
  - `HEAD /health`: Health check endpoint for head requests.

- **Project Routes**: Manage projects.
  - `GET /api/projects`: Retrieve all projects for a user.
  - `GET /api/projects/{project_id}`: Retrieve a specific project.
  - `POST /api/projects/create-project`: Create a new project.

- **Product Routes**: Manage products.
  - `POST /api/products/create-product`: Create a new product.
  - `GET /api/products/get-all-products`: Retrieve all products.
  - `GET /api/products/{product_id}`: Retrieve a specific product.
  - `PUT /api/products/{product_id}`: Update a specific product.

- **User Routes**: Manage user profiles and credits.
  - `POST /api/check-beta`: Check if a user is a beta user.
  - `GET /api/users/get_credits`: Get user credits.
  - `POST /api/users/reduce_credits`: Reduce user credits.

- **Webhook Routes**: Handle external service callbacks.
  - `POST /webhook/replicate`: Handle webhook from the replicate service.

- **Video Layout Routes**: Manage video layouts.
  - `GET /api/video-layouts`: Retrieve all video layouts.

- **Script Routes**: Manage scripts.
  - `POST /api/projects/{project_id}/generate-script`: Generate a script for a project.
  - `GET /api/projects/{project_id}/scripts`: Retrieve scripts for a project.

For more details, refer to the code in the following files:
- `src/api/routes/main_routes.py` (startLine: 1, endLine: 179)
- `src/api/routes/projects_routes.py` (startLine: 1, endLine: 32)
- `src/api/routes/products_routes.py` (startLine: 1, endLine: 31)
- `src/api/routes/scripts_routes.py` (startLine: 1, endLine: 50)
- `src/api/routes/webhook_routes.py` (startLine: 1, endLine: 47)
- `src/api/routes/video_layout_routes.py` (startLine: 1, endLine: 40)

## Database

The application uses Supabase for database management. The tables include:

- **Projects**: Stores project details and statuses.
- **Products**: Stores product information.
- **Users**: Manages user profiles and credits.
- **Video Layouts**: Stores video layout configurations.

Database interactions are handled through the `supabase_tools` module. Refer to:
- `src/supabase_tools/handle_project_tb_updates.py` (startLine: 1, endLine: 29)
- `src/supabase_tools/handle_product_tb_updates.py` (startLine: 1, endLine: 31)
- `src/supabase_tools/handle_layout_tb_updates.py` (startLine: 1, endLine: 25)

## Services

The backend includes several services for processing and generating content:

- **Script Generation**: Uses LLMs to generate ad scripts.
  - `src/services/script_generation/generate_script.py` (startLine: 37, endLine: 61)

- **Voice Over Generation**: Converts scripts to audio using T2S.
  - `src/services/voice_over_generation/generate_t2s.py`

- **Lip Sync Generation**: Creates lip-synced videos.
  - `src/services/lipsync_generation/generate_lipsync.py`

- **Video Editing**: Combines assets and generates final videos.
  - `src/services/video_editing/edit_video.py`

- **Caption Generation**: Adds captions to videos.
  - `src/services/captions_generation/add_captions.py`

## Types and Models

The application defines several types and models to structure data:

- **Enums**: Define various types and statuses.
  - `AssetType`, `ProjectStatus`, `DurationOption`, `OpenAIVoiceIdentifier`, `VideoLayoutType`, `AspectRatio`

- **Models**: Define the structure of data entities.
  - `Asset`, `VideoConfiguration`, `Script`, `ProductBase`, `Product`

Refer to:
- `src/models/base_models.py` (startLine: 1, endLine: 110)

## Storage

The application uses both persistent and temporary storage:

- **Supabase Bucket (Persistent Storage)**:
  - Stores actor videos, product logos, voice samples, and final project outputs.

- **Local VM Storage (Temporary Storage)**:
  - Used for processing intermediate files during video generation.

Refer to:
- `Readme.md` (startLine: 44, endLine: 72)

## Monitoring and Notifications

- **Sentry**: Used for error tracking and monitoring.
- **Slack**: Notifications are sent to a Slack channel for important events.
- **Email**: Users are notified via email when their video is ready.

Refer to:
- `src/notification/async_slack_bot.py`
- `src/config.py` (startLine: 1, endLine: 17)

## Deployment

The application is containerized using Docker and deployed on AWS EC2. The CI/CD pipeline is managed using GitHub Actions.

- **CI/CD Workflow**: `.github/workflows/cicd_prod.yaml`
- **Deployment Workflow**: `.github/workflows/deploy.yml`

## Environment Variables

The application requires several environment variables for configuration. These include API keys, database URLs, and other secrets. Refer to the `.env` file for a complete list.

## Setup and Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/reelsai-pro-backend.git
   cd reelsai-pro-backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

4. **Access the API documentation**:
   Visit `http://localhost:8000/docs` for the Swagger UI.

For more detailed setup instructions, refer to the `Dockerfile` and `setup.py`.