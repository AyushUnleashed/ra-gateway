from uuid import UUID
from src.supabase_tools.supabase_client import SUPABASE_CLIENT
from src.config.constants import TableNames

def get_email_and_full_name_from_user_id(user_id: UUID) -> tuple[str, str]:
    response = SUPABASE_CLIENT.table(TableNames.PROFILES).select("email, full_name").eq("id", str(user_id)).single().execute()
    profile_data = response.data
    return profile_data['email'], profile_data['full_name']