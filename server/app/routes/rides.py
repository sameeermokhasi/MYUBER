from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

# Import your database dependency and the Ride model
from .. import models
from ..database import get_db

# --- Pydantic Models (Schemas) ---
# These define the shape of the data for your API
class Location(BaseModel):
    latitude: float = Field(..., example=12.9716)
    longitude: float = Field(..., example=77.5946)

class RideRequest(BaseModel):
    user_id: int = Field(..., example=123)
    pickup_location: Location
    dropoff_location: Location

class RideResponse(BaseModel):
    id: int
    user_id: int
    status: str
    pickup_location: Location
    dropoff_location: Location

    class Config:
        orm_mode = True # This allows the model to read data from SQLAlchemy objects

# --- API Router ---
router = APIRouter()

@router.post("/rides", response_model=RideResponse)
async def request_ride(ride: RideRequest, db: Session = Depends(get_db)):
    """Receives a new ride request and saves it to the database."""
    
    # Create a new Ride database object from the request data
    new_ride = models.Ride(
        user_id=ride.user_id,
        pickup_latitude=ride.pickup_location.latitude,
        pickup_longitude=ride.pickup_location.longitude,
        dropoff_latitude=ride.dropoff_location.latitude,
        dropoff_longitude=ride.dropoff_location.longitude,
        status="requested"
    )
    
    # Add the new ride to the database session and commit it
    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)
    
    # Return the created ride data
    return RideResponse(
        id=new_ride.id,
        user_id=new_ride.user_id,
        status=new_ride.status,
        pickup_location={
            "latitude": new_ride.pickup_latitude,
            "longitude": new_ride.pickup_longitude,
        },
        dropoff_location={
            "latitude": new_ride.dropoff_latitude,
            "longitude": new_ride.dropoff_longitude,
        },
    )

