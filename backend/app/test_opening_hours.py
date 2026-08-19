from app.services.daily_scheduler import schedule_itinerary
from app.services.time_constraints import validate_time_constraints


def print_separator():
    print("=" * 70)


def run_test(test_name, itinerary):
    print_separator()
    print(test_name)
    print_separator()

    scheduled = schedule_itinerary(itinerary)

    validation = validate_time_constraints(scheduled)

    for day in scheduled.get("days", []):
        print(f"\nDAY {day.get('day')}")

        for place in day.get("places", []):
            print(f"\nPlace: {place.get('name')}")
            print(f"Opening hours: {place.get('opening_hours')}")
            print(f"Arrival: {place.get('arrival_time')}")
            print(f"Departure: {place.get('departure_time')}")
            print(
                f"Visit duration: "
                f"{place.get('visit_duration_minutes')} minutes"
            )

    print("\nTIME VALIDATION")
    print(f"Valid: {validation.get('valid')}")

    print("\nErrors:")
    if validation.get("errors"):
        for error in validation["errors"]:
            print(f"  ❌ {error}")
    else:
        print("  ✅ No errors")

    print("\nWarnings:")
    if validation.get("warnings"):
        for warning in validation["warnings"]:
            print(f"  ⚠️ {warning}")
    else:
        print("  ✅ No warnings")

    return scheduled, validation


# ============================================================
# TEST 1 — PLACE OPEN DURING VISIT
# ============================================================

test_1 = {
    "city": "Chennai",
    "days": [
        {
            "day": 1,
            "places": [
                {
                    "name": "Morning Museum",
                    "category": "museum",
                    "latitude": 13.0827,
                    "longitude": 80.2707,
                    "opening_hours": "Mo-Su 09:30-17:30",
                    "visit_duration_minutes": 60,
                    "distance_from_previous_km": 0
                }
            ]
        }
    ]
}


# ============================================================
# TEST 2 — PLACE OPENS LATER
# ============================================================

test_2 = {
    "city": "Chennai",
    "days": [
        {
            "day": 1,
            "places": [
                {
                    "name": "Late Opening Museum",
                    "category": "museum",
                    "latitude": 13.0827,
                    "longitude": 80.2707,
                    "opening_hours": "Mo-Su 11:00-17:00",
                    "visit_duration_minutes": 60,
                    "distance_from_previous_km": 0
                }
            ]
        }
    ]
}


# ============================================================
# TEST 3 — SHORT OPENING WINDOW
# ============================================================

test_3 = {
    "city": "Chennai",
    "days": [
        {
            "day": 1,
            "places": [
                {
                    "name": "Short Window Temple",
                    "category": "place_of_worship",
                    "latitude": 13.0827,
                    "longitude": 80.2707,
                    "opening_hours": "Mo-Su 10:00-12:00",
                    "visit_duration_minutes": 60,
                    "distance_from_previous_km": 0
                }
            ]
        }
    ]
}


# ============================================================
# TEST 4 — ALWAYS OPEN
# ============================================================

test_4 = {
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
                    "opening_hours": "Mo-Su 00:00-23:59",
                    "visit_duration_minutes": 90,
                    "distance_from_previous_km": 0
                }
            ]
        }
    ]
}


# ============================================================
# RUN TESTS
# ============================================================

print("\n")
print_separator()
print("STEP 30 — OPENING HOURS TEST")
print_separator()

run_test(
    "TEST 1 — NORMAL OPENING HOURS",
    test_1
)

run_test(
    "TEST 2 — LATE OPENING",
    test_2
)

run_test(
    "TEST 3 — SHORT OPENING WINDOW",
    test_3
)

run_test(
    "TEST 4 — ALWAYS OPEN",
    test_4
)

print("\n")
print_separator()
print("STEP 30 TEST EXECUTION COMPLETE")
print_separator()