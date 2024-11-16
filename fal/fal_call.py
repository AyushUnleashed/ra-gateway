import fal_client

def submit_image_to_video():
    try:
        handler = fal_client.submit(
            "fal-ai/kling-video/v1/pro/image-to-video",
            arguments={
                "prompt": "Female YouTuber talking, keeping mouth closed and still. Natural movements: gentle head tilts, subtle blinks, slight shoulder sway, hair movement. Maintain blonde hair, floral pink top, neutral background with plants. Vertical format, high quality.",
                "image_url": "https://replicate.delivery/czjl/RV7DiBXkgT5EHNYOyfxP0ceEIR45vX0TFfy8Xk9ghVq4zEinA/tmps_d_woog.jpg"
            },
            webhook_url="https://optional.webhook.url/for/results",
        )
        request_id = handler.request_id
        print(f"Request succeeded with request ID: {request_id}")
        return request_id
    except Exception as e:
        print(f"Request failed with error: {e}")
        return None


if __name__ == "__main__":
    submit_image_to_video()

# Call the function
# submit_image_to_video()

# 4564d66d-c5d8-4f97-9596-ef17a0e40e0e
# 41daf5a9-a8a0-4e85-83c9-a703a8617fbf