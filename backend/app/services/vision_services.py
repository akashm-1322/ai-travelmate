import json
import os

from dotenv import load_dotenv

from google import genai
from google.genai import types


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


if not GEMINI_API_KEY:

    raise RuntimeError(
        "GEMINI_API_KEY is not configured"
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# VISION MODEL FALLBACKS
# ============================================================

VISION_MODELS = [

    "gemini-3.6-flash",

    "gemini-3.5-flash-lite",

    "gemini-3.1-flash-lite",

]


# ============================================================
# VISION PROMPT
# ============================================================

VISION_PROMPT = """
You are AI TravelMate Sightseeing Lens.

Analyze the supplied travel image carefully.

The image may contain:

- a landmark
- monument
- temple
- church
- mosque
- museum
- beach
- historical structure
- street scene
- restaurant
- menu
- food
- sign board
- foreign language text
- ordinary travel object

Return ONLY valid JSON.

Use exactly this structure:

{
  "analysis_type": "landmark | menu | food | sign | object | unknown",

  "place_name": "",

  "city_or_region": "",

  "country": "",

  "summary": "",

  "history": "",

  "interesting_facts": [],

  "detected_text": "",

  "translation": "",

  "vegetarian_items": [],

  "travel_tip": "",

  "confidence": 0.0
}

RULES:

1. Do not pretend to know the exact landmark if uncertain.

2. If uncertain, clearly say so in the summary
   and reduce the confidence value.

3. confidence must be between 0 and 1.

4. For landmarks:
   focus on identification, architecture,
   cultural significance, history and useful
   visitor context.

5. For menus:
   extract visible text,
   translate when necessary,
   and identify likely vegetarian dishes.

6. For signs:
   extract and translate visible text.

7. If information is not applicable,
   return an empty string or empty list.

8. Do not use markdown.

9. Do not wrap the JSON in code fences.

10. Never invent:
    - current opening hours
    - current ticket prices
    - live availability
    - current events
    - other real-time information

11. If the exact location cannot be reliably
    inferred from the image, leave city_or_region
    or country empty rather than guessing.

12. Make summary suitable for a travel application.

13. Keep interesting_facts concise.
"""


# ============================================================
# NORMALIZE RESULT
# ============================================================

def normalize_analysis(
    result: dict
) -> dict:

    if not isinstance(
        result,
        dict
    ):

        raise ValueError(
            "Vision response must be a JSON object"
        )


    # --------------------------------------------------------
    # DEFAULT STRING FIELDS
    # --------------------------------------------------------

    string_fields = [

        "analysis_type",

        "place_name",

        "city_or_region",

        "country",

        "summary",

        "history",

        "detected_text",

        "translation",

        "travel_tip",

    ]


    for field in string_fields:

        value = result.get(
            field
        )


        if value is None:

            result[field] = ""

        elif not isinstance(
            value,
            str
        ):

            result[field] = str(
                value
            )


    if not result[
        "analysis_type"
    ]:

        result[
            "analysis_type"
        ] = "unknown"


    # --------------------------------------------------------
    # ALLOWED ANALYSIS TYPES
    # --------------------------------------------------------

    allowed_types = {

        "landmark",

        "menu",

        "food",

        "sign",

        "object",

        "unknown",

    }


    if (
        result[
            "analysis_type"
        ].lower()
        not in allowed_types
    ):

        result[
            "analysis_type"
        ] = "unknown"

    else:

        result[
            "analysis_type"
        ] = (
            result[
                "analysis_type"
            ].lower()
        )


    # --------------------------------------------------------
    # LIST FIELDS
    # --------------------------------------------------------

    interesting_facts = result.get(
        "interesting_facts",
        []
    )


    if not isinstance(
        interesting_facts,
        list
    ):

        interesting_facts = []


    result[
        "interesting_facts"
    ] = [

        str(item).strip()

        for item
        in interesting_facts

        if str(item).strip()

    ]


    vegetarian_items = result.get(
        "vegetarian_items",
        []
    )


    if not isinstance(
        vegetarian_items,
        list
    ):

        vegetarian_items = []


    result[
        "vegetarian_items"
    ] = [

        str(item).strip()

        for item
        in vegetarian_items

        if str(item).strip()

    ]


    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    confidence = result.get(
        "confidence",
        0.0
    )


    try:

        confidence = float(
            confidence
        )

    except (
        TypeError,
        ValueError
    ):

        confidence = 0.0


    result["confidence"] = max(

        0.0,

        min(
            1.0,
            confidence
        )

    )


    return result


# ============================================================
# ANALYZE TRAVEL IMAGE
# ============================================================

async def analyze_travel_image(
    image_bytes: bytes,
    mime_type: str
) -> dict:

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not image_bytes:

        raise ValueError(
            "Image data is empty"
        )


    if not mime_type:

        raise ValueError(
            "Image MIME type is missing"
        )


    if not mime_type.startswith(
        "image/"
    ):

        raise ValueError(
            "Unsupported file type"
        )


    last_error = None

    quota_error = None


    # ========================================================
    # TRY MODELS IN ORDER
    # ========================================================

    for model in VISION_MODELS:

        try:

            print()

            print(
                f"Trying vision model: "
                f"{model}"
            )


            # ------------------------------------------------
            # GEMINI MULTIMODAL REQUEST
            # ------------------------------------------------

            response = (
                client.models.generate_content(

                    model=model,

                    contents=[

                        VISION_PROMPT,

                        types.Part.from_bytes(

                            data=image_bytes,

                            mime_type=mime_type

                        )

                    ],

                    config=(
                        types.GenerateContentConfig(

                            response_mime_type=(
                                "application/json"
                            )

                        )
                    )

                )
            )


            # ------------------------------------------------
            # READ RESPONSE
            # ------------------------------------------------

            raw_response = (
                response.text
                or ""
            ).strip()


            if not raw_response:

                raise RuntimeError(
                    "Vision model returned no response"
                )


            # ------------------------------------------------
            # PARSE JSON
            # ------------------------------------------------

            try:

                result = json.loads(
                    raw_response
                )

            except json.JSONDecodeError as exc:

                raise RuntimeError(
                    "Vision model returned invalid JSON. "
                    f"{exc}"
                ) from exc


            # ------------------------------------------------
            # NORMALIZE RESULT
            # ------------------------------------------------

            result = normalize_analysis(
                result
            )


            print(
                f"Successful vision model: "
                f"{model}"
            )


            return result


        except Exception as exc:

            last_error = exc

            error_text = str(
                exc
            )


            print(
                f"Vision model {model} failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )


            # ------------------------------------------------
            # QUOTA / RATE LIMIT
            # ------------------------------------------------

            if (
                "429" in error_text
                or
                "RESOURCE_EXHAUSTED"
                in error_text
            ):

                quota_error = exc

                print(
                    "Vision model quota exhausted. "
                    "Trying fallback model..."
                )

                continue


            # ------------------------------------------------
            # MODEL NOT AVAILABLE
            # ------------------------------------------------

            if (
                "404" in error_text
                or
                "NOT_FOUND"
                in error_text
            ):

                print(
                    "Vision model unavailable. "
                    "Trying fallback model..."
                )

                continue


            # ------------------------------------------------
            # OTHER MODEL ERROR
            # ------------------------------------------------

            print(
                "Vision model failed. "
                "Trying fallback model..."
            )

            continue


    # ========================================================
    # ALL MODELS FAILED
    # ========================================================

    if quota_error is not None:

        raise RuntimeError(

            "VISION_QUOTA_EXHAUSTED: "
            "All currently usable Gemini vision "
            "models are rate-limited or unavailable. "
            f"Last error: {last_error}"

        )


    raise RuntimeError(

        "VISION_MODELS_FAILED: "
        "All Gemini vision models failed. "
        f"Last error: {last_error}"

    )