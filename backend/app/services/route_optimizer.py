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
# DISTANCE BETWEEN TWO PLACES
# ============================================================

def distance_between_places(
    place1: Dict[str, Any],
    place2: Dict[str, Any]
) -> float:

    return calculate_distance_km(

        float(place1["latitude"]),
        float(place1["longitude"]),

        float(place2["latitude"]),
        float(place2["longitude"])

    )


# ============================================================
# FIND SPECIAL CUSTOM LOCATIONS
# ============================================================

def split_special_locations(
    places: List[Dict[str, Any]]
):

    start_location = None
    end_location = None

    normal_places = []

    for place in places:

        if not place.get(
            "custom_location",
            False
        ):

            normal_places.append(place)

            continue

        role = str(
            place.get(
                "custom_role",
                "waypoint"
            )
        ).lower()

        if role == "start":

            start_location = place

        elif role == "end":

            end_location = place

        else:

            normal_places.append(place)

    return (
        start_location,
        normal_places,
        end_location
    )


# ============================================================
# OPTIMIZE ONE DAY
# ============================================================

def optimize_day_route(
    places: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    if len(places) <= 1:
        return places

    origins = [
        place
        for place in places
        if place.get("origin") is True
    ]

    normal_places = [
        place
        for place in places
        if place.get("origin") is not True
    ]

    # --------------------------------------------------------
    # If an origin exists, it MUST remain first.
    # --------------------------------------------------------

    if origins:

        origin = origins[0].copy()

        origin["distance_from_previous_km"] = 0.0

        optimized = [origin]

        remaining = normal_places.copy()

        current = origin

    else:

        remaining = places.copy()

        optimized = []

        current = remaining.pop(0).copy()

        current[
            "distance_from_previous_km"
        ] = 0.0

        optimized.append(current)

    # --------------------------------------------------------
    # Nearest-neighbour optimization
    # --------------------------------------------------------

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
# NORMAL ROUTE OPTIMIZATION
# ============================================================

def optimize_normal_route(
    places: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    if len(places) <= 1:

        result = [
            dict(place)
            for place in places
        ]

        if result:

            result[0][
                "distance_from_previous_km"
            ] = 0.0

        return result

    remaining = [
        dict(place)
        for place in places
    ]

    optimized = []

    current = remaining.pop(0)

    current[
        "distance_from_previous_km"
    ] = 0.0

    optimized.append(
        current
    )

    while remaining:

        nearest_index = min(

            range(
                len(remaining)
            ),

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

        optimized_places = (
            optimize_day_route(
                places
            )
        )

        # ----------------------------------------------------
        # Calculate total distance
        # ----------------------------------------------------

        total_distance = 0.0

        for place in optimized_places:

            total_distance += float(
                place.get(
                    "distance_from_previous_km",
                    0
                ) or 0
            )

        optimized_days.append({

            "day":
                day.get("day"),

            "places":
                optimized_places,

            "total_distance_km":
                round(
                    total_distance,
                    2
                )

        })

    return {

        "city":
            itinerary.get("city"),

        "days":
            optimized_days

    }

def add_destination_distance(
    itinerary: Dict[str, Any]
) -> Dict[str, Any]:

    for day in itinerary.get("days", []):

        places = day.get("places", [])

        if not places:
            continue

        destination = places[-1]

        if not destination.get("destination"):
            continue

        if len(places) < 2:
            continue

        previous_place = places[-2]

        distance = distance_between_places(
            previous_place,
            destination
        )

        destination["distance_from_previous_km"] = distance

    return itinerary