import httpx


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


async def get_weather(city: str):

    async with httpx.AsyncClient(timeout=10.0) as client:

        # Convert city name to coordinates
        geo_response = await client.get(
            GEOCODING_URL,
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        results = geo_data.get("results", [])

        if not results:
            return {
                "success": False,
                "error": f"Could not find location: {city}"
            }

        location = results[0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        resolved_city = location["name"]
        country = location.get("country", "")

        # Get current weather
        weather_response = await client.get(
            WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "is_day,"
                    "precipitation,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
                "timezone": "auto",
            },
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        current = weather_data["current"]

        return {
            "success": True,
            "location": resolved_city,
            "country": country,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": weather_data.get("timezone"),
            "time": current.get("time"),
            "temperature_c": current.get(
                "temperature_2m"
            ),
            "feels_like_c": current.get(
                "apparent_temperature"
            ),
            "humidity_percent": current.get(
                "relative_humidity_2m"
            ),
            "precipitation_mm": current.get(
                "precipitation"
            ),
            "wind_speed_kmh": current.get(
                "wind_speed_10m"
            ),
            "weather_code": current.get(
                "weather_code"
            ),
            "is_day": current.get(
                "is_day"
            ),
        }