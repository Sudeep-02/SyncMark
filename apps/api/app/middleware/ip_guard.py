# app/middleware/ip_guard.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.redis import redis_client

EDGE_LIMIT = 250
WINDOW_SECONDS = 60


class IPGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        # ✅ Let CORS middleware handle OPTIONS
        if request.method == "OPTIONS":
            return await call_next(request)

        # Always bypass health
        if request.url.path == "/health":
            return await call_next(request)

        ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or request.headers.get("x-real-ip")
            or (request.client.host if request.client else "unknown")
        )

        key = f"edge:{ip}"

        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, WINDOW_SECONDS)

        if count > EDGE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"}
            )

        return await call_next(request)
