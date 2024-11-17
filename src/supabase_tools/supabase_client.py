from src.config.settings import Settings
from supabase import create_client, Client


def create_supabase_client():
    supabase_client: Client = create_client(Settings.SUPABASE_URL, Settings.SUPABASE_SERVICE_KEY)
    return supabase_client

SUPABASE_CLIENT = create_supabase_client()