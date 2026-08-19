from app.services.daily_scheduler import schedule_day


def print_separator():
    print("=" * 70)


def main():

    # ============================================================
    # TEST DATA
    # ============================================================
    #
    # Route:
    #
    # Start Point
    #      ↓
    # Government Museum
    #      ↓
    # Kapaleeshwarar Temple
    #      ↓
    # Marina Beach
    #      ↓
    # Hotel
    #
    # Distances are intentionally supplied so that
    # daily_scheduler can recalculate them from coordinates.
    #
    # ============================================================

    places = [

        {
            "name": "Start Point",
            "category": "hotel",

            "latitude": 13.0827,
            "longitude": 80.2707,

            "origin": True,
            "custom_location": True,
            "custom_role": "start",

            "preferred_start_time": "09:00",

            "opening_hours": "Mo-Su 00:00-23:59"
        },

        {
            "name": "Government Museum",
            "category": "museum",

            "latitude": 13.0694,
            "longitude": 80.2574,

            "opening_hours": "Mo-Su 09:30-17:30"
        },

        {
            "name": "Kapaleeshwarar Temple",
            "category": "place_of_worship",

            "latitude": 13.0339,
            "longitude": 80.2695,

            "opening_hours": "Mo-Su 06:00-12:00"
        },

        {
            "name": "Marina Beach",
            "category": "beach",

            "latitude": 13.0500,
            "longitude": 80.2824,

            "opening_hours": "Mo-Su 00:00-23:59"
        },

        {
            "name": "Hotel",
            "category": "hotel",

            "latitude": 13.0827,
            "longitude": 80.2707,

            "destination": True,
            "custom_location": True,
            "custom_role": "destination",

            "preferred_end_time": "18:00",

            "opening_hours": "Mo-Su 00:00-23:59"
        }

    ]

    # ============================================================
    # RUN SCHEDULER
    # ============================================================

    result = schedule_day(
        places,
        start_time="09:00"
    )

    # ============================================================
    # BASIC RESULT
    # ============================================================

    print()
    print_separator()
    print("             DAILY SCHEDULER TEST")
    print_separator()

    print()
    print("Start Time:")
    print(result["start_time"])

    print()
    print("End Time:")
    print(result["end_time"])

    print()
    print("Total Distance:")
    print(
        f'{result["total_distance_km"]:.2f} km'
    )

    # ============================================================
    # SCHEDULED ROUTE
    # ============================================================

    print()
    print_separator()
    print("             SCHEDULED ROUTE")
    print_separator()

    for index, place in enumerate(
        result["places"],
        start=1
    ):

        print()
        print(
            f'{index}. {place["name"]}'
        )

        print(
            f'   Distance from previous: '
            f'{place.get("distance_from_previous_km", 0):.2f} km'
        )

        print(
            f'   Travel time: '
            f'{place.get("travel_time_minutes", 0)} minutes'
        )

        print(
            f'   Visit duration: '
            f'{place.get("visit_duration_minutes", 0)} minutes'
        )

        print(
            f'   Arrival: '
            f'{place.get("arrival_time", "N/A")}'
        )

        print(
            f'   Departure: '
            f'{place.get("departure_time", "N/A")}'
        )

        print(
            f'   Opening hours: '
            f'{place.get("opening_hours", "N/A")}'
        )

    # ============================================================
    # TIME VALIDATION
    # ============================================================

    validation = result[
        "time_validation"
    ]

    print()
    print_separator()
    print("             TIME VALIDATION")
    print_separator()

    print()
    print(
        "Valid:",
        validation["valid"]
    )

    # ============================================================
    # ERRORS
    # ============================================================

    print()
    print("Errors:")

    if validation["errors"]:

        for error in validation["errors"]:

            print(
                f"  ❌ {error}"
            )

    else:

        print(
            "  ✅ No errors"
        )

    # ============================================================
    # WARNINGS
    # ============================================================

    print()
    print("Warnings:")

    if validation["warnings"]:

        for warning in validation["warnings"]:

            print(
                f"  ⚠️ {warning}"
            )

    else:

        print(
            "  ✅ No warnings"
        )

    # ============================================================
    # FINAL CHECKS
    # ============================================================

    print()
    print_separator()
    print("             AUTOMATIC CHECKS")
    print_separator()

    scheduled_places = result[
        "places"
    ]

    # ------------------------------------------------------------
    # Check 1: Route exists
    # ------------------------------------------------------------

    if scheduled_places:

        print(
            "✅ Route contains scheduled places"
        )

    else:

        print(
            "❌ Route contains no places"
        )

    # ------------------------------------------------------------
    # Check 2: Origin first
    # ------------------------------------------------------------

    first_place = scheduled_places[0]

    if (
        first_place.get("origin") is True
        or (
            first_place.get(
                "custom_location",
                False
            )
            and str(
                first_place.get(
                    "custom_role",
                    ""
                )
            ).lower()
            == "start"
        )
    ):

        print(
            "✅ Origin is first"
        )

    else:

        print(
            "❌ Origin is NOT first"
        )

    # ------------------------------------------------------------
    # Check 3: Destination last
    # ------------------------------------------------------------

    last_place = scheduled_places[-1]

    if (
        last_place.get("destination") is True
        or (
            last_place.get(
                "custom_location",
                False
            )
            and str(
                last_place.get(
                    "custom_role",
                    ""
                )
            ).lower()
            == "destination"
        )
    ):

        print(
            "✅ Destination is last"
        )

    else:

        print(
            "❌ Destination is NOT last"
        )

    # ------------------------------------------------------------
    # Check 4: Every place has arrival/departure
    # ------------------------------------------------------------

    timing_valid = True

    for place in scheduled_places:

        if (
            not place.get("arrival_time")
            or not place.get("departure_time")
        ):

            timing_valid = False

            print(
                f'❌ Missing timing for '
                f'{place.get("name", "Unknown")}'
            )

    if timing_valid:

        print(
            "✅ Arrival/departure times generated for all places"
        )

    # ------------------------------------------------------------
    # Check 5: Distance is calculated
    # ------------------------------------------------------------

    distance_valid = True

    for index, place in enumerate(
        scheduled_places
    ):

        distance = place.get(
            "distance_from_previous_km"
        )

        if distance is None:

            distance_valid = False

            print(
                f'❌ Missing distance for '
                f'{place.get("name", "Unknown")}'
            )

        elif index > 0 and distance <= 0:

            distance_valid = False

            print(
                f'❌ Invalid distance for '
                f'{place.get("name", "Unknown")}'
            )

    if distance_valid:

        print(
            "✅ Route distances calculated"
        )

    # ============================================================
    # FINAL RESULT
    # ============================================================

    print()
    print_separator()

    if validation["valid"]:

        print(
            "🎉 DAILY SCHEDULER TEST PASSED"
        )

    else:

        print(
            "⚠️ DAILY SCHEDULER COMPLETED WITH VALIDATION ISSUES"
        )

    print_separator()
    print()


if __name__ == "__main__":

    main()