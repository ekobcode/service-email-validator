from fastapi import Header, HTTPException

from core.config import API_KEYS

async def api_key_auth(x_api_key: str = Header(...)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key
