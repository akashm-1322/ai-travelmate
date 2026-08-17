from pydantic import BaseModel, Field
from typing import List, Optional


class Activity(BaseModel):
    time: Optional[str] = None
    title: str
    description: Optional[str] = None
    location: Optional[str] = None


class DayPlan(BaseModel):
    day: int
    theme: Optional[str] = None
    activities: List[Activity] = []


class TripPlan(BaseModel):
    destination: str
    duration_days: int
    budget: Optional[float] = None
    currency: str = "INR"
    interests: List[str] = []
    itinerary: List[DayPlan] = []