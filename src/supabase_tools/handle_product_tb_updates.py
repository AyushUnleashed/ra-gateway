from src.models.base_models import Product
from uuid import UUID
from src.supabase_tools.supabase_client import SUPABASE_CLIENT

def add_product_to_db(product: Product):
    response = SUPABASE_CLIENT.table("products").insert(product.dict()).execute()
    if response.status_code != 201:
        raise Exception("Failed to add product to the database")

def get_product_from_db(product_id: UUID) -> Product:
    response = SUPABASE_CLIENT.table("products").select("*").eq("id", str(product_id)).single().execute()
    if response.status_code != 200:
        raise Exception("Failed to retrieve product from the database")
    product_data = response.data
    return Product(**product_data)