from fastapi import Header, HTTPException, status
from uuid import UUID


def get_device_id(
    x_device_id: str = Header(..., alias="x-device-id")
) -> str:
    """
    Ensures:
    - x-device-id header exists
    - Is a valid UUID
    """

    try:
        # validate UUID format
        UUID(x_device_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid device id format"
        )

    return x_device_id
