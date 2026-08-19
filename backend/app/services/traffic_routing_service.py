import os

import httpx

from dotenv import load_dotenv


load_dotenv()


TOMTOM_API_KEY = os.getenv(
    "TOMTOM_API_KEY"
)


TOMTOM_ROUTE_URL = (
    "https://api.tomtom.com/"
    "routing/1/calculateRoute"
)


# ============================================================
# TRAFFIC ROUTE
# ============================================================

async def get_traffic_route(
    origin_latitude: float,
    origin_longitude: float,
    destination_latitude: float,
    destination_longitude: float,
) -> dict:

    if not TOMTOM_API_KEY:

        return {
            "success": False,
            "error": (
                "TOMTOM_API_KEY is not configured."
            ),
        }


    locations = (

        f"{origin_latitude},"
        f"{origin_longitude}:"

        f"{destination_latitude},"
        f"{destination_longitude}"

    )


    url = (
        f"{TOMTOM_ROUTE_URL}/"
        f"{locations}/json"
    )


    params = {

        "key":
            TOMTOM_API_KEY,

        "traffic":
            "true",

        "travelMode":
            "car",

        "routeType":
            "fastest",

        "computeTravelTimeFor":
            "all",

        "routeRepresentation":
            "summaryOnly",

    }


    try:

        async with httpx.AsyncClient(
            timeout=15.0
        ) as client:

            response = await client.get(
                url,
                params=params,
            )


            response.raise_for_status()


            data = response.json()


    except httpx.TimeoutException:

        return {
            "success": False,
            "error": (
                "Traffic routing request timed out."
            ),
        }


    except httpx.HTTPStatusError as exc:

        print(
            "TomTom routing HTTP error:",
            exc.response.status_code,
            exc.response.text,
        )


        return {
            "success": False,
            "error": (
                "Traffic routing provider rejected "
                "the request."
            ),
        }


    except Exception as exc:

        print(
            "Traffic routing error:",
            type(exc).__name__,
            exc,
        )


        return {
            "success": False,
            "error": (
                "Unable to calculate traffic route."
            ),
        }


    routes = data.get(
        "routes",
        []
    )


    if not routes:

        return {
            "success": False,
            "error": (
                "No road route was found."
            ),
        }


    summary = (
        routes[0]
        .get(
            "summary",
            {}
        )
    )


    distance_meters = (
        summary.get(
            "lengthInMeters",
            0
        )
        or 0
    )


    travel_seconds = (
        summary.get(
            "travelTimeInSeconds",
            0
        )
        or 0
    )


    traffic_delay_seconds = (
        summary.get(
            "trafficDelayInSeconds",
            0
        )
        or 0
    )


    no_traffic_seconds = (
        summary.get(
            "noTrafficTravelTimeInSeconds",
            travel_seconds
        )
        or travel_seconds
    )


    historic_seconds = (
        summary.get(
            "historicTrafficTravelTimeInSeconds",
            0
        )
        or 0
    )


    live_incident_seconds = (
        summary.get(
            "liveTrafficIncidentsTravelTimeInSeconds",
            0
        )
        or 0
    )


    return {

        "success":
            True,

        "distance_km":
            round(
                distance_meters
                / 1000,
                2,
            ),

        "travel_time_minutes":
            max(
                1,
                round(
                    travel_seconds
                    / 60
                ),
            ),

        "traffic_delay_minutes":
            round(
                traffic_delay_seconds
                / 60
            ),

        "no_traffic_minutes":
            max(
                1,
                round(
                    no_traffic_seconds
                    / 60
                ),
            ),

        "historic_traffic_minutes":
            (
                round(
                    historic_seconds
                    / 60
                )
                if historic_seconds
                else None
            ),

        "live_incident_minutes":
            (
                round(
                    live_incident_seconds
                    / 60
                )
                if live_incident_seconds
                else None
            ),

        "provider":
            "TomTom",

    }