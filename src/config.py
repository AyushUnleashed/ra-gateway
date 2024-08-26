import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    REPLICATE_TOKEN = os.getenv("REPLICATE_TOKEN")