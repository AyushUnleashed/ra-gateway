
- **app.py**
    - Endpoint: `app.get`
      - Path: `/sentry-debug`
      - Function: `trigger_error`

- **setup.py**

### `src`

- **src\__init__.py**

### `src\api`

- **src\api\utils.py**
    - Function: `encode_jwt_part`
    - Function: `verify_token`

### `src\api\llm_api`

- **src\api\llm_api\openai_async.py**
    - Function: `prepare_llm_prompt`
    - Function: `reset_chat_history`
    - Function: `set_system_prompt`
    - Function: `fetch_openai_response`
    - Function: `fetch_openai_response_with_system_prompt`
    - Function: `_fetch_openai_response_internal`

- **src\api\llm_api\openai_sync.py**
    - Function: `prepare_llm_prompt`
    - Function: `reset_chat_history`
    - Function: `set_system_prompt`
    - Function: `fetch_openai_response`
    - Function: `fetch_openai_response_with_system_prompt`

- **src\api\llm_api\prompts.py**
  - Class: `Prompts`

### `src\api\routes`

- **src\api\routes\actor_routes.py**
    - Endpoint: `actors_router.get`
      - Path: `/api/actors-and-voices`
      - Function: `get_actors_and_voices`
  - Class: `SelectActorVoiceRequest`
    - Endpoint: `actors_router.post`
      - Path: `/api/projects/{project_id}/select-actor-voice`
      - Function: `select_actor_voice`

- **src\api\routes\main_routes.py**
    - Endpoint: `main_router.get`
      - Path: `/health`
      - Function: `root`
    - Endpoint: `main_router.head`
      - Path: `/health`
      - Function: `root`
    - Endpoint: `main_router.post`
      - Path: `/api/projects/{project_id}/video-configuration`
      - Function: `configure_video`
    - Endpoint: `main_router.post`
      - Path: `/api/projects/{project_id}/assets`
      - Function: `upload_asset`
    - Endpoint: `main_router.post`
      - Path: `/api/projects/{project_id}/generate-final-video`
      - Function: `generate_final_video`

- **src\api\routes\products_routes.py**
  - Class: `CreateProductRequest`
    - Endpoint: `products_router.post`
      - Path: `/api/products/create-product`
      - Function: `create_product`
    - Endpoint: `products_router.get`
      - Path: `/api/products/get-all-products`
      - Function: `get_all_products`
    - Endpoint: `products_router.get`
      - Path: `/api/products/{product_id}`
      - Function: `get_product`
    - Endpoint: `products_router.put`
      - Path: `/api/products/{product_id}`
      - Function: `update_product`

- **src\api\routes\projects_routes.py**
  - Class: `CreateProjectRequest`
    - Endpoint: `projects_router.get`
      - Path: `/api/projects`
      - Function: `get_all_project_dtos`
    - Endpoint: `projects_router.get`
      - Path: `/api/projects/{project_id}`
      - Function: `get_project`
    - Endpoint: `projects_router.post`
      - Path: `/api/projects/create-project`
      - Function: `create_project`

- **src\api\routes\scripts_routes.py**
    - Endpoint: `scripts_router.post`
      - Path: `/api/projects/{project_id}/generate-script`
      - Function: `generate_script`
    - Endpoint: `scripts_router.get`
      - Path: `/api/projects/{project_id}/scripts`
      - Function: `get_script`
    - Endpoint: `scripts_router.put`
      - Path: `/api/projects/{project_id}/scripts/update`
      - Function: `update_script`
    - Endpoint: `scripts_router.put`
      - Path: `/api/projects/{project_id}/scripts/finalize`
      - Function: `finalize_script`

- **src\api\routes\users_routes.py**
    - Endpoint: `users_router.post`
      - Path: `/api/check-beta`
      - Function: `check_beta`
    - Endpoint: `users_router.get`
      - Path: `/api/users/get_credits`
      - Function: `get_credits`
    - Endpoint: `users_router.post`
      - Path: `/api/users/reduce_credits`
      - Function: `reduce_credit`
    - Function: `process_credit_reduction`

- **src\api\routes\video_layouts_routes.py**
  - Class: `SelectLayoutRequest`
    - Endpoint: `video_layouts_router.get`
      - Path: `/api/video-layouts`
      - Function: `get_video_layouts`
    - Function: `get_video_layout_base`
    - Endpoint: `video_layouts_router.post`
      - Path: `/api/projects/{project_id}/select-layout`
      - Function: `select_layout`

- **src\api\routes\webhook_routes.py**
    - Function: `save_to_file`
    - Endpoint: `webhook_router.post`
      - Path: `/webhook/replicate`
      - Function: `replicate_webhook`
    - Function: `process_replicate_webhook`
    - Function: `get_and_update_project`
    - Function: `update_project_status`
    - Function: `handle_webhook_error`

- **src\api\routes\__init__.py**

### `src\aws_tools`

- **src\aws_tools\upload_to_s3.py**
    - Function: `upload_to_s3`
    - Function: `handle_s3_upload`

### `src\config`

- **src\config\constants.py**
  - Class: `Constants`
  - Class: `TableNames`

- **src\config\settings.py**
  - Class: `Settings`

### `src\models`

- **src\models\base_models.py**
  - Class: `AssetType`
  - Class: `ProjectStatus`
  - Class: `DurationOption`
  - Class: `OpenAIVoiceIdentifier`
  - Class: `VideoLayoutType`
  - Class: `AspectRatio`
  - Class: `Asset`
    - Function: `serialize_for_db`
  - Class: `VideoConfiguration`
    - Function: `serialize_for_db`
  - Class: `Script`
    - Function: `serialize_for_db`
  - Class: `ProductBase`
  - Class: `Product`
    - Function: `serialize_for_db`
  - Class: `ActorBase`
  - Class: `Actor`
    - Function: `serialize_for_db`
  - Class: `TTSProvider`
  - Class: `ElevenLabsVoiceIdentifier`
  - Class: `VoiceBase`
  - Class: `Voice`
    - Function: `serialize_for_db`
  - Class: `VideoLayoutBase`
  - Class: `VideoLayout`
    - Function: `serialize_for_db`
  - Class: `ProjectDTO`
  - Class: `Project`
    - Function: `serialize_for_db`
  - Class: `User`
    - Function: `serialize_for_db`

- **src\models\shared_state.py**

- **src\models\__init__.py**

### `src\notification`

- **src\notification\async_slack_bot.py**
  - Class: `SlackBot`
    - Function: `__init__`
    - Function: `send_message`

- **src\notification\gmail_service.py**
    - Function: `send_email`
    - Function: `send_video_ready_alert_by_email`

### `src\services\bg_vid_generation`

- **src\services\bg_vid_generation\generate_bg_video.py**
    - Function: `generate_background_video_using_assets`

### `src\services\captions_generation`

- **src\services\captions_generation\add_captions.py**
  - Class: `CaptionType`
    - Function: `__init__`
    - Function: `render`
    - Function: `get_text_size`
  - Class: `HighlightedWordsCaption`
    - Function: `__init__`
    - Function: `render`
  - Class: `BoxedHighlightCaption`
    - Function: `__init__`
    - Function: `render`
    - Function: `transcribe_video`
    - Function: `process_video_for_captions`

- **src\services\captions_generation\add_captions_backup.py**
  - Class: `CaptionType`
    - Function: `__init__`
    - Function: `render`
  - Class: `StandardCaption`
    - Function: `__init__`
    - Function: `render`
  - Class: `OutlinedCaption`
    - Function: `__init__`
    - Function: `render`
  - Class: `HighlightedWordsCaption`
    - Function: `__init__`
    - Function: `render`
    - Function: `get_max_words_per_line`
    - Function: `transcribe_video`
    - Function: `process_video`

### `src\services\lipsync_generation`

- **src\services\lipsync_generation\generate_lipsync.py**
    - Function: `generate_lipsync_video`
    - Function: `main`

- **src\services\lipsync_generation\muse_talk_lipsync.py**
  - Class: `MuseTalkPredictionResponse`
    - Function: `create_muste_talk_prediction`
    - Function: `poll_for_lipsync_video`
    - Function: `main`

- **src\services\lipsync_generation\wav2lip_lipsync.py**
    - Function: `generate_actor_video`

### `src\services\script_generation`

- **src\services\script_generation\generate_script.py**
    - Function: `generate_script_with_llm`
    - Function: `generate_script`
    - Function: `main`

### `src\services\video_editing`

- **src\services\video_editing\combine_videos.py**
    - Function: `combine_videos_vertically`
    - Function: `center_crop_to_9_8`

- **src\services\video_editing\edit_asset_video.py**
    - Function: `save_intermediate_clip`
    - Function: `generate_asset_video`

- **src\services\video_editing\optimised_edit_asset_video.py**
    - Function: `edit_asset_video`
    - Function: `process_asset`
    - Function: `create_composite_clip`
    - Function: `write_frames`

### `src\services\voice_over_generation`

- **src\services\voice_over_generation\elevenlabs_t2s.py**
    - Function: `elevenlabs_text_to_speech`

- **src\services\voice_over_generation\generate_t2s.py**
    - Function: `generate_t2s_audio`
    - Function: `get_audio_duration_librosa`
    - Function: `main`

- **src\services\voice_over_generation\openai_t2s.py**
    - Function: `openai_text_to_speech`

### `src\supabase_tools`

- **src\supabase_tools\handle_actor_tb_updates.py**
    - Function: `get_actors_from_db`
    - Function: `get_actor_from_db`

- **src\supabase_tools\handle_bucket_updates.py**
    - Function: `upload_file`
    - Function: `upload_file_to_projects`
    - Function: `get_public_url`

- **src\supabase_tools\handle_layout_tb_updates.py**
    - Function: `get_layouts_from_db`
    - Function: `get_layout_from_db`

- **src\supabase_tools\handle_product_tb_updates.py**
    - Function: `add_product_to_db`
    - Function: `get_product_from_db`
    - Function: `get_all_products_from_db`
    - Function: `update_product_in_db`
    - Function: `main`

- **src\supabase_tools\handle_project_tb_updates.py**
    - Function: `add_project_to_db`
    - Function: `get_project_from_db`
    - Function: `get_all_projects_from_db`
    - Function: `update_project_in_db`
    - Function: `get_project_id_from_prediction_id`
    - Function: `project_to_dto`
    - Function: `get_dummy_project`
    - Function: `main`

- **src\supabase_tools\handle_users_tb_updates.py**
    - Function: `get_user_from_db`
    - Function: `update_user_in_db`
    - Function: `main`

- **src\supabase_tools\handle_voice_tb_updates.py**
  - Class: `DatabaseError`
    - Function: `get_voices_from_db`
    - Function: `get_voice_from_db`

- **src\supabase_tools\supabase_client.py**
    - Function: `create_supabase_client`

- **src\supabase_tools\upload_file_to_supabase.py**

### `src\utils`

- **src\utils\file_handling.py**
  - Class: `LocalPaths`
  - Class: `SupabasePaths`
    - Function: `get_local_path`
    - Function: `save_local_file`
    - Function: `get_supabase_path`

- **src\utils\logger.py**

- **src\utils\util_functions.py**
    - Function: `download_video`
    - Function: `save_file_locally`
    - Function: `determine_asset_type`

- **src\utils\video_utils.py**

### `src\workflow`

- **src\workflow\video_gen_workflow.py**
    - Function: `start_lipsync_gen_with_audio`
    - Function: `start_assets_video_generation`
    - Function: `video_post_processing`
    - Function: `generate_asset_video_async`
    - Function: `combine_videos`
    - Function: `add_captions_to_video`

- **src\workflow\wrokflow_utils.py**
    - Function: `download_lipsync_video`
    - Function: `upload_final_video`
    - Function: `handle_error`
    - Function: `send_video_ready_notification`
    - Function: `notify_via_slack`
    - Function: `handle_success`
