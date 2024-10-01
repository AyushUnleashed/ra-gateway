from src.models.base_models import Product
from uuid import UUID
from typing import List
from src.supabase_tools.supabase_client import SUPABASE_CLIENT
from src.utils.constants import TableNames

async def add_product_to_db(product: Product):
    serialized_product = product.serialize_for_db()
    response = SUPABASE_CLIENT.table(TableNames.PRODUCTS).insert(serialized_product).execute()
    if not response.data:
        raise Exception("Failed to add product to the database")

async def get_product_from_db(product_id: UUID) -> Product:
    response = SUPABASE_CLIENT.table(TableNames.PRODUCTS).select("*").eq("id", str(product_id)).single().execute()
    product_data = response.data
    return Product(**product_data)

async def get_all_products_from_db(user_id: UUID) -> List[Product]:
    response = SUPABASE_CLIENT.table(TableNames.PRODUCTS).select("*").eq("user_id", str(user_id)).execute()
    products_data = response.data
    for product in products_data:
        print(product)
    return [Product(**product) for product in products_data]

async def update_product_in_db(product: Product) -> Product:
    serialized_product = product.serialize_for_db()
    response = SUPABASE_CLIENT.table(TableNames.PRODUCTS).update(serialized_product).eq("id", str(product.id)).execute()
    if not response.data:
        raise Exception("Failed to update product in the database")
    updated_product_data = response.data[0]
    return Product(**updated_product_data)


if __name__ == "__main__":
    import asyncio
    from datetime import datetime
    async def main():
        product = Product(
            id=UUID("12345678-1234-5678-1234-567812345678"),
            name="Sample Product",
            description="This is a sample product",
            product_link=str("https://example.com"),
            logo_url=None,
            thumbnail_url=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        await add_product_to_db(product)
        print(f"Added product with ID {product.id} to the database.")
        
        # all_products = await get_all_products_from_db()
        # print(f"Retrieved {len(all_products)} products from the database.")

        # for product in all_products:
        #     retrieved_product = await get_product_from_db(product.id)
        #     print(f"Retrieved product: {retrieved_product}")

    asyncio.run(main())