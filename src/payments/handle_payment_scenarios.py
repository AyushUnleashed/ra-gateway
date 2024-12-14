
from typing import Any, Dict
from src.utils.logger import logger


def handle_payment_event(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle different payment-related events
    """
    if event_type == "payment.succeeded":
        # Process successful payment
        payment_id = data["payment_id"]
        amount = data["total_amount"]
        currency = data["currency"]
        customer = data["customer"]
        
        # Add your business logic here
        logger.debug(f"Processing successful payment: ID={payment_id}, Amount={amount}, Currency={currency}, Customer={customer}")
        return {
            "status": "processed",
            "message": f"Successfully processed payment {payment_id}"
        }
        
    elif event_type == "payment.failed":
        # Handle failed payment
        payment_id = data["payment_id"]
        # Add your failure handling logic here
        return {
            "status": "processed",
            "message": f"Recorded failed payment {payment_id}"
        }
    
    return {"status": "unhandled", "message": f"Unhandled payment event type: {event_type}"}

def handle_refund_event(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle refund-related events
    """
    if event_type == "refund.succeeded":
        refund = data["refunds"][0]  # Get the first refund
        refund_id = refund["refund_id"]
        amount = refund["amount"]
        
        # Add your refund processing logic here
        return {
            "status": "processed",
            "message": f"Successfully processed refund {refund_id}"
        }
    
    return {"status": "unhandled", "message": f"Unhandled refund event type: {event_type}"}

def handle_dispute_event(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle dispute-related events
    """
    if data.get("disputes"):
        dispute = data["disputes"][0]  # Get the first dispute
        dispute_id = dispute["dispute_id"]
        
        if event_type == "dispute.opened":
            # Handle new dispute
            return {
                "status": "processed",
                "message": f"New dispute recorded: {dispute_id}"
            }
        elif event_type == "dispute.won":
            # Handle won dispute
            return {
                "status": "processed",
                "message": f"Dispute won: {dispute_id}"
            }
    
    return {"status": "unhandled", "message": f"Unhandled dispute event type: {event_type}"}
