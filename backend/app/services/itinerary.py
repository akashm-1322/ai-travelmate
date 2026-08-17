from typing import Any, Dict, List

from app.tools.places import find_place
from app.services.place_recovery import find_alternative_place


async def resolve_itinerary(
    itinerary: Dict[str, Any]
) -> Dict[str, Any]:

    resolved_days = []

    for day in itinerary.get(
        "days",
        []
    ):

        resolved_places = []

        for place in day.get(
            "places",
            []
        ):

            requested_name = place.get(
                "name",
                ""
            )

            # ------------------------------------------------
            # STEP 1: Normal place lookup
            # ------------------------------------------------

            location = find_place(
                requested_name,
                itinerary["city"]
            )

            # ------------------------------------------------
            # STEP 2: Recovery if not found
            # ------------------------------------------------

            if not location:

                location = await find_alternative_place(

                    original_name=requested_name,

                    city=itinerary["city"],

                    existing_places=resolved_places,

                )

            # ------------------------------------------------
            # STEP 3: Still unavailable
            # ------------------------------------------------

            if not location:

                print(
                    f"WARNING: Could not resolve place: "
                    f"{requested_name}"
                )

                continue

            # ------------------------------------------------
            # STEP 4: Add resolved location
            # ------------------------------------------------

            resolved_places.append({

                "name":
                    location.get(
                        "name"
                    ),

                "category":
                    location.get(
                        "category"
                    ),

                "description":
                    location.get(
                        "description"
                    ),

                "latitude":
                    location.get(
                        "latitude"
                    ),

                "longitude":
                    location.get(
                        "longitude"
                    ),

                "address":
                    location.get(
                        "address"
                    ),

                "opening_hours":
                    location.get(
                        "opening_hours"
                    ),

                "map_url":
                    location.get(
                        "map_url"
                    ),

            })

        resolved_days.append({

            "day":
                day.get("day"),

            "places":
                resolved_places,

        })

    return {

        "city":
            itinerary.get("city"),

        "days":
            resolved_days,

    }