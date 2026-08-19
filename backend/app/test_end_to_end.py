from app.services.itinerary_quality import (
    improve_itinerary,
    check_itinerary_quality,
)

from app.services.daily_scheduler import schedule_itinerary

from app.services.time_constraints import (
    validate_time_constraints,
)

from app.services.custom_location import (
    create_custom_location,
    inject_custom_locations,
)

from app.services.route_optimizer import (
    add_destination_distance,
)


# ============================================================
# HELPERS
# ============================================================

def separator():
    print("=" * 75)


def print_route(itinerary):
    for day in itinerary.get("days", []):
        print(f"\nDAY {day.get('day')}")

        for index, place in enumerate(
            day.get("places", []),
            1
        ):
            print(
                f"{index}. {place.get('name')}"
            )

            print(
                f"   Category: "
                f"{place.get('category')}"
            )

            print(
                f"   Coordinates: "
                f"{place.get('latitude')}, "
                f"{place.get('longitude')}"
            )

            print(
                f"   Distance: "
                f"{place.get('distance_from_previous_km', 0)} km"
            )

            print(
                f"   Travel: "
                f"{place.get('travel_time_minutes', 0)} min"
            )

            print(
                f"   Visit: "
                f"{place.get('visit_duration_minutes', 0)} min"
            )

            print(
                f"   Arrival: "
                f"{place.get('arrival_time')}"
            )

            print(
                f"   Departure: "
                f"{place.get('departure_time')}"
            )

            if place.get("opening_hours"):
                print(
                    f"   Opening hours: "
                    f"{place.get('opening_hours')}"
                )

            if place.get("origin"):
                print("   Role: ORIGIN")

            if place.get("destination"):
                print("   Role: DESTINATION")

            if place.get("custom_location"):
                print(
                    f"   Custom role: "
                    f"{place.get('custom_role')}"
                )


# ============================================================
# STEP 32 — END-TO-END TEST DATA
# ============================================================

itinerary = {
    "city": "Chennai",

    "days": [

        # ====================================================
        # DAY 1
        # ====================================================

        {
            "day": 1,

            "places": [

                {
                    "name": "Ashtalakshmi Temple",
                    "category": "place_of_worship",
                    "latitude": 12.9925521,
                    "longitude": 80.270367,
                    "description": None,
                    "address": None,
                    "opening_hours":
                        "Mo-Su 06:00-12:00",
                    "distance_from_previous_km": 0,
                    "travel_time_minutes": 0,
                    "visit_duration_minutes": 60,
                    "arrival_time": "09:00",
                    "departure_time": "10:00",
                },

                {
                    "name": "Adyar Ananda Bhavan",
                    "category": "restaurant",
                    "latitude": 12.9732002,
                    "longitude": 80.2203482,
                    "description": None,
                    "address": None,
                    "opening_hours":
                        "Mo-Su 10:00-22:00",
                    "distance_from_previous_km": 5.91,
                    "travel_time_minutes": 14,
                    "visit_duration_minutes": 60,
                    "arrival_time": "10:14",
                    "departure_time": "11:14",
                },

                {
                    "name": "Zone 13 Adyar",
                    "category": "park",
                    "latitude": 12.9909495,
                    "longitude": 80.2684998,
                    "description": None,
                    "address": None,
                    "opening_hours":
                        "Mo-Su 06:00-20:00",
                    "distance_from_previous_km": 5.58,
                    "travel_time_minutes": 13,
                    "visit_duration_minutes": 45,
                    "arrival_time": "11:27",
                    "departure_time": "12:12",
                },
            ],
        },

        # ====================================================
        # DAY 2
        # ====================================================

        {
            "day": 2,

            "places": [

                {
                    "name": "Siva Vishnu Temple",
                    "category": "place_of_worship",
                    "latitude": 12.9581693,
                    "longitude": 80.199008,
                    "description": None,
                    "address": None,
                    "opening_hours":
                        "Mo-Su 06:00-12:00",
                    "distance_from_previous_km": 0,
                    "travel_time_minutes": 0,
                    "visit_duration_minutes": 60,
                    "arrival_time": "09:00",
                    "departure_time": "10:00",
                },

                {
                    "name": "Phoenix Marketcity Chennai",
                    "category": "shopping",
                    "latitude": 12.991551,
                    "longitude": 80.2166235,
                    "description": None,
                    "address": None,
                    "opening_hours":
                        "Mo-Su 10:00-22:00",
                    "distance_from_previous_km": 3.80,
                    "travel_time_minutes": 9,
                    "visit_duration_minutes": 120,
                    "arrival_time": "10:09",
                    "departure_time": "12:09",
                },

            ],
        },

        # ====================================================
        # DAY 3
        # ====================================================

        {
            "day": 3,

            "places": [

                {
                    "name": "Annai Velankanni Shrine",
                    "category": "place_of_worship",
                    "latitude": 12.9951775,
                    "longitude": 80.2700337,
                    "description": None,
                    "address": None,
                    "opening_hours":
                        "Mo-Su 06:00-21:00",
                    "distance_from_previous_km": 0,
                    "travel_time_minutes": 0,
                    "visit_duration_minutes": 60,
                    "arrival_time": "09:00",
                    "departure_time": "10:00",
                },

                {
                    "name": "Marina Beach",
                    "category": "beach",
                    "latitude": 13.0500,
                    "longitude": 80.2824,
                    "description": None,
                    "address": None,
                    "opening_hours":
                        "Mo-Su 00:00-23:59",
                    "distance_from_previous_km": 6.20,
                    "travel_time_minutes": 15,
                    "visit_duration_minutes": 90,
                    "arrival_time": "10:15",
                    "departure_time": "11:45",
                },
            ],
        },
    ],
}


# ============================================================
# STEP 32A — CREATE CUSTOM WAYPOINT
# ============================================================

custom_waypoint = create_custom_location(
    name="My Custom Place",
    latitude=13.0200,
    longitude=80.2600,
    category="custom_location",
    visit_duration_minutes=45,
    role="waypoint",
    day=3,
)


# ============================================================
# STEP 32B — CREATE ORIGIN
# ============================================================

origin = create_custom_location(
    name="My Location",
    latitude=13.0827,
    longitude=80.2707,
    category="origin",
    visit_duration_minutes=0,
    role="start",
    day=1,
    start_time="09:00",
)


# ============================================================
# STEP 32C — CREATE DESTINATION
# ============================================================

destination = create_custom_location(
    name="Chennai Central",
    latitude=13.0827,
    longitude=80.2785,
    category="destination",
    visit_duration_minutes=0,
    role="destination",
    day=3,
    end_time="18:00",
)


# ============================================================
# STEP 32D — INJECT CUSTOM LOCATIONS
# ============================================================

custom_locations = [
    origin,
    custom_waypoint,
    destination,
]

print("\n")
separator()
print("STEP 32 — END-TO-END ITINERARY TEST")
separator()

print("\nInjecting custom locations...")

itinerary = inject_custom_locations(
    itinerary,
    custom_locations,
)

print("✅ Custom locations injected")


# ============================================================
# STEP 32E — QUALITY IMPROVEMENT
# ============================================================

print("\nApplying itinerary quality rules...")

itinerary = improve_itinerary(
    itinerary
)

print("✅ Quality improvement completed")


# ============================================================
# STEP 32F — DESTINATION DISTANCE
# ============================================================

print("\nCalculating destination distance...")

try:

    itinerary = add_destination_distance(
        itinerary
    )

    print(
        "✅ Destination distance calculation completed"
    )

except Exception as e:

    print(
        "\n❌ Destination distance calculation failed"
    )

    print(
        f"Error: {type(e).__name__}: {e}"
    )

    raise
# ============================================================
# STEP 32F.5 — DAILY SCHEDULING
# ============================================================

print("\nRunning daily scheduler...")

try:

    itinerary = schedule_itinerary(
        itinerary,
        start_time="09:00"
    )

    print(
        "✅ Daily scheduling completed"
    )

except Exception as e:

    print(
        "\n❌ Daily scheduling failed"
    )

    print(
        f"Error: {type(e).__name__}: {e}"
    )

    raise

# ============================================================
# STEP 32G — QUALITY VALIDATION
# ============================================================

print("\nRunning quality validation...")

quality_result = check_itinerary_quality(
    itinerary
)

print(
    f"Quality valid: "
    f"{quality_result['valid']}"
)

print("\nQuality errors:")

if quality_result["errors"]:

    for error in quality_result["errors"]:
        print(f"  ❌ {error}")

else:

    print("  ✅ No errors")


print("\nQuality warnings:")

if quality_result["warnings"]:

    for warning in quality_result["warnings"]:
        print(f"  ⚠️ {warning}")

else:

    print("  ✅ No warnings")


# ============================================================
# STEP 32H — TIME VALIDATION
# ============================================================

print("\nRunning time validation...")

time_result = validate_time_constraints(
    itinerary
)

print(
    f"Time validation valid: "
    f"{time_result['valid']}"
)

print("\nTime errors:")

if time_result["errors"]:

    for error in time_result["errors"]:
        print(f"  ❌ {error}")

else:

    print("  ✅ No errors")


print("\nTime warnings:")

if time_result["warnings"]:

    for warning in time_result["warnings"]:
        print(f"  ⚠️ {warning}")

else:

    print("  ✅ No warnings")


# ============================================================
# STEP 32I — FINAL ROUTE
# ============================================================

separator()
print("FINAL END-TO-END ITINERARY")
separator()

print_route(itinerary)


# ============================================================
# AUTOMATIC CHECKS
# ============================================================

separator()
print("AUTOMATIC CHECKS")
separator()


# ------------------------------------------------------------
# CHECK 1 — CITY
# ------------------------------------------------------------

assert itinerary.get("city") == "Chennai"

print("✅ City preserved")


# ------------------------------------------------------------
# CHECK 2 — THREE DAYS
# ------------------------------------------------------------

assert len(itinerary.get("days", [])) == 3

print("✅ Three days preserved")


# ------------------------------------------------------------
# CHECK 3 — ORIGIN
# ------------------------------------------------------------

day_1_places = itinerary["days"][0]["places"]

assert day_1_places[0].get("origin") is True

print("✅ Origin exists and is first")


# ------------------------------------------------------------
# CHECK 4 — CUSTOM WAYPOINT
# ------------------------------------------------------------

day_3_places = itinerary["days"][2]["places"]

custom_found = any(
    place.get("name") == "My Custom Place"
    for place in day_3_places
)

assert custom_found

print("✅ Custom waypoint exists")


# ------------------------------------------------------------
# CHECK 5 — DESTINATION
# ------------------------------------------------------------

destination_found = any(
    place.get("destination") is True
    for place in day_3_places
)

assert destination_found

print("✅ Destination exists")


# ------------------------------------------------------------
# CHECK 6 — DESTINATION IS LAST
# ------------------------------------------------------------

assert day_3_places[-1].get("destination") is True

print("✅ Destination is last")


# ------------------------------------------------------------
# CHECK 7 — ARRIVAL / DEPARTURE
# ------------------------------------------------------------

for day in itinerary["days"]:

    for place in day["places"]:

        assert place.get("arrival_time") is not None
        assert place.get("departure_time") is not None

print(
    "✅ Arrival/departure times exist "
    "for all places"
)


# ------------------------------------------------------------
# CHECK 8 — TRAVEL TIMES
# ------------------------------------------------------------

for day in itinerary["days"]:

    for place in day["places"]:

        assert (
            place.get("travel_time_minutes")
            is not None
        )

print("✅ Travel times exist")


# ------------------------------------------------------------
# CHECK 9 — DISTANCES
# ------------------------------------------------------------

for day in itinerary["days"]:

    for place in day["places"]:

        assert (
            place.get("distance_from_previous_km")
            is not None
        )

print("✅ Route distances exist")


# ------------------------------------------------------------
# CHECK 10 — TIME VALIDATION
# ------------------------------------------------------------

assert time_result["valid"] is True

print("✅ Time validation passed")


# ------------------------------------------------------------
# CHECK 11 — QUALITY VALIDATION
# ------------------------------------------------------------

assert quality_result["valid"] is True

print("✅ Quality validation passed")


# ============================================================
# FINAL RESULT
# ============================================================

separator()
print("STEP 32 TEST EXECUTION COMPLETE")
separator()

print("\n")

print("🎯 END-TO-END PIPELINE CHECKS")

print(
    "✅ Base itinerary created"
)

print(
    "✅ Three days preserved"
)

print(
    "✅ Origin injected"
)

print(
    "✅ Custom waypoint injected"
)

print(
    "✅ Destination injected"
)

print(
    "✅ Quality processing completed"
)

print(
    "✅ Destination distance processing completed"
)

print(
    "✅ Distances available"
)

print(
    "✅ Travel times available"
)

print(
    "✅ Arrival/departure times available"
)

print(
    "✅ Time constraints validated"
)

print(
    "✅ Quality constraints validated"
)

print("\n🎉 STEP 32 — END-TO-END TEST PASSED")
separator()