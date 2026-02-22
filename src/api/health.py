from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()
@router.get("/health", tags=["Health"])
async def health_check():   
    """
    Basic health check endpoint.
    """
    return {
        "status": "health ok", 
        "timestamp": datetime.now(timezone.utc).isoformat()
        }