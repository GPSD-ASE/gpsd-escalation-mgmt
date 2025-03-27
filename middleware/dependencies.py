from fastapi import Header, HTTPException, Depends
from config import ACCESS_API_KEYS

API_KEY_NAME = "x-api-key"


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key not in ACCESS_API_KEYS:
        raise HTTPException(
            status_code=401, detail="Invalid or missing API Key"
        )

    return x_api_key
