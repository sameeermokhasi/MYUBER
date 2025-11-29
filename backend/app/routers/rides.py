from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
import math
from datetime import datetime

from app.database import get_db
from app.models import User, Ride, DriverProfile, RideStatus, UserRole
from app.schemas import RideCreate, RideResponse, RideUpdate, RideRating, LocationUpdate
from app.auth import get_current_active_user
from app.websocket import manager

router = APIRouter()

def calculate_fare(distance_km: float, vehicle_type: str) -> float:
    """Calculate ride fare based on distance and vehicle type"""
    base_fare = {
        "economy": 50,
        "premium": 100,
        "suv": 120,
        "luxury": 200
    }
    
    per_km_rate = {
        "economy": 10,
        "premium": 15,
        "suv": 18,
        "luxury": 25
    }
    
    base = base_fare.get(vehicle_type, 50)
    rate = per_km_rate.get(vehicle_type, 10)
    
    return base + (distance_km * rate)

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def find_nearby_drivers(db: Session, pickup_lat: float, pickup_lng: float, max_distance_km: float = 5.0) -> List[User]:
    """Find drivers within specified distance of pickup location"""
    try:
        # Get all available drivers with location data
        drivers = db.query(User).join(DriverProfile).filter(
            and_(
                User.role == UserRole.DRIVER,
                User.is_active == True,
                DriverProfile.is_available == True,
                DriverProfile.current_lat != None,
                DriverProfile.current_lng != None
            )
        ).all()
        
        print(f"Total available drivers in system: {len(drivers)}")
        
        nearby_drivers = []
        for driver in drivers:
            if driver.driver_profile and driver.driver_profile.current_lat is not None and driver.driver_profile.current_lng is not None:
                try:
                    # Convert to float to ensure proper comparison
                    driver_lat = float(driver.driver_profile.current_lat)
                    driver_lng = float(driver.driver_profile.current_lng)
                    
                    distance = calculate_distance(
                        pickup_lat, pickup_lng,
                        driver_lat, driver_lng
                    )
                    print(f"Driver {driver.id} distance: {distance} km")
                    if distance <= max_distance_km:  # Within specified distance
                        nearby_drivers.append(driver)
                        print(f"Driver {driver.id} added to nearby drivers list")
                    else:
                        print(f"Driver {driver.id} is too far away ({distance} km)")
                except Exception as e:
                    print(f"Error calculating distance for driver {driver.id}: {e}")
                    continue
        
        print(f"Found {len(nearby_drivers)} nearby drivers within {max_distance_km} km")
        return nearby_drivers
    except Exception as e:
        print(f"Error in find_nearby_drivers: {e}")
        # Return empty list as fallback
        return []

@router.post("/", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
async def create_ride(
    ride_data: RideCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new ride request"""
    if current_user.role != UserRole.RIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only riders can create ride requests"
        )
    
    # Calculate distance
    distance = calculate_distance(
        float(ride_data.pickup_lat), float(ride_data.pickup_lng),
        float(ride_data.destination_lat), float(ride_data.destination_lng)
    )
    
    # Calculate estimated fare
    estimated_fare = calculate_fare(distance, ride_data.vehicle_type.value)
    
    # Estimate duration (assuming average speed of 40 km/h)
    duration = int((distance / 40) * 60)
    
    new_ride = Ride(
        rider_id=current_user.id,
        pickup_address=ride_data.pickup_address,
        pickup_lat=float(ride_data.pickup_lat),
        pickup_lng=float(ride_data.pickup_lng),
        destination_address=ride_data.destination_address,
        destination_lat=float(ride_data.destination_lat),
        destination_lng=float(ride_data.destination_lng),
        vehicle_type=ride_data.vehicle_type,
        distance_km=distance,
        duration_minutes=duration,
        estimated_fare=estimated_fare,
        scheduled_time=ride_data.scheduled_time
    )
    
    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)
    
    # Broadcast to nearby drivers
    nearby_drivers = find_nearby_drivers(db, float(ride_data.pickup_lat), float(ride_data.pickup_lng))
    print(f"Found {len(nearby_drivers)} nearby drivers")
    
    # Send notification to each nearby driver
    for driver in nearby_drivers:
        try:
            print(f"Sending ride request to driver {driver.id}")
            await manager.send_personal_message({
                "type": "new_ride_request",
                "ride_id": new_ride.id,
                "pickup_address": new_ride.pickup_address,
                "destination_address": new_ride.destination_address,
                "distance_km": round(float(new_ride.distance_km or 0), 2),
                "estimated_fare": round(float(new_ride.estimated_fare or 0), 2),
                "vehicle_type": new_ride.vehicle_type.value if new_ride.vehicle_type is not None else "economy"
            }, driver.id)
            print(f"Successfully sent ride request to driver {driver.id}")
        except Exception as e:
            print(f"Failed to send ride request to driver {driver.id}: {e}")
    
    # Only send to nearby drivers, not all connected drivers
    # The individual messages to nearby drivers above should be sufficient
    
    return new_ride

@router.get("/", response_model=List[RideResponse])
async def get_rides(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    status: Optional[str] = None
):
    """Get rides for current user"""
    query = db.query(Ride)
    
    if current_user.role.value == UserRole.RIDER.value:
        query = query.filter(Ride.rider_id == current_user.id)
    elif current_user.role.value == UserRole.DRIVER.value:
        # For drivers, show their assigned rides (accepted, in_progress, completed)
        # and pending rides that they can accept
        query = query.filter(
            or_(
                Ride.driver_id == current_user.id,
                and_(
                    Ride.status == RideStatus.PENDING,
                    Ride.driver_id == None
                )
            )
        )
    
    if status:
        query = query.filter(Ride.status == status)
    
    rides = query.order_by(Ride.created_at.desc()).all()
    return rides

@router.get("/available", response_model=List[RideResponse])
async def get_available_rides(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get available rides for drivers"""
    print(f"=== GET AVAILABLE RIDES DEBUG ===")
    print(f"Current user ID: {current_user.id}")
    print(f"Current user email: {current_user.email}")
    print(f"Current user role: {current_user.role}")
    print(f"Current user role type: {type(current_user.role)}")
    print(f"Current user role value: {current_user.role.value}")
    print(f"Expected driver role: {UserRole.DRIVER}")
    print(f"Expected driver value: {UserRole.DRIVER.value}")
    print(f"Role comparison result: {str(current_user.role) == UserRole.DRIVER.value}")
    print(f"Direct comparison: {current_user.role == UserRole.DRIVER}")
    
    # Fix the role comparison - use direct enum comparison
    if current_user.role != UserRole.DRIVER:
        print(f"Role check failed. User is not a driver.")
        print(f"User role: {current_user.role}")
        print(f"User role value: {current_user.role.value}")
        print(f"Expected role value: {UserRole.DRIVER.value}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only drivers can view available rides"
        )
    
    # Check if driver is available and has location
    driver_profile = db.query(DriverProfile).filter(
        DriverProfile.user_id == current_user.id
    ).first()
    
    print(f"Driver profile found: {driver_profile is not None}")
    if driver_profile:
        print(f"Driver is available: {driver_profile.is_available}")
        print(f"Driver has location: {driver_profile.current_lat is not None and driver_profile.current_lng is not None}")
        if driver_profile.current_lat is not None:
            print(f"Driver lat: {driver_profile.current_lat} (type: {type(driver_profile.current_lat)})")
        if driver_profile.current_lng is not None:
            print(f"Driver lng: {driver_profile.current_lng} (type: {type(driver_profile.current_lng)})")
    
    # Even if driver profile doesn't exist, we'll still try to return rides
    # This is a more permissive approach to help with debugging
    
    # Get all pending rides that don't have a driver assigned yet
    rides_query = db.query(Ride).filter(
        Ride.status == RideStatus.PENDING,
        Ride.driver_id == None
    )
    
    print(f"Total pending rides in system: {rides_query.count()}")
    
    # For debugging purposes, return all pending rides
    # In production, you might want to filter by location
    rides = rides_query.order_by(Ride.created_at.desc()).limit(20).all()  # Limit to 20 for performance
    
    print(f"Returning {len(rides)} available rides")
    for ride in rides:
        print(f"  Ride {ride.id}: {ride.pickup_address} -> {ride.destination_address}")
    print("=== END GET AVAILABLE RIDES DEBUG ===")
    return rides

@router.get("/{ride_id}", response_model=RideResponse)
async def get_ride(
    ride_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific ride"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Check authorization
    if current_user.role.value == UserRole.RIDER.value and str(ride.rider_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this ride"
        )
    elif current_user.role.value == UserRole.DRIVER.value and str(ride.driver_id) != str(current_user.id):
        if str(ride.status) != RideStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this ride"
            )
    
    return ride

@router.patch("/{ride_id}", response_model=RideResponse)
async def update_ride(
    ride_id: int,
    ride_update: RideUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update ride status"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Handle driver accepting ride
    print(f"=== DEBUG RIDE UPDATE ===")
    print(f"Ride update status: {ride_update.status}")
    print(f"Ride update status type: {type(ride_update.status)}")
    print(f"Current user role: {current_user.role}")
    print(f"Current user role value: {current_user.role.value}")
    print(f"UserRole.DRIVER.value: {UserRole.DRIVER.value}")
    print(f"Ride current status: {ride.status}")
    print(f"Ride current status value: {ride.status.value}")
    print(f"RideStatus.PENDING.value: {RideStatus.PENDING.value}")
    
    # Handle driver accepting ride
    if ride_update.status == RideStatus.ACCEPTED:
        print("Processing ride acceptance")
        if current_user.role == UserRole.DRIVER:
            print("User is a driver")
            if ride.status == RideStatus.PENDING:
                print("Ride is pending, accepting ride")
                ride.driver_id = current_user.id
                ride.status = RideStatus.ACCEPTED
                print(f"Ride accepted. Driver ID: {ride.driver_id}, Status: {ride.status}")
                
                # Commit the changes
                db.commit()
                db.refresh(ride)
                
                # Send WebSocket notifications to both rider and driver
                # Also notify all drivers to remove this ride from their available list
                try:
                    # Notify rider
                    await manager.send_personal_message({
                        "type": "ride_status_update",
                        "ride_id": ride.id,
                        "status": "accepted"
                    }, int(ride.rider_id) if ride.rider_id is not None else 0)
                    
                    # Notify driver
                    await manager.send_personal_message({
                        "type": "ride_status_update",
                        "ride_id": ride.id,
                        "status": "accepted"
                    }, int(ride.driver_id) if ride.driver_id is not None else 0)
                    
                    # Notify all drivers to remove this ride from available list
                    await manager.broadcast({
                        "type": "ride_removed",
                        "ride_id": ride.id
                    })
                    
                    print(f"Sent ride status update notifications for ride {ride.id}")
                except Exception as e:
                    print(f"Failed to send WebSocket notifications: {e}")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ride is not available for acceptance"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only drivers can accept rides"
            )
    
    # Handle driver starting ride
    elif ride_update.status == RideStatus.IN_PROGRESS:
        print("Processing ride start")
        if current_user.role == UserRole.DRIVER and str(ride.driver_id) == str(current_user.id):
            print("User is the assigned driver")
            if ride.status == RideStatus.ACCEPTED:
                print("Ride is accepted, starting ride")
                ride.status = RideStatus.IN_PROGRESS
                ride.started_at = datetime.utcnow()
                print(f"Ride started. Status: {ride.status}")
                
                # Commit the changes
                db.commit()
                db.refresh(ride)
                
                # Send WebSocket notifications to both rider and driver
                try:
                    # Notify rider
                    await manager.send_personal_message({
                        "type": "ride_status_update",
                        "ride_id": ride.id,
                        "status": "in_progress"
                    }, int(ride.rider_id) if ride.rider_id is not None else 0)
                    
                    # Notify driver
                    await manager.send_personal_message({
                        "type": "ride_status_update",
                        "ride_id": ride.id,
                        "status": "in_progress"
                    }, int(ride.driver_id) if ride.driver_id is not None else 0)
                    
                    print(f"Sent ride status update notifications for ride {ride.id}")
                except Exception as e:
                    print(f"Failed to send WebSocket notifications: {e}")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ride must be accepted before starting"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the assigned driver can start this ride"
            )
    
    # Handle driver completing ride
    elif ride_update.status == RideStatus.COMPLETED:
        print("Processing ride completion")
        if current_user.role == UserRole.DRIVER and str(ride.driver_id) == str(current_user.id):
            print("User is the assigned driver")
            if ride.status == RideStatus.IN_PROGRESS:
                print("Ride is in progress, completing ride")
                ride.status = RideStatus.COMPLETED
                ride.completed_at = datetime.utcnow()
                if ride_update.final_fare:
                    ride.final_fare = float(ride_update.final_fare)
                else:
                    ride.final_fare = float(ride.estimated_fare)
                
                # Update driver stats
                driver_profile = db.query(DriverProfile).filter(
                    DriverProfile.user_id == current_user.id
                ).first()
                if driver_profile:
                    driver_profile.total_rides = int(driver_profile.total_rides) + 1
                print(f"Ride completed. Status: {ride.status}")
                
                # Commit the changes
                db.commit()
                db.refresh(ride)
                if driver_profile:
                    db.refresh(driver_profile)
                
                # Send WebSocket notifications to both rider and driver
                try:
                    # Notify rider
                    await manager.send_personal_message({
                        "type": "ride_status_update",
                        "ride_id": ride.id,
                        "status": "completed"
                    }, int(ride.rider_id) if ride.rider_id is not None else 0)
                    
                    # Notify driver
                    await manager.send_personal_message({
                        "type": "ride_status_update",
                        "ride_id": ride.id,
                        "status": "completed"
                    }, int(ride.driver_id) if ride.driver_id is not None else 0)
                    
                    print(f"Sent ride status update notifications for ride {ride.id}")
                except Exception as e:
                    print(f"Failed to send WebSocket notifications: {e}")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ride must be in progress before completing"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the assigned driver can complete this ride"
            )
    
    # Handle rider cancelling ride
    elif ride_update.status == RideStatus.CANCELLED:
        print("Processing ride cancellation")
        if (current_user.role == UserRole.RIDER and str(ride.rider_id) == str(current_user.id)) or \
           (current_user.role == UserRole.DRIVER and str(ride.driver_id) == str(current_user.id)):
            print("User is authorized to cancel ride")
            if ride.status in [RideStatus.PENDING, RideStatus.ACCEPTED]:
                print("Ride can be cancelled")
                ride.status = RideStatus.CANCELLED
                
                # Commit the changes
                db.commit()
                db.refresh(ride)
                
                # Send WebSocket notifications to both rider and driver (if assigned)
                try:
                    # Notify rider
                    await manager.send_personal_message({
                        "type": "ride_status_update",
                        "ride_id": ride.id,
                        "status": "cancelled"
                    }, int(ride.rider_id) if ride.rider_id is not None else 0)
                    
                    # Notify driver if assigned
                    if ride.driver_id:
                        await manager.send_personal_message({
                            "type": "ride_status_update",
                            "ride_id": ride.id,
                            "status": "cancelled"
                        }, int(ride.driver_id) if ride.driver_id is not None else 0)
                    
                    print(f"Sent ride status update notifications for ride {ride.id}")
                except Exception as e:
                    print(f"Failed to send WebSocket notifications: {e}")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ride cannot be cancelled at this stage"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the rider or assigned driver can cancel this ride"
            )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status update"
        )
    
    return ride

@router.post("/{ride_id}/rate", response_model=RideResponse)
async def rate_ride(
    ride_id: int,
    rating_data: RideRating,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Rate a completed ride"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    if str(ride.rider_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to rate this ride"
        )
    
    if str(ride.status) != RideStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only rate completed rides"
        )
    
    ride.rating = int(str(rating_data.rating))
    ride.feedback = rating_data.feedback
    
    # Update driver rating
    if ride.driver_id is not None:
        driver_profile = db.query(DriverProfile).filter(
            DriverProfile.user_id == ride.driver_id
        ).first()
        if driver_profile:
            # Calculate new average rating
            total_rated_rides = db.query(Ride).filter(
                Ride.driver_id == ride.driver_id,
                Ride.rating != None
            ).count()
            
            total_rating = db.query(Ride).filter(
                Ride.driver_id == ride.driver_id,
                Ride.rating != None
            ).with_entities(Ride.rating).all()
            
            avg_rating = sum([int(str(r[0])) for r in total_rating]) / total_rated_rides if total_rated_rides > 0 else 5.0
            driver_profile.rating = float(str(round(avg_rating, 2)))
    
    db.commit()
    db.refresh(ride)
    
    return ride

@router.delete("/{ride_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_ride(
    ride_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel a ride"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Check if the current user is the rider who booked the ride
    if ride.rider_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this ride"
        )
    
    # Check if the ride is in a cancellable state
    if str(ride.status) in [RideStatus.COMPLETED.value, RideStatus.CANCELLED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel this ride"
        )
    
    # Cancel the ride
    ride.status = RideStatus.CANCELLED.value
    db.commit()

    return None

