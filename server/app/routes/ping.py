from fastapi import APIRouter, HTTPException
from datetime import datetime
from ..models.schemas import PingRequest, PingResponse

router = APIRouter()

@router.post("/ping", response_model=PingResponse)
async def ping_endpoint(request: PingRequest):
    """
    Ping endpoint that returns pong when data is 'ping'
    """
    # Fixed: correct condition check
    if request.data == "ping":
        return PingResponse(
            message="pong",
            timestamp=datetime.now().isoformat()
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid data. Expected 'ping'"
        )
