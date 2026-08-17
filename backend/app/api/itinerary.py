from fastapi import APIRouter
from pydantic import BaseModel

from typing import Optional, List

from app.services.itinerary_generator import generate_itinerary
from app.services.itinerary import resolve_itinerary
from app.services.route_optimizer import optimize_itinerary
from app.services.daily_scheduler import schedule_itinerary
from app.services.itinerary_quality import improve_itinerary
from app.services.origin import create_origin
from app.services.destination import create_destination
from app.services.route_optimizer import (
    optimize_itinerary,
    add_destination_distance
)

from app.services.custom_location import (
    create_custom_location,
    inject_custom_locations
)


router = APIRouter(
    prefix="/itinerary",
    tags=["Itinerary"]
)


# ============================================================
# CUSTOM LOCATION REQUEST
# ============================================================

class CustomLocationRequest(BaseModel):

    name: str

    latitude: float

    longitude: float

    category: str = "custom_location"

    visit_duration_minutes: int = 0

    opening_hours: Optional[str] = None

    day: int = 1

    role: str = "waypoint"

    start_time: Optional[str] = None

class OriginRequest(BaseModel):

    name: str = "Current Location"

    latitude: float

    longitude: float

    start_time: str = "09:00"

    category: str = "origin"

class DestinationRequest(BaseModel):

    name: str

    latitude: float

    longitude: float

    end_time: Optional[str] = None

    category: str = "destination"

# ============================================================
# ITINERARY REQUEST
# ============================================================

class ItineraryRequest(BaseModel):

    city: str

    days: int

    interests: str = ""

    budget: str = "moderate"

    custom_locations: List[CustomLocationRequest] = []

    origin: Optional[OriginRequest] = None

    destination: Optional[DestinationRequest] = None

# ============================================================
# CREATE ITINERARY
# ============================================================

@router.post("/")
async def create_itinerary(
    request: ItineraryRequest
):

    # ========================================================
    # 0. CREATE CUSTOM LOCATIONS
    # ========================================================

    custom_locations = []

    for location in request.custom_locations:

        custom_location = create_custom_location(

            name=location.name,

            latitude=location.latitude,

            longitude=location.longitude,

            category=location.category,

            visit_duration_minutes=(
                location.visit_duration_minutes
            ),

            opening_hours=(
                location.opening_hours
            ),

            role=location.role,

            day=location.day,

            start_time=location.start_time,
        )

        custom_locations.append(
            custom_location
        )

    # ========================================================
    # 1. GENERATE
    # ========================================================

    itinerary = await generate_itinerary(

        city=request.city,

        days=request.days,

        interests=request.interests,

        budget=request.budget
    )

    # ========================================================
    # 2. RESOLVE PLACES
    # ========================================================

    resolved_itinerary = await resolve_itinerary(
        itinerary
    )

    # ========================================================
    # 3. INJECT CUSTOM LOCATIONS
    # ========================================================

    resolved_itinerary = inject_custom_locations(

        resolved_itinerary,

        custom_locations
    )

    if request.origin:

        origin = create_origin(
        name=request.origin.name,
        latitude=request.origin.latitude,
        longitude=request.origin.longitude,
        start_time=request.origin.start_time,
        category=request.origin.category,
    )

        if resolved_itinerary.get("days"):

            first_day = resolved_itinerary["days"][0]

            first_day["places"].insert(
            0,
            origin
        )

    # ========================================================
    # 4. OPTIMIZE ROUTES
    # ========================================================

    optimized_itinerary = optimize_itinerary(
        resolved_itinerary
    )

    # ========================================================
# 4A. ADD DESTINATION
# ========================================================

    if request.destination:

        destination = create_destination(
        name=request.destination.name,
        latitude=request.destination.latitude,
        longitude=request.destination.longitude,
        end_time=request.destination.end_time,
        category=request.destination.category,
    )

        if optimized_itinerary.get("days"):

            last_day = optimized_itinerary["days"][-1]

            last_day["places"].append(
            destination
            )

        optimized_itinerary = add_destination_distance(
        optimized_itinerary
    )

    # ========================================================
    # 5. CREATE TIME SCHEDULE
    # ========================================================

    scheduled_itinerary = schedule_itinerary(
        optimized_itinerary
    )

    # ========================================================
    # 6. QUALITY IMPROVEMENT
    # ========================================================

    improved_itinerary = improve_itinerary(
        scheduled_itinerary
    )

    return improved_itinerary

