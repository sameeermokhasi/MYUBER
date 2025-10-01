from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

# This line imports the 'Base' class from your database.py file.
# This is where the connection between the two files is made.
from .database import Base

class Ride(Base):
    """
    SQLAlchemy model for the 'rides' table.
    """
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    pickup_latitude = Column(Float, nullable=False)
    pickup_longitude = Column(Float, nullable=False)
    dropoff_latitude = Column(Float, nullable=False)
    dropoff_longitude = Column(Float, nullable=False)
    status = Column(String, default="requested")
    created_at = Column(DateTime(timezone=True), server_default=func.now())