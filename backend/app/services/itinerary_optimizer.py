from typing import Any, Dict, List


# ============================================================
# VALIDATION RESULT
# ============================================================

def validate_itinerary(
    itinerary: Dict[str, Any]
) -> Dict[str, Any]:

    errors: List[str] = []
    warnings: List[str] = []

    # --------------------------------------------------------
    # BASIC STRUCTURE
    # --------------------------------------------------------

    if not isinstance(itinerary, dict):
        return {
            "valid": False,
            "errors": ["Itinerary must be a dictionary"],
            "warnings": [],
            "itinerary": itinerary
        }

    city = itinerary.get("city")

    if not city:
        errors.append(
            "Itinerary city is missing"
        )

    days = itinerary.get("days")

    if not isinstance(days, list):
        errors.append(
            "Itinerary days must be a list"
        )
        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
            "itinerary": itinerary
        }

    if not days:
        errors.append(
            "Itinerary contains no days"
        )

    # --------------------------------------------------------
    # TRACK DUPLICATES
    # --------------------------------------------------------

    global_place_names = set()

    # --------------------------------------------------------
    # VALIDATE EACH DAY
    # --------------------------------------------------------

    for day in days:

        day_number = day.get(
            "day",
            "unknown"
        )

        places = day.get(
            "places",
            []
        )

        if not isinstance(
            places,
            list
        ):
            errors.append(
                f"Day {day_number}: places must be a list"
            )
            continue

        if not places:
            errors.append(
                f"Day {day_number}: no places found"
            )
            continue

        # ----------------------------------------------------
        # DAY LENGTH WARNING
        # ----------------------------------------------------

        if len(places) > 8:

            warnings.append(
                f"Day {day_number}: "
                f"{len(places)} places may be too many"
            )

        # ----------------------------------------------------
        # DAY DISTANCE
        # ----------------------------------------------------

        total_distance = float(
            day.get(
                "total_distance_km",
                0
            ) or 0
        )

        if total_distance > 100:

            warnings.append(
                f"Day {day_number}: "
                f"very high travel distance "
                f"({total_distance:.2f} km)"
            )

        # ----------------------------------------------------
        # TIME VALIDATION
        # ----------------------------------------------------

        previous_arrival = None
        previous_departure = None

        for index, place in enumerate(
            places,
            start=1
        ):

            place_name = str(
                place.get(
                    "name",
                    ""
                )
            ).strip()

            # ------------------------------------------------
            # PLACE NAME
            # ------------------------------------------------

            if not place_name:

                errors.append(
                    f"Day {day_number}, "
                    f"place {index}: "
                    f"place name is missing"
                )

                continue

            # ------------------------------------------------
            # DUPLICATE PLACE
            # ------------------------------------------------

            normalized_name = (
                place_name.lower()
            )

            if normalized_name in global_place_names:

                warnings.append(
                    f"Duplicate place found: "
                    f"{place_name}"
                )

            global_place_names.add(
                normalized_name
            )

            # ------------------------------------------------
            # COORDINATES
            # ------------------------------------------------

            latitude = place.get(
                "latitude"
            )

            longitude = place.get(
                "longitude"
            )

            if latitude is None:

                errors.append(
                    f"{place_name}: "
                    f"latitude is missing"
                )

            if longitude is None:

                errors.append(
                    f"{place_name}: "
                    f"longitude is missing"
                )

            if latitude is not None:

                try:

                    latitude = float(
                        latitude
                    )

                    if not -90 <= latitude <= 90:

                        errors.append(
                            f"{place_name}: "
                            f"invalid latitude"
                        )

                except (
                    TypeError,
                    ValueError
                ):

                    errors.append(
                        f"{place_name}: "
                        f"latitude is invalid"
                    )

            if longitude is not None:

                try:

                    longitude = float(
                        longitude
                    )

                    if not -180 <= longitude <= 180:

                        errors.append(
                            f"{place_name}: "
                            f"invalid longitude"
                        )

                except (
                    TypeError,
                    ValueError
                ):

                    errors.append(
                        f"{place_name}: "
                        f"longitude is invalid"
                    )

            # ------------------------------------------------
            # DISTANCE
            # ------------------------------------------------

            distance = place.get(
                "distance_from_previous_km"
            )

            if distance is not None:

                try:

                    distance = float(
                        distance
                    )

                    if distance < 0:

                        errors.append(
                            f"{place_name}: "
                            f"negative distance"
                        )

                except (
                    TypeError,
                    ValueError
                ):

                    errors.append(
                        f"{place_name}: "
                        f"invalid distance"
                    )

            # ------------------------------------------------
            # TRAVEL TIME
            # ------------------------------------------------

            travel_time = place.get(
                "travel_time_minutes"
            )

            if travel_time is not None:

                try:

                    travel_time = float(
                        travel_time
                    )

                    if travel_time < 0:

                        errors.append(
                            f"{place_name}: "
                            f"negative travel time"
                        )

                except (
                    TypeError,
                    ValueError
                ):

                    errors.append(
                        f"{place_name}: "
                        f"invalid travel time"
                    )

            # ------------------------------------------------
            # VISIT DURATION
            # ------------------------------------------------

            visit_duration = place.get(
                "visit_duration_minutes"
            )

            if visit_duration is not None:

                try:

                    visit_duration = float(
                        visit_duration
                    )

                    if visit_duration <= 0:

                        errors.append(
                            f"{place_name}: "
                            f"invalid visit duration"
                        )

                except (
                    TypeError,
                    ValueError
                ):

                    errors.append(
                        f"{place_name}: "
                        f"invalid visit duration"
                    )

            # ------------------------------------------------
            # ARRIVAL / DEPARTURE
            # ------------------------------------------------

            arrival = place.get(
                "arrival_time"
            )

            departure = place.get(
                "departure_time"
            )

            if arrival and departure:

                try:

                    arrival_minutes = (
                        _time_to_minutes(
                            arrival
                        )
                    )

                    departure_minutes = (
                        _time_to_minutes(
                            departure
                        )
                    )

                    if departure_minutes <= arrival_minutes:

                        errors.append(
                            f"{place_name}: "
                            f"departure time must "
                            f"be after arrival time"
                        )

                    # ----------------------------------------
                    # ORDER WITH PREVIOUS PLACE
                    # ----------------------------------------

                    if previous_arrival is not None:

                        if arrival_minutes < previous_departure:

                            errors.append(
                                f"Day {day_number}: "
                                f"{place_name} arrives "
                                f"before previous place "
                                f"has departed"
                            )

                    previous_arrival = (
                        arrival_minutes
                    )

                    previous_departure = (
                        departure_minutes
                    )

                except ValueError:

                    errors.append(
                        f"{place_name}: "
                        f"invalid time format"
                    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "valid":
            len(errors) == 0,

        "errors":
            errors,

        "warnings":
            warnings,

        "itinerary":
            itinerary

    }


# ============================================================
# TIME CONVERSION
# ============================================================

def _time_to_minutes(
    value: str
) -> int:

    parts = value.split(":")

    if len(parts) != 2:

        raise ValueError(
            "Invalid time"
        )

    hours = int(
        parts[0]
    )

    minutes = int(
        parts[1]
    )

    if not 0 <= hours <= 23:

        raise ValueError(
            "Invalid hour"
        )

    if not 0 <= minutes <= 59:

        raise ValueError(
            "Invalid minute"
        )

    return (
        hours * 60
        + minutes
    )