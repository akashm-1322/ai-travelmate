
from typing import Any, Dict


# ============================================================
# CALCULATE ITINERARY SUMMARY
# ============================================================

def summarize_itinerary(
    itinerary: Dict[str, Any]
) -> Dict[str, Any]:

    total_places = 0
    total_distance = 0.0
    total_travel_minutes = 0
    total_visit_minutes = 0

    for day in itinerary.get("days", []):

        places = day.get("places", [])

        total_places += len(places)

        for place in places:

            total_distance += float(
                place.get(
                    "distance_from_previous_km",
                    0
                ) or 0
            )

            total_travel_minutes += int(
                place.get(
                    "travel_time_minutes",
                    0
                ) or 0
            )

            total_visit_minutes += int(
                place.get(
                    "visit_duration_minutes",
                    0
                ) or 0
            )

    return {

        "total_days": len(
            itinerary.get("days", [])
        ),

        "total_places": total_places,

        "total_distance_km": round(
            total_distance,
            2
        ),

        "estimated_travel_time_minutes":
            total_travel_minutes,

        "estimated_visit_time_minutes":
            total_visit_minutes,

    }
