from app.services.route_optimizer import optimize_day


places = [
    {
        "name": "Start Point",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "origin": True,
        "custom_location": True,
        "custom_role": "start"
    },
    {
        "name": "Marina Beach",
        "latitude": 13.0500,
        "longitude": 80.2824,
        "category": "beach"
    },
    {
        "name": "Kapaleeshwarar Temple",
        "latitude": 13.0338,
        "longitude": 80.2676,
        "category": "place_of_worship"
    },
    {
        "name": "Government Museum",
        "latitude": 13.0694,
        "longitude": 80.2609,
        "category": "museum"
    },
    {
        "name": "Hotel",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "destination": True,
        "custom_location": True,
        "custom_role": "destination"
    }
]


result = optimize_day(places)

print("\n===== OPTIMIZED ROUTE =====")

for index, place in enumerate(result["places"], 1):

    print(
        index,
        place["name"],
        "->",
        place.get("distance_from_previous_km"),
        "km"
    )

print("\n===== TOTAL DISTANCE =====")
print(result["total_distance_km"])

print("\n===== OPTIMIZATION =====")
print(result["optimization"])