import os
from typing import Optional

import httpx
from dotenv import load_dotenv

from app.services.place_cleaner import clean_places


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

GEOCODING_URL = "https://api.geoapify.com/v1/geocode/search"
PLACES_URL = "https://api.geoapify.com/v2/places"


# ============================================================
# PLACE CATEGORIES
# ============================================================

PLACE_CATEGORIES = [
    "tourism",
    "tourism.attraction",
    "leisure.park",
    "catering.restaurant",
    "catering.cafe",
    "accommodation.hotel",
    "service.vehicle.fuel",
    "amenity.toilet",
    "commercial.shopping_mall",
    "religion.place_of_worship",
]


# ============================================================
# CITY ALIASES
# ============================================================

CITY_ALIASES = {

    # Tamil Nadu
    "madras": "Chennai",
    "chennai": "Chennai",

    "trichy": "Tiruchirappalli",
    "tiruchy": "Tiruchirappalli",
    "tiruchirapalli": "Tiruchirappalli",
    "tiruchirappalli": "Tiruchirappalli",

    "tanjore": "Thanjavur",
    "thanjore": "Thanjavur",
    "thanjavur": "Thanjavur",

    "madurai": "Madurai",

    "coimbatore": "Coimbatore",
    "kovai": "Coimbatore",

    "salem": "Salem",
    "erode": "Erode",
    "vellore": "Vellore",

    "tirunelveli": "Tirunelveli",

    "thoothukudi": "Thoothukudi",
    "tuticorin": "Thoothukudi",

    "dindigul": "Dindigul",
    "karur": "Karur",
    "namakkal": "Namakkal",
    "hosur": "Hosur",

    "kanchipuram": "Kanchipuram",
    "kancheepuram": "Kanchipuram",

    "tiruppur": "Tiruppur",
    "cuddalore": "Cuddalore",
    "nagapattinam": "Nagapattinam",
    "mayiladuthurai": "Mayiladuthurai",

    "sivakasi": "Sivakasi",
    "virudhunagar": "Virudhunagar",
    "ramanathapuram": "Ramanathapuram",
    "pudukkottai": "Pudukkottai",
    "pollachi": "Pollachi",

    "ooty": "Udagamandalam",
    "udhagamandalam": "Udagamandalam",

    "kodaikanal": "Kodaikanal",

    "rameswaram": "Rameswaram",
    "rameshwaram": "Rameswaram",

    "vellankanni": "Velankanni",
    "chidambaram": "Chidambaram",
    "kumbakonam": "Kumbakonam",
    "karaikudi": "Karaikudi",

    "arakkonam": "Arakkonam",
    "ambur": "Ambur",
    "ranipet": "Ranipet",

    "chengalpattu": "Chengalpattu",
    "chingleput": "Chengalpattu",

    "chromepet": "Chromepet",
    "tambaram": "Tambaram",
    "avadi": "Avadi",
    "porur": "Porur",

    "mahabalipuram": "Mahabalipuram",
    "mamallapuram": "Mahabalipuram",

    # Karnataka
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",

    "mysore": "Mysuru",
    "mysuru": "Mysuru",

    "mangalore": "Mangaluru",
    "mangaluru": "Mangaluru",

    "hubli": "Hubballi",
    "hubballi": "Hubballi",

    "belgaum": "Belagavi",
    "belagavi": "Belagavi",

    "gulbarga": "Kalaburagi",
    "kalaburagi": "Kalaburagi",

    "shimoga": "Shivamogga",
    "shivamogga": "Shivamogga",

    "tumkur": "Tumakuru",
    "tumakuru": "Tumakuru",

    "udupi": "Udupi",
    "coorg": "Kodagu",
    "madikeri": "Madikeri",

    # Maharashtra
    "bombay": "Mumbai",
    "mumbai": "Mumbai",
    "pune": "Pune",
    "nagpur": "Nagpur",
    "nashik": "Nashik",
    "nasik": "Nashik",

    "aurangabad": "Chhatrapati Sambhajinagar",
    "chhatrapati sambhajinagar": "Chhatrapati Sambhajinagar",

    "solapur": "Solapur",
    "kolhapur": "Kolhapur",
    "navi mumbai": "Navi Mumbai",
    "thane": "Thane",
    "satara": "Satara",
    "lonavala": "Lonavala",

    # Telangana
    "hyderabad": "Hyderabad",
    "warangal": "Warangal",
    "hanamkonda": "Hanamkonda",
    "karimnagar": "Karimnagar",
    "nizamabad": "Nizamabad",
    "khammam": "Khammam",

    # Andhra Pradesh
    "visakhapatnam": "Visakhapatnam",
    "vizag": "Visakhapatnam",
    "vijayawada": "Vijayawada",
    "tirupati": "Tirupati",
    "guntur": "Guntur",
    "nellore": "Nellore",
    "kakinada": "Kakinada",

    "rajahmundry": "Rajamahendravaram",
    "rajamahendravaram": "Rajamahendravaram",

    "anantapur": "Anantapur",
    "kadapa": "Kadapa",
    "kurnool": "Kurnool",

    # Kerala
    "kochi": "Kochi",
    "cochin": "Kochi",

    "thiruvananthapuram": "Thiruvananthapuram",
    "trivandrum": "Thiruvananthapuram",

    "kozhikode": "Kozhikode",
    "calicut": "Kozhikode",

    "thrissur": "Thrissur",
    "kollam": "Kollam",
    "quilon": "Kollam",

    "alappuzha": "Alappuzha",
    "alleppey": "Alappuzha",

    "kannur": "Kannur",
    "palakkad": "Palakkad",
    "kottayam": "Kottayam",

    # Delhi / NCR
    "delhi": "New Delhi",
    "new delhi": "New Delhi",
    "gurgaon": "Gurugram",
    "gurugram": "Gurugram",
    "noida": "Noida",
    "greater noida": "Greater Noida",
    "faridabad": "Faridabad",
    "ghaziabad": "Ghaziabad",

    # West Bengal
    "calcutta": "Kolkata",
    "kolkata": "Kolkata",
    "siliguri": "Siliguri",
    "durgapur": "Durgapur",
    "asansol": "Asansol",

    # Gujarat
    "ahmedabad": "Ahmedabad",
    "surat": "Surat",
    "vadodara": "Vadodara",
    "baroda": "Vadodara",
    "rajkot": "Rajkot",
    "gandhinagar": "Gandhinagar",
    "bhavnagar": "Bhavnagar",

    # Rajasthan
    "jaipur": "Jaipur",
    "jodhpur": "Jodhpur",
    "udaipur": "Udaipur",
    "kota": "Kota",
    "ajmer": "Ajmer",
    "bikaner": "Bikaner",

    # Uttar Pradesh
    "lucknow": "Lucknow",
    "kanpur": "Kanpur",
    "varanasi": "Varanasi",
    "banaras": "Varanasi",
    "agra": "Agra",

    "prayagraj": "Prayagraj",
    "allahabad": "Prayagraj",

    "meerut": "Meerut",
    "bareilly": "Bareilly",
    "mathura": "Mathura",
    "ayodhya": "Ayodhya",

    # Punjab
    "amritsar": "Amritsar",
    "ludhiana": "Ludhiana",
    "jalandhar": "Jalandhar",
    "patiala": "Patiala",

    # Bihar
    "patna": "Patna",
    "gaya": "Gaya",
    "muzaffarpur": "Muzaffarpur",

    # Odisha
    "bhubaneswar": "Bhubaneswar",
    "cuttack": "Cuttack",
    "puri": "Puri",
    "rourkela": "Rourkela",

    # Madhya Pradesh
    "bhopal": "Bhopal",
    "indore": "Indore",
    "gwalior": "Gwalior",
    "jabalpur": "Jabalpur",

    # Chhattisgarh
    "raipur": "Raipur",
    "bilaspur": "Bilaspur",

    # Jharkhand
    "ranchi": "Ranchi",
    "jamshedpur": "Jamshedpur",
    "dhanbad": "Dhanbad",

    # Assam
    "guwahati": "Guwahati",
    "dibrugarh": "Dibrugarh",

    # Goa
    "panaji": "Panaji",
    "panjim": "Panaji",
    "margao": "Margao",

    # Uttarakhand
    "dehradun": "Dehradun",
    "haridwar": "Haridwar",
    "rishikesh": "Rishikesh",
    "nainital": "Nainital",

    # Himachal Pradesh
    "shimla": "Shimla",
    "manali": "Manali",
    "dharamshala": "Dharamshala",

    # J&K
    "srinagar": "Srinagar",
    "jammu": "Jammu",

    # Northeast
    "imphal": "Imphal",
    "shillong": "Shillong",
    "aizawl": "Aizawl",
    "kohima": "Kohima",
    "gangtok": "Gangtok",
    "itanagar": "Itanagar",
}


# ============================================================
# CITY NORMALIZATION
# ============================================================

def normalize_city(city: str) -> str:

    if not city:
        return city

    cleaned = " ".join(
        city.strip().split()
    )

    return CITY_ALIASES.get(
        cleaned.lower(),
        cleaned
    )


# ============================================================
# GEOCODING
# ============================================================

async def _geocode_city(city: str):

    normalized_city = normalize_city(city)

    params = {
        "text": f"{normalized_city}, India",
        "type": "city",
        "format": "json",
        "limit": 5,
        "apiKey": GEOAPIFY_API_KEY,
    }

    async with httpx.AsyncClient(
        timeout=20,
        follow_redirects=True,
    ) as client:

        response = await client.get(
            GEOCODING_URL,
            params=params,
        )

        if response.status_code != 200:
            raise RuntimeError(
                "Geocoding failed: "
                f"HTTP {response.status_code}: "
                f"{response.text[:500]}"
            )

        data = response.json()

    results = data.get("results", [])

    if not results:
        raise RuntimeError(
            f"Could not find Indian city: {city}"
        )

    indian_results = [
        result
        for result in results
        if str(
            result.get("country", "")
        ).lower() == "india"
    ]

    return (
        indian_results[0]
        if indian_results
        else results[0]
    )


# ============================================================
# SEARCH PLACES
# ============================================================

async def search_places(city: str):

    if not GEOAPIFY_API_KEY:

        return {
            "success": False,
            "location": city,
            "count": 0,
            "categories": {},
            "places": [],
            "error": (
                "GEOAPIFY_API_KEY is missing "
                "from .env"
            ),
        }

    try:

        normalized_city = normalize_city(city)

        print(f"Requested city: {city}")
        print(f"Normalized city: {normalized_city}")

        # ----------------------------------------------------
        # GEOCODE
        # ----------------------------------------------------

        city_info = await _geocode_city(
            normalized_city
        )

        place_id = city_info.get("place_id")

        if not place_id:

            return {
                "success": False,
                "location": city,
                "count": 0,
                "categories": {},
                "places": [],
                "error": (
                    "Geoapify did not return "
                    "a place_id"
                ),
            }

        # ----------------------------------------------------
        # COUNTRY VALIDATION
        # ----------------------------------------------------

        country = str(
            city_info.get("country", "")
        ).lower()

        if country and country != "india":

            return {
                "success": False,
                "location": city,
                "count": 0,
                "categories": {},
                "places": [],
                "error": (
                    f"'{city}' resolved to "
                    f"{city_info.get('formatted')} "
                    "instead of an Indian city."
                ),
            }

        print(
            f"Geoapify city: "
            f"{city_info.get('formatted')}"
        )

        print(
            f"Geoapify place_id: "
            f"{place_id}"
        )

        # ----------------------------------------------------
        # QUERY PLACES
        # ----------------------------------------------------

        params = {
            "categories": ",".join(
                PLACE_CATEGORIES
            ),
            "filter": f"place:{place_id}",
            "limit": 100,
            "apiKey": GEOAPIFY_API_KEY,
        }

        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
        ) as client:

            response = await client.get(
                PLACES_URL,
                params=params,
            )

        if response.status_code != 200:

            return {
                "success": False,
                "location": city,
                "count": 0,
                "categories": {},
                "places": [],
                "error": (
                    "Geoapify Places API returned "
                    f"HTTP {response.status_code}: "
                    f"{response.text[:500]}"
                ),
            }

        data = response.json()

        # ----------------------------------------------------
        # EXTRACT RAW PLACES
        # ----------------------------------------------------

        raw_places = []

        for feature in data.get(
            "features",
            []
        ):

            properties = feature.get(
                "properties",
                {}
            )

            latitude = properties.get("lat")
            longitude = properties.get("lon")

            if (
                latitude is None
                or longitude is None
            ):
                continue

            name = (
                properties.get("name")
                or properties.get("address_line1")
                or properties.get("formatted")
            )

            if not name:
                continue

            categories = properties.get(
                "categories",
                []
            )

            if isinstance(
                categories,
                str
            ):
                categories = [categories]

            raw_places.append({

                "name": name,

                "latitude": latitude,

                "longitude": longitude,

                "category": (
                    categories[0]
                    if categories
                    else "place"
                ),

                "categories": categories,

                "description": properties.get(
                    "description"
                ),

                "address": properties.get(
                    "formatted"
                ),

                "street": properties.get(
                    "street"
                ),

                "city": properties.get(
                    "city"
                ),

                "postcode": properties.get(
                    "postcode"
                ),

                "opening_hours": properties.get(
                    "opening_hours"
                ),

                "phone": properties.get(
                    "contact:phone"
                ),

                "website": properties.get(
                    "website"
                ),

                "place_id": properties.get(
                    "place_id"
                ),

            })

        # ----------------------------------------------------
        # CLEAN
        # ----------------------------------------------------

        unique_places = clean_places(
            raw_places,
            max_places=200,
        )

        # ----------------------------------------------------
        # GROUP
        # ----------------------------------------------------

        categories = {}

        for place in unique_places:

            category = place.get(
                "category",
                "place"
            )

            categories.setdefault(
                category,
                []
            ).append(place)

        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        return {

            "success": True,

            "requested_city": city,

            "normalized_city": normalized_city,

            "location": (
                city_info.get("city")
                or city_info.get("name")
                or normalized_city
            ),

            "country": city_info.get(
                "country"
            ),

            "latitude": city_info.get(
                "lat"
            ),

            "longitude": city_info.get(
                "lon"
            ),

            "count": len(
                unique_places
            ),

            "categories": categories,

            "places": unique_places,
        }

    except httpx.RequestError as e:

        return {
            "success": False,
            "location": city,
            "count": 0,
            "categories": {},
            "places": [],
            "error": f"Network error: {str(e)}",
        }

    except Exception as e:

        return {
            "success": False,
            "location": city,
            "count": 0,
            "categories": {},
            "places": [],
            "error": str(e),
        }