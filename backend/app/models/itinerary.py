from pydantic import BaseModel
from typing import List


class ItineraryPlace(BaseModel):
    name: str
    category: str | None = None


class ItineraryDay(BaseModel):
    day: int
    places: List[ItineraryPlace]


class Itinerary(BaseModel):
    city: str
    days: List[ItineraryDay]