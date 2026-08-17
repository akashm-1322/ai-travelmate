import asyncio
import pprint

from app.tools.places import search_places


CITIES = [
    "Chennai",
    "Bangalore",
    "Mumbai",
    "Delhi",
    "Hyderabad",
    "Paris",
    "Tokyo",
]


async def main():

    for city in CITIES:

        print("\n" + "=" * 80)
        print(f"TESTING: {city}")
        print("=" * 80)

        try:

            result = await search_places(city)

            print(f"Success : {result.get('success')}")
            print(f"Location: {result.get('location')}")
            print(f"Count   : {result.get('count')}")

            if result.get("error"):
                print(f"ERROR   : {result['error']}")
                continue

            print("\nCategories:")

            for category, places in result.get("categories", {}).items():
                print(f"  {category}: {len(places)}")

            print("\nFirst 3 places:")

            for place in result.get("places", [])[:3]:
                pprint.pp(place)

        except Exception as e:

            print(f"EXCEPTION: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())