import boto3
from botocore.exceptions import NoCredentialsError
import os
import boto3
from botocore.exceptions import NoCredentialsError
from src.utils.constants import Constants

def upload_to_s3(file_name, bucket, s3_file_name):
    # Normalize file paths to use forward slashes
    file_name = file_name.replace('\\', '/')
    s3_file_name = s3_file_name.replace('\\', '/')

    s3 = boto3.client('s3')
    # Construct the S3 file URL correctly with forward slashes
    s3_file_url = f"https://{bucket}.s3.amazonaws.com/{s3_file_name}"

    try:
        # Upload the file, overwriting if it already exists
        s3.upload_file(file_name, bucket, s3_file_name)
        print("File uploaded successfully, overwriting the existing one if necessary.")
        return True, s3_file_url
    except NoCredentialsError:
        print("Credentials not available")
        return False, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False, None
    
def handle_s3_upload(file_path: str):
    file_path = f'{file_path}'
    # Replace backslashes with forward slashes to ensure URL compatibility
    file_path = file_path.replace('\\', '/')

    s3_bucket = Constants.S3_BUCKET_NAME
    # Create the full path of the file where the image will be saved
    s3_file_path = file_path

    return upload_to_s3(file_path, s3_bucket, s3_file_path)

if __name__ == "__main__":
    # Assuming the sample user image is stored in 'user_content/sample/' directory
    sample_image_directory = ''
    sample_image_name = 'aws_tools/temp.mp4'  # Replace with your actsual image file name
    sample_image_path = os.path.join(sample_image_directory, sample_image_name)
    print(sample_image_path)
    # Upload the sample user image to S3
    print(handle_s3_upload(sample_image_path))