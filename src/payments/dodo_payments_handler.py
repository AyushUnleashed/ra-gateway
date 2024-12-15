# 1. generate dodo payments link for frontend

from typing import Literal
from src.payments.payments_utils import get_product_id_from_pack_type
from src.config.constants import Settings
from src.supabase_tools.handle_profiles_tb_updates import get_email_and_full_name_from_user_id
from src.utils.logger import logger
from src.config.settings import Settings

async def generate_payment_link(user_email, product_id, full_name, redirect_url=Settings.REDIRECT_URL) -> str:
    first_name, last_name = full_name.split(' ', 1)
    logger.info(f"Settings.IS_PRODUCTION: {Settings.IS_PRODUCTION}")
    prefix = "" if Settings.IS_PRODUCTION else "test."
    return f"https://{prefix}checkout.dodopayments.com/buy/{product_id}?quantity=1&email={user_email}&redirect_url={redirect_url}&disableEmail=true&firstName={first_name}&lastName={last_name}"


async def get_dodo_payment_link(user_id, pack_type) -> str:
    try:
        user_email, full_name = await get_email_and_full_name_from_user_id(user_id)
        product_id = get_product_id_from_pack_type(pack_type)
        if not product_id:
            raise ValueError("Invalid pack type provided.")
        payment_link = await generate_payment_link(user_email, product_id,full_name)
        return payment_link
    except Exception as e:
        logger.error(f"Error generating payment link: {str(e)}")
        raise