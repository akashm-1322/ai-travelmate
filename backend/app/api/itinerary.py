from fastapi import APIRouter
from pydantic import BaseModel

from app.services.itinerary_generator import generate_itinerary
from app.services.itinerary import resolve_itinerary
from app.services.route_optimizer import optimize_itinerary
from app.services.daily_scheduler import schedule_itinerary
from app.services.itinerary_quality import improve_itinerary


router = APIRouter(
    prefix="/itinerary",
    tags=["Itinerary"]
)


class ItineraryRequest(BaseModel):

    city: str
    days: int
    interests: str = ""
    budget: str = "moderate"


@router.post("/")
async def create_itinerary(
    request: ItineraryRequest
):

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
    # 3. OPTIMIZE ROUTES
    # ========================================================

    optimized_itinerary = optimize_itinerary(
        resolved_itinerary
    )

    # ========================================================
    # 4. CREATE TIME SCHEDULE
    # ========================================================

    scheduled_itinerary = schedule_itinerary(
        optimized_itinerary
    )

    # ========================================================
    # 5. QUALITY IMPROVEMENT
    # ========================================================

    improved_itinerary = improve_itinerary(
        scheduled_itinerary
    )

    return improved_itinerary