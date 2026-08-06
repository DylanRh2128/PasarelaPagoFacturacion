import os

from fastapi import Header, HTTPException


def verify_api_key(x_api_key: str = Header(default="")):
    if x_api_key != os.environ["API_KEY"]:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")
