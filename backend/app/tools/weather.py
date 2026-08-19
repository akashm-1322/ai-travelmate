import httpx


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


async def get_weather(city: str):

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(15.0),
            follow_redirects=True,
        ) as client:

            # ---------------------------------
            # 1. Convert city -> coordinates
            # ---------------------------------

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
                    "error": f"Could not find location: {city}",
                }

            location = results[0]

            latitude = location["latitude"]
            longitude = location["longitude"]

            resolved_city = location["name"]
            country = location.get("country", "")

            # ---------------------------------
            # 2. Get live weather
            # ---------------------------------

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

    except httpx.TimeoutException:

        print(
            f"Weather API timeout for city: {city}"
        )

        return {
            "success": False,
            "error": (
                "Weather service timed out. "
                "Please try again."
            ),
        }

    except httpx.ConnectError as exc:

        print(
            f"Weather API connection error: {exc}"
        )

        return {
            "success": False,
            "error": (
                "Unable to connect to the weather "
                "service right now."
            ),
        }

    except httpx.HTTPStatusError as exc:

        print(
            f"Weather API HTTP error: "
            f"{exc.response.status_code}"
        )

        return {
            "success": False,
            "error": (
                "Weather service returned an error."
            ),
        }

    except Exception as exc:

        print(
            f"Unexpected weather error: "
            f"{type(exc).__name__}: {exc}"
        )

        return {
            "success": False,
            "error": (
                "Unable to retrieve weather "
                "information right now."
            ),
        }
# ============================================================
# HOURLY WEATHER FORECAST
# ============================================================

async def get_hourly_forecast(
    city: str
) -> dict:

    try:

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(
                15.0
            ),
            follow_redirects=True,
        ) as client:

            # ------------------------------------------------
            # 1. GEOCODE CITY
            # ------------------------------------------------

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


            geo_data = (
                geo_response.json()
            )


            results = (
                geo_data.get(
                    "results",
                    []
                )
            )


            if not results:

                return {
                    "success": False,
                    "error": (
                        f"Could not find location: {city}"
                    ),
                }


            location = (
                results[0]
            )


            latitude = (
                location[
                    "latitude"
                ]
            )

            longitude = (
                location[
                    "longitude"
                ]
            )


            # ------------------------------------------------
            # 2. HOURLY FORECAST
            # ------------------------------------------------

            forecast_response = (
                await client.get(

                    WEATHER_URL,

                    params={

                        "latitude":
                            latitude,

                        "longitude":
                            longitude,

                        "hourly": (
                            "temperature_2m,"
                            "apparent_temperature,"
                            "precipitation_probability,"
                            "precipitation,"
                            "weather_code"
                        ),

                        "timezone":
                            "auto",

                        "forecast_days":
                            7,

                    },

                )
            )


            forecast_response.raise_for_status()


            data = (
                forecast_response.json()
            )


            hourly = (
                data.get(
                    "hourly",
                    {}
                )
            )


            return {

                "success":
                    True,

                "location":
                    location.get(
                        "name"
                    ),

                "country":
                    location.get(
                        "country",
                        ""
                    ),

                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "timezone":
                    data.get(
                        "timezone"
                    ),

                "hourly":
                    hourly,

            }


    except httpx.TimeoutException:

        return {

            "success": False,

            "error": (
                "Hourly weather forecast timed out."
            ),

        }


    except httpx.HTTPError as exc:

        print(
            "Hourly forecast HTTP error: "
            f"{exc}"
        )


        return {

            "success": False,

            "error": (
                "Unable to retrieve hourly weather forecast."
            ),

        }


    except Exception as exc:

        print(
            "Unexpected hourly forecast error: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )


        return {

            "success": False,

            "error": (
                "Unable to retrieve hourly weather forecast."
            ),

        }