from typing import Any, Dict, List, Optional

from app.services.geoapify_places import search_places


# ============================================================
# CACHE
# ============================================================

_PLACES_CACHE: Dict[str, List[Dict[str, Any]]] = {}


# ============================================================
# LOAD CITY PLACES
# ============================================================

async def load_city_places(
    city: str
) -> List[Dict[str, Any]]:

    result = await search_places(city)

    if not result.get("success"):
        return []

    places = result.get(
        "places",
        []
    )

    normalized_city = result.get(
        "normalized_city",
        city
    ).lower()

    _PLACES_CACHE[
        normalized_city
    ] = places

    return places


# ============================================================
# GET CACHED PLACES
# ============================================================

def get_cached_places(
    city: str
) -> List[Dict[str, Any]]:

    return _PLACES_CACHE.get(
        city.lower(),
        []
    )

def find_place(
    name: str,
    city: Optional[str] = None
) -> Optional[Dict[str, Any]]:

    if not name:
        return None

    search_name = (
        name.strip().lower()
    )

    # --------------------------------------------------------
    # Search city cache first
    # --------------------------------------------------------

    if city:

        places = get_cached_places(
            city
        )

    else:

        places = []

        for cached_places in (
            _PLACES_CACHE.values()
        ):

            places.extend(
                cached_places
            )

    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

    for place in places:

        place_name = str(
            place.get("name", "")
        ).strip().lower()

        if place_name == search_name:

            return place

    # --------------------------------------------------------
    # Safe partial match
    # --------------------------------------------------------

    # Do not resolve generic place types
    # such as "temple", "park", etc.

    generic_names = {
        "temple",
        "park",
        "restaurant",
        "cafe",
        "hotel",
        "beach",
        "mall",
        "museum",
        "church",
        "mosque",
        "attraction",
        "shopping mall",
        "fuel station"
    }

    if search_name in generic_names:

        return None

    # --------------------------------------------------------
    # Partial match
    # --------------------------------------------------------

    for place in places:

        place_name = str(
            place.get("name", "")
        ).strip().lower()

        if (
            search_name in place_name
            or place_name in search_name
        ):

            return place

    return None

# ============================================================
# SEARCH BY CATEGORY
# ============================================================

def find_places_by_category(
    category: str,
    city: str
) -> List[Dict[str, Any]]:

    places = get_cached_places(
        city
    )

    category = category.lower()

    return [
        place
        for place in places
        if str(
            place.get("category", "")
        ).lower() == category
    ]


# ============================================================
# CLEAR CACHE
# ============================================================

def clear_places_cache():

    _PLACES_CACHE.clear()