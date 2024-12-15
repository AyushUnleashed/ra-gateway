import asyncio
from src.models.base_models import DoDoWebhook
from uuid import UUID
from src.supabase_tools.supabase_client import SUPABASE_CLIENT
from src.config.constants import TableNames
from src.utils.logger import logger


async def insert_new_webhook(webhook_data: DoDoWebhook) -> bool:
    """
    Insert a new webhook into the dodo_webhooks table in Supabase.
    """
    seriazlied_webhook_data = webhook_data.serialize_for_db()
    logger.info(f"Serialized webhook data to be inserted: {seriazlied_webhook_data}")
    try:
        response = SUPABASE_CLIENT.table(TableNames.DODO_WEBHOOKS).insert(seriazlied_webhook_data).execute()
        logger.info(f"Response from database insert operation: {response}")
        if not response.data:
            logger.error("Failed to insert new webhook into the database")
            raise Exception("Failed to insert new webhook into the database")
        return True
    except Exception as e:
        logger.error(f"An error occurred while inserting the new webhook into the database: {e}")
        raise Exception(f"An error occurred while inserting the new webhook into the database: {e}")

async def check_existing_webhook(payment_id: UUID) -> tuple[bool, dict]:
    """
    Check if a webhook with the given payment_id already exists in the dodo_webhooks table.
    """
    try:
        response = SUPABASE_CLIENT.table(TableNames.DODO_WEBHOOKS).select("*").eq("payment_id", str(payment_id)).execute()
        webhook_data = response.data
        logger.info(f"Webhook data: {webhook_data}")
        if webhook_data:
            return True, webhook_data
        return False, {}
    except Exception as e:
        raise Exception(f"An error occurred while checking for existing webhook in the database: {e}")

if __name__ == "__main__":
    asyncio.run(check_existing_webhook("123e4567-e89b-12d3-a456-426614174000"))