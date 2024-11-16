import fal_client

def get_status_with_logs(client, endpoint, request_id):
    return client.status(endpoint, request_id, with_logs=True)

request_id = "41daf5a9-a8a0-4e85-83c9-a703a8617fbf"
status = get_status_with_logs(fal_client, "fal-ai/kling-video/v1/pro/image-to-video", request_id)
print(status)