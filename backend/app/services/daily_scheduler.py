from datetime import datetime, timedelta
from typing import Any, Dict, List


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
# GET VISIT DURATION
# ============================================================

def get_visit_duration(place: Dict[str, Any]) -> int:

    category = str(
        place.get("category", "")
    ).lower()

    return DEFAULT_VISIT_DURATION.get(
        category,
        60
    )


# ============================================================
# CALCULATE TRAVEL TIME
# ============================================================

def calculate_travel_time(
    distance_km: float
) -> int:

    if distance_km <= 0:
        return 0

    hours = distance_km / AVERAGE_SPEED_KMPH

    minutes = hours * 60

    return max(
        5,
        round(minutes)
    )


# ============================================================
# PARSE OPENING HOUR
# ============================================================

def get_opening_time(
    opening_hours: Any
) -> str:

    if not opening_hours:
        return "09:00"

    opening_hours = str(
        opening_hours
    )

    # Example:
    # Mo-Su 10:00-13:00

    if " " in opening_hours:

        time_part = (
            opening_hours
            .split(" ", 1)[1]
        )

        if "-" in time_part:

            return (
                time_part
                .split("-", 1)[0]
            )

    return "09:00"


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
# SCHEDULE ONE DAY
# ============================================================

def schedule_day(
    places: List[Dict[str, Any]],
    start_time: str = "09:00"
) -> Dict[str, Any]:

    current_time = parse_time(
        start_time
    )

    scheduled_places = []

    total_distance = 0

    for index, place in enumerate(places):

        # ----------------------------------------------------
        # Distance from previous location
        # ----------------------------------------------------

        distance = float(
            place.get(
                "distance_from_previous_km",
                0
            ) or 0
        )

        # ----------------------------------------------------
        # Travel time
        # ----------------------------------------------------

        travel_minutes = calculate_travel_time(
            distance
        )

        current_time += timedelta(
            minutes=travel_minutes
        )

        # ----------------------------------------------------
        # Opening time
        # ----------------------------------------------------

        opening_time = get_opening_time(
            place.get(
                "opening_hours"
            )
        )

        opening_datetime = parse_time(
            opening_time
        )

        # ----------------------------------------------------
        # Wait if place hasn't opened
        # ----------------------------------------------------

        if current_time < opening_datetime:

            current_time = opening_datetime

        # ----------------------------------------------------
        # Arrival
        # ----------------------------------------------------

        arrival_time = current_time

        # ----------------------------------------------------
        # Visit duration
        # ----------------------------------------------------

        visit_duration = get_visit_duration(
            place
        )

        departure_time = (
            arrival_time
            + timedelta(
                minutes=visit_duration
            )
        )

        # ----------------------------------------------------
        # Store scheduled place
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
        # Update current time
        # ----------------------------------------------------

        current_time = departure_time

        total_distance += distance

    return {

        "places": scheduled_places,

        "total_distance_km":
            round(
                total_distance,
                2
            ),

        "start_time":
            start_time,

        "end_time":
            format_time(
                current_time
            ),

    }


# ============================================================
# SCHEDULE COMPLETE ITINERARY
# ============================================================

def schedule_itinerary(
    itinerary: Dict[str, Any],
    start_time: str = "09:00"
) -> Dict[str, Any]:

    scheduled_days = []

    for day in itinerary.get(
        "days",
        []
    ):

        scheduled_day_result = schedule_day(
            day.get(
                "places",
                []
            ),
            start_time
        )

        scheduled_days.append({

            "day":
                day.get("day"),

            "places":
                scheduled_day_result[
                    "places"
                ],

            "total_distance_km":
                scheduled_day_result[
                    "total_distance_km"
                ],

            "start_time":
                scheduled_day_result[
                    "start_time"
                ],

            "end_time":
                scheduled_day_result[
                    "end_time"
                ],

        })

    return {

        "city":
            itinerary.get("city"),

        "days":
            scheduled_days

    }