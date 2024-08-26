import uuid
from fastapi import APIRouter
basic_router = APIRouter()

from src.models.base_models import ProductInfo, Actor
from src.models.request_models import AddProductRequest, SetVideoInfoRequest
from src.supabase_tools.handle_product_tb_updates import add_product_to_db, get_product_from_db

@basic_router.get("/")
async def read_root():
    return {"message": "Welcome to the reels ai backend gateway. This is the root endpoint."}



@basic_router.post("/add_product")
async def add_product(request: AddProductRequest):
    try:
        product_id = str(uuid.uuid4())
        product_info = ProductInfo(
            product_id=product_id,
            name=request.name,
            description=request.description,
            logo=request.logo
        )
        # Assuming add_product_to_db is a function that saves the product_info to the database
        add_product_to_db(product_info)
        return {"product_id": product_id}
    except Exception as e:
        return {"error": str(e)}

from src.services.script_generation.generate_script import generate_script
from src.models.base_models import VideoInfo

def download_video_assets(video_info, video_assets):
    import os
    import shutil

    assets_folder = "assets"
    if not os.path.exists(assets_folder):
        os.makedirs(assets_folder)

    for asset in video_assets:
        asset_type = asset.asset_type.name.lower()
        asset_folder = os.path.join(assets_folder, video_info.product_id, video_info.video_id, asset_type)
        if not os.path.exists(asset_folder):
            os.makedirs(asset_folder)

        asset_path = os.path.join(asset_folder, os.path.basename(asset.asset_local_path))
        shutil.copy(asset.asset_local_path, asset_path)
        asset.asset_local_path = asset_path

    return video_info


# after this we have video info object with local paths to the assets
@basic_router.post("/set_video_info")
async def set_video_info(set_video_info_request: SetVideoInfoRequest):
    try:
        video_info:VideoInfo = set_video_info_request.video_info
        video_assets = set_video_info_request.video_assets

        video_info:VideoInfo = download_video_assets(video_info, video_assets)  # Assuming this function downloads the video assets to the local filesystem

        product: ProductInfo = get_product_from_db(video_info.product_id)
        script = generate_script(
            product_description=product.description,
            product_name=product.name ,  # Assuming product_name is not needed for script generation
            cta=video_info.cta,
            target_audience=video_info.target_audience,
            duration_limit=video_info.duration_limit
        )
        return {"script": script, "video_info": video_info}
    except Exception as e:
        return {"error": str(e)}



from src.services.lipsync_generation.generate_wav2lip import do_lipsync
from src.services.voice_over_generation.generate_t2s import generate_audio_from_script

@basic_router.post("/generate_reel")
async def generate_reel(video_info: VideoInfo, actor_id: str, voice_id: str, layout_type: str, caption_type:str):
    try:

        reel_script = video_info.script

        # 1. Generate T2s audio, get url
        t2s_audio_url = generate_audio_from_script(reel_script, voice_id, video_info.product_id, video_info.video_id)
        # 2. Get Actor original video url
        curr_actor = Actor(actor_id)

        actor_video_url = curr_actor.original_video_url

        # 3. Generate lipsync video, get url
        lip_sync_video_path = do_lipsync(t2s_audio_url, actor_video_url, video_info.product_id, video_info.video_id)

        #4. Generate background video
        background_video_path = generate_background_video_using_assets(video_info.assets,video_info.actual_video_length)

        #5. Combine all videos
        combined_video_path = combine_videos(lip_sync_video_path, background_video_path,layout_type="TOP_BOTTOM")

        #6. Add captions to video
        final_video_path_with_captions = add_captions(combined_video_path, caption_type="RED_WHITE",layout_type="TOP_BOTTOM")

        #7. Upload to S3
        s3_final_video_url = upload_to_s3(final_video_path_with_captions)

        return {"final_video_url": s3_final_video_url}

    except Exception as e:
        return {"error": str(e)}




# 1. Create a new product
# 2. Generate multiple scripts for the product


