# app/routers/v1/__pycache__/root_router.py
from fastapi import APIRouter

router = APIRouter(
    tags=["Root"],
)


@router.get("/health")
async def health():
    """
    Health check endpoint that returns the API status.
    """
    return {"status": "ok"}
