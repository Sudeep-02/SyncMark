from fastapi import Header, HTTPException, status, Request
from uuid import UUID


def get_device_id(
    request: Request,
    x_device_id: str | None = Header(default=None, alias="x-device-id"),
) -> UUID:
    """
    Ensures:
    - device_id comes from header OR cookie
    - Is a valid UUID
    - No DB access
    """

    # ✅ Allow CORS preflight
    if request.method == "OPTIONS":
        return UUID(int=0)  # dummy UUID, never used
    
    # 1. Prefer header (website)
    raw_device_id = x_device_id or request.cookies.get("device_id")

    if not raw_device_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Device id missing",
        )

    # 2. Validate UUID format
    try:
        return UUID(raw_device_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid device id format",
        )
