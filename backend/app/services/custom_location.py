from typing import Any, Dict, List


# ============================================================
# CREATE CUSTOM LOCATION
# ============================================================

def create_custom_location(
    name: str,
    latitude: float,
    longitude: float,
    category: str = "custom_location",
    visit_duration_minutes: int = 0,
    opening_hours: str | None = None,
    role: str = "waypoint",
    day: int = 1,
    start_time: str | None = None,
) -> Dict[str, Any]:

    return {
        "name": name,
        "category": category,
        "description": None,

        "latitude": float(latitude),
        "longitude": float(longitude),

        "address": None,
        "opening_hours": opening_hours,

        "map_url": (
            f"https://www.openstreetmap.org/"
            f"?mlat={latitude}&mlon={longitude}"
        ),

        "distance_from_previous_km": 0,

        "visit_duration_minutes":
            max(0, int(visit_duration_minutes)),

        "custom_location": True,

        "custom_role": role,

        "day": int(day),

        "preferred_start_time": start_time,
    }


# ============================================================
# INJECT CUSTOM LOCATIONS INTO ITINERARY
# ============================================================

def inject_custom_locations(
    itinerary: Dict[str, Any],
    custom_locations: List[Dict[str, Any]]
) -> Dict[str, Any]:

    if not custom_locations:
        return itinerary

    result = {
        "city": itinerary.get("city"),
        "days": []
    }

    # --------------------------------------------------------
    # Copy existing days
    # --------------------------------------------------------

    for day in itinerary.get("days", []):

        result["days"].append({
            "day": day.get("day"),
            "places": [
                dict(place)
                for place in day.get("places", [])
            ]
        })

    # --------------------------------------------------------
    # Inject each custom location
    # --------------------------------------------------------

    for location in custom_locations:

        target_day = int(
            location.get("day", 1)
        )

        role = str(
            location.get(
                "custom_role",
                "waypoint"
            )
        ).lower()

        # ----------------------------------------------------
        # Find requested day
        # ----------------------------------------------------

        target = None

        for day in result["days"]:

            if day["day"] == target_day:
                target = day
                break

        # ----------------------------------------------------
        # If requested day doesn't exist,
        # create it.
        # ----------------------------------------------------

        if target is None:

            target = {
                "day": target_day,
                "places": []
            }

            result["days"].append(
                target
            )

        # ----------------------------------------------------
        # START LOCATION
        # ----------------------------------------------------

        if role == "start":

            target["places"].insert(
                0,
                dict(location)
            )

        # ----------------------------------------------------
        # END LOCATION
        # ----------------------------------------------------

        elif role == "end":

            target["places"].append(
                dict(location)
            )

        # ----------------------------------------------------
        # WAYPOINT
        # ----------------------------------------------------

        else:

            target["places"].append(
                dict(location)
            )

    # --------------------------------------------------------
    # Keep days ordered
    # --------------------------------------------------------

    result["days"].sort(
        key=lambda day: day["day"]
    )

    return result
