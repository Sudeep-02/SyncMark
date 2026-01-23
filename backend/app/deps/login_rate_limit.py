from fastapi import Request, HTTPException, status
from app.core.redis import redis_client

LOGIN_LIMIT = 10
WINDOW = 60


def get_client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()

    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip

    if request.client:
        return request.client.host

    return "unknown"


async def login_rate_limit(request: Request):
    # Safely read body
    try:
        body = await request.json()
    except Exception:
        body = {}

    email = body.get("email", "unknown")
    ip = get_client_ip(request)

    key = f"login:{ip}:{email}"

    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, WINDOW)

    if count > LOGIN_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts"
        )
