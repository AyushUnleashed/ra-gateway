import json
import base64
from src.utils.logger import logger
from src.config.settings import Settings
def encode_jwt_part(data):
    # Convert the data to JSON
    json_data = json.dumps(data, separators=(',', ':'))
    
    # Encode to Base64
    base64_encoded = base64.urlsafe_b64encode(json_data.encode()).decode()
    
    # Remove padding
    return base64_encoded.rstrip('=')
from fastapi import Depends, Header, HTTPException
import jwt
from uuid import UUID

# Helper function to verify JWT token
def verify_token(authorization: str = Header(...)) -> UUID:
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = authorization.split(" ")[1]
        # print(token)
        payload = jwt.decode(token, key=Settings.SUPABASE_JWT_SECRET, algorithms=["HS256"],options={"verify_aud": False})
        
        user_id = payload.get("sub")
        logger.info(f"User ID: {user_id}")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: User ID not found")
        
        return UUID(user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid user ID format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
