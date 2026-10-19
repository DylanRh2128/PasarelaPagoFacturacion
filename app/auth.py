import os
import secrets

from fastapi import Header, HTTPException


def verify_api_key(x_api_key: str = Header(default="")):
    if not secrets.compare_digest(x_api_key.encode(), os.environ["API_KEY"].encode()):
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")
