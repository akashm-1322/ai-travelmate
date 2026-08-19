from datetime import (
    datetime,
    timedelta,
)


# ============================================================
# OUTDOOR DEFINITIONS
# ============================================================

OUTDOOR_WORDS = {

    "beach",

    "park",

    "garden",

    "marina",

    "promenade",

    "lake",

    "viewpoint",

    "fort",

    "zoo",

    "outdoor",

}


OUTDOOR_CATEGORIES = {

    "beach",

    "park",

    "garden",

    "tourism",

    "attraction",

    "viewpoint",

    "zoo",

    "outdoor",

}


PROTECTED_CATEGORIES = {

    "origin",

    "destination",

}


# ============================================================
# NORMALIZE CATEGORY
# ============================================================

def normalize_category(
    value: str | None
) -> str:

    return (
        value
        or ""
    ).strip().lower()


# ============================================================
# OUTDOOR DETECTION
# ============================================================

def is_outdoor(
    place: dict
) -> bool:

    category = normalize_category(
        place.get(
            "category"
        )
    )


    if (
        category
        in OUTDOOR_CATEGORIES
    ):

        return True


    name = (

        place.get(
            "name",
            ""
        )
        or ""

    ).lower()


    return any(

        word in name

        for word
        in OUTDOOR_WORDS

    )


# ============================================================
# BUILD FORECAST LOOKUP
# ============================================================

def build_forecast_lookup(
    forecast: dict
) -> dict:

    hourly = (
        forecast.get(
            "hourly",
            {}
        )
    )


    times = hourly.get(
        "time",
        []
    )


    rain_probability = (
        hourly.get(
            "precipitation_probability",
            []
        )
    )


    precipitation = (
        hourly.get(
            "precipitation",
            []
        )
    )


    apparent_temperature = (
        hourly.get(
            "apparent_temperature",
            []
        )
    )


    weather_code = (
        hourly.get(
            "weather_code",
            []
        )
    )


    lookup = {}


    for index, time_value in enumerate(
        times
    ):

        try:

            timestamp = (
                datetime.fromisoformat(
                    time_value
                )
            )


            key = (
                timestamp.strftime(
                    "%Y-%m-%d %H"
                )
            )


            lookup[
                key
            ] = {

                "datetime":
                    timestamp.isoformat(),

                "precipitation_probability":
                    (
                        rain_probability[
                            index
                        ]
                        if index <
                        len(
                            rain_probability
                        )
                        else 0
                    ),

                "precipitation":
                    (
                        precipitation[
                            index
                        ]
                        if index <
                        len(
                            precipitation
                        )
                        else 0
                    ),

                "apparent_temperature":
                    (
                        apparent_temperature[
                            index
                        ]
                        if index <
                        len(
                            apparent_temperature
                        )
                        else 0
                    ),

                "weather_code":
                    (
                        weather_code[
                            index
                        ]
                        if index <
                        len(
                            weather_code
                        )
                        else 0
                    ),

            }


        except Exception:

            continue


    return lookup


# ============================================================
# WEATHER RISK SCORE
# ============================================================

def weather_risk_score(
    forecast_hour: dict,
    outdoor: bool
) -> int:

    if not outdoor:

        return 0


    probability = float(

        forecast_hour.get(
            "precipitation_probability",
            0
        )
        or 0

    )


    precipitation = float(

        forecast_hour.get(
            "precipitation",
            0
        )
        or 0

    )


    apparent_temperature = float(

        forecast_hour.get(
            "apparent_temperature",
            0
        )
        or 0

    )


    score = 0


    # --------------------------------------------------------
    # RAIN PROBABILITY
    # --------------------------------------------------------

    if probability >= 80:

        score += 5

    elif probability >= 60:

        score += 4

    elif probability >= 40:

        score += 2

    elif probability >= 25:

        score += 1


    # --------------------------------------------------------
    # ACTUAL PRECIPITATION
    # --------------------------------------------------------

    if precipitation >= 3:

        score += 5

    elif precipitation >= 1:

        score += 3

    elif precipitation > 0.2:

        score += 2


    # --------------------------------------------------------
    # HEAT
    # --------------------------------------------------------

    if apparent_temperature >= 42:

        score += 4

    elif apparent_temperature >= 39:

        score += 3

    elif apparent_temperature >= 36:

        score += 1


    return score


# ============================================================
# FORECAST FOR EXACT ITINERARY TIME
# ============================================================

def get_forecast_for_place(
    day_date: str,
    arrival_time: str,
    lookup: dict
) -> dict:

    if not (
        day_date
        and
        arrival_time
    ):

        return {}


    try:

        timestamp = (
            datetime.fromisoformat(

                f"{day_date}"
                f"T"
                f"{arrival_time}:00"

            )
        )


        key = (
            timestamp.strftime(
                "%Y-%m-%d %H"
            )
        )


        return (
            lookup.get(
                key,
                {}
            )
        )


    except Exception:

        return {}


# ============================================================
# FIND BEST WEATHER HOUR ON SAME DAY
# ============================================================

def find_best_weather_hour(
    day_date: str,
    lookup: dict,
    current_hour: int
) -> dict | None:

    candidates = []


    # --------------------------------------------------------
    # Search useful sightseeing hours only.
    # --------------------------------------------------------

    for hour in range(
        8,
        19
    ):

        key = (
            f"{day_date} "
            f"{hour:02d}"
        )


        forecast_hour = (
            lookup.get(
                key
            )
        )


        if not forecast_hour:

            continue


        risk = (
            weather_risk_score(

                forecast_hour,

                outdoor=True,

            )
        )


        # ----------------------------------------------------
        # Prefer safer weather.
        #
        # If risk is equal, prefer hour closest
        # to existing scheduled hour.
        # ----------------------------------------------------

        distance_from_original = abs(
            hour -
            current_hour
        )


        candidates.append({

            "hour":
                hour,

            "time":
                f"{hour:02d}:00",

            "risk_score":
                risk,

            "distance_from_original":
                distance_from_original,

            "forecast":
                forecast_hour,

        })


    if not candidates:

        return None


    candidates.sort(

        key=lambda item: (

            item[
                "risk_score"
            ],

            item[
                "distance_from_original"
            ],

            item[
                "hour"
            ],

        )

    )


    return candidates[0]


# ============================================================
# FIND BEST EXISTING ITINERARY POSITION
# ============================================================

def find_target_place_index(
    places: list[dict],
    best_hour: int,
    source_index: int
) -> int | None:

    candidates = []


    for index, place in enumerate(
        places
    ):

        if index == source_index:

            continue


        category = normalize_category(
            place.get(
                "category"
            )
        )


        if (
            category
            in PROTECTED_CATEGORIES
        ):

            continue


        arrival_time = (
            place.get(
                "arrival_time"
            )
        )


        if not arrival_time:

            continue


        try:

            place_hour = int(

                arrival_time.split(
                    ":"
                )[0]

            )

        except Exception:

            continue


        candidates.append({

            "index":
                index,

            "hour_difference":
                abs(
                    place_hour -
                    best_hour
                ),

        })


    if not candidates:

        return None


    candidates.sort(

        key=lambda item:
            item[
                "hour_difference"
            ]

    )


    return (
        candidates[0][
            "index"
        ]
    )


# ============================================================
# ANALYZE FORECAST TIMING
# ============================================================

def analyze_forecast_timing(
    itinerary: dict,
    forecast: dict,
    start_date: str
) -> dict:

    lookup = (
        build_forecast_lookup(
            forecast
        )
    )


    days = (
        itinerary.get(
            "days",
            []
        )
    )


    alerts = []


    try:

        trip_start = (
            datetime.fromisoformat(
                start_date
            ).date()
        )

    except Exception:

        raise ValueError(
            "Invalid trip start date."
        )


    # ========================================================
    # EACH DAY
    # ========================================================

    for day_offset, day in enumerate(
        days
    ):

        day_date = (

            trip_start
            +
            timedelta(
                days=day_offset
            )

        ).isoformat()


        places = (
            day.get(
                "places",
                []
            )
        )


        # ====================================================
        # EACH PLACE
        # ====================================================

        for index, place in enumerate(
            places
        ):

            if not is_outdoor(
                place
            ):

                continue


            category = normalize_category(
                place.get(
                    "category"
                )
            )


            if (
                category
                in PROTECTED_CATEGORIES
            ):

                continue


            arrival_time = (
                place.get(
                    "arrival_time"
                )
            )


            if not arrival_time:

                continue


            hour_weather = (
                get_forecast_for_place(

                    day_date,

                    arrival_time,

                    lookup,

                )
            )


            if not hour_weather:

                continue


            current_risk = (
                weather_risk_score(

                    hour_weather,

                    outdoor=True,

                )
            )


            # ------------------------------------------------
            # Only alert meaningfully risky stops.
            # ------------------------------------------------

            if current_risk < 3:

                continue


            try:

                current_hour = int(

                    arrival_time.split(
                        ":"
                    )[0]

                )

            except Exception:

                current_hour = 9


            # ------------------------------------------------
            # Search better hour
            # ------------------------------------------------

            best_hour = (
                find_best_weather_hour(

                    day_date=(
                        day_date
                    ),

                    lookup=(
                        lookup
                    ),

                    current_hour=(
                        current_hour
                    ),

                )
            )


            recommendation = None


            if best_hour:

                improvement = (

                    current_risk

                    -

                    best_hour[
                        "risk_score"
                    ]

                )


                target_index = (
                    find_target_place_index(

                        places=(
                            places
                        ),

                        best_hour=(
                            best_hour[
                                "hour"
                            ]
                        ),

                        source_index=(
                            index
                        ),

                    )
                )


                if (
                    improvement > 0
                    and
                    target_index
                    is not None
                ):

                    recommendation = {

                        "recommended_time":
                            best_hour[
                                "time"
                            ],

                        "recommended_hour":
                            best_hour[
                                "hour"
                            ],

                        "recommended_risk_score":
                            best_hour[
                                "risk_score"
                            ],

                        "risk_improvement":
                            improvement,

                        "target_place_index":
                            target_index,

                        "target_place_name":
                            places[
                                target_index
                            ].get(
                                "name"
                            ),

                        "forecast":
                            best_hour[
                                "forecast"
                            ],

                    }


            # ------------------------------------------------
            # ALERT
            # ------------------------------------------------

            alerts.append({

                "day":
                    day.get(
                        "day"
                    ),

                "date":
                    day_date,

                "place_index":
                    index,

                "place_name":
                    place.get(
                        "name"
                    ),

                "arrival_time":
                    arrival_time,

                "risk_score":
                    current_risk,

                "forecast":
                    hour_weather,

                "smart_timing":
                    recommendation,

            })


    return {

        "success":
            True,

        "alert_count":
            len(
                alerts
            ),

        "has_timing_risks":
            len(
                alerts
            ) > 0,

        "alerts":
            alerts,

    }