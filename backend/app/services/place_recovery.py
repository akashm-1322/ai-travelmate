from typing import Any, Dict, List, Optional

from app.services.geoapify_places import search_places


# ============================================================
# GENERIC / INVALID PLACE NAMES
# ============================================================

GENERIC_NAMES = {
    "temple",
    "park",
    "beach",
    "restaurant",
    "cafe",
    "museum",
    "church",
    "hotel",
    "mall",
    "market",
    "place",
    "attraction",
}


# ============================================================
# NORMALIZE NAME
# ============================================================

def normalize_name(name: str) -> str:

    return (
        str(name or "")
        .strip()
        .lower()
    )


# ============================================================
# CHECK WHETHER PLACE IS VALID
# ============================================================

def is_valid_place_name(name: str) -> bool:

    normalized = normalize_name(name)

    if not normalized:
        return False

    if normalized in GENERIC_NAMES:
        return False

    return True


# ============================================================
# SEARCH FOR ALTERNATIVE
# ============================================================

async def find_alternative_place(
    original_name: str,
    city: str,
    existing_places: Optional[List[Dict[str, Any]]] = None,
) -> Optional[Dict[str, Any]]:

    existing_places = existing_places or []

    existing_names = {
        normalize_name(
            place.get("name", "")
        )
        for place in existing_places
    }

    # --------------------------------------------------------
    # Strategy 1
    # Search using the original name
    # --------------------------------------------------------

    result = await search_places(city)

    if not result.get("success"):
        return None

    places = result.get(
        "places",
        []
    )

    # --------------------------------------------------------
    # Try to find a place with a similar name
    # --------------------------------------------------------

    original_normalized = normalize_name(
        original_name
    )

    for place in places:

        place_name = normalize_name(
            place.get("name", "")
        )

        if not place_name:
            continue

        if place_name in existing_names:
            continue

        if (
            original_normalized in place_name
            or place_name in original_normalized
        ):
            return place

    # --------------------------------------------------------
    # Strategy 2
    # Find first usable specific place
    # --------------------------------------------------------

    for place in places:

        place_name = normalize_name(
            place.get("name", "")
        )

        if not place_name:
            continue

        if place_name in existing_names:
            continue

        if not is_valid_place_name(
            place_name
        ):
            continue

        return place

    return None