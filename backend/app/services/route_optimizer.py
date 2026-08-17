from math import radians, sin, cos, sqrt, atan2
from typing import List, Dict, Any


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def calculate_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:

    R = 6371.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return round(
        R * c,
        2
    )


# ============================================================
# CALCULATE DISTANCE BETWEEN TWO PLACES
# ============================================================

def distance_between_places(
    place1: Dict[str, Any],
    place2: Dict[str, Any]
) -> float:

    return calculate_distance_km(

        place1["latitude"],
        place1["longitude"],

        place2["latitude"],
        place2["longitude"]

    )


# ============================================================
# OPTIMIZE ONE DAY
# ============================================================

def optimize_day_route(
    places: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    if len(places) <= 1:
        return places

    remaining = places.copy()

    optimized = []

    current = remaining.pop(0)

    current = current.copy()

    current["distance_from_previous_km"] = 0.0

    optimized.append(current)

    while remaining:

        nearest_index = min(
            range(len(remaining)),
            key=lambda index:
                distance_between_places(
                    current,
                    remaining[index]
                )
        )

        nearest_place = remaining.pop(
            nearest_index
        )

        distance = (
            distance_between_places(
                current,
                nearest_place
            )
        )

        nearest_place = nearest_place.copy()

        nearest_place[
            "distance_from_previous_km"
        ] = distance

        optimized.append(
            nearest_place
        )

        current = nearest_place

    return optimized

# ============================================================
# OPTIMIZE COMPLETE ITINERARY
# ============================================================

def optimize_itinerary(
    itinerary: Dict[str, Any]
) -> Dict[str, Any]:

    optimized_days = []

    for day in itinerary.get(
        "days",
        []
    ):

        places = day.get(
            "places",
            []
        )

        optimized_places = optimize_day_route(
            places
        )

        # ----------------------------------------------------
        # Calculate total distance for the day
        # ----------------------------------------------------

        total_distance = 0.0

        for place in optimized_places:

            total_distance += place.get(
                "distance_from_previous_km",
                0
            )

        optimized_days.append({

            "day": day["day"],

            "places": optimized_places,

            "total_distance_km": round(
                total_distance,
                2
            )

        })

    return {

        "city": itinerary["city"],

        "days": optimized_days

    }