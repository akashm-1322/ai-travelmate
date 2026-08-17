from typing import Dict, Any


def create_destination(
    name: str,
    latitude: float,
    longitude: float,
    end_time: str | None = None,
    category: str = "destination"
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
        "custom_role": "destination",

        "preferred_end_time": end_time,

        "destination": True,
    }