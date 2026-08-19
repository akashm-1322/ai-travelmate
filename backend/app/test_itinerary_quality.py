from app.services.itinerary_quality import (
    improve_itinerary,
    check_itinerary_quality,
)


def separator():
    print("=" * 70)


def print_places(itinerary):
    for day in itinerary.get("days", []):
        print(f"\nDAY {day.get('day')}")

        places = day.get("places", [])

        for index, place in enumerate(places, 1):
            print(
                f"{index}. "
                f"{place.get('name')} "
                f"[{place.get('category', 'unknown')}]"
            )


# ============================================================
# TEST 1 — DUPLICATE REMOVAL
# ============================================================

test_duplicates = {
    "city": "Chennai",
    "days": [
        {
            "day": 1,
            "places": [
                {
                    "name": "Marina Beach",
                    "category": "beach",
                    "latitude": 13.0500,
                    "longitude": 80.2824,
                },
                {
                    "name": "Marina Beach",
                    "category": "beach",
                    "latitude": 13.0500,
                    "longitude": 80.2824,
                },
                {
                    "name": "Kapaleeshwarar Temple",
                    "category": "place_of_worship",
                    "latitude": 13.0339,
                    "longitude": 80.2694,
                },
            ],
        }
    ],
}


# ============================================================
# TEST 2 — RESTAURANT LIMIT
# ============================================================

test_restaurant_limit = {
    "city": "Chennai",
    "days": [
        {
            "day": 1,
            "places": [
                {
                    "name": "Restaurant 1",
                    "category": "restaurant",
                },
                {
                    "name": "Restaurant 2",
                    "category": "restaurant",
                },
                {
                    "name": "Restaurant 3",
                    "category": "restaurant",
                },
                {
                    "name": "Marina Beach",
                    "category": "beach",
                },
            ],
        }
    ],
}


# ============================================================
# TEST 3 — MAXIMUM PLACES PER DAY
# ============================================================

test_max_places = {
    "city": "Chennai",
    "days": [
        {
            "day": 1,
            "places": [
                {
                    "name": f"Place {i}",
                    "category": "attraction",
                }
                for i in range(1, 9)
            ],
        }
    ],
}


# ============================================================
# TEST 4 — CATEGORY DIVERSITY
# ============================================================

test_category_diversity = {
    "city": "Chennai",
    "days": [
        {
            "day": 1,
            "places": [
                {
                    "name": "Temple 1",
                    "category": "place_of_worship",
                },
                {
                    "name": "Temple 2",
                    "category": "place_of_worship",
                },
                {
                    "name": "Temple 3",
                    "category": "place_of_worship",
                },
            ],
        }
    ],
}


# ============================================================
# TEST 5 — ORIGIN AND DESTINATION PRESERVATION
# ============================================================

test_origin_destination = {
    "city": "Chennai",
    "days": [
        {
            "day": 1,
            "places": [
                {
                    "name": "My Location",
                    "category": "origin",
                    "origin": True,
                    "custom_location": True,
                    "custom_role": "start",
                    "preferred_start_time": "09:00",
                },
                {
                    "name": "Marina Beach",
                    "category": "beach",
                },
                {
                    "name": "Chennai Central",
                    "category": "destination",
                    "destination": True,
                    "custom_location": True,
                    "custom_role": "destination",
                    "preferred_end_time": "18:00",
                },
            ],
        }
    ],
}


# ============================================================
# TEST 6 — MULTI-DAY QUALITY
# ============================================================

test_multi_day = {
    "city": "Chennai",
    "days": [
        {
            "day": 1,
            "places": [
                {
                    "name": "Marina Beach",
                    "category": "beach",
                },
                {
                    "name": "Marina Beach",
                    "category": "beach",
                },
                {
                    "name": "Restaurant 1",
                    "category": "restaurant",
                },
                {
                    "name": "Restaurant 2",
                    "category": "restaurant",
                },
                {
                    "name": "Restaurant 3",
                    "category": "restaurant",
                },
            ],
        },
        {
            "day": 2,
            "places": [
                {
                    "name": "Phoenix Marketcity Chennai",
                    "category": "shopping",
                },
                {
                    "name": "Guindy National Park",
                    "category": "park",
                },
            ],
        },
        {
            "day": 3,
            "places": [
                {
                    "name": "Kapaleeshwarar Temple",
                    "category": "place_of_worship",
                },
                {
                    "name": "Chennai Central",
                    "category": "destination",
                    "destination": True,
                    "custom_role": "destination",
                },
            ],
        },
    ],
}


# ============================================================
# RUN TEST
# ============================================================

def run_test(test_name, itinerary):
    separator()

    print(test_name)

    separator()

    print("\nBEFORE IMPROVEMENT")
    print_places(itinerary)

    improved = improve_itinerary(itinerary)

    print("\nAFTER IMPROVEMENT")
    print_places(improved)

    quality = check_itinerary_quality(improved)

    print("\nQUALITY RESULT")
    print(f"Valid: {quality['valid']}")

    print("\nErrors:")

    if quality["errors"]:
        for error in quality["errors"]:
            print(f"  ❌ {error}")
    else:
        print("  ✅ No errors")

    print("\nWarnings:")

    if quality["warnings"]:
        for warning in quality["warnings"]:
            print(f"  ⚠️ {warning}")
    else:
        print("  ✅ No warnings")

    return improved, quality


# ============================================================
# EXECUTION
# ============================================================

print("\n")
separator()
print("STEP 31 — ITINERARY QUALITY TEST")
separator()


# ------------------------------------------------------------
# TEST 1
# ------------------------------------------------------------

improved_1, result_1 = run_test(
    "TEST 1 — DUPLICATE REMOVAL",
    test_duplicates,
)

assert len(improved_1["days"][0]["places"]) == 2

print("\n✅ Duplicate removal check passed")


# ------------------------------------------------------------
# TEST 2
# ------------------------------------------------------------

improved_2, result_2 = run_test(
    "TEST 2 — RESTAURANT LIMIT",
    test_restaurant_limit,
)

restaurant_count = sum(
    1
    for place in improved_2["days"][0]["places"]
    if place.get("category") == "restaurant"
)

assert restaurant_count <= 2

print("\n✅ Restaurant limit check passed")


# ------------------------------------------------------------
# TEST 3
# ------------------------------------------------------------

improved_3, result_3 = run_test(
    "TEST 3 — MAXIMUM PLACES PER DAY",
    test_max_places,
)

assert len(improved_3["days"][0]["places"]) <= 6

print("\n✅ Maximum places/day check passed")


# ------------------------------------------------------------
# TEST 4
# ------------------------------------------------------------

improved_4, result_4 = run_test(
    "TEST 4 — CATEGORY DIVERSITY",
    test_category_diversity,
)

assert any(
    "category diversity"
    in warning.lower()
    for warning in result_4["warnings"]
)

print("\n✅ Category diversity warning check passed")


# ------------------------------------------------------------
# TEST 5
# ------------------------------------------------------------

improved_5, result_5 = run_test(
    "TEST 5 — ORIGIN AND DESTINATION",
    test_origin_destination,
)

places_5 = improved_5["days"][0]["places"]

assert places_5[0].get("origin") is True
assert places_5[-1].get("destination") is True

print("\n✅ Origin/destination preservation check passed")


# ------------------------------------------------------------
# TEST 6
# ------------------------------------------------------------

improved_6, result_6 = run_test(
    "TEST 6 — MULTI-DAY QUALITY",
    test_multi_day,
)

assert len(improved_6["days"]) == 3

for day in improved_6["days"]:
    assert len(day["places"]) <= 6

print("\n✅ Multi-day quality check passed")


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
separator()
print("STEP 31 TEST EXECUTION COMPLETE")
separator()

print("\nAutomatic checks:")
print("✅ Duplicate places removed")
print("✅ Restaurant limit enforced")
print("✅ Maximum 6 places/day enforced")
print("✅ Category diversity warning detected")
print("✅ Origin preserved")
print("✅ Destination preserved")
print("✅ Three days preserved")

print("\n🎉 ITINERARY QUALITY TEST PASSED")
separator()