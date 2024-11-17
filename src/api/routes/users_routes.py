from fastapi import APIRouter, Depends
from uuid import UUID
from src.api.utils import verify_token
from src.models.base_models import User
from src.supabase_tools.handle_users_tb_updates import get_user_from_db, update_user_in_db
from src.utils.logger import logger

users_router = APIRouter()

@users_router.post("/api/check-beta")
async def check_beta(user_id=Depends(verify_token)):
    user = await get_user_from_db(user_id)
    return {"is_beta_user": user.beta}

@users_router.get("/api/users/get_credits")
async def get_credits(user_id=Depends(verify_token)):
    user = await get_user_from_db(user_id)
    return {"credits": user.credits}

@users_router.post("/api/users/reduce_credits")
async def reduce_credit(user_id: UUID=Depends(verify_token)):
    logger.info(f"Attempting to reduce credits for user {user_id}")
    
    # Retrieve the existing user from the database
    user = await get_user_from_db(user_id)
    logger.info(f"Retrieved user {user_id} with {user.credits} credits")

    reduced_credits, updated_credits = await process_credit_reduction(user)
    
    return {"reduced_credits": reduced_credits, "updated_credits": updated_credits}

async def process_credit_reduction(user : User):
    reduced_credits = False
    if user.credits >= 1:
        # Update the user's credits
        user.credits -= 1
        reduced_credits = True
        logger.info(f"Reduced credits for user {user.id}. New credits: {user.credits}")
    else:
        logger.warning(f"User {user.id} does not have enough credits to reduce")

    # Call the relevant function to update the user in the database
    _, updated_credits = await update_user_in_db(user)
    logger.info(f"Updated user {user.id} in the database with {updated_credits} credits")
    
    return reduced_credits, updated_credits
