from typing import Any, Dict, List, Optional
from math import radians, sin, cos, sqrt, atan2


# ============================================================
# CONFIGURATION
# ============================================================

MAX_OPTIMIZATION_ITERATIONS = 100


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def calculate_coordinate_distance_km(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float
) -> float:

    earth_radius_km = 6371.0

    lat1 = radians(float(latitude1))
    lon1 = radians(float(longitude1))

    lat2 = radians(float(latitude2))
    lon2 = radians(float(longitude2))

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        sin(delta_lat / 2) ** 2
        +
        cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    # Protect against tiny floating-point errors.
    a = max(0.0, min(1.0, a))

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius_km * c


# ============================================================
# BACKWARD-COMPATIBLE ALIAS
# ============================================================

def calculate_distance_km(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float
) -> float:

    return calculate_coordinate_distance_km(
        latitude1,
        longitude1,
        latitude2,
        longitude2
    )


# ============================================================
# ORIGIN CHECK
# ============================================================

def is_origin(
    place: Dict[str, Any]
) -> bool:

    if place.get("origin") is True:
        return True

    if not place.get(
        "custom_location",
        False
    ):
        return False

    role = str(
        place.get(
            "custom_role",
            ""
        )
    ).strip().lower()

    return role == "start"


# ============================================================
# DESTINATION CHECK
# ============================================================

def is_destination(
    place: Dict[str, Any]
) -> bool:

    if place.get("destination") is True:
        return True

    if not place.get(
        "custom_location",
        False
    ):
        return False

    role = str(
        place.get(
            "custom_role",
            ""
        )
    ).strip().lower()

    return role == "destination"


# ============================================================
# FIND ORIGIN
# ============================================================

def find_origin(
    places: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:

    for place in places:

        if is_origin(place):
            return place

    return None


# ============================================================
# FIND DESTINATION
# ============================================================

def find_destination(
    places: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:

    for place in places:

        if is_destination(place):
            return place

    return None


# ============================================================
# EXTRACT NORMAL WAYPOINTS
# ============================================================

def extract_waypoints(
    places: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    waypoints = []

    for place in places:

        if is_origin(place):
            continue

        if is_destination(place):
            continue

        waypoints.append(place)

    return waypoints


# ============================================================
# DISTANCE BETWEEN TWO PLACES
# ============================================================

def distance_between_places(
    place1: Dict[str, Any],
    place2: Dict[str, Any]
) -> float:

    try:

        return calculate_coordinate_distance_km(
            place1["latitude"],
            place1["longitude"],
            place2["latitude"],
            place2["longitude"]
        )

    except (
        KeyError,
        TypeError,
        ValueError
    ):

        return 0.0


# ============================================================
# CHECK COORDINATES
# ============================================================

def has_valid_coordinates(
    place: Dict[str, Any]
) -> bool:

    try:

        float(place["latitude"])
        float(place["longitude"])

        return True

    except (
        KeyError,
        TypeError,
        ValueError
    ):

        return False


# ============================================================
# TOTAL ROUTE DISTANCE
# ============================================================

def calculate_route_distance(
    places: List[Dict[str, Any]]
) -> float:

    if len(places) <= 1:
        return 0.0

    total_distance = 0.0

    for index in range(
        1,
        len(places)
    ):

        previous_place = places[index - 1]
        current_place = places[index]

        if not has_valid_coordinates(
            previous_place
        ):
            continue

        if not has_valid_coordinates(
            current_place
        ):
            continue

        total_distance += (
            distance_between_places(
                previous_place,
                current_place
            )
        )

    return round(
        total_distance,
        2
    )


# ============================================================
# RECALCULATE ROUTE DISTANCES
# ============================================================

def recalculate_distances(
    places: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    result = []

    for index, place in enumerate(
        places
    ):

        updated_place = dict(
            place
        )

        # ----------------------------------------------------
        # First location
        # ----------------------------------------------------

        if index == 0:

            updated_place[
                "distance_from_previous_km"
            ] = 0.0

            result.append(
                updated_place
            )

            continue

        previous_place = places[
            index - 1
        ]

        # ----------------------------------------------------
        # Missing coordinates
        # ----------------------------------------------------

        if (
            not has_valid_coordinates(
                previous_place
            )
            or
            not has_valid_coordinates(
                place
            )
        ):

            updated_place[
                "distance_from_previous_km"
            ] = 0.0

            result.append(
                updated_place
            )

            continue

        # ----------------------------------------------------
        # Calculate actual distance
        # ----------------------------------------------------

        distance = (
            distance_between_places(
                previous_place,
                place
            )
        )

        updated_place[
            "distance_from_previous_km"
        ] = round(
            distance,
            2
        )

        result.append(
            updated_place
        )

    return result


# ============================================================
# VALIDATE / RECALCULATE ROUTE DISTANCES
# ============================================================

def validate_route_distances(
    places: List[Dict[str, Any]]
) -> List[str]:

    warnings = []

    if not places:
        return warnings

    for index, place in enumerate(
        places
    ):

        # ----------------------------------------------------
        # First location
        # ----------------------------------------------------

        if index == 0:

            place[
                "distance_from_previous_km"
            ] = 0.0

            continue

        previous_place = places[
            index - 1
        ]

        # ----------------------------------------------------
        # Validate coordinates
        # ----------------------------------------------------

        if not has_valid_coordinates(
            previous_place
        ):

            warnings.append(
                "Missing or invalid coordinates for "
                f"'{previous_place.get('name', 'Unknown')}'."
            )

            continue

        if not has_valid_coordinates(
            place
        ):

            warnings.append(
                "Missing or invalid coordinates for "
                f"'{place.get('name', 'Unknown')}'."
            )

            continue

        # ----------------------------------------------------
        # Calculate actual distance
        # ----------------------------------------------------

        calculated_distance = (
            distance_between_places(
                previous_place,
                place
            )
        )

        calculated_distance = round(
            calculated_distance,
            2
        )

        # ----------------------------------------------------
        # Existing distance
        # ----------------------------------------------------

        try:

            existing_distance = float(
                place.get(
                    "distance_from_previous_km",
                    0
                ) or 0
            )

        except (
            TypeError,
            ValueError
        ):

            existing_distance = 0.0

        # ----------------------------------------------------
        # Detect mismatch
        # ----------------------------------------------------

        difference = abs(
            existing_distance
            - calculated_distance
        )

        if difference > 1.0:

            warnings.append(
                "Route distance corrected between "
                f"'{previous_place.get('name', 'Unknown')}' "
                "and "
                f"'{place.get('name', 'Unknown')}'. "
                f"Previous value: "
                f"{existing_distance:.2f} km, "
                f"coordinate distance: "
                f"{calculated_distance:.2f} km."
            )

        # ----------------------------------------------------
        # ALWAYS use coordinate distance
        # ----------------------------------------------------

        place[
            "distance_from_previous_km"
        ] = calculated_distance

    return warnings


# ============================================================
# NEAREST NEIGHBOR
# ============================================================

def nearest_neighbor(
    start: Dict[str, Any],
    waypoints: List[Dict[str, Any]],
    destination: Optional[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    remaining = list(
        waypoints
    )

    route = []

    current = start

    # --------------------------------------------------------
    # If start coordinates are invalid, preserve input order.
    # --------------------------------------------------------

    if not has_valid_coordinates(
        start
    ):

        return list(
            waypoints
        )

    while remaining:

        valid_remaining = [
            place
            for place in remaining
            if has_valid_coordinates(place)
        ]

        # ----------------------------------------------------
        # No valid coordinate waypoints left.
        # ----------------------------------------------------

        if not valid_remaining:

            route.extend(
                remaining
            )

            break

        # ----------------------------------------------------
        # Find nearest waypoint.
        # ----------------------------------------------------

        nearest = min(

            valid_remaining,

            key=lambda place:
                distance_between_places(
                    current,
                    place
                )

        )

        route.append(
            nearest
        )

        remaining.remove(
            nearest
        )

        current = nearest

    return route


# ============================================================
# 2-OPT
# ============================================================

def two_opt(
    start: Dict[str, Any],
    waypoints: List[Dict[str, Any]],
    destination: Optional[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    if len(waypoints) < 3:

        return list(
            waypoints
        )

    route = list(
        waypoints
    )

    iterations = 0

    while (
        iterations
        < MAX_OPTIMIZATION_ITERATIONS
    ):

        iterations += 1

        improved = False

        current_full_route = (
            [start]
            + route
        )

        if destination is not None:

            current_full_route.append(
                destination
            )

        current_distance = (
            calculate_route_distance(
                current_full_route
            )
        )

        # ----------------------------------------------------
        # Try every possible reversal.
        # ----------------------------------------------------

        for i in range(
            0,
            len(route) - 1
        ):

            for j in range(
                i + 1,
                len(route)
            ):

                candidate = (
                    route[:i]
                    +
                    list(
                        reversed(
                            route[i:j + 1]
                        )
                    )
                    +
                    route[j + 1:]
                )

                candidate_full_route = (
                    [start]
                    + candidate
                )

                if destination is not None:

                    candidate_full_route.append(
                        destination
                    )

                candidate_distance = (
                    calculate_route_distance(
                        candidate_full_route
                    )
                )

                if (
                    candidate_distance
                    < current_distance - 0.0001
                ):

                    route = candidate

                    improved = True

                    break

            if improved:
                break

        if not improved:
            break

    return route


# ============================================================
# REBUILD ROUTE
# ============================================================

def rebuild_route(
    origin: Optional[Dict[str, Any]],
    waypoints: List[Dict[str, Any]],
    destination: Optional[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    result = []

    if origin is not None:

        result.append(
            dict(origin)
        )

    for waypoint in waypoints:

        result.append(
            dict(waypoint)
        )

    if destination is not None:

        result.append(
            dict(destination)
        )

    return result


# ============================================================
# DESTINATION DEADLINE
# ============================================================

def get_destination_deadline(
    destination: Optional[
        Dict[str, Any]
    ]
) -> Optional[str]:

    if not destination:
        return None

    deadline = destination.get(
        "preferred_end_time"
    )

    if not deadline:
        return None

    return str(
        deadline
    )


# ============================================================
# ROUTE SCORE
# ============================================================

def route_score(
    origin: Optional[Dict[str, Any]],
    waypoints: List[Dict[str, Any]],
    destination: Optional[Dict[str, Any]]
) -> float:

    route = rebuild_route(
        origin,
        waypoints,
        destination
    )

    return calculate_route_distance(
        route
    )


# ============================================================
# ADD DESTINATION DISTANCE
# ============================================================

def add_destination_distance(
    itinerary: Dict[str, Any],
    destination: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:

    # ========================================================
    # SAFETY CHECK
    # ========================================================

    if not itinerary:
        return itinerary

    # --------------------------------------------------------
    # Work on a copy so the original itinerary is not
    # unexpectedly modified.
    # --------------------------------------------------------

    result = dict(itinerary)

    days = result.get(
        "days",
        []
    )

    updated_days = []

    # ========================================================
    # PROCESS EACH DAY
    # ========================================================

    for day in days:

        updated_day = dict(day)

        places = day.get(
            "places",
            []
        )

        updated_places = [
            dict(place)
            for place in places
        ]

        # ----------------------------------------------------
        # Only add the supplied destination if it does not
        # already exist in the itinerary.
        # ----------------------------------------------------

        if destination is not None:

            destination_exists = False

            for place in updated_places:

                if (
                    place.get("destination") is True
                    or (
                        place.get(
                            "custom_location",
                            False
                        )
                        and str(
                            place.get(
                                "custom_role",
                                ""
                            )
                        ).lower()
                        == "destination"
                    )
                ):

                    destination_exists = True
                    break

            if not destination_exists:

                # ------------------------------------------------
                # Destination belongs on the final day.
                # ------------------------------------------------

                if day is days[-1]:

                    updated_places.append(
                        dict(destination)
                    )

        # ----------------------------------------------------
        # Recalculate distances for this day's route.
        # ----------------------------------------------------

        updated_places = recalculate_distances(
            updated_places
        )

        updated_day["places"] = updated_places

        # ----------------------------------------------------
        # Recalculate total distance for the day.
        # ----------------------------------------------------

        updated_day[
            "total_distance_km"
        ] = calculate_route_distance(
            updated_places
        )

        updated_days.append(
            updated_day
        )

    # ========================================================
    # UPDATE ITINERARY
    # ========================================================

    result["days"] = updated_days

    # --------------------------------------------------------
    # Calculate complete itinerary distance.
    # --------------------------------------------------------

    total_distance = 0.0

    for day in updated_days:

        total_distance += float(
            day.get(
                "total_distance_km",
                0.0
            )
        )

    result[
        "total_distance_km"
    ] = round(
        total_distance,
        2
    )

    return result

# ============================================================
# OPTIMIZE ONE DAY
# ============================================================

def optimize_day(
    places: List[Dict[str, Any]]
) -> Dict[str, Any]:

    if not places:

        return {
            "places": [],
            "total_distance_km": 0.0,
            "optimization": {
                "origin_protected": False,
                "destination_protected": False,
                "waypoints_optimized": False,
                "initial_distance_km": 0.0,
                "optimized_distance_km": 0.0
            }
        }

    # ========================================================
    # FIND SPECIAL LOCATIONS
    # ========================================================

    origin = find_origin(
        places
    )

    destination = find_destination(
        places
    )

    waypoints = extract_waypoints(
        places
    )

    # ========================================================
    # NO ORIGIN
    # ========================================================

    if origin is None:

        if destination is not None:

            remaining = [
                place
                for place in places
                if not is_destination(place)
            ]

            route = (
                remaining
                + [destination]
            )

        else:

            route = list(
                places
            )

        route = recalculate_distances(
            route
        )

        total_distance = (
            calculate_route_distance(
                route
            )
        )

        return {

            "places": route,

            "total_distance_km":
                total_distance,

            "optimization": {

                "origin_protected":
                    False,

                "destination_protected":
                    destination is not None,

                "waypoints_optimized":
                    False,

                "initial_distance_km":
                    total_distance,

                "optimized_distance_km":
                    total_distance

            }

        }

    # ========================================================
    # NO WAYPOINTS
    # ========================================================

    if not waypoints:

        route = rebuild_route(
            origin,
            [],
            destination
        )

        route = recalculate_distances(
            route
        )

        total_distance = (
            calculate_route_distance(
                route
            )
        )

        return {

            "places": route,

            "total_distance_km":
                total_distance,

            "optimization": {

                "origin_protected":
                    True,

                "destination_protected":
                    destination is not None,

                "waypoints_optimized":
                    False,

                "initial_distance_km":
                    total_distance,

                "optimized_distance_km":
                    total_distance

            }

        }

    # ========================================================
    # INITIAL ROUTE
    # ========================================================

    initial_waypoints = nearest_neighbor(

        origin,

        waypoints,

        destination

    )

    initial_distance = route_score(

        origin,

        initial_waypoints,

        destination

    )

    # ========================================================
    # 2-OPT
    # ========================================================

    optimized_waypoints = two_opt(

        origin,

        initial_waypoints,

        destination

    )

    optimized_distance = route_score(

        origin,

        optimized_waypoints,

        destination

    )

    # ========================================================
    # SAFETY CHECK
    # ========================================================

    if optimized_distance > initial_distance:

        optimized_waypoints = list(
            initial_waypoints
        )

        optimized_distance = (
            initial_distance
        )

    # ========================================================
    # BUILD FINAL ROUTE
    # ========================================================

    final_route = rebuild_route(

        origin,

        optimized_waypoints,

        destination

    )

    # ========================================================
    # RECALCULATE LEG DISTANCES
    # ========================================================

    final_route = recalculate_distances(
        final_route
    )

    # ========================================================
    # FINAL TOTAL
    # ========================================================

    total_distance = (
        calculate_route_distance(
            final_route
        )
    )

    # ========================================================
    # RETURN
    # ========================================================

    return {

        "places":
            final_route,

        "total_distance_km":
            total_distance,

        "optimization": {

            "origin_protected":
                True,

            "destination_protected":
                destination is not None,

            "waypoints_optimized":
                len(waypoints) >= 3,

            "initial_distance_km":
                round(
                    initial_distance,
                    2
                ),

            "optimized_distance_km":
                round(
                    total_distance,
                    2
                )

        }

    }


# ============================================================
# OPTIMIZE COMPLETE ITINERARY
# ============================================================

def optimize_itinerary(
    itinerary: Dict[str, Any]
) -> Dict[str, Any]:

    optimized_days = []

    all_distance = 0.0

    all_warnings = []

    days = itinerary.get(
        "days",
        []
    )

    for day in days:

        places = day.get(
            "places",
            []
        )

        # ----------------------------------------------------
        # Validate input distances first.
        # ----------------------------------------------------

        distance_warnings = (
            validate_route_distances(
                places
            )
        )

        all_warnings.extend(
            distance_warnings
        )

        # ----------------------------------------------------
        # Optimize.
        # ----------------------------------------------------

        result = optimize_day(
            places
        )

        optimized_days.append({

            "day":
                day.get("day"),

            "places":
                result["places"],

            "total_distance_km":
                result[
                    "total_distance_km"
                ],

            "optimization":
                result[
                    "optimization"
                ]

        })

        all_distance += (
            result[
                "total_distance_km"
            ]
        )

    return {

        "city":
            itinerary.get("city"),

        "days":
            optimized_days,

        "total_distance_km":
            round(
                all_distance,
                2
            ),

        "optimization_warnings":
            all_warnings

    }