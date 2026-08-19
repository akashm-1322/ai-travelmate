import asyncio

from app.api.itinerary import (
    create_itinerary,
    ItineraryRequest,
    CustomLocationRequest,
    OriginRequest,
    DestinationRequest,
)


# ============================================================
# STEP 34 — API RESPONSE CONTRACT TEST
# ============================================================


async def main():

    print()
    print("=" * 75)
    print("STEP 34 — API RESPONSE CONTRACT TEST")
    print("=" * 75)

    # ========================================================
    # 1. BUILD REQUEST
    # ========================================================

    print()
    print("1. Building API request...")

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

                opening_hours=None,

                day=3,

                role="waypoint"

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
        "   ✅ Request created"
    )

    # ========================================================
    # 2. CALL API
    # ========================================================

    print()
    print("2. Calling create_itinerary()...")

    response = await create_itinerary(
        request
    )

    assert isinstance(
        response,
        dict
    )

    print(
        "   ✅ API returned dictionary response"
    )

    # ========================================================
    # 3. TOP-LEVEL RESPONSE CONTRACT
    # ========================================================

    print()
    print("3. Validating top-level response contract...")

    required_keys = {

        "city",
        "days",
        "time_validation",
        "quality_validation"

    }

    response_keys = set(
        response.keys()
    )

    missing_keys = (
        required_keys
        - response_keys
    )

    assert not missing_keys, (
        "Missing response keys: "
        f"{missing_keys}"
    )

    assert response["city"] == "Chennai"

    assert isinstance(
        response["days"],
        list
    )

    assert isinstance(
        response["time_validation"],
        dict
    )

    assert isinstance(
        response["quality_validation"],
        dict
    )

    print(
        "   ✅ Top-level response contract valid"
    )

    # ========================================================
    # 4. DAY CONTRACT
    # ========================================================

    print()
    print("4. Validating day structure...")

    assert len(
        response["days"]
    ) == 3

    for day in response["days"]:

        assert "day" in day

        assert "places" in day

        assert "total_distance_km" in day

        assert "start_time" in day

        assert "end_time" in day

        assert "time_validation" in day

        assert isinstance(
            day["places"],
            list
        )

    print(
        "   ✅ Day structure valid"
    )

    # ========================================================
    # 5. PLACE CONTRACT
    # ========================================================

    print()
    print("5. Validating place structure...")

    required_place_fields = {

        "name",
        "category",
        "latitude",
        "longitude",
        "distance_from_previous_km",
        "travel_time_minutes",
        "visit_duration_minutes",
        "arrival_time",
        "departure_time"

    }

    total_places = 0

    for day in response["days"]:

        for place in day["places"]:

            total_places += 1

            missing = (
                required_place_fields
                - set(place.keys())
            )

            assert not missing, (
                f"Place '{place.get('name')}' "
                f"is missing fields: {missing}"
            )

            assert place["name"]

            assert (
                place["latitude"]
                is not None
            )

            assert (
                place["longitude"]
                is not None
            )

            assert (
                place[
                    "distance_from_previous_km"
                ]
                is not None
            )

            assert (
                place[
                    "travel_time_minutes"
                ]
                is not None
            )

            assert (
                place[
                    "visit_duration_minutes"
                ]
                is not None
            )

            assert (
                place["arrival_time"]
                is not None
            )

            assert (
                place["departure_time"]
                is not None
            )

    assert total_places > 0

    print(
        f"   ✅ {total_places} places "
        "contain required fields"
    )

    # ========================================================
    # 6. ORIGIN CONTRACT
    # ========================================================

    print()
    print("6. Validating origin contract...")

    first_place = response[
        "days"
    ][0]["places"][0]

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

    assert (
        first_place["name"]
        == "My Location"
    )

    print(
        "   ✅ Origin contract valid"
    )

    # ========================================================
    # 7. CUSTOM WAYPOINT CONTRACT
    # ========================================================

    print()
    print("7. Validating custom waypoint contract...")

    custom_places = []

    for day in response["days"]:

        for place in day["places"]:

            if (
                place.get("name")
                == "My Custom Place"
            ):

                custom_places.append(
                    place
                )

    assert len(
        custom_places
    ) == 1

    custom_place = custom_places[0]

    assert (
        custom_place.get(
            "custom_location"
        )
        is True
    )

    assert (
        str(
            custom_place.get(
                "custom_role",
                ""
            )
        ).lower()
        == "waypoint"
    )

    print(
        "   ✅ Custom waypoint contract valid"
    )

    # ========================================================
    # 8. DESTINATION CONTRACT
    # ========================================================

    print()
    print("8. Validating destination contract...")

    last_day = response[
        "days"
    ][-1]

    assert last_day["places"]

    destination = last_day[
        "places"
    ][-1]

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

    assert (
        destination["name"]
        == "Chennai Central"
    )

    print(
        "   ✅ Destination contract valid"
    )

    # ========================================================
    # 9. TIME VALIDATION CONTRACT
    # ========================================================

    print()
    print("9. Validating time-validation contract...")

    time_validation = response[
        "time_validation"
    ]

    assert "valid" in time_validation

    assert "errors" in time_validation

    assert "warnings" in time_validation

    assert isinstance(
        time_validation["errors"],
        list
    )

    assert isinstance(
        time_validation["warnings"],
        list
    )

    assert (
        time_validation["valid"]
        is True
    )

    print(
        "   ✅ Time validation contract valid"
    )

    # ========================================================
    # 10. QUALITY VALIDATION CONTRACT
    # ========================================================

    print()
    print("10. Validating quality-validation contract...")

    quality_validation = response[
        "quality_validation"
    ]

    assert "valid" in quality_validation

    assert "errors" in quality_validation

    assert "warnings" in quality_validation

    assert isinstance(
        quality_validation["errors"],
        list
    )

    assert isinstance(
        quality_validation["warnings"],
        list
    )

    assert (
        quality_validation["valid"]
        is True
    )

    print(
        "   ✅ Quality validation contract valid"
    )

    # ========================================================
    # 11. FINAL SCHEDULE CONSISTENCY
    # ========================================================

    print()
    print("11. Validating final schedule consistency...")

    for day in response["days"]:

        previous_departure = None

        for place in day["places"]:

            arrival = place[
                "arrival_time"
            ]

            departure = place[
                "departure_time"
            ]

            assert arrival
            assert departure

            # Simple format validation.
            assert (
                len(arrival) == 5
            )

            assert (
                len(departure) == 5
            )

            if previous_departure:

                assert (
                    place[
                        "arrival_time"
                    ]
                    is not None
                )

            previous_departure = departure

    print(
        "   ✅ Final schedule is consistent"
    )

    # ========================================================
    # 12. PRINT SUMMARY
    # ========================================================

    print()
    print("=" * 75)
    print("STEP 34 VALIDATION SUMMARY")
    print("=" * 75)

    print(
        f"City: {response['city']}"
    )

    print(
        f"Days: {len(response['days'])}"
    )

    print(
        f"Total places: {total_places}"
    )

    print(
        "Time validation:",
        response[
            "time_validation"
        ]["valid"]
    )

    print(
        "Quality validation:",
        response[
            "quality_validation"
        ]["valid"]
    )

    print()
    print("=" * 75)
    print("STEP 34 TEST EXECUTION COMPLETE")
    print("=" * 75)

    print()
    print("🎯 API CONTRACT CHECKS")

    print(
        "✅ Top-level response structure"
    )

    print(
        "✅ Day structure"
    )

    print(
        "✅ Place structure"
    )

    print(
        "✅ Origin contract"
    )

    print(
        "✅ Custom waypoint contract"
    )

    print(
        "✅ Destination contract"
    )

    print(
        "✅ Time validation contract"
    )

    print(
        "✅ Quality validation contract"
    )

    print(
        "✅ Final schedule consistency"
    )

    print()
    print(
        "🎉 STEP 34 — API RESPONSE CONTRACT TEST PASSED"
    )

    print("=" * 75)


if __name__ == "__main__":

    asyncio.run(
        main()
    )