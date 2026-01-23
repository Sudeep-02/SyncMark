# app/dependencies/user_action_limit.py
from fastapi import Depends,HTTPException
from app.deps.auth import get_current_user
from app.core.redis import redis_client

USER_LIMIT = 60
WINDOW = 60

async def user_action_rate_limit(user=Depends(get_current_user)):
    key = f"user:{user.id}"

    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, WINDOW)

    if count > USER_LIMIT:
        raise HTTPException(429, "Slow down")
