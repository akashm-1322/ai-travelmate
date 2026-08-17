import json

from app.llm.provider import generate_response
from app.tools.places import load_city_places


async def generate_itinerary(
    city: str,
    days: int,
    interests: str = "",
    budget: str = "moderate"
):

    # =========================================================
    # 1. LOAD REAL PLACES FROM GEOAPIFY
    # =========================================================

    places = await load_city_places(city)

    if not places:
        raise RuntimeError(
            f"No real places found for {city}"
        )

    # =========================================================
    # 2. BUILD AUTHORITATIVE PLACE LIST
    # =========================================================

    available_places = []

    seen_names = set()

    for place in places:

        name = str(
            place.get("name", "")
        ).strip()

        if not name:
            continue

        normalized_name = name.lower()

        # Avoid duplicate place names
        if normalized_name in seen_names:
            continue

        seen_names.add(
            normalized_name
        )

        available_places.append({

            "name": name,

            "category": place.get(
                "category"
            ),

            "address": place.get(
                "address"
            ),

            "opening_hours": place.get(
                "opening_hours"
            )

        })

    if not available_places:

        raise RuntimeError(
            f"Geoapify returned no usable places for {city}"
        )

    # =========================================================
    # 3. LIMIT LIST SIZE
    # =========================================================

    # We don't need to send hundreds of places to Gemini.
    available_places = available_places[:50]

    places_json = json.dumps(
        available_places,
        ensure_ascii=False,
        indent=2
    )

    # =========================================================
    # 4. BUILD ITINERARY PROMPT
    # =========================================================

    prompt = f"""
Create a travel itinerary for the user.

CITY:
{city}

NUMBER OF DAYS:
{days}

INTERESTS:
{interests}

BUDGET:
{budget}


=========================================================
AUTHORITATIVE REAL PLACES
=========================================================

You MUST select places ONLY from the following list.

These places were retrieved from a real places database.

DO NOT invent places.

DO NOT modify place names.

DO NOT create generic place names.

AVAILABLE PLACES:

{places_json}


=========================================================
OUTPUT FORMAT
=========================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "city": "{city}",
    "days": [
        {{
            "day": 1,
            "places": [
                {{
                    "name": "Exact place name from available places"
                }}
            ]
        }}
    ]
}}


=========================================================
STRICT RULES
=========================================================

1. Create exactly {days} days.

2. Each day should contain 2 to 4 places.

3. Every place MUST come from the
   AUTHORITATIVE REAL PLACES list.

4. The "name" must exactly match a name
   from the available places list.

5. NEVER invent a place.

6. NEVER use generic names such as:

   - Temple
   - Park
   - Restaurant
   - Cafe
   - Beach
   - Mall
   - Museum
   - Church
   - Hotel
   - Monument
   - Attraction

7. Do not repeat the same place across days.

8. The "name" field must contain ONLY the
   exact place name.

9. Do not add descriptions.

10. Do not add coordinates.

11. Do not add addresses.

12. Do not add opening hours.

13. Do not add map URLs.

14. Do not add any fields other than "name".

15. Do not use markdown.

16. Do not wrap the JSON inside ```json.

17. Consider the user's interests.

18. Consider the user's budget.

19. Prefer places whose category matches
    the user's interests.

20. If there are not enough suitable places,
    use other places from the authoritative list.

21. Never use a place that is not present
    in the authoritative list.


=========================================================
FINAL VALIDATION BEFORE ANSWERING
=========================================================

Before returning the JSON, verify:

- Exactly {days} days exist.
- Every day has 2 to 4 places.
- Every place exists in the authoritative list.
- No place is repeated.
- No generic names are used.
- Every "name" exactly matches the source list.
- Output is valid JSON only.
"""

    # =========================================================
    # 5. GENERATE ITINERARY
    # =========================================================

    response = await generate_response(
        prompt=prompt
    )

    print(
        "\n================ ITINERARY RAW RESPONSE ================\n"
    )

    print(response)

    print(
        "\n==========================================================\n"
    )

    # =========================================================
    # 6. CLEAN RESPONSE
    # =========================================================

    response = response.strip()

    if response.startswith("```json"):
        response = response[7:]

    elif response.startswith("```"):
        response = response[3:]

    if response.endswith("```"):
        response = response[:-3]

    response = response.strip()

    # =========================================================
    # 7. PARSE JSON
    # =========================================================

    try:

        itinerary = json.loads(
            response
        )

    except json.JSONDecodeError as e:

        raise RuntimeError(
            f"Gemini returned invalid itinerary JSON: {e}"
        )

    # =========================================================
    # 8. BASIC VALIDATION
    # =========================================================

    if not isinstance(
        itinerary,
        dict
    ):

        raise RuntimeError(
            "Itinerary must be a JSON object"
        )

    if itinerary.get("city") != city:

        itinerary["city"] = city

    generated_days = itinerary.get(
        "days",
        []
    )

    if len(generated_days) != days:

        raise RuntimeError(
            f"Expected {days} days, "
            f"but Gemini generated "
            f"{len(generated_days)}"
        )

    # =========================================================
    # 9. VALIDATE EVERY PLACE AGAINST REAL DATA
    # =========================================================

    valid_names = {
        place["name"].strip().lower()
        for place in available_places
    }

    used_names = set()

    for day in generated_days:

        if not isinstance(
            day,
            dict
        ):

            raise RuntimeError(
                "Invalid day structure"
            )

        for place in day.get(
            "places",
            []
        ):

            name = str(
                place.get("name", "")
            ).strip()

            normalized_name = (
                name.lower()
            )

            # ---------------------------------------------
            # Must exist in Geoapify list
            # ---------------------------------------------

            if normalized_name not in valid_names:

                raise RuntimeError(
                    f"Invalid place generated by Gemini: "
                    f"{name}"
                )

            # ---------------------------------------------
            # Must not be generic
            # ---------------------------------------------

            generic_names = {
                "temple",
                "park",
                "restaurant",
                "cafe",
                "beach",
                "mall",
                "museum",
                "church",
                "hotel",
                "monument",
                "attraction"
            }

            if normalized_name in generic_names:

                raise RuntimeError(
                    f"Generic place name generated: "
                    f"{name}"
                )

            # ---------------------------------------------
            # Must not repeat
            # ---------------------------------------------

            if normalized_name in used_names:

                raise RuntimeError(
                    f"Duplicate place generated: "
                    f"{name}"
                )

            used_names.add(
                normalized_name
            )

    # =========================================================
    # 10. RETURN CLEAN ITINERARY
    # =========================================================

    return itinerary