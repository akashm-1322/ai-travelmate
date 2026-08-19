from typing import Any
from datetime import datetime, timedelta
from math import (
    asin,
    cos,
    radians,
    sin,
    sqrt,
)


# ============================================================
# CATEGORY GROUPS
# ============================================================

OUTDOOR_CATEGORIES = {
    "park",
    "beach",
    "attraction",
    "tourism",
    "viewpoint",
    "garden",
    "zoo",
    "outdoor",
}


INDOOR_CATEGORIES = {
    "museum",
    "shopping",
    "mall",
    "restaurant",
    "cafe",
    "place_of_worship",
    "cinema",
    "gallery",
}


# ============================================================
# WEATHER HELPERS
# ============================================================

def weather_risk(
    weather: dict
) -> dict:

    precipitation = float(
        weather.get(
            "precipitation_mm",
            0
        )
        or 0
    )

    feels_like = float(
        weather.get(
            "feels_like_c",
            0
        )
        or 0
    )

    weather_code = int(
        weather.get(
            "weather_code",
            0
        )
        or 0
    )


    rain_risk = (
        precipitation > 0.2
        or weather_code
        in {
            51, 53, 55,
            56, 57,
            61, 63, 65,
            66, 67,
            80, 81, 82,
            95, 96, 99,
        }
    )


    heat_risk = (
        feels_like >= 30
    )


    return {
        "rain_risk":
            rain_risk,

        "heat_risk":
            heat_risk,

        "precipitation_mm":
            precipitation,

        "feels_like_c":
            feels_like,

        "weather_code":
            weather_code,
    }


# ============================================================
# CATEGORY NORMALIZATION
# ============================================================

def normalize_category(
    category: str | None
) -> str:

    return (
        category
        or ""
    ).strip().lower()


# ============================================================
# IS OUTDOOR
# ============================================================

def is_outdoor_place(
    place: dict
) -> bool:

    category = normalize_category(
        place.get(
            "category"
        )
    )


    if category in OUTDOOR_CATEGORIES:

        return True


    name = (
        place.get(
            "name",
            ""
        )
        or ""
    ).lower()


    outdoor_words = [
        "beach",
        "park",
        "garden",
        "marina",
        "promenade",
        "lake",
        "viewpoint",
        "fort",
        "zoo",
    ]


    return any(
        word in name
        for word
        in outdoor_words
    )


# ============================================================
# FIND INDOOR ALTERNATIVE
# ============================================================

def find_indoor_alternative(
    places: list[dict],
    current_place: dict
) -> dict | None:

    for candidate in places:

        if (
            candidate
            is current_place
        ):
            continue


        category = normalize_category(
            candidate.get(
                "category"
            )
        )


        if (
            category
            in INDOOR_CATEGORIES
        ):

            return candidate


    return None


# ============================================================
# ANALYZE ITINERARY
# ============================================================

def analyze_itinerary_disruptions(
    itinerary: dict,
    weather: dict
) -> dict:

    risk = weather_risk(
        weather
    )


    disruptions = []


    days = itinerary.get(
        "days",
        []
    )


    for day in days:

        day_number = day.get(
            "day"
        )


        places = day.get(
            "places",
            []
        )


        for index, place in enumerate(
            places
        ):

            # --------------------------------------------
            # Skip origin/destination
            # --------------------------------------------

            category = normalize_category(
                place.get(
                    "category"
                )
            )


            if category in {
                "origin",
                "destination",
            }:

                continue


            if not is_outdoor_place(
                place
            ):

                continue


            reasons = []


            if risk["rain_risk"]:

                reasons.append(
                    "Current weather indicates rain or precipitation risk."
                )


            if risk["heat_risk"]:

                reasons.append(
                    "The apparent temperature is high for prolonged outdoor activity."
                )


            if not reasons:

                continue


            alternative = (
                find_indoor_alternative(
                    places,
                    place
                )
            )


            disruption = {

                "day":
                    day_number,

                "place_index":
                    index,

                "place_name":
                    place.get(
                        "name",
                        "Unknown place"
                    ),

                "category":
                    category,

                "severity":
                    (
                        "high"
                        if (
                            risk["rain_risk"]
                            and
                            risk["heat_risk"]
                        )
                        else "medium"
                    ),

                "reasons":
                    reasons,

                "suggested_action":
                    (
                        "swap"
                        if alternative
                        else "reschedule"
                    ),

                "suggested_alternative": (
    {
        "name":
            alternative.get(
                "name"
            ),

        "category":
            alternative.get(
                "category"
            ),

        "latitude":
            alternative.get(
                "latitude"
            ),

        "longitude":
            alternative.get(
                "longitude"
            ),

        "place_index":
            places.index(
                alternative
            ),
    }
    if alternative
    else None
),

            }


            disruptions.append(
                disruption
            )


    return {

        "weather": {
            "location":
                weather.get(
                    "location"
                ),

            "temperature_c":
                weather.get(
                    "temperature_c"
                ),

            "feels_like_c":
                weather.get(
                    "feels_like_c"
                ),

            "precipitation_mm":
                weather.get(
                    "precipitation_mm"
                ),

            "weather_code":
                weather.get(
                    "weather_code"
                ),
        },

        "risk": risk,

        "has_disruptions":
            len(
                disruptions
            ) > 0,

        "disruption_count":
            len(
                disruptions
            ),

        "disruptions":
            disruptions,

    }

# ============================================================
# DISTANCE
# ============================================================

def calculate_distance_km(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float
) -> float:

    radius_km = 6371.0

    lat1 = radians(
        latitude_1
    )

    lon1 = radians(
        longitude_1
    )

    lat2 = radians(
        latitude_2
    )

    lon2 = radians(
        longitude_2
    )


    delta_lat = (
        lat2 - lat1
    )

    delta_lon = (
        lon2 - lon1
    )


    value = (

        sin(
            delta_lat / 2
        ) ** 2

        +

        cos(lat1)
        *
        cos(lat2)
        *
        sin(
            delta_lon / 2
        ) ** 2

    )


    central_angle = (
        2
        *
        asin(
            sqrt(value)
        )
    )


    return round(
        radius_km
        *
        central_angle,
        2
    )


# ============================================================
# ESTIMATE TRAVEL TIME
# ============================================================

def estimate_travel_minutes(
    distance_km: float
) -> int:

    if distance_km <= 0:

        return 0


    # Conservative urban-city average.

    average_speed_kmh = 25


    minutes = round(

        (
            distance_km
            /
            average_speed_kmh
        )
        *
        60

    )


    return max(
        5,
        minutes
    )


# ============================================================
# TIME HELPERS
# ============================================================

def parse_clock_time(
    value: str
) -> datetime:

    try:

        return datetime.strptime(
            value,
            "%H:%M"
        )

    except Exception:

        return datetime.strptime(
            "09:00",
            "%H:%M"
        )


def format_clock_time(
    value: datetime
) -> str:

    return value.strftime(
        "%H:%M"
    )


# ============================================================
# RECALCULATE ONE DAY
# ============================================================

def recalculate_day(
    day: dict
) -> dict:

    places = day.get(
        "places",
        []
    )


    if not places:

        return day


    # --------------------------------------------------------
    # Determine day start time
    # --------------------------------------------------------

    start_time = (
        day.get(
            "start_time"
        )
        or
        places[0].get(
            "arrival_time"
        )
        or
        places[0].get(
            "preferred_start_time"
        )
        or
        "09:00"
    )


    current_time = (
        parse_clock_time(
            start_time
        )
    )


    total_distance = 0.0


    # ========================================================
    # FIRST PLACE
    # ========================================================

    first_place = places[0]


    first_place[
        "distance_from_previous_km"
    ] = 0.0


    first_place[
        "travel_time_minutes"
    ] = 0


    first_place[
        "arrival_time"
    ] = format_clock_time(
        current_time
    )


    visit_minutes = int(
        first_place.get(
            "visit_duration_minutes",
            0
        )
        or 0
    )


    current_time += timedelta(
        minutes=visit_minutes
    )


    first_place[
        "departure_time"
    ] = format_clock_time(
        current_time
    )


    # ========================================================
    # REMAINING PLACES
    # ========================================================

    for index in range(
        1,
        len(places)
    ):

        previous_place = (
            places[
                index - 1
            ]
        )

        current_place = (
            places[
                index
            ]
        )


        try:

            distance = (
                calculate_distance_km(

                    float(
                        previous_place[
                            "latitude"
                        ]
                    ),

                    float(
                        previous_place[
                            "longitude"
                        ]
                    ),

                    float(
                        current_place[
                            "latitude"
                        ]
                    ),

                    float(
                        current_place[
                            "longitude"
                        ]
                    ),

                )
            )

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            distance = 0.0


        travel_minutes = (
            estimate_travel_minutes(
                distance
            )
        )


        total_distance += (
            distance
        )


        current_place[
            "distance_from_previous_km"
        ] = distance


        current_place[
            "travel_time_minutes"
        ] = travel_minutes


        current_time += timedelta(
            minutes=travel_minutes
        )


        current_place[
            "arrival_time"
        ] = format_clock_time(
            current_time
        )


        visit_minutes = int(
            current_place.get(
                "visit_duration_minutes",
                0
            )
            or 0
        )


        current_time += timedelta(
            minutes=visit_minutes
        )


        current_place[
            "departure_time"
        ] = format_clock_time(
            current_time
        )


    # ========================================================
    # DAY SUMMARY
    # ========================================================

    day[
        "places"
    ] = places


    day[
        "total_distance_km"
    ] = round(
        total_distance,
        2
    )


    day[
        "start_time"
    ] = start_time


    day[
        "end_time"
    ] = format_clock_time(
        current_time
    )


    return day


# ============================================================
# APPLY WEATHER-AWARE SWAP
# ============================================================

def apply_disruption_swap(
    itinerary: dict,
    day_number: int,
    from_index: int,
    to_index: int
) -> dict:

    days = itinerary.get(
        "days",
        []
    )


    target_day = None


    for day in days:

        if (
            day.get(
                "day"
            )
            ==
            day_number
        ):

            target_day = day

            break


    if target_day is None:

        raise ValueError(
            f"Day {day_number} does not exist."
        )


    places = target_day.get(
        "places",
        []
    )


    if (
        from_index < 0
        or
        from_index >= len(
            places
        )
    ):

        raise ValueError(
            "Invalid source place index."
        )


    if (
        to_index < 0
        or
        to_index >= len(
            places
        )
    ):

        raise ValueError(
            "Invalid target place index."
        )


    # --------------------------------------------------------
    # Protect origin / destination
    # --------------------------------------------------------

    source_category = (
        places[
            from_index
        ]
        .get(
            "category",
            ""
        )
        .lower()
    )


    target_category = (
        places[
            to_index
        ]
        .get(
            "category",
            ""
        )
        .lower()
    )


    protected_categories = {
        "origin",
        "destination",
    }


    if (
        source_category
        in protected_categories
        or
        target_category
        in protected_categories
    ):

        raise ValueError(
            "Origin and destination cannot be reordered."
        )


    # --------------------------------------------------------
    # Swap places
    # --------------------------------------------------------

    places[
        from_index
    ], places[
        to_index
    ] = (

        places[
            to_index
        ],

        places[
            from_index
        ],

    )


    target_day[
        "places"
    ] = places


    # --------------------------------------------------------
    # Recalculate route + schedule
    # --------------------------------------------------------

    recalculate_day(
        target_day
    )


    itinerary[
        "days"
    ] = days


    return itinerary