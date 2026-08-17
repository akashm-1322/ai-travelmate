from typing import Any, Dict, List, Optional
import re


# =========================================================
# CATEGORY NORMALIZATION
# =========================================================

CATEGORY_MAP = {
    # Tourism
    "tourism": "attraction",
    "tourism.attraction": "attraction",
    "tourism.sights": "attraction",
    "tourism.museum": "museum",
    "tourism.gallery": "museum",
    "tourism.viewpoint": "viewpoint",

    # Food
    "catering.restaurant": "restaurant",
    "catering.cafe": "cafe",
    "catering.fast_food": "restaurant",
    "catering.food_court": "restaurant",

    # Shopping
    "commercial.supermarket": "shopping",
    "commercial.shopping_mall": "shopping",
    "commercial.marketplace": "shopping",

    # Accommodation
    "accommodation.hotel": "hotel",
    "accommodation.guest_house": "hotel",
    "accommodation.hostel": "hotel",

    # Health
    "healthcare.hospital": "hospital",
    "healthcare.pharmacy": "pharmacy",

    # Travel stops
    "service.vehicle.fuel": "fuel_station",

    # Facilities
    "amenity.toilet": "toilet",
    "amenity.restroom": "toilet",

    # Recreation
    "leisure.park": "park",
    "leisure.playground": "park",

    # Religion
    "religion.place_of_worship": "place_of_worship",
    "religion.hindu": "place_of_worship",
    "religion.christian": "place_of_worship",
    "religion.muslim": "place_of_worship",
}


# =========================================================
# JUNK / INVALID NAMES
# =========================================================

JUNK_NAMES = {
    "",
    "unknown",
    "unnamed",
    "test",
    "sample",
    "null",
    "none",
}


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_text(value: Any) -> Optional[str]:
    """
    Safely convert a value into clean text.

    Handles:
    - None
    - strings
    - numbers
    - unexpected objects
    """

    if value is None:
        return None

    if isinstance(value, str):

        value = value.strip()

        if not value:
            return None

        # Collapse repeated whitespace.
        value = re.sub(
            r"\s+",
            " ",
            value
        )

        return value

    # Don't convert dictionaries/lists into ugly strings.
    if isinstance(value, (dict, list, tuple, set)):
        return None

    value = str(value).strip()

    return value if value else None


# =========================================================
# CATEGORY NORMALIZATION
# =========================================================

def normalize_category(
    categories: Any
) -> str:
    """
    Convert Geoapify categories into one
    TravelMate category.

    Example:

    catering.restaurant
        -> restaurant

    tourism.museum
        -> museum
    """

    if not categories:
        return "place"

    # Geoapify normally gives a list.
    if isinstance(categories, str):
        categories = [categories]

    # Defensive handling.
    if not isinstance(categories, (list, tuple, set)):
        return "place"

    for category in categories:

        if not isinstance(
            category,
            str
        ):
            continue

        category = (
            category
            .strip()
            .lower()
        )

        if not category:
            continue

        # Exact match.
        if category in CATEGORY_MAP:
            return CATEGORY_MAP[category]

        # Flexible matching.
        if "restaurant" in category:
            return "restaurant"

        if "cafe" in category:
            return "cafe"

        if (
            "museum" in category
            or "gallery" in category
        ):
            return "museum"

        if (
            "hotel" in category
            or "hostel" in category
            or "guest_house" in category
        ):
            return "hotel"

        if (
            "toilet" in category
            or "restroom" in category
        ):
            return "toilet"

        if "fuel" in category:
            return "fuel_station"

        if "park" in category:
            return "park"

        if "viewpoint" in category:
            return "viewpoint"

        if (
            "attraction" in category
            or "sights" in category
        ):
            return "attraction"

        if (
            "shopping" in category
            or "supermarket" in category
            or "mall" in category
            or "marketplace" in category
        ):
            return "shopping"

        if (
            "place_of_worship"
            in category
            or category.startswith("religion.")
        ):
            return "place_of_worship"

        if "hospital" in category:
            return "hospital"

        if "pharmacy" in category:
            return "pharmacy"

    return "place"


# =========================================================
# COORDINATE EXTRACTION
# =========================================================

def get_coordinates(
    place: Dict[str, Any]
):
    """
    Extract latitude and longitude from
    several possible Geoapify structures.
    """

    if not isinstance(place, dict):
        return None, None

    # -----------------------------------------------------
    # Direct fields
    # -----------------------------------------------------

    latitude = place.get("latitude")
    longitude = place.get("longitude")

    if latitude is None:
        latitude = place.get("lat")

    if longitude is None:
        longitude = place.get("lon")

    # -----------------------------------------------------
    # GeoJSON geometry
    # -----------------------------------------------------

    if (
        latitude is None
        or longitude is None
    ):

        geometry = place.get(
            "geometry"
        )

        if isinstance(
            geometry,
            dict
        ):

            coordinates = geometry.get(
                "coordinates"
            )

            if (
                isinstance(
                    coordinates,
                    (list, tuple)
                )
                and len(coordinates) >= 2
            ):

                longitude = coordinates[0]
                latitude = coordinates[1]

    # -----------------------------------------------------
    # Validate
    # -----------------------------------------------------

    try:

        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )

    except (
        TypeError,
        ValueError
    ):

        return None, None

    if not (
        -90 <= latitude <= 90
    ):
        return None, None

    if not (
        -180 <= longitude <= 180
    ):
        return None, None

    return latitude, longitude


# =========================================================
# NESTED VALUE HELPER
# =========================================================

def get_nested_value(
    source: Dict[str, Any],
    *keys: str
):
    """
    Safely retrieve nested dictionary values.

    Example:

    get_nested_value(
        source,
        "contact",
        "phone"
    )
    """

    current = source

    for key in keys:

        if not isinstance(
            current,
            dict
        ):
            return None

        current = current.get(
            key
        )

    return current


# =========================================================
# CLEAN ONE PLACE
# =========================================================

def clean_place(
    raw_place: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Convert one raw Geoapify place into
    a clean TravelMate place.
    """

    if not isinstance(
        raw_place,
        dict
    ):
        return None

    # -----------------------------------------------------
    # Coordinates
    # -----------------------------------------------------

    latitude, longitude = get_coordinates(
        raw_place
    )

    if (
        latitude is None
        or longitude is None
    ):
        return None

    # -----------------------------------------------------
    # Geoapify may store data in properties.
    # -----------------------------------------------------

    properties = raw_place.get(
        "properties"
    )

    if isinstance(
        properties,
        dict
    ):
        source = properties
    else:
        source = raw_place

    # -----------------------------------------------------
    # Name
    # -----------------------------------------------------

    name = (
        source.get("name")
        or source.get(
            "address_line1"
        )
        or source.get(
            "formatted"
        )
    )

    name = clean_text(name)

    if not name:
        return None

    # Remove obvious junk names.
    if name.lower() in JUNK_NAMES:
        return None

    # -----------------------------------------------------
    # Categories
    # -----------------------------------------------------

    raw_categories = (
        source.get("categories")
        or raw_place.get(
            "categories"
        )
        or []
    )

    # Keep categories safe.
    if isinstance(
        raw_categories,
        str
    ):
        category_list = [
            raw_categories
        ]

    elif isinstance(
        raw_categories,
        (list, tuple, set)
    ):
        category_list = [
            item
            for item in raw_categories
            if isinstance(
                item,
                str
            )
        ]

    else:
        category_list = []

    category = normalize_category(
        category_list
    )

    # -----------------------------------------------------
    # Address
    # -----------------------------------------------------

    address = (
        source.get("formatted")
        or source.get(
            "address_line2"
        )
        or source.get(
            "address_line1"
        )
    )

    address = clean_text(
        address
    )

    # -----------------------------------------------------
    # Description
    # -----------------------------------------------------

    description = clean_text(
        source.get(
            "description"
        )
    )

    # -----------------------------------------------------
    # Opening hours
    # -----------------------------------------------------

    opening_hours = clean_text(
        source.get(
            "opening_hours"
        )
    )

    # -----------------------------------------------------
    # Phone
    # -----------------------------------------------------

    phone = (
        get_nested_value(
            source,
            "contact",
            "phone"
        )
        or source.get(
            "contact:phone"
        )
        or source.get(
            "phone"
        )
    )

    phone = clean_text(
        phone
    )

    # -----------------------------------------------------
    # Website
    # -----------------------------------------------------

    website = clean_text(
        source.get(
            "website"
        )
    )

    # -----------------------------------------------------
    # Place ID
    # -----------------------------------------------------

    place_id = (
        source.get(
            "place_id"
        )
        or source.get(
            "id"
        )
        or raw_place.get(
            "place_id"
        )
    )

    place_id = clean_text(
        place_id
    )

    # -----------------------------------------------------
    # Other useful information
    # -----------------------------------------------------

    street = clean_text(
        source.get(
            "street"
        )
    )

    city = clean_text(
        source.get(
            "city"
        )
    )

    postcode = clean_text(
        source.get(
            "postcode"
        )
    )

    # -----------------------------------------------------
    # Map URL
    # -----------------------------------------------------

    map_url = (
        "https://www.openstreetmap.org/"
        f"?mlat={latitude}"
        f"&mlon={longitude}"
    )

    # -----------------------------------------------------
    # Final normalized place
    # -----------------------------------------------------

    return {

        "id": place_id,

        "name": name,

        "category": category,

        "categories": category_list,

        "latitude": latitude,

        "longitude": longitude,

        "description": description,

        "address": address,

        "street": street,

        "city": city,

        "postcode": postcode,

        "opening_hours": opening_hours,

        "phone": phone,

        "website": website,

        "map_url": map_url,
    }


# =========================================================
# REMOVE DUPLICATES
# =========================================================

def remove_duplicates(
    places: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Remove duplicate places using
    name + coordinates.
    """

    unique_places = []

    seen = set()

    for place in places:

        if not isinstance(
            place,
            dict
        ):
            continue

        name = clean_text(
            place.get("name")
        )

        latitude = place.get(
            "latitude"
        )

        longitude = place.get(
            "longitude"
        )

        if (
            not name
            or latitude is None
            or longitude is None
        ):
            continue

        key = (
            name.lower(),
            round(
                float(latitude),
                5
            ),
            round(
                float(longitude),
                5
            ),
        )

        if key in seen:
            continue

        seen.add(key)

        unique_places.append(
            place
        )

    return unique_places


# =========================================================
# MAIN CLEANER
# =========================================================

def clean_places(
    raw_places: List[Dict[str, Any]],
    max_places: int = 300
) -> List[Dict[str, Any]]:
    """
    Clean all raw Geoapify places.

    IMPORTANT:
    This function returns a LIST.

    places.py expects:

        unique_places = clean_places(...)

    Therefore it must NOT return a dictionary.
    """

    if not isinstance(
        raw_places,
        list
    ):
        return []

    cleaned = []

    # -----------------------------------------------------
    # Clean every place
    # -----------------------------------------------------

    for raw_place in raw_places:

        try:

            place = clean_place(
                raw_place
            )

            if place is not None:
                cleaned.append(
                    place
                )

        except Exception:
            # One bad record must not
            # break the entire search.
            continue

    # -----------------------------------------------------
    # Remove duplicates
    # -----------------------------------------------------

    cleaned = remove_duplicates(
        cleaned
    )

    # -----------------------------------------------------
    # Limit results
    # -----------------------------------------------------

    if max_places > 0:

        cleaned = cleaned[
            :max_places
        ]

    return cleaned