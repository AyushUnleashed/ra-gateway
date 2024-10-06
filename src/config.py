import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    RAI_GATEWAY_BACKEND_URL = os.getenv("RAI_GATEWAY_BACKEND_URL")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
    ZOHO_APP_PASSWORD = os.getenv("ZOHO_APP_PASSWORD")