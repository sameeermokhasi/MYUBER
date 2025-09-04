from pydantic import BaseModel
from typing import Optional

class PingRequest(BaseModel):
    """Request model for ping endpoint"""
    data: str

class PingResponse(BaseModel):
    """Response model for ping endpoint"""
    message: str
    status: str = "success"
    timestamp: Optional[str] = None

