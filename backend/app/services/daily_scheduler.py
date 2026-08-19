
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# ============================================================
# ROUTE OPTIMIZER IMPORTS
# ============================================================
# IMPORTANT:
# Route/distance validation belongs to route_optimizer.py.
# daily_scheduler.py only USES that validation.
#
# If your project is:
#
# backend/
# └── app/
#     └── services/
#         ├── daily_scheduler.py
#         └── route_optimizer.py
#
# use this absolute import.

from app.services.route_optimizer import (
    validate_route_distances,
)


# ============================================================
# DEFAULT VISIT DURATIONS
# ============================================================

DEFAULT_VISIT_DURATION = {
    "place_of_worship": 60,
    "park": 45,
    "beach": 90,
    "museum": 120,
    "shopping": 120,
    "restaurant": 60,
    "cafe": 45,
    "hotel": 30,
    "attraction": 60,
}


# ============================================================
# DEFAULT TRAVEL SPEED
# ============================================================

AVERAGE_SPEED_KMPH = 25


# ============================================================
# VISIT DURATION
# ============================================================

def get_visit_duration(
    place: Dict[str, Any]
) -> int:

    # --------------------------------------------------------
    # Custom locations can specify their own duration.
    # --------------------------------------------------------

    if place.get("custom_location"):

        custom_duration = place.get(
            "visit_duration_minutes"
        )

        if custom_duration is not None:

            return max(
                0,
                int(custom_duration)
            )

    # --------------------------------------------------------
    # Otherwise use category-based duration.
    # --------------------------------------------------------

    category = str(
        place.get(
            "category",
            ""
        )
    ).lower()

    return DEFAULT_VISIT_DURATION.get(
        category,
        60
    )


# ============================================================
# TRAVEL TIME
# ============================================================

def calculate_travel_time(
    distance_km: float
) -> int:

    if distance_km <= 0:
        return 0

    minutes = (
        distance_km
        / AVERAGE_SPEED_KMPH
        * 60
    )

    # Minimum 5 minutes for any non-zero movement.
    return max(
        5,
        round(minutes)
    )


# ============================================================
# OPENING TIME
# ============================================================

def get_opening_time(
    opening_hours: Any
) -> str:

    # --------------------------------------------------------
    # If no opening hours are available,
    # do not artificially force a 09:00 opening.
    # --------------------------------------------------------

    if not opening_hours:
        return "00:00"

    opening_hours = str(
        opening_hours
    ).strip()

    # Example:
    # Mo-Su 10:00-13:00

    if " " in opening_hours:

        time_part = (
            opening_hours
            .split(
                " ",
                1
            )[1]
        )

        if "-" in time_part:

            return (
                time_part
                .split(
                    "-",
                    1
                )[0]
                .strip()
            )

    return "00:00"


# ============================================================
# TIME HELPERS
# ============================================================

def parse_time(
    value: str
) -> datetime:

    return datetime.strptime(
        value,
        "%H:%M"
    )


def format_time(
    value: datetime
) -> str:

    return value.strftime(
        "%H:%M"
    )


# ============================================================
# FIND ORIGIN
# ============================================================

def get_origin(
    places: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:

    for place in places:

        # Explicit origin flag.
        if place.get("origin") is True:
            return place

        # Custom START location.
        if (
            place.get(
                "custom_location",
                False
            )
            and str(
                place.get(
                    "custom_role",
                    ""
                )
            ).lower() == "start"
        ):
            return place

    return None


# ============================================================
# FIND DESTINATION
# ============================================================

def get_destination(
    places: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:

    for place in places:

        # Explicit destination flag.
        if place.get("destination") is True:
            return place

        # Custom DESTINATION location.
        if (
            place.get(
                "custom_location",
                False
            )
            and str(
                place.get(
                    "custom_role",
                    ""
                )
            ).lower() == "destination"
        ):
            return place

    return None


# ============================================================
# CUSTOM START TIME
# ============================================================

def get_custom_start_time(
    places: List[Dict[str, Any]]
) -> Optional[str]:

    origin = get_origin(
        places
    )

    if not origin:
        return None

    preferred_time = origin.get(
        "preferred_start_time"
    )

    if not preferred_time:
        return None

    try:

        parse_time(
            preferred_time
        )

        return preferred_time

    except (
        ValueError,
        TypeError
    ):

        return None


# ============================================================
# DESTINATION DEADLINE
# ============================================================

def get_destination_deadline(
    destination: Optional[Dict[str, Any]]
) -> Optional[str]:

    if not destination:
        return None

    # --------------------------------------------------------
    # Preferred end time is the destination deadline.
    # --------------------------------------------------------

    deadline = destination.get(
        "preferred_end_time"
    )

    if not deadline:
        return None

    try:

        parse_time(
            deadline
        )

        return deadline

    except (
        ValueError,
        TypeError
    ):

        return None


# ============================================================
# NORMALIZE PLACE ORDER
# ============================================================

def normalize_place_order(
    places: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    origin = get_origin(
        places
    )

    destination = get_destination(
        places
    )

    middle_places = []

    for place in places:

        # ----------------------------------------------------
        # Remove origin from middle.
        # ----------------------------------------------------

        if (
            origin is not None
            and place is origin
        ):
            continue

        # ----------------------------------------------------
        # Remove destination from middle.
        # ----------------------------------------------------

        if (
            destination is not None
            and place is destination
        ):
            continue

        middle_places.append(
            place
        )

    result = []

    # --------------------------------------------------------
    # Origin MUST be first.
    # --------------------------------------------------------

    if origin is not None:

        result.append(
            origin
        )

    # --------------------------------------------------------
    # Normal attractions remain in the middle.
    # --------------------------------------------------------

    result.extend(
        middle_places
    )

    # --------------------------------------------------------
    # Destination MUST be last.
    # --------------------------------------------------------

    if destination is not None:

        result.append(
            destination
        )

    return result


# ============================================================
# SCHEDULE ONE DAY
# ============================================================

def schedule_day(
    places: List[Dict[str, Any]],
    start_time: str = "09:00"
) -> Dict[str, Any]:

    # ========================================================
    # 1. NORMALIZE ORDER
    # ========================================================

    places = normalize_place_order(
        places
    )

    # ========================================================
    # 2. STEP 24
    # RECALCULATE ROUTE DISTANCES
    # ========================================================
    #
    # IMPORTANT:
    # validate_route_distances() is implemented in
    # route_optimizer.py.
    #
    # We call it AFTER normalize_place_order()
    # because normalization may change:
    #
    # origin -> waypoint
    # waypoint -> waypoint
    # waypoint -> destination
    #
    # Therefore every distance must be recalculated.
    # ========================================================

    route_warnings = (
        validate_route_distances(
            places
        )
    )

    # ========================================================
    # 3. DETERMINE START TIME
    # ========================================================

    custom_start_time = (
        get_custom_start_time(
            places
        )
    )

    actual_start_time = (
        custom_start_time
        or start_time
    )

    try:

        current_time = parse_time(
            actual_start_time
        )

    except (
        ValueError,
        TypeError
    ):

        actual_start_time = "09:00"

        current_time = parse_time(
            actual_start_time
        )

    # ========================================================
    # 4. INITIALIZE
    # ========================================================

    scheduled_places = []

    total_distance = 0.0

    warnings = list(
        route_warnings
    )

    errors = []

    # ========================================================
    # 5. FIND ORIGIN / DESTINATION
    # ========================================================

    origin = get_origin(
        places
    )

    destination = get_destination(
        places
    )

    # ========================================================
    # 6. VALIDATE ORIGIN
    # ========================================================

    if origin is None:

        warnings.append(
            "No origin was provided. "
            "The itinerary is being scheduled "
            "from the default start time."
        )

    else:

        # ----------------------------------------------------
        # Origin should always be first.
        # ----------------------------------------------------

        if places:

            if places[0] is not origin:

                errors.append(
                    "Origin validation failed: "
                    "origin is not the first location."
                )

    # ========================================================
    # 7. VALIDATE DESTINATION
    # ========================================================

    if destination is not None:

        # ----------------------------------------------------
        # Destination must be last.
        # ----------------------------------------------------

        if places:

            if places[-1] is not destination:

                errors.append(
                    "Destination validation failed: "
                    "destination is not the final location."
                )

        destination_deadline = (
            get_destination_deadline(
                destination
            )
        )

    else:

        destination_deadline = None

    # ========================================================
    # 8. SCHEDULE ALL PLACES
    # ========================================================

    for index, place in enumerate(
        places
    ):

        # ----------------------------------------------------
        # Distance from previous location.
        # ----------------------------------------------------

        distance = float(
            place.get(
                "distance_from_previous_km",
                0
            ) or 0
        )

        # ----------------------------------------------------
        # Travel time.
        # ----------------------------------------------------

        travel_minutes = (
            calculate_travel_time(
                distance
            )
        )

        # ----------------------------------------------------
        # Move to location.
        # ----------------------------------------------------

        current_time += timedelta(
            minutes=travel_minutes
        )

        # ----------------------------------------------------
        # Opening hours.
        # ----------------------------------------------------

        opening_time = get_opening_time(
            place.get(
                "opening_hours"
            )
        )

        try:

            opening_datetime = parse_time(
                opening_time
            )

        except (
            ValueError,
            TypeError
        ):

            opening_datetime = parse_time(
                "00:00"
            )

        # ----------------------------------------------------
        # Wait until location opens.
        # ----------------------------------------------------

        if current_time < opening_datetime:

            current_time = (
                opening_datetime
            )

        # ----------------------------------------------------
        # Arrival.
        # ----------------------------------------------------

        arrival_time = current_time

        # ----------------------------------------------------
        # Visit duration.
        # ----------------------------------------------------

        visit_duration = (
            get_visit_duration(
                place
            )
        )

        # ----------------------------------------------------
        # Departure.
        # ----------------------------------------------------

        departure_time = (
            arrival_time
            + timedelta(
                minutes=visit_duration
            )
        )

        # ----------------------------------------------------
        # Create scheduled place.
        # ----------------------------------------------------

        scheduled_place = dict(
            place
        )

        scheduled_place.update({

            "travel_time_minutes":
                travel_minutes,

            "visit_duration_minutes":
                visit_duration,

            "arrival_time":
                format_time(
                    arrival_time
                ),

            "departure_time":
                format_time(
                    departure_time
                ),

        })

        scheduled_places.append(
            scheduled_place
        )

        # ----------------------------------------------------
        # Update current time.
        # ----------------------------------------------------

        current_time = (
            departure_time
        )

        # ----------------------------------------------------
        # Update total distance.
        # ----------------------------------------------------

        total_distance += distance

    # ========================================================
    # 9. DESTINATION DEADLINE VALIDATION
    # ========================================================

    if destination_deadline:

        scheduled_destination = None

        # ----------------------------------------------------
        # Find scheduled destination explicitly.
        # ----------------------------------------------------

        for place in scheduled_places:

            role = str(
                place.get(
                    "custom_role",
                    ""
                )
            ).lower()

            if (
                place.get(
                    "destination",
                    False
                ) is True
                or (
                    place.get(
                        "custom_location",
                        False
                    )
                    and role == "destination"
                )
            ):

                scheduled_destination = (
                    place
                )

                break

        # ----------------------------------------------------
        # Destination found.
        # ----------------------------------------------------

        if scheduled_destination:

            try:

                actual_arrival = parse_time(
                    scheduled_destination[
                        "arrival_time"
                    ]
                )

                deadline = parse_time(
                    destination_deadline
                )

            except (
                ValueError,
                TypeError
            ):

                errors.append(
                    "Destination deadline validation "
                    "could not be completed because "
                    "the time format is invalid."
                )

            else:

                # --------------------------------------------
                # Destination arrived AFTER deadline.
                # --------------------------------------------

                if actual_arrival > deadline:

                    late_minutes = int(
                        (
                            actual_arrival
                            - deadline
                        ).total_seconds()
                        / 60
                    )

                    errors.append(
                        "Destination deadline exceeded: "
                        f"required arrival by "
                        f"{destination_deadline}, "
                        f"estimated arrival "
                        f"{scheduled_destination['arrival_time']} "
                        f"({late_minutes} minutes late)."
                    )

                # --------------------------------------------
                # Destination arrived BEFORE deadline.
                # --------------------------------------------

                elif actual_arrival < deadline:

                    early_minutes = int(
                        (
                            deadline
                            - actual_arrival
                        ).total_seconds()
                        / 60
                    )

                    warnings.append(
                        "Destination is reached "
                        f"{early_minutes} minutes before "
                        f"the requested deadline of "
                        f"{destination_deadline}."
                    )

                # --------------------------------------------
                # Exact deadline.
                # --------------------------------------------

                else:

                    pass

        else:

            errors.append(
                "Destination deadline was specified, "
                "but no destination location was found "
                "in the scheduled itinerary."
            )

    # ========================================================
    # 10. CHECK FINAL DESTINATION POSITION
    # ========================================================

    if destination is not None:

        if not scheduled_places:

            errors.append(
                "Destination exists but "
                "the itinerary contains no scheduled places."
            )

        else:

            final_place = (
                scheduled_places[-1]
            )

            final_is_destination = (
                final_place.get(
                    "destination",
                    False
                ) is True
                or (
                    final_place.get(
                        "custom_location",
                        False
                    )
                    and str(
                        final_place.get(
                            "custom_role",
                            ""
                        )
                    ).lower()
                    == "destination"
                )
            )

            if not final_is_destination:

                errors.append(
                    "Destination validation failed: "
                    "the final scheduled location "
                    "is not the requested destination."
                )

    # ========================================================
    # 11. RETURN
    # ========================================================

    return {

        "places":
            scheduled_places,

        "total_distance_km":
            round(
                total_distance,
                2
            ),

        "start_time":
            actual_start_time,

        "end_time":
            format_time(
                current_time
            ),

        "time_validation": {

            "valid":
                len(errors) == 0,

            "errors":
                errors,

            "warnings":
                warnings

        }

    }


# ============================================================
# SCHEDULE COMPLETE ITINERARY
# ============================================================

def schedule_itinerary(
    itinerary: Dict[str, Any],
    start_time: str = "09:00"
) -> Dict[str, Any]:

    scheduled_days = []

    all_errors = []

    all_warnings = []

    days = itinerary.get(
        "days",
        []
    )

    # ========================================================
    # SCHEDULE EACH DAY
    # ========================================================

    for index, day in enumerate(
        days
    ):

        # ----------------------------------------------------
        # Day 1 uses supplied start time.
        #
        # If an origin contains preferred_start_time,
        # schedule_day() overrides it.
        # ----------------------------------------------------

        if index == 0:

            day_start_time = (
                start_time
            )

        else:

            day_start_time = (
                day.get(
                    "start_time",
                    "09:00"
                )
            )

        result = schedule_day(

            day.get(
                "places",
                []
            ),

            day_start_time

        )

        # ----------------------------------------------------
        # Store scheduled day.
        # ----------------------------------------------------

        scheduled_days.append({

            "day":
                day.get(
                    "day"
                ),

            "places":
                result[
                    "places"
                ],

            "total_distance_km":
                result[
                    "total_distance_km"
                ],

            "start_time":
                result[
                    "start_time"
                ],

            "end_time":
                result[
                    "end_time"
                ],

            "time_validation":
                result[
                    "time_validation"
                ]

        })

        # ----------------------------------------------------
        # Preserve BOTH errors and warnings.
        # ----------------------------------------------------

        all_errors.extend(
            result[
                "time_validation"
            ][
                "errors"
            ]
        )

        all_warnings.extend(
            result[
                "time_validation"
            ][
                "warnings"
            ]
        )

    # ========================================================
    # RETURN COMPLETE ITINERARY
    # ========================================================

    return {

        "city":
            itinerary.get(
                "city"
            ),

        "days":
            scheduled_days,

        "time_validation": {

            "valid":
                len(all_errors) == 0,

            "errors":
                all_errors,

            "warnings":
                all_warnings

        }

    }
