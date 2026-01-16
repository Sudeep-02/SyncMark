from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.redis import redis_client

RATE_LIMIT = 10          # requests
WINDOW_SECONDS = 60       # per minute


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        # ---- Safe IP extraction ----
        ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or request.headers.get("x-real-ip")
            or (request.client.host if request.client else "unknown")
        )

        key = f"rate:{ip}"

        # ---- Atomic Redis operation ----
        count = await redis_client.incr(key)

        # Set expiry only once
        if count == 1:
            await redis_client.expire(key, WINDOW_SECONDS)

        if count > RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"}
            )

        return await call_next(request)
