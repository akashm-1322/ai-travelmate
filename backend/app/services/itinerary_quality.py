from typing import Any, Dict, List


# ============================================================
# QUALITY RULES
# ============================================================

MAX_PLACES_PER_DAY = 6
MAX_RESTAURANTS_PER_DAY = 2
MAX_DAY_DISTANCE_KM = 25.0


# ============================================================
# CATEGORY HELPERS
# ============================================================

def normalize_category(place: Dict[str, Any]) -> str:
    return str(
        place.get("category", "")
    ).strip().lower()


def is_restaurant(place: Dict[str, Any]) -> bool:
    return normalize_category(place) == "restaurant"


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicate_places(
    places: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    seen = set()
    result = []

    for place in places:

        name = str(
            place.get("name", "")
        ).strip().lower()

        if not name:
            continue

        if name in seen:
            continue

        seen.add(name)
        result.append(place)

    return result


# ============================================================
# LIMIT RESTAURANTS
# ============================================================

def limit_restaurants(
    places: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    restaurants = 0
    result = []

    for place in places:

        if is_restaurant(place):

            if restaurants >= MAX_RESTAURANTS_PER_DAY:
                continue

            restaurants += 1

        result.append(place)

    return result


# ============================================================
# LIMIT PLACES PER DAY
# ============================================================

def limit_places(
    places: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    return places[
        :MAX_PLACES_PER_DAY
    ]


# ============================================================
# COUNT CATEGORIES
# ============================================================

def category_counts(
    places: List[Dict[str, Any]]
) -> Dict[str, int]:

    counts: Dict[str, int] = {}

    for place in places:

        category = normalize_category(
            place
        )

        if not category:
            continue

        counts[category] = (
            counts.get(category, 0) + 1
        )

    return counts


# ============================================================
# QUALITY WARNINGS
# ============================================================

def check_day_quality(
    places: List[Dict[str, Any]]
) -> List[str]:

    warnings = []

    if not places:
        warnings.append(
            "This day contains no places."
        )
        return warnings

    if len(places) > MAX_PLACES_PER_DAY:

        warnings.append(
            f"This day contains more than "
            f"{MAX_PLACES_PER_DAY} places."
        )

    restaurant_count = sum(
        1
        for place in places
        if is_restaurant(place)
    )

    if restaurant_count > MAX_RESTAURANTS_PER_DAY:

        warnings.append(
            "This day contains too many restaurants."
        )

    categories = category_counts(
        places
    )

    if len(categories) == 1:

        warnings.append(
            "This day has very little category diversity."
        )

    return warnings


# ============================================================
# QUALITY CHECK COMPLETE ITINERARY
# ============================================================

def check_itinerary_quality(
    itinerary: Dict[str, Any]
) -> Dict[str, Any]:

    errors = []
    warnings = []

    days = itinerary.get(
        "days",
        []
    )

    if not days:

        errors.append(
            "Itinerary contains no days."
        )

    for day in days:

        places = day.get(
            "places",
            []
        )

        day_number = day.get(
            "day",
            "?"
        )

        day_warnings = check_day_quality(
            places
        )

        for warning in day_warnings:

            warnings.append(
                f"Day {day_number}: {warning}"
            )

        distance = float(
            day.get(
                "total_distance_km",
                0
            ) or 0
        )

        if distance > MAX_DAY_DISTANCE_KM:

            warnings.append(
                f"Day {day_number}: "
                f"distance is {distance} km, "
                f"which may be excessive."
            )

    return {

        "valid":
            len(errors) == 0,

        "errors":
            errors,

        "warnings":
            warnings

    }


# ============================================================
# IMPROVE ONE DAY
# ============================================================

def improve_day(
    places: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    # 1. Remove duplicates
    places = remove_duplicate_places(
        places
    )

    # 2. Avoid excessive restaurants
    places = limit_restaurants(
        places
    )

    # 3. Prevent extremely long days
    places = limit_places(
        places
    )

    return places


# ============================================================
# IMPROVE COMPLETE ITINERARY
# ============================================================

def improve_itinerary(
    itinerary: Dict[str, Any]
) -> Dict[str, Any]:

    improved_days = []

    for day in itinerary.get(
        "days",
        []
    ):

        places = day.get(
            "places",
            []
        )

        improved_places = improve_day(
            places
        )

        improved_days.append({

            "day":
                day.get("day"),

            "places":
                improved_places

        })

    return {

        "city":
            itinerary.get("city"),

        "days":
            improved_days

    }