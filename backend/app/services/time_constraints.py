from typing import Dict, Any, List
from datetime import datetime, timedelta


TIME_FORMAT = "%H:%M"


def time_to_minutes(value: str) -> int:
    """
    Convert HH:MM into minutes from midnight.
    """

    hours, minutes = map(int, value.split(":"))

    return hours * 60 + minutes


def minutes_to_time(minutes: int) -> str:
    """
    Convert minutes from midnight into HH:MM.
    """

    minutes = minutes % (24 * 60)

    hours = minutes // 60
    mins = minutes % 60

    return f"{hours:02d}:{mins:02d}"


def add_minutes(
    time_value: str,
    minutes: int
) -> str:

    total = (
        time_to_minutes(time_value)
        + minutes
    )

    return minutes_to_time(total)


def calculate_day_end_time(
    places: List[Dict[str, Any]]
) -> str | None:

    if not places:
        return None

    last_place = places[-1]

    return last_place.get(
        "departure_time"
    ) or last_place.get(
        "arrival_time"
    )


def validate_time_constraints(
    itinerary: Dict[str, Any]
) -> Dict[str, Any]:

    errors = []
    warnings = []

    for day in itinerary.get("days", []):

        places = day.get("places", [])

        if not places:
            continue

        # ----------------------------------------------------
        # CHECK ORIGIN
        # ----------------------------------------------------

        origin = places[0]

        if origin.get("origin"):

            preferred_start = (
                origin.get(
                    "preferred_start_time"
                )
            )

            actual_start = (
                origin.get(
                    "departure_time"
                )
                or origin.get(
                    "arrival_time"
                )
            )

            if (
                preferred_start
                and actual_start
            ):

                if (
                    time_to_minutes(actual_start)
                    < time_to_minutes(preferred_start)
                ):

                    warnings.append(
                        f"Day {day.get('day')}: "
                        f"route starts before preferred "
                        f"start time "
                        f"{preferred_start}"
                    )

        # ----------------------------------------------------
        # CHECK DESTINATION
        # ----------------------------------------------------

        destination = places[-1]

        if destination.get("destination"):

            preferred_end = (
                destination.get(
                    "preferred_end_time"
                )
            )

            arrival_time = (
                destination.get(
                    "arrival_time"
                )
            )

            if (
                preferred_end
                and arrival_time
            ):

                arrival_minutes = (
                    time_to_minutes(
                        arrival_time
                    )
                )

                deadline_minutes = (
                    time_to_minutes(
                        preferred_end
                    )
                )

                if arrival_minutes > deadline_minutes:

                    errors.append(
                        f"Day {day.get('day')}: "
                        f"destination deadline missed. "
                        f"Arrival {arrival_time}, "
                        f"required by {preferred_end}"
                    )

                else:

                    waiting_minutes = (
                        deadline_minutes
                        - arrival_minutes
                    )

                    if waiting_minutes > 0:

                        destination[
                            "available_before_deadline_minutes"
                        ] = waiting_minutes

        # ----------------------------------------------------
        # CHECK CHRONOLOGY
        # ----------------------------------------------------

        previous_departure = None

        for place in places:

            arrival = place.get(
                "arrival_time"
            )

            departure = place.get(
                "departure_time"
            )

            if (
                arrival
                and departure
            ):

                arrival_minutes = (
                    time_to_minutes(arrival)
                )

                departure_minutes = (
                    time_to_minutes(departure)
                )

                if (
                    departure_minutes
                    < arrival_minutes
                ):

                    errors.append(
                        f"Day {day.get('day')}: "
                        f"{place.get('name')} has "
                        f"departure before arrival."
                    )

            if (
                previous_departure
                and arrival
            ):

                if (
                    time_to_minutes(arrival)
                    < time_to_minutes(
                        previous_departure
                    )
                ):

                    errors.append(
                        f"Day {day.get('day')}: "
                        f"{place.get('name')} has "
                        f"invalid chronological order."
                    )

            if departure:
                previous_departure = departure

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }