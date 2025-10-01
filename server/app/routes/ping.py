from fastapi import APIRouter
from pydantic import BaseModel, Field

# Define the Pydantic models directly in this file
class PingRequest(BaseModel):
    input: str = Field(..., example="test")

class PingResponse(BaseModel):
    output: str = Field(..., example="test")

# Create the router
router = APIRouter()

@router.post("/ping")
async def ping(request: PingRequest) -> PingResponse:
    """Responds with the same message it received."""
    return PingResponse(output=request.input)
