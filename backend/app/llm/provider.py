import os
import asyncio
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.tools.weather import get_weather
from app.tools.places import search_places

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=GEMINI_API_KEY)


MODELS = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
]


SYSTEM_INSTRUCTION = """
You are AI TravelMate, an intelligent travel planning assistant.

Your responsibilities:

1. Help users plan trips.
2. Recommend destinations, attractions, food and activities.
3. Give practical and budget-conscious travel advice.
4. Use live tools when the user asks for real-time information.
5. Never invent current weather information.
6. Use the places tool when the user asks for real places, attractions,
   restaurants, cafes, hotels, fuel stations, shopping malls, parks,
   temples or other locations in a city.

AVAILABLE TOOLS:

get_weather(city)
- Use this tool whenever the user asks about:
  - current temperature
  - current weather
  - humidity
  - rain
  - wind
  - current weather conditions.

search_places(city)
- Use this tool when the user asks about actual places in a city.
- Use it for attractions, restaurants, cafes, hotels, parks,
  shopping malls, fuel stations, temples and other places.
- Prefer information returned by this tool instead of inventing places.

For normal travel planning questions, answer naturally.
"""


# ---------------------------------------------------------
# WEATHER TOOL DEFINITION FOR GEMINI
# ---------------------------------------------------------

weather_tool = types.FunctionDeclaration(
    name="get_weather",
    description=(
        "Get the current weather information for a city. "
        "Use this for current temperature, humidity, "
        "precipitation, wind and weather conditions."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "city": types.Schema(
                type=types.Type.STRING,
                description="Name of the city"
            )
        },
        required=["city"]
    )
)

# ---------------------------------------------------------
# PLACES TOOL DEFINITION FOR GEMINI
# ---------------------------------------------------------

places_tool = types.FunctionDeclaration(
    name="search_places",
    description=(
        "Search for real places in a city using Geoapify. "
        "Returns attractions, restaurants, cafes, hotels, "
        "parks, shopping malls, fuel stations, places of worship "
        "and other locations."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "city": types.Schema(
                type=types.Type.STRING,
                description="Name of the city to search"
            )
        },
        required=["city"]
    )
)

tool_config = types.Tool(
    function_declarations=[
        weather_tool,
        places_tool
    ]
)


# ---------------------------------------------------------
# MANUAL TOOL EXECUTION
# ---------------------------------------------------------

async def execute_tool(
    function_name: str,
    arguments: dict
):

    # -----------------------------------------------------
    # WEATHER
    # -----------------------------------------------------

    if function_name == "get_weather":

        city = arguments.get("city")

        if not city:

            return {
                "success": False,
                "error": "City is required"
            }

        return await get_weather(city)


    # -----------------------------------------------------
    # PLACES
    # -----------------------------------------------------

    if function_name == "search_places":

        city = arguments.get("city")

        if not city:

            return {
                "success": False,
                "error": "City is required"
            }

        return await search_places(city)


    # -----------------------------------------------------
    # UNKNOWN TOOL
    # -----------------------------------------------------

    return {
        "success": False,
        "error": (
            f"Unknown tool: {function_name}"
        )
    }
# ---------------------------------------------------------
# GEMINI REQUEST
# ---------------------------------------------------------

async def generate_response(
    prompt: str,
    conversation_history=None,
    retrieved_documents=None
) -> str:

    conversation_history = conversation_history or []
    retrieved_documents = retrieved_documents or []

    last_error = None

    # ---------------------------------------------------------
    # BUILD CONTEXT
    # ---------------------------------------------------------

    history_text = ""

    for message in conversation_history:

        role = message.get("role", "user")
        content = message.get("content", "")

        history_text += (
            f"{role}: {content}\n"
        )

    retrieved_text = ""

    for document in retrieved_documents:

        content = document.get(
            "content",
            ""
        )

        if content:

            retrieved_text += (
                f"\n{content}\n"
            )

    # ---------------------------------------------------------
    # FINAL PROMPT
    # ---------------------------------------------------------

    full_prompt = f"""
CONVERSATION HISTORY:

{history_text}

RELEVANT KNOWLEDGE:

{retrieved_text}

CURRENT USER MESSAGE:

{prompt}
"""

    for model in MODELS:

        try:

            print(
                f"Trying model: {model}"
            )

            contents = [

                types.Content(

                    role="user",

                    parts=[

                        types.Part(
                            text=full_prompt
                        )

                    ]

                )

            ]

            response = client.models.generate_content(

                model=model,

                contents=contents,

                config=types.GenerateContentConfig(

                    system_instruction=SYSTEM_INSTRUCTION,

                    tools=[
                        tool_config
                    ],

                    temperature=0.3,

                ),

            )

            # -------------------------------------------------
            # CHECK TOOL CALL
            # -------------------------------------------------

            function_call = None

            if response.candidates:

                for candidate in response.candidates:

                    if not candidate.content:
                        continue

                    for part in candidate.content.parts:

                        if part.function_call:

                            function_call = (
                                part.function_call
                            )

                            break

                    if function_call:
                        break

            # -------------------------------------------------
            # NORMAL RESPONSE
            # -------------------------------------------------

            if not function_call:

                print(
                    f"Successful model: {model}"
                )

                return (
                    response.text
                    or
                    "I couldn't generate a response."
                )

            # -------------------------------------------------
            # TOOL CALL
            # -------------------------------------------------

            print(
                f"Tool requested: "
                f"{function_call.name}"
            )

            arguments = dict(
                function_call.args or {}
            )

            print(
                f"Tool arguments: "
                f"{arguments}"
            )

            tool_result = await execute_tool(

                function_call.name,

                arguments

            )

            print(
                f"Tool result: "
                f"{tool_result}"
            )

            # -------------------------------------------------
            # SEND TOOL RESULT BACK
            # -------------------------------------------------

            contents.append(
                response.candidates[0].content
            )

            contents.append(

                types.Content(

                    role="tool",

                    parts=[

                        types.Part(

                            function_response=(
                                types.FunctionResponse(

                                    name=(
                                        function_call.name
                                    ),

                                    response=tool_result

                                )
                            )

                        )

                    ]

                )

            )

            final_response = (
                client.models.generate_content(

                    model=model,

                    contents=contents,

                    config=(
                        types.GenerateContentConfig(

                            system_instruction=(
                                SYSTEM_INSTRUCTION
                            ),

                            tools=[
                                tool_config
                            ],

                            temperature=0.3,

                        )
                    ),

                )
            )

            print(
                f"Successful model: {model}"
            )

            return (
                final_response.text
                or
                "I couldn't generate a final response."
            )

        except Exception as e:

            last_error = e

            print(
                f"Model {model} failed: "
                f"{type(e).__name__}: {e}"
            )

            await asyncio.sleep(1)

            continue

    raise RuntimeError(
        f"All Gemini models failed. "
        f"Last error: {last_error}"
    )