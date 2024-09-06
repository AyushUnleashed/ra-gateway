from src.config import Config
from supabase import create_client, Client


def create_supabase_client():
    supabase_client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
    return supabase_client

SUPABASE_CLIENT = create_supabase_client()