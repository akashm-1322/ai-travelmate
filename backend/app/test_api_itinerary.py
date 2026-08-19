import asyncio

from app.api.itinerary import (
    create_itinerary,
    ItineraryRequest,
    CustomLocationRequest,
    OriginRequest,
    DestinationRequest,
)


# ============================================================
# STEP 33 — FASTAPI ITINERARY API INTEGRATION TEST
# ============================================================

async def main():

    print()
    print("=" * 75)
    print("STEP 33 — FASTAPI ITINERARY API INTEGRATION TEST")
    print("=" * 75)

    # ========================================================
    # 1. BUILD REAL API REQUEST
    # ========================================================

    print()
    print("1. Building ItineraryRequest...")

    request = ItineraryRequest(

        city="Chennai",

        days=3,

        interests=(
            "temples, beaches, food, shopping"
        ),

        budget="moderate",

        custom_locations=[

            CustomLocationRequest(

                name="My Custom Place",

                latitude=13.0200,

                longitude=80.2600,

                category="custom_location",

                visit_duration_minutes=45,

                role="waypoint",

                day=3

            )

        ],

        origin=OriginRequest(

            name="My Location",

            latitude=13.0827,

            longitude=80.2707,

            start_time="09:00",

            category="origin"

        ),

        destination=DestinationRequest(

            name="Chennai Central",

            latitude=13.0827,

            longitude=80.2785,

            end_time=None,

            category="destination"

        )

    )

    print(
        "   ✅ ItineraryRequest created"
    )

    # ========================================================
    # 2. CALL ACTUAL API HANDLER
    # ========================================================

    print()
    print("2. Calling create_itinerary()...")

    result = await create_itinerary(
        request
    )

    print(
        "   ✅ create_itinerary() completed"
    )

    # ========================================================
    # 3. BASIC RESPONSE VALIDATION
    # ========================================================

    print()
    print("3. Validating API response...")

    assert isinstance(
        result,
        dict
    )

    assert result.get(
        "city"
    ) == "Chennai"

    assert "days" in result

    assert isinstance(
        result["days"],
        list
    )

    assert len(
        result["days"]
    ) == 3

    print(
        "   ✅ Response structure valid"
    )

    # ========================================================
    # 4. VALIDATE EVERY DAY
    # ========================================================

    print()
    print("4. Validating three days...")

    for day in result["days"]:

        assert "day" in day

        assert "places" in day

        assert isinstance(
            day["places"],
            list
        )

        assert len(
            day["places"]
        ) > 0

    print(
        "   ✅ Three valid days returned"
    )

    # ========================================================
    # 5. ORIGIN CHECK
    # ========================================================

    print()
    print("5. Validating origin...")

    day_1_places = result[
        "days"
    ][0]["places"]

    assert len(
        day_1_places
    ) > 0

    first_place = day_1_places[0]

    origin_valid = (

        first_place.get(
            "origin"
        ) is True

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
    )

    assert origin_valid

    assert first_place.get(
        "name"
    ) == "My Location"

    print(
        "   ✅ Origin exists and is first"
    )

    # ========================================================
    # 6. CUSTOM WAYPOINT CHECK
    # ========================================================

    print()
    print("6. Validating custom waypoint...")

    custom_found = False

    for day in result["days"]:

        for place in day["places"]:

            if place.get(
                "name"
            ) == "My Custom Place":

                custom_found = True

                assert (
                    place.get(
                        "custom_location"
                    )
                    is True
                )

                assert (
                    str(
                        place.get(
                            "custom_role",
                            ""
                        )
                    ).lower()
                    == "waypoint"
                )

    assert custom_found

    print(
        "   ✅ Custom waypoint preserved"
    )

    # ========================================================
    # 7. DESTINATION CHECK
    # ========================================================

    print()
    print("7. Validating destination...")

    last_day_places = result[
        "days"
    ][-1]["places"]

    assert len(
        last_day_places
    ) > 0

    destination = last_day_places[-1]

    destination_valid = (

        destination.get(
            "destination"
        ) is True

        or (

            destination.get(
                "custom_location",
                False
            )

            and str(
                destination.get(
                    "custom_role",
                    ""
                )
            ).lower()
            == "destination"
        )
    )

    assert destination_valid

    assert destination.get(
        "name"
    ) == "Chennai Central"

    print(
        "   ✅ Destination exists and is last"
    )

    # ========================================================
    # 8. TIMING CHECK
    # ========================================================

    print()
    print("8. Validating scheduling...")

    for day in result["days"]:

        for place in day["places"]:

            assert (
                place.get(
                    "arrival_time"
                )
                is not None
            )

            assert (
                place.get(
                    "departure_time"
                )
                is not None
            )

            assert (
                place.get(
                    "travel_time_minutes"
                )
                is not None
            )

            assert (
                place.get(
                    "visit_duration_minutes"
                )
                is not None
            )

    print(
        "   ✅ Arrival/departure/travel/visit times exist"
    )

    # ========================================================
    # 9. DISTANCE CHECK
    # ========================================================

    print()
    print("9. Validating route distances...")

    for day in result["days"]:

        for index, place in enumerate(
            day["places"]
        ):

            assert (
                place.get(
                    "distance_from_previous_km"
                )
                is not None
            )

            if index > 0:

                assert (
                    place.get(
                        "distance_from_previous_km"
                    )
                    >= 0
                )

    print(
        "   ✅ Route distances exist"
    )

    # ========================================================
    # 10. QUALITY VALIDATION
    # ========================================================

    print()
    print("10. Validating quality result...")

    quality = result.get(
        "quality_validation"
    )

    if quality is not None:

        assert isinstance(
            quality,
            dict
        )

        assert (
            quality.get(
                "valid"
            )
            is True
        )

        print(
            "   ✅ Quality validation passed"
        )

    else:

        print(
            "   ℹ️ Quality validation not exposed in response"
        )

    # ========================================================
    # 11. TIME VALIDATION
    # ========================================================

    print()
    print("11. Validating time constraints...")

    time_validation = result.get(
        "time_validation"
    )

    assert isinstance(
        time_validation,
        dict
    )

    assert (
        time_validation.get(
            "valid"
        )
        is True
    )

    assert isinstance(
        time_validation.get(
            "errors",
            []
        ),
        list
    )

    assert isinstance(
        time_validation.get(
            "warnings",
            []
        ),
        list
    )

    print(
        "   ✅ Time validation passed"
    )

    # ========================================================
    # 12. PRINT FINAL API RESULT
    # ========================================================

    print()
    print("=" * 75)
    print("FINAL API ITINERARY")
    print("=" * 75)

    for day in result["days"]:

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

    # ========================================================
    # 13. FINAL RESULT
    # ========================================================

    print()
    print("=" * 75)
    print("STEP 33 TEST EXECUTION COMPLETE")
    print("=" * 75)

    print()
    print("🎯 API PIPELINE CHECKS")

    print(
        "✅ FastAPI request accepted"
    )

    print(
        "✅ Itinerary generation completed"
    )

    print(
        "✅ Place resolution completed"
    )

    print(
        "✅ Custom waypoint preserved"
    )

    print(
        "✅ Origin preserved"
    )

    print(
        "✅ Destination preserved"
    )

    print(
        "✅ Route optimization completed"
    )

    print(
        "✅ Destination distance available"
    )

    print(
        "✅ Daily scheduling completed"
    )

    print(
        "✅ Arrival/departure times available"
    )

    print(
        "✅ Route distances available"
    )

    print(
        "✅ Time validation passed"
    )

    print()
    print(
        "🎉 STEP 33 — FASTAPI API INTEGRATION TEST PASSED"
    )

    print("=" * 75)


if __name__ == "__main__":

    asyncio.run(
        main()
    )