from app.services.route_optimizer import optimize_itinerary
from app.services.daily_scheduler import schedule_itinerary


def print_separator():
    print("=" * 75)


def main():

    # ============================================================
    # STEP 25 — END-TO-END ITINERARY TEST
    # ============================================================

    itinerary = {

        "city": "Chennai",

        "days": [

            {
                "day": 1,

                "start_time": "09:00",

                "places": [

                    {
                        "name": "Start Point",
                        "category": "hotel",

                        "latitude": 13.0827,
                        "longitude": 80.2707,

                        "origin": True,
                        "custom_location": True,
                        "custom_role": "start",

                        "preferred_start_time": "09:00",

                        "opening_hours":
                            "Mo-Su 00:00-23:59"
                    },

                    {
                        "name": "Marina Beach",
                        "category": "beach",

                        "latitude": 13.0500,
                        "longitude": 80.2824,

                        "opening_hours":
                            "Mo-Su 00:00-23:59"
                    },

                    {
                        "name": "Government Museum",
                        "category": "museum",

                        "latitude": 13.0694,
                        "longitude": 80.2574,

                        "opening_hours":
                            "Mo-Su 09:30-17:30"
                    },

                    {
                        "name": "Kapaleeshwarar Temple",
                        "category": "place_of_worship",

                        "latitude": 13.0339,
                        "longitude": 80.2695,

                        "opening_hours":
                            "Mo-Su 06:00-12:00"
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

                        "opening_hours":
                            "Mo-Su 00:00-23:59"
                    }

                ]
            }
        ]
    }

    # ============================================================
    # 1. OPTIMIZE ITINERARY
    # ============================================================

    print()
    print_separator()
    print("STEP 25 — ROUTE + SCHEDULER INTEGRATION TEST")
    print_separator()

    print()
    print("1. Running route optimizer...")

    optimized = optimize_itinerary(
        itinerary
    )

    print("   ✅ Route optimization completed")

    # ============================================================
    # SHOW OPTIMIZED ROUTE
    # ============================================================

    optimized_day = optimized["days"][0]

    print()
    print_separator()
    print("OPTIMIZED ROUTE")
    print_separator()

    for index, place in enumerate(
        optimized_day["places"],
        start=1
    ):

        print(
            f'{index}. {place["name"]}'
        )

    print()

    print(
        "Optimized distance:",
        optimized_day["total_distance_km"],
        "km"
    )

    # ============================================================
    # 2. SEND OPTIMIZED ROUTE TO SCHEDULER
    # ============================================================

    print()
    print("2. Running daily scheduler...")

    scheduled = schedule_itinerary(
        optimized,
        start_time="09:00"
    )

    print(
        "   ✅ Daily scheduler completed"
    )

    # ============================================================
    # 3. DISPLAY FINAL SCHEDULE
    # ============================================================

    scheduled_day = scheduled["days"][0]

    print()
    print_separator()
    print("FINAL SCHEDULE")
    print_separator()

    for index, place in enumerate(
        scheduled_day["places"],
        start=1
    ):

        print()
        print(
            f'{index}. {place["name"]}'
        )

        print(
            f'   Distance: '
            f'{place.get("distance_from_previous_km", 0):.2f} km'
        )

        print(
            f'   Travel: '
            f'{place.get("travel_time_minutes", 0)} minutes'
        )

        print(
            f'   Visit: '
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

    # ============================================================
    # 4. VALIDATION
    # ============================================================

    validation = scheduled[
        "time_validation"
    ]

    print()
    print_separator()
    print("FINAL VALIDATION")
    print_separator()

    print()

    print(
        "Validation:",
        validation["valid"]
    )

    print(
        "Total distance:",
        scheduled_day["total_distance_km"],
        "km"
    )

    print(
        "Start time:",
        scheduled_day["start_time"]
    )

    print(
        "End time:",
        scheduled_day["end_time"]
    )

    # ============================================================
    # ERRORS
    # ============================================================

    print()
    print("Errors:")

    if validation["errors"]:

        for error in validation["errors"]:

            print(
                "  ❌",
                error
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
                "  ⚠️",
                warning
            )

    else:

        print(
            "  ✅ No warnings"
        )

    # ============================================================
    # 5. AUTOMATIC CHECKS
    # ============================================================

    print()
    print_separator()
    print("AUTOMATIC INTEGRATION CHECKS")
    print_separator()

    final_places = scheduled_day[
        "places"
    ]

    # ------------------------------------------------------------
    # Check 1
    # ------------------------------------------------------------

    if final_places:

        print(
            "✅ Final itinerary contains places"
        )

    else:

        print(
            "❌ Final itinerary is empty"
        )

    # ------------------------------------------------------------
    # Check 2 — Origin
    # ------------------------------------------------------------

    first = final_places[0]

    origin_valid = (

        first.get("origin") is True

        or (

            first.get(
                "custom_location",
                False
            )

            and str(
                first.get(
                    "custom_role",
                    ""
                )
            ).lower()
            == "start"
        )
    )

    if origin_valid:

        print(
            "✅ Origin preserved as first location"
        )

    else:

        print(
            "❌ Origin was not preserved"
        )

    # ------------------------------------------------------------
    # Check 3 — Destination
    # ------------------------------------------------------------

    last = final_places[-1]

    destination_valid = (

        last.get("destination") is True

        or (

            last.get(
                "custom_location",
                False
            )

            and str(
                last.get(
                    "custom_role",
                    ""
                )
            ).lower()
            == "destination"
        )
    )

    if destination_valid:

        print(
            "✅ Destination preserved as last location"
        )

    else:

        print(
            "❌ Destination was not preserved"
        )

    # ------------------------------------------------------------
    # Check 4 — Timing
    # ------------------------------------------------------------

    timing_valid = True

    for place in final_places:

        if not place.get("arrival_time"):

            timing_valid = False

        if not place.get("departure_time"):

            timing_valid = False

    if timing_valid:

        print(
            "✅ Arrival/departure times generated"
        )

    else:

        print(
            "❌ Missing arrival/departure times"
        )

    # ------------------------------------------------------------
    # Check 5 — Distances
    # ------------------------------------------------------------

    distances_valid = True

    for index, place in enumerate(
        final_places
    ):

        distance = place.get(
            "distance_from_previous_km"
        )

        if distance is None:

            distances_valid = False

        if index > 0 and distance <= 0:

            distances_valid = False

    if distances_valid:

        print(
            "✅ Distances calculated for complete route"
        )

    else:

        print(
            "❌ Distance calculation problem"
        )

    # ============================================================
    # FINAL RESULT
    # ============================================================

    print()
    print_separator()

    all_passed = (

        bool(final_places)

        and origin_valid

        and destination_valid

        and timing_valid

        and distances_valid

        and validation["valid"]
    )

    if all_passed:

        print(
            "🎉 STEP 25 PASSED"
        )

        print()
        print(
            "Route Optimizer + Daily Scheduler "
            "are successfully integrated."
        )

    else:

        print(
            "⚠️ STEP 25 HAS ISSUES"
        )

        print()
        print(
            "Review the errors above before continuing."
        )

    print_separator()
    print()


if __name__ == "__main__":

    main()