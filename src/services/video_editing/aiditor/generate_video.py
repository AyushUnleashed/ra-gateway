from math import floor
from PIL import Image
import requests
from io import BytesIO
import cv2
import json
import os
import hashlib
from pathlib import Path
import uuid
import time
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

frame_width = 1080
frame_height = 1920

frame_center = [frame_width/2, frame_height/2]
full_frame_container_dimensions = [frame_width, frame_height]

upper_container_dimensions = [frame_width, frame_height/2]
lower_container_dimensions = [frame_width, frame_height/2]

upper_container_center = [frame_width/2, frame_height/4]
lower_container_center = [frame_width/2, frame_height/4*3]

# Create cache directory if it doesn't exist
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

def get_cached_file_path(url):
    # Create a unique filename using URL hash
    url_hash = hashlib.md5(url.encode()).hexdigest()
    file_ext = url.split('.')[-1].lower()
    return CACHE_DIR / f"{url_hash}.{file_ext}"

def download_and_cache(url):
    cache_path = get_cached_file_path(url)
    
    # If file exists in cache, return the cached path
    if cache_path.exists():
        return str(cache_path)
    
    # Download and save to cache
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(cache_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return str(cache_path)
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return None
    
def get_video_duration(actor_video_url):
    """Get the duration of a video file in milliseconds"""
    try:
        video_path = download_and_cache(actor_video_url)
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = (frame_count / fps) * 1000  # Convert to milliseconds
        video.release()
        return int(duration)
    except Exception as e:
        print(f"Error getting video duration: {str(e)}")
        return 30000  # Default duration if unable to get actual duration

def get_position_and_scale(container_center, asset_url, z_index, fit_dimension='auto', rotation=0, is_full_frame=False):
    try:
        # Get cached file path or download
        local_path = download_and_cache(asset_url)
        if not local_path:
            raise Exception("Failed to download or retrieve from cache")
        
        file_ext = asset_url.split('.')[-1].lower()
        
        if file_ext in ['jpg', 'jpeg', 'png', 'gif']:
            media = Image.open(local_path)
            width, height = media.size
            
        elif file_ext in ['mp4', 'mov', 'avi', 'webm']:
            video = cv2.VideoCapture(local_path)
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video.release()
            
            # If video dimensions couldn't be read, use default dimensions
            if width == 0 or height == 0:
                width, height = frame_width, frame_height
                
        elif file_ext in ['mp3', 'wav', 'aac']:
            width, height = 100, 100
            
        else:
            width, height = frame_width, frame_height

        # Use full frame dimensions if is_full_frame is True
        container_dims = full_frame_container_dimensions if is_full_frame else upper_container_dimensions

        # Calculate scale based on fit_dimension
        if fit_dimension == 'width':
            scale = container_dims[0] / width
        elif fit_dimension == 'height':
            scale = container_dims[1] / height
        else:
            # If no fit_dimension specified, fit based on larger dimension
            width_scale = container_dims[0] / width
            height_scale = container_dims[1] / height
            scale = width_scale if width >= height else height_scale
        
        return {
            "position": {
                "x": container_center[0],
                "y": container_center[1],
                "z": z_index
            },
            "transform": {
                "scale": {
                    "x": scale,
                    "y": scale
                },
                "rotation": rotation
            },
            "size": {
                "width": width,
                "height": height
            }
        }
    except Exception as e:
        print(f"Error processing {asset_url}: {str(e)}")
        return {
            "position": {
                "x": container_center[0],
                "y": container_center[1],
                "z": z_index
            },
            "transform": {
                "scale": {
                    "x": 1,
                    "y": 1
                },
                "rotation": rotation
            },
            "size": {
                "width": frame_width,
                "height": frame_height
            }
        }

# Video structure:
# First 5s: Actor video
# Middle: Alternating between AA (two assets) and AD (asset + actor) patterns
# Last 5s: Actor video

only_actor_time = 5000

def create_video_json(actor_video_url, total_duration, assets, background_color_hex="#000000"):
    # Download files first...
    print("Caching actor video...")
    download_and_cache(actor_video_url)
    
    print("Caching assets...")
    for asset_url in assets:
        download_and_cache(asset_url)
    
    n = len(assets)
    P = floor(n/3)
    AD = n - 2*P
    AA = P
    no_of_screens = (AA+AD)
    total_duration_of_asset_screens = total_duration - 2*only_actor_time
    duration_of_asset_screens = total_duration_of_asset_screens / no_of_screens
    
    clips = []

    clips.append(get_captions_clip(x_position=540,y_position=1600,start_time=0,offset=0,end_time=only_actor_time))
    
    # First 5 seconds - Actor video (full screen)
    actor_start = get_position_and_scale(frame_center, actor_video_url, 0, 'height', 0, True)
    clips.append({
        "id": str(uuid.uuid4()),
        "type": "video",
        "name": actor_video_url.split('/')[-1],
        "source": actor_video_url,
        "timeFrame": {
            "start": 0,
            "end": only_actor_time,
            "offset": 0
        },
        "position": actor_start["position"],
        "volume": 1,
        "transform": actor_start["transform"],
        "size": actor_start["size"]
    })
    
    current_time = only_actor_time
    asset_index = 0
    
    # Alternate between AA and AD patterns
    remaining_aa = AA
    remaining_ad = AD
    
    
    clips.append(get_captions_clip(x_position=540,y_position=960,start_time=current_time,offset=current_time,end_time=current_time+total_duration_of_asset_screens))

    while remaining_aa > 0 or remaining_ad > 0:
        # Handle AA pattern
        if remaining_aa > 0:
            # Add solid background color clip for AA pattern
            clips.append({
                "id": str(uuid.uuid4()),
                "type": "image",
                "name": "background",
                "source": "https://aiditor-uploads.s3.ap-south-1.amazonaws.com/uploads/05b4fbc3f169175e6deb97b3977175b6.jpg",
                "timeFrame": {
                    "start": current_time,
                    "end": current_time + duration_of_asset_screens
                },
                "position": {
                    "x": frame_width/2,
                    "y": frame_height/2,
                    "z": 1
                },
                "transform": {
                    "scale": {
                        "x": 1,
                        "y": 1
                    },
                    "rotation": 0
                },
                "size": {
                    "width": frame_width,
                    "height": frame_height
                }
            })
            
            # First asset in upper container
            upper_asset = get_position_and_scale(upper_container_center, assets[asset_index], 2)
            clips.append({
                "id": str(uuid.uuid4()),
                "type": "video" if assets[asset_index].lower().endswith(('mp4', 'mov', 'avi', 'webm')) else "image",
                "name": assets[asset_index].split('/')[-1],
                "source": assets[asset_index],
                "timeFrame": {
                    "start": current_time,
                    "end": current_time + duration_of_asset_screens
                },
                "position": upper_asset["position"],
                "volume": 1,
                "transform": upper_asset["transform"],
                "size": upper_asset["size"]
            })
            
            # Second asset in lower container
            asset_index += 1
            lower_asset = get_position_and_scale(lower_container_center, assets[asset_index], 2)
            clips.append({
                "id": str(uuid.uuid4()),
                "type": "video" if assets[asset_index].lower().endswith(('mp4', 'mov', 'avi', 'webm')) else "image",
                "name": assets[asset_index].split('/')[-1],
                "source": assets[asset_index],
                "timeFrame": {
                    "start": current_time,
                    "end": current_time + duration_of_asset_screens
                },
                "position": lower_asset["position"],
                "volume": 1,
                "transform": lower_asset["transform"],
                "size": lower_asset["size"]
            })
            asset_index += 1
            current_time += duration_of_asset_screens
            remaining_aa -= 1
        
        # Handle AD pattern
        if remaining_ad > 0:
            # Asset in upper container
            upper_asset = get_position_and_scale(upper_container_center, assets[asset_index], 2)
            clips.append({
                "id": str(uuid.uuid4()),
                "type": "video" if assets[asset_index].lower().endswith(('mp4', 'mov', 'avi', 'webm')) else "image",
                "name": assets[asset_index].split('/')[-1],
                "source": assets[asset_index],
                "timeFrame": {
                    "start": current_time,
                    "end": current_time + duration_of_asset_screens
                },
                "position": upper_asset["position"],
                "volume": 1,
                "transform": upper_asset["transform"],
                "size": upper_asset["size"]
            })
            
            # If this is the first AD pattern, add the continuous actor video
            if remaining_ad == AD:
                actor_clip = get_position_and_scale(lower_container_center, actor_video_url, 0)
                clips.append({
                    "id": str(uuid.uuid4()),
                    "type": "video",
                    "name": actor_video_url.split('/')[-1],
                    "source": actor_video_url,
                    "timeFrame": {
                        "start": only_actor_time,
                        "end": total_duration - only_actor_time,
                        "offset": max(0, only_actor_time - 0.1)
                    },
                    "position": actor_clip["position"],
                    "volume": 1,
                    "transform": actor_clip["transform"],
                    "size": actor_clip["size"]
                })
            
            asset_index += 1
            current_time += duration_of_asset_screens
            remaining_ad -= 1

    
        
    clips.append(get_captions_clip(x_position=540,y_position=1600,start_time=current_time,offset=current_time,end_time=total_duration))
    
    # Last 5 seconds - Actor video (full screen)
    actor_end = get_position_and_scale(frame_center, actor_video_url, 0, 'height', 0, True)
    clips.append({
        "id": str(uuid.uuid4()),
        "type": "video",
        "name": actor_video_url.split('/')[-1],
        "source": actor_video_url,
        "timeFrame": {
            "start": total_duration - only_actor_time,
            "end": total_duration,
            "offset": total_duration - only_actor_time
        },
        "position": actor_end["position"],
        "volume": 1,
        "transform": actor_end["transform"],
        "size": actor_end["size"]
    })
    
    # Add caption clip if provided
    
    result = {
        "metadata": {
            "backgroundColor": background_color_hex,  # Updated to use passed background color
            "duration": total_duration,
            "fps": 25,
            "canvas": {
                "width": frame_width,
                "height": frame_height
            },
            "name": "Reels AI Template"
        },
        "clips": clips
    }
    
    # Save to JSON file
    with open('video_template.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    return result

def render_video(video_json: Dict) -> Optional[str]:
    """
    Send a POST request to initiate video rendering
    
    Args:
        video_json (Dict): The video template JSON
    
    Returns:
        Optional[str]: The render ID if successful, None otherwise
    """
    API_KEY = os.environ.get('VIDEOAIDITOR_API_KEY')
    if not API_KEY:
        print("Error: VIDEOAIDITOR_API_KEY environment variable not set")
        return None
    
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY
    }
    
    # Prepare the request payload
    payload = {
        # "renderOptionsInUI": [],
        "metadata": video_json["metadata"],
        "clips": video_json["clips"],
        # "additional": {},
        # "autoGenerateCaptionWords": False,
        # "captionLanguageCode": "en-US"
    }
    
    try:
        response = requests.post(
            'https://api.videoaiditor.com/v1/renders',
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        render_id = response.json()['data']['_id']
        print(f"Render initiated with ID: {render_id}")
        return render_id
        
    except requests.exceptions.RequestException as e:
        print(f"Error initiating render: {str(e)}")
        return None

def monitor_render_progress(render_id: str, max_attempts: int = 60) -> Optional[str]:
    """
    Monitor the rendering progress and return the output URL when complete
    
    Args:
        render_id (str): The render ID to monitor
        max_attempts (int): Maximum number of attempts to check status (default: 60)
    
    Returns:
        Optional[str]: The output URL if successful, None otherwise
    """
    API_KEY = os.environ.get('VIDEOAIDITOR_API_KEY')
    if not API_KEY:
        print("Error: VIDEOAIDITOR_API_KEY environment variable not set")
        return None
    
    headers = {
        'x-api-key': API_KEY
    }
    
    attempt = 0
    while attempt < max_attempts:
        try:
            response = requests.get(
                f'https://api.videoaiditor.com/v1/renders/{render_id}',
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()['data']
            status = data.get('status')
            
            if status == 'completed':
                output_url = data.get('outputUrl')
                print(f"\nRendering completed!")
                print(f"Output URL: {output_url}")
                return output_url
            
            elif status == 'failed':
                error = data.get('error', 'Unknown error')
                print(f"\nRendering failed: {error}")
                return None
            
            else:
                print(f"Rendering in progress... Status: {status}")
                time.sleep(60)  # Wait 60 seconds before next check
                attempt += 1
                
        except requests.exceptions.RequestException as e:
            print(f"Error checking render status: {str(e)}")
            return None
    
    print("Timeout: Maximum attempts reached")
    return None


def create_and_render_video(actor_url: str, total_duration: int, assets: list) -> Optional[str]:
    """
    Create video JSON and initiate rendering
    
    Returns:
        Optional[str]: The output URL if successful, None otherwise
    """
    # Create video JSON template
    video_json = create_video_json(actor_url, total_duration, assets)
    
    # Initiate rendering
    render_id = render_video(video_json)
    if not render_id:
        return None
    
    # Monitor progress and get output URL
    return monitor_render_progress(render_id)

if __name__ == "__main__":
    actor_url = "https://aiditor-uploads.s3.ap-south-1.amazonaws.com/uploads/4cd491c7-f68c-46e1-9cda-089a883076d0.mp4"
    total_duration = get_video_duration(actor_video_url=actor_url) 
    assets = [
        "https://aiditor-uploads.s3.ap-south-1.amazonaws.com/uploads/72ac7657-7164-4442-bb4e-15851e9fc4e8.jpg",
        "https://aiditor-uploads.s3.ap-south-1.amazonaws.com/uploads/573135ba-9dcb-4690-993b-5bc943c36582.jpg",
        "https://aiditor-uploads.s3.ap-south-1.amazonaws.com/uploads/667545c5-1ae7-4c15-b2fc-dad6920a8adb.jpg",
        "https://aiditor-uploads.s3.ap-south-1.amazonaws.com/uploads/a0352f12-ff7c-4e0f-88ea-4437ccb8f4a4.jpg",
        "https://aiditor-uploads.s3.ap-south-1.amazonaws.com/uploads/4e667862-ba03-4184-bd92-94a913a6605a.jpg",
        "https://aiditor-uploads.s3.ap-south-1.amazonaws.com/uploads/0f1dd400-5d9d-451e-93f5-ec49e3be8b96.jpg",
        "https://aiditor-uploads.s3.ap-south-1.amazonaws.com/uploads/86ac3bfe-b121-4865-a6a8-4c7b85735743.jpg",
        "https://aiditor-uploads.s3.ap-south-1.amazonaws.com/uploads/57bfc58c-4662-4066-85ed-61a5c5b19a96.jpg",
        "https://aiditor-uploads.s3.ap-south-1.amazonaws.com/uploads/3f7bbb22-7b7a-4023-9f42-058b66605b73.jpg"
    ]

    caption_words = [
          {
            "start": 320,
            "end": 432,
            "word": "Welcome"
          },
          {
            "start": 432,
            "end": 568,
            "word": "to"
          },
          {
            "start": 568,
            "end": 816,
            "word": "Reels"
          },
          {
            "start": 816,
            "end": 1128,
            "word": "AI"
          },
          {
            "start": 1137,
            "end": 1609,
            "word": ".Pro"
          },
          {
            "start": 1737,
            "end": 1977,
            "word": "Want"
          },
          {
            "start": 2001,
            "end": 2137,
            "word": "to"
          },
          {
            "start": 2161,
            "end": 2393,
            "word": "create"
          },
          {
            "start": 2449,
            "end": 2873,
            "word": "amazing"
          },
          {
            "start": 2929,
            "end": 3193,
            "word": "video"
          },
          {
            "start": 3249,
            "end": 3457,
            "word": "ads"
          },
          {
            "start": 3481,
            "end": 3593,
            "word": "in"
          },
          {
            "start": 3609,
            "end": 3737,
            "word": "a"
          },
          {
            "start": 3761,
            "end": 4445,
            "word": "snap?"
          },
          {
            "start": 4825,
            "end": 5137,
            "word": "Just"
          },
          {
            "start": 5161,
            "end": 5345,
            "word": "visit"
          },
          {
            "start": 5385,
            "end": 5697,
            "word": "Reels"
          },
          {
            "start": 5761,
            "end": 6129,
            "word": "AI"
          },
          {
            "start": 6217,
            "end": 6489,
            "word": ".Pro"
          },
          {
            "start": 6537,
            "end": 6769,
            "word": "now"
          },
          {
            "start": 6817,
            "end": 6977,
            "word": "and"
          },
          {
            "start": 7001,
            "end": 7161,
            "word": "start"
          },
          {
            "start": 7193,
            "end": 7465,
            "word": "crafting"
          },
          {
            "start": 7505,
            "end": 7657,
            "word": "your"
          },
          {
            "start": 7681,
            "end": 7961,
            "word": "first"
          },
          {
            "start": 8032,
            "end": 8289,
            "word": "ad"
          },
          {
            "start": 8337,
            "end": 8929,
            "word": "today."
          },
          {
            "start": 9097,
            "end": 9377,
            "word": "For"
          },
          {
            "start": 9401,
            "end": 9513,
            "word": "all"
          },
          {
            "start": 9529,
            "end": 9681,
            "word": "you"
          },
          {
            "start": 9713,
            "end": 10089,
            "word": "founders"
          },
          {
            "start": 10137,
            "end": 10273,
            "word": "out"
          },
          {
            "start": 10289,
            "end": 10537,
            "word": "there,"
          },
          {
            "start": 10601,
            "end": 10849,
            "word": "this"
          },
          {
            "start": 10897,
            "end": 11105,
            "word": "tool"
          },
          {
            "start": 11145,
            "end": 11297,
            "word": "is"
          },
          {
            "start": 11321,
            "end": 11481,
            "word": "a"
          },
          {
            "start": 11513,
            "end": 11729,
            "word": "game"
          },
          {
            "start": 11777,
            "end": 12569,
            "word": "changer."
          },
          {
            "start": 12737,
            "end": 13017,
            "word": "So"
          },
          {
            "start": 13041,
            "end": 13153,
            "word": "what"
          },
          {
            "start": 13169,
            "end": 13249,
            "word": "are"
          },
          {
            "start": 13257,
            "end": 13401,
            "word": "you"
          },
          {
            "start": 13433,
            "end": 13625,
            "word": "waiting"
          },
          {
            "start": 13665,
            "end": 14153,
            "word": "for?"
          },
          {
            "start": 14289,
            "end": 14489,
            "word": "Get"
          },
          {
            "start": 14497,
            "end": 14665,
            "word": "your"
          },
          {
            "start": 14705,
            "end": 14905,
            "word": "ad"
          },
          {
            "start": 14945,
            "end": 15433,
            "word": "on."
          },
          {
            "start": 15569,
            "end": 15977,
            "word": "It's"
          },
          {
            "start": 16041,
            "end": 16457,
            "word": "so"
          },
          {
            "start": 16561,
            "end": 17009,
            "word": "easy."
          },
          {
            "start": 17097,
            "end": 17465,
            "word": "Visit,"
          },
          {
            "start": 17545,
            "end": 18365,
            "word": "generate,"
          },
          {
            "start": 18705,
            "end": 19281,
            "word": "see,"
          },
          {
            "start": 19393,
            "end": 19945,
            "word": "upload,"
          },
          {
            "start": 20025,
            "end": 20441,
            "word": "select,"
          },
          {
            "start": 20513,
            "end": 20793,
            "word": "and"
          },
          {
            "start": 20849,
            "end": 21473,
            "word": "bam."
          },
          {
            "start": 21649,
            "end": 22129,
            "word": "AI"
          },
          {
            "start": 22177,
            "end": 22385,
            "word": "ad"
          },
          {
            "start": 22425,
            "end": 22617,
            "word": "ready"
          },
          {
            "start": 22641,
            "end": 22777,
            "word": "to"
          },
          {
            "start": 22801,
            "end": 23401,
            "word": "roll."
          },
          {
            "start": 23553,
            "end": 23889,
            "word": "Boost"
          },
          {
            "start": 23937,
            "end": 24121,
            "word": "your"
          },
          {
            "start": 24153,
            "end": 24369,
            "word": "product"
          },
          {
            "start": 24417,
            "end": 24817,
            "word": "engagement"
          },
          {
            "start": 24841,
            "end": 25001,
            "word": "with"
          },
          {
            "start": 25033,
            "end": 25441,
            "word": "Reels"
          },
          {
            "start": 25513,
            "end": 25953,
            "word": "AI"
          },
          {
            "start": 26009,
            "end": 26465,
            "word": ".Pro"
          },
          {
            "start": 26585,
            "end": 26881,
            "word": "It's"
          },
          {
            "start": 26913,
            "end": 27153,
            "word": "super"
          },
          {
            "start": 27209,
            "end": 27425,
            "word": "smooth."
          }
        ]
    
    def get_captions_clip(x_position: int, y_position: int, start_time:int, offset:int,end_time:int) -> dict:
        import uuid
        
        return {
            "id": str(uuid.uuid4()),
            "type": "caption",
            "name": "Caption",
            "timeFrame": {
                "start":start_time,
                "offset": offset,
                "end": end_time
            },
            "position": {
                "x": x_position,
                "y": y_position,
                "z": 10
            },
            "volume": 1,
            "transform": {
                "scale": {
                    "x": 1,
                    "y": 1
                },
                "rotation": 0
            },
            "size": {
                "width": 500,
                "height": 100
            },
            "captionProperties": {
                "words": caption_words,
                "highlightTextProperties": {
                    "fontSize": 80,
                    "color": "#FFFFFF",
                    "fontFamily": "Montserrat",
                    "fontWeight": 800,
                    "fontStyle": "normal",
                    "underline": False,
                    "backgroundColor": "#ff1414",
                    "padding": 8,
                    "strokeWidth": 4,
                    "strokeColor": "#000000"
                },
                "nonHighlightTextProperties": {
                    "fontSize": 60,
                    "color": "#ffffff",
                    "fontFamily": "Montserrat",
                    "fontWeight": 600,
                    "fontStyle": "normal",
                    "underline": False,
                    "padding": 0,
                    "strokeWidth": 4,
                    "borderWidth": 0,
                    "strokeColor": "#000000"
                },
                "textAlign": "center",
                "maxWidth": 1080,
                "maxWordsInFrame": 5
            },
            "textAlign": "center",
            "maxWidth": 1080,
            "maxWordsInFrame": 5
        }

    output_url = create_and_render_video(actor_url, total_duration, assets)
    # create_video_json(actor_url, total_duration, assets, captions_clip)
    if output_url:
        print(f"\nFinal video URL: {output_url}")