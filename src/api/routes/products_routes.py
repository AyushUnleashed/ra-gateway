
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException
from src.utils.logger import logger
from pydantic import BaseModel

from src.api.utils import verify_token
from src.models.base_models import Product
from src.supabase_tools.handle_product_tb_updates import add_product_to_db, get_all_products_from_db, get_product_from_db, update_product_in_db

products_router = APIRouter()

class CreateProductRequest(BaseModel):
    name: str
    description: str
    product_link: Optional[str]  = None

    # logo: Optional[UploadFile] = None
# Create product endpoint
@products_router.post("/api/products/create-product")
async def create_product(
    request: CreateProductRequest,
    user_id: UUID = Depends(verify_token)
):
    try:
        logger.info(f"Received request to create product: {request}")
        logger.info(f"Authenticated user ID: {user_id}")
        product_id = uuid4()
        logo_url = None
        # if request.logo:
        #     logo_url = upload_to_supabase(f"products/{product_id}/logo.png", logo)

        # Create product
        product = Product(
            id=product_id,
            user_id=user_id,
            name=request.name,
            description=request.description,
            product_link=request.product_link,
            logo_url=logo_url,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        await add_product_to_db(product)

        return {"product_id": product_id}
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while creating the product: {str(e)}")


@products_router.get("/api/products/get-all-products")
async def get_all_products(user_id: UUID = Depends(verify_token)):
    products = await get_all_products_from_db(user_id)
    return products

@products_router.get("/api/products/{product_id}")
async def get_product(product_id: UUID):
    product = await get_product_from_db(product_id)
    return product.model_dump()

@products_router.put("/api/products/{product_id}")
async def update_product(product_id: UUID, request: CreateProductRequest):
    # Retrieve the existing product from the database
    existing_product = await get_product_from_db(product_id)
    
    # Update the product fields with the new data from the request
    updated_product = existing_product.copy(update={
        "name": request.name,
        "description": request.description,
        "product_link": request.product_link,
        "updated_at": datetime.now()
    })
    
    # Call the relevant function to update the product in the database
    updated_product_in_db = await update_product_in_db(updated_product)
    
    return updated_product_in_db.model_dump()
