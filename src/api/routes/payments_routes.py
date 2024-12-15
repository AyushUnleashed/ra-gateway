
from fastapi import APIRouter, HTTPException
from src.utils.logger import logger
from pydantic import BaseModel
from src.payments.dodo_payments_handler import get_dodo_payment_link

payments_router = APIRouter()

class PaymentRequest(BaseModel):
    user_id: str
    pack_type: str

@payments_router.post("/api/payments/generate_payment_link")
async def generate_payment_link(request: PaymentRequest):
    try:
        payment_link = await get_dodo_payment_link(request.user_id, request.pack_type)
        return {"payment_link": payment_link}
    except Exception as e:
        logger.error(f"Error generating payment link: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while generating the payment link.")