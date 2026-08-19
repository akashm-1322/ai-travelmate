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
    opening_hours=None,
    role: str = "waypoint",
    day: int = 1,
    start_time=None,
    end_time=None,
) -> Dict[str, Any]:

    location: Dict[str, Any] = {
        "name": name,
        "category": category,

        "latitude": float(latitude),
        "longitude": float(longitude),

        "description": None,
        "address": None,
        "opening_hours": opening_hours,

        "distance_from_previous_km": 0.0,

        "visit_duration_minutes": max(
            0,
            int(visit_duration_minutes)
        ),

        "custom_location": True,
        "custom_role": role,

        "day": int(day),
    }

    # ========================================================
    # START LOCATION
    # ========================================================

    if role == "start":

        location["preferred_start_time"] = (
            start_time or "09:00"
        )

        location["origin"] = True

    # ========================================================
    # DESTINATION
    # ========================================================

    elif role == "destination":

        location["preferred_end_time"] = (
            end_time
        )

        location["destination"] = True

    # ========================================================
    # WAYPOINT
    # ========================================================

    else:

        location["custom_role"] = "waypoint"

    return location


# ============================================================
# INJECT CUSTOM LOCATIONS INTO ITINERARY
# ============================================================

def inject_custom_locations(
    itinerary: Dict[str, Any],
    custom_locations: List[Dict[str, Any]]
) -> Dict[str, Any]:

    if not custom_locations:
        return itinerary

    result: Dict[str, Any] = {
        "city": itinerary.get("city"),
        "days": []
    }

    # ========================================================
    # COPY EXISTING DAYS
    # ========================================================

    for day in itinerary.get("days", []):

        result["days"].append({

            "day": day.get("day"),

            "places": [
                dict(place)
                for place in day.get(
                    "places",
                    []
                )
            ]

        })

    # ========================================================
    # INJECT CUSTOM LOCATIONS
    # ========================================================

    for location in custom_locations:

        target_day = int(
            location.get(
                "day",
                1
            )
        )

        role = str(
            location.get(
                "custom_role",
                "waypoint"
            )
        ).lower()

        # ----------------------------------------------------
        # FIND REQUESTED DAY
        # ----------------------------------------------------

        target = None

        for day in result["days"]:

            if day["day"] == target_day:

                target = day
                break

        # ----------------------------------------------------
        # CREATE DAY IF IT DOES NOT EXIST
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
        # START
        # ----------------------------------------------------

        if role == "start":

            target["places"].insert(
                0,
                dict(location)
            )

        # ----------------------------------------------------
        # DESTINATION
        #
        # IMPORTANT:
        # Use "destination", not "end",
        # because the scheduling system searches
        # for custom_role == "destination".
        # ----------------------------------------------------

        elif role == "destination":

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

    # ========================================================
    # KEEP DAYS ORDERED
    # ========================================================

    result["days"].sort(
        key=lambda day: day["day"]
    )

    return result