from src.models.base_models import User
from uuid import UUID
from src.supabase_tools.supabase_client import SUPABASE_CLIENT
from src.config.constants import TableNames

# async def add_user_to_db(user: User):
#     try:
#         print("Adding user to the database")
#         print(user)
#         print("\n\n")
#         serialized_user = user.serialize_for_db()
#         response = SUPABASE_CLIENT.table(TableNames.USERS).insert(serialized_user).execute()
#         if not response.data:
#             raise Exception("Failed to add user to the database")
#         return True
#     except Exception as e:
#         raise Exception(f"An error occurred while adding the user to the database: {e}")

async def get_user_from_db(user_id: UUID) -> User:
    try:
        response = SUPABASE_CLIENT.table(TableNames.PROFILES).select("*").eq("id", str(user_id)).single().execute()
        user_data = response.data
        if not user_data:
            raise Exception("User not found")
        return User(**user_data)
    except Exception as e:
        raise Exception(f"An error occurred while fetching the user from the database: {e}")

async def update_user_in_db(user: User) -> User:
    try:
        serialized_user = user.serialize_for_db()
        response = SUPABASE_CLIENT.table(TableNames.PROFILES).update(serialized_user).eq("id", str(user.id)).execute()
        if not response.data:
            raise Exception("Failed to update user in the database")
        user_credits = response.data[0].get("credits")
        return True, user_credits
    except Exception as e:
        raise Exception(f"An error occurred while updating the user in the database: {e}")

# async def delete_user_from_db(user_id: UUID):
#     try:
#         response = SUPABASE_CLIENT.table(TableNames.USERS).delete().eq("id", str(user_id)).execute()
#         if not response.data:
#             raise Exception("Failed to delete user from the database")
#         return True
#     except Exception as e:
#         raise Exception(f"An error occurred while deleting the user from the database: {e}")

async def get_email_and_full_name_from_user_id(user_id: UUID) -> tuple[str, str]:
    user = await get_user_from_db(user_id)
    return user.email, user.full_name

async def get_user_id_from_email(email: str) -> UUID:
    try:
        response = SUPABASE_CLIENT.table(TableNames.PROFILES).select("id").eq("email", email).single().execute()
        user_data = response.data
        if not user_data:
            raise Exception("User not found")
        return UUID(user_data["id"])
    except Exception as e:
        raise Exception(f"An error occurred while fetching the user ID from the database: {e}")

async def update_user_credits(user_id: UUID, additional_credits: int) -> bool:
    try:
        if additional_credits <= 0:
            raise ValueError("Additional credits must be a positive number")
        user = await get_user_from_db(user_id)
        new_credits: int = user.credits + additional_credits
        update_response = SUPABASE_CLIENT.table(TableNames.PROFILES).update({"credits": new_credits}).eq("id", str(user.id)).execute()
        return True
    except Exception as e:
        raise Exception(f"An error occurred while updating user credits: {e}")

import asyncio

if __name__ == "__main__":
    async def main():
        user_id = UUID("814f3aa0-421b-475f-9489-38aea444f364")
        user = await get_user_from_db(user_id)
        print(f"Retrieved user with ID {user_id}: {user}")

    asyncio.run(main())