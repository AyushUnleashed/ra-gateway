import hashlib
import hmac
from typing import Any, Dict
from src.config.settings import Settings
from src.utils.logger import logger


from standardwebhooks.webhooks import Webhook
import base64
import json
import time

WEBHOOK_SECRET = Settings.DODO_WEBHOOK_SECRET_KEY

def verify_signature(webhook_id: str, webhook_timestamp: str, payload: bytes, signature: str) -> bool:
    """
    Verify the webhook signature using the standardwebhooks library
    """
    logger.info(f"webhook_id = {webhook_id}")
    logger.debug(f"webhook_timestamp = {webhook_timestamp}")
    logger.debug(f"payload = {payload}")
    logger.debug(f"signature = {signature}")
    # logger.debug(f"WEBHOOK_SECRET = {WEBHOOK_SECRET}")  # Logging the webhook secret for debugging purposes

    # Initialize the Webhook object with the base64 secret
    wh = Webhook(WEBHOOK_SECRET)

    # Prepare headers and payload for verification
    webhook_headers = {
        "webhook-id": webhook_id,
        "webhook-signature": signature,
        "webhook-timestamp": webhook_timestamp
    }
    webhook_payload = payload.decode()

    # Verify the signature using the Webhook library
    result = wh.verify(webhook_payload, webhook_headers)
    logger.debug(f"signature verification result = {result}")

    return result

# def verify_signature_simple(webhook_id: str, webhook_timestamp: str, payload: bytes, signature: str) -> bool:
#     """
#     Verify the webhook signature without using the standardwebhooks library
#     """
#     logger.info(f"webhook_id = {webhook_id}")
#     logger.debug(f"webhook_timestamp = {webhook_timestamp}")
#     logger.debug(f"payload = {payload}")
#     logger.debug(f"signature = {signature}")
#     logger.debug(f"WEBHOOK_SECRET = {WEBHOOK_SECRET}")  # Logging the webhook secret for debugging purposes

#     # Decode the payload
#     data = payload.decode()

#     # # Verify timestamp (assuming a tolerance of 5 minutes for example)
#     # current_time = int(time.time())
#     # if abs(current_time - int(webhook_timestamp)) > 300:
#     #     logger.error("Timestamp verification failed.")
#     #     return False

#     # Create the expected signature
#     message = f"{webhook_id}.{webhook_timestamp}.{data}".encode()
#     expected_sig = hmac.new(WEBHOOK_SECRET.encode(), message, hashlib.sha256).digest()
#     expected_sig_base64 = base64.b64encode(expected_sig).decode()

#     # Compare the expected signature with the provided signature
#     passed_sigs = signature.split(" ")
#     for versioned_sig in passed_sigs:
#         version, sig = versioned_sig.split(",")
#         if version != "v1":
#             continue
#         if hmac.compare_digest(expected_sig_base64, sig):
#             logger.debug("Signature verification succeeded.")
#             return True

#     logger.error("No matching signature found.")
#     return False
