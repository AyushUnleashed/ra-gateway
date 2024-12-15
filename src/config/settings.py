import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    RAI_GATEWAY_BACKEND_URL = os.getenv("RAI_GATEWAY_BACKEND_URL")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
    ZOHO_APP_PASSWORD = os.getenv("ZOHO_APP_PASSWORD")
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    APP_ENV = os.getenv("APP_ENV")
    ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
    SLACKBOT_RA_WEBHOOK_URL = os.getenv("SLACKBOT_RA_WEBHOOK_URL")
    DODO_WEBHOOK_SECRET_KEY = os.getenv("DODO_WEBHOOK_SECRET_KEY")
    IS_PRODUCTION = os.getenv("IS_PRODUCTION", "TRUE").upper() == "TRUE"
    REDIRECT_URL = os.getenv("REDIRECT_URL")


if __name__ == "__main__":
    print(os.getenv("IS_PRODUCTION", "TRUE"))
    print(os.getenv("IS_PRODUCTION", "TRUE").upper() == "TRUE")
    print(Settings.IS_PRODUCTION)
    # print(Settings.__dict__)