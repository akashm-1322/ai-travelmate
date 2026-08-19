import requests


BASE_URL = "http://127.0.0.1:8000"


def separator():
    print("=" * 75)


def main():

    separator()
    print("STEP 35 — LIVE FASTAPI HTTP INTEGRATION TEST")
    separator()

    # ============================================================
    # 1. HEALTH CHECK
    # ============================================================

    print()
    print("1. Checking /health...")

    response = requests.get(
        f"{BASE_URL}/health",
        timeout=30
    )

    assert response.status_code == 200

    health = response.json()

    assert health.get("status") == "healthy"

    print("   ✅ Health endpoint passed")

    # ============================================================
    # 2. ROOT CHECK
    # ============================================================

    print()
    print("2. Checking /...")

    response = requests.get(
        f"{BASE_URL}/",
        timeout=30
    )

    assert response.status_code == 200

    root = response.json()

    assert root.get(
        "message"
    ) == "AI TravelMate API is running"

    print("   ✅ Root endpoint passed")

    # ============================================================
    # 3. BUILD REAL HTTP REQUEST
    # ============================================================

    print()
    print("3. Building real HTTP itinerary request...")

    payload = {

        "city": "Chennai",

        "days": 3,

        "interests":
            "temples, food, beaches",

        "budget":
            "moderate",

        "origin": {

            "name":
                "My Location",

            "latitude":
                13.0827,

            "longitude":
                80.2707,

            "start_time":
                "09:00",

            "category":
                "origin"
        },

        "custom_locations": [

            {

                "name":
                    "My Custom Place",

                "latitude":
                    13.0200,

                "longitude":
                    80.2600,

                "category":
                    "custom_location",

                "visit_duration_minutes":
                    45,

                "opening_hours":
                    "Mo-Su 00:00-23:59",

                "day":
                    3,

                "role":
                    "waypoint"
            }

        ],

        "destination": {

            "name":
                "Chennai Central",

            "latitude":
                13.0827,

            "longitude":
                80.2785,

            "end_time":
                "18:00",

            "category":
                "destination"
        }
    }

    print("   ✅ Request payload created")

    # ============================================================
    # 4. REAL HTTP POST
    # ============================================================

    print()
    print("4. Sending POST /itinerary/...")

    response = requests.post(

        f"{BASE_URL}/itinerary/",

        json=payload,

        timeout=180
    )

    print(
        "   HTTP status:",
        response.status_code
    )

    assert response.status_code == 200

    result = response.json()

    print("   ✅ Real HTTP request completed")

    # ============================================================
    # 5. TOP LEVEL CONTRACT
    # ============================================================

    print()
    print("5. Validating top-level response...")

    assert isinstance(
        result,
        dict
    )

    assert result.get(
        "city"
    ) == "Chennai"

    assert isinstance(
        result.get("days"),
        list
    )

    assert isinstance(
        result.get("time_validation"),
        dict
    )

    assert isinstance(
        result.get("quality_validation"),
        dict
    )

    print("   ✅ Top-level response valid")

    # ============================================================
    # 6. THREE DAYS
    # ============================================================

    print()
    print("6. Validating three days...")

    days = result["days"]

    assert len(days) == 3

    for index, day in enumerate(
        days,
        start=1
    ):

        assert day.get(
            "day"
        ) == index

        assert isinstance(
            day.get("places"),
            list
        )

        assert len(
            day["places"]
        ) > 0

    print("   ✅ Three valid days returned")

    # ============================================================
    # 7. ORIGIN
    # ============================================================

    print()
    print("7. Validating origin...")

    first_day_places = days[0]["places"]

    origin = first_day_places[0]

    assert (
        origin.get("origin") is True
    )

    assert (
        origin.get("name")
        == "My Location"
    )

    assert (
        origin.get("custom_role")
        == "start"
    )

    print("   ✅ Origin exists and is first")

    # ============================================================
    # 8. CUSTOM WAYPOINT
    # ============================================================

    print()
    print("8. Validating custom waypoint...")

    day_3_places = days[2]["places"]

    custom_places = [

        place

        for place in day_3_places

        if place.get("name")
        == "My Custom Place"
    ]

    assert len(custom_places) == 1

    custom = custom_places[0]

    assert (
        custom.get("custom_location")
        is True
    )

    assert (
        custom.get("custom_role")
        == "waypoint"
    )

    print("   ✅ Custom waypoint preserved")

    # ============================================================
    # 9. DESTINATION
    # ============================================================

    print()
    print("9. Validating destination...")

    destination = day_3_places[-1]

    assert (
        destination.get("destination")
        is True
    )

    assert (
        destination.get("name")
        == "Chennai Central"
    )

    assert (
        destination.get("custom_role")
        == "destination"
    )

    print("   ✅ Destination exists and is last")

    # ============================================================
    # 10. PLACE FIELDS
    # ============================================================

    print()
    print("10. Validating route/place fields...")

    total_places = 0

    for day in days:

        for place in day["places"]:

            total_places += 1

            assert place.get(
                "name"
            ) is not None

            assert place.get(
                "latitude"
            ) is not None

            assert place.get(
                "longitude"
            ) is not None

            assert place.get(
                "distance_from_previous_km"
            ) is not None

            assert place.get(
                "travel_time_minutes"
            ) is not None

            assert place.get(
                "visit_duration_minutes"
            ) is not None

            assert place.get(
                "arrival_time"
            ) is not None

            assert place.get(
                "departure_time"
            ) is not None

    print(
        f"   ✅ {total_places} places validated"
    )

    # ============================================================
    # 11. TIME VALIDATION
    # ============================================================

    print()
    print("11. Validating time constraints...")

    time_validation = result[
        "time_validation"
    ]

    assert (
        time_validation.get("valid")
        is True
    )

    assert isinstance(
        time_validation.get("errors"),
        list
    )

    assert isinstance(
        time_validation.get("warnings"),
        list
    )

    print("   ✅ Time validation passed")

    # ============================================================
    # 12. QUALITY VALIDATION
    # ============================================================

    print()
    print("12. Validating quality constraints...")

    quality_validation = result[
        "quality_validation"
    ]

    assert (
        quality_validation.get("valid")
        is True
    )

    assert isinstance(
        quality_validation.get("errors"),
        list
    )

    assert isinstance(
        quality_validation.get("warnings"),
        list
    )

    print("   ✅ Quality validation passed")

    # ============================================================
    # 13. FINAL ITINERARY
    # ============================================================

    print()
    separator()
    print("FINAL LIVE API ITINERARY")
    separator()

    for day in days:

        print()
        print(
            f"DAY {day['day']}"
        )

        for index, place in enumerate(
            day["places"],
            start=1
        ):

            print(
                f"{index}. "
                f"{place.get('name')}"
            )

            print(
                f"   Category: "
                f"{place.get('category')}"
            )

            print(
                f"   Distance: "
                f"{place.get('distance_from_previous_km')} km"
            )

            print(
                f"   Travel: "
                f"{place.get('travel_time_minutes')} min"
            )

            print(
                f"   Visit: "
                f"{place.get('visit_duration_minutes')} min"
            )

            print(
                f"   Arrival: "
                f"{place.get('arrival_time')}"
            )

            print(
                f"   Departure: "
                f"{place.get('departure_time')}"
            )

    # ============================================================
    # 14. FINAL SUMMARY
    # ============================================================

    print()
    separator()
    print("STEP 35 VALIDATION SUMMARY")
    separator()

    print(
        f"City: {result['city']}"
    )

    print(
        f"Days: {len(days)}"
    )

    print(
        f"Total places: {total_places}"
    )

    print(
        "Origin:",
        origin["name"]
    )

    print(
        "Custom waypoint:",
        custom["name"]
    )

    print(
        "Destination:",
        destination["name"]
    )

    print(
        "Time validation:",
        time_validation["valid"]
    )

    print(
        "Quality validation:",
        quality_validation["valid"]
    )

    # ============================================================
    # FINAL RESULT
    # ============================================================

    print()
    separator()

    print(
        "🎉 STEP 35 — LIVE API INTEGRATION TEST PASSED"
    )

    print(
        "The complete AI TravelMate itinerary pipeline "
        "successfully works through real HTTP."
    )

    separator()
    print()


if __name__ == "__main__":

    main()
