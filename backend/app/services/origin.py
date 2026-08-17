from typing import Dict, Any


def create_origin(
    name: str,
    latitude: float,
    longitude: float,
    start_time: str = "09:00",
    category: str = "origin"
) -> Dict[str, Any]:

    return {
        "name": name,
        "category": category,

        "latitude": float(latitude),
        "longitude": float(longitude),

        "description": None,
        "address": None,
        "opening_hours": None,

        "distance_from_previous_km": 0.0,

        "visit_duration_minutes": 0,

        "custom_location": True,
        "custom_role": "start",

        "preferred_start_time": start_time,

        "origin": True,
    }