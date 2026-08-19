from typing import Any

from fastapi import (
    APIRouter,
    HTTPException,
)

from pydantic import BaseModel

from app.tools.weather import (
    get_weather,
    get_hourly_forecast,
)

from app.services.forecast_services import (
    analyze_forecast_timing,
)

from app.services.disruption_service import (
    analyze_itinerary_disruptions,
    apply_disruption_swap,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/disruptions",
    tags=[
        "Dynamic Travel Copilot"
    ],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class DisruptionRequest(
    BaseModel
):

    city: str

    itinerary: dict[
        str,
        Any
    ]


class ForecastTimingRequest(
    BaseModel
):

    city: str

    start_date: str

    itinerary: dict[
        str,
        Any
    ]


class ApplyDisruptionRequest(
    BaseModel
):

    itinerary: dict[
        str,
        Any
    ]

    day: int

    from_index: int

    to_index: int


# ============================================================
# CURRENT-WEATHER DISRUPTION ANALYSIS
# ============================================================

@router.post(
    "/analyze"
)
async def analyze_disruptions(
    request: DisruptionRequest
):

    city = (
        request.city
        or ""
    ).strip()


    if not city:

        raise HTTPException(
            status_code=400,
            detail="City is required."
        )


    if not request.itinerary:

        raise HTTPException(
            status_code=400,
            detail="Itinerary is required."
        )


    # ========================================================
    # 1. FETCH CURRENT WEATHER
    # ========================================================

    weather = await get_weather(
        city
    )


    if not weather.get(
        "success"
    ):

        raise HTTPException(
            status_code=503,
            detail=(
                weather.get(
                    "error"
                )
                or
                "Weather service unavailable."
            )
        )


    # ========================================================
    # 2. ANALYZE CURRENT ITINERARY
    # ========================================================

    result = (
        analyze_itinerary_disruptions(
            itinerary=(
                request.itinerary
            ),
            weather=(
                weather
            ),
        )
    )


    # ========================================================
    # 3. RETURN
    # ========================================================

    return {
        "success": True,
        **result,
    }


# ============================================================
# APPLY ITINERARY SWAP
# ============================================================

@router.post(
    "/apply"
)
async def apply_disruption(
    request: ApplyDisruptionRequest
):

    if not request.itinerary:

        raise HTTPException(
            status_code=400,
            detail="Itinerary is required."
        )


    try:

        updated_itinerary = (
            apply_disruption_swap(
                itinerary=(
                    request.itinerary
                ),
                day_number=(
                    request.day
                ),
                from_index=(
                    request.from_index
                ),
                to_index=(
                    request.to_index
                ),
            )
        )


    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(
                exc
            )
        )


    return {
        "success": True,

        "message": (
            "Suggested itinerary "
            "adjustment applied."
        ),

        "itinerary":
            updated_itinerary,
    }


# ============================================================
# FORECAST-AWARE TIMING ANALYSIS
# ============================================================

@router.post(
    "/forecast-analyze"
)
async def analyze_forecast_disruptions(
    request: ForecastTimingRequest
):

    city = (
        request.city
        or ""
    ).strip()


    # ========================================================
    # 1. VALIDATE
    # ========================================================

    if not city:

        raise HTTPException(
            status_code=400,
            detail="City is required."
        )


    if not request.start_date:

        raise HTTPException(
            status_code=400,
            detail=(
                "Trip start date is required."
            )
        )


    if not request.itinerary:

        raise HTTPException(
            status_code=400,
            detail="Itinerary is required."
        )


    # ========================================================
    # 2. FETCH HOURLY FORECAST
    # ========================================================

    forecast = (
        await get_hourly_forecast(
            city
        )
    )


    if not forecast.get(
        "success"
    ):

        raise HTTPException(
            status_code=503,
            detail=(
                forecast.get(
                    "error"
                )
                or
                "Hourly forecast unavailable."
            )
        )


    # ========================================================
    # 3. FORECAST TIMING ANALYSIS
    # ========================================================

    try:

        result = (
            analyze_forecast_timing(
                itinerary=(
                    request.itinerary
                ),
                forecast=(
                    forecast
                ),
                start_date=(
                    request.start_date
                ),
            )
        )


    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(
                exc
            )
        )


    except Exception as exc:

        print(
            "Forecast timing analysis error: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "TravelMate could not analyze "
                "forecast timing."
            )
        )


    # ========================================================
    # 4. DIAGNOSTIC LOG
    # ========================================================

    print()
    print("=" * 70)
    print("FORECAST TIMING ANALYSIS")
    print("=" * 70)

    print(
        f"Location: "
        f"{forecast.get('location')}"
    )

    print(
        f"Start date: "
        f"{request.start_date}"
    )

    print(
        f"Has timing risks: "
        f"{result.get('has_timing_risks')}"
    )

    print(
        f"Alert count: "
        f"{result.get('alert_count')}"
    )


    for alert in result.get(
        "alerts",
        []
    ):

        print()

        print(
            f"Place: "
            f"{alert.get('place_name')}"
        )

        print(
            f"Scheduled time: "
            f"{alert.get('arrival_time')}"
        )

        print(
            f"Risk score: "
            f"{alert.get('risk_score')}"
        )

        print(
            f"Forecast: "
            f"{alert.get('forecast')}"
        )

        print(
            f"Smart timing: "
            f"{alert.get('smart_timing')}"
        )


    print("=" * 70)
    print()


    # ========================================================
    # 5. RETURN
    # ========================================================

    return {
        "success": True,

        "forecast_location":
            forecast.get(
                "location"
            ),

        "timezone":
            forecast.get(
                "timezone"
            ),

        **result,
    }