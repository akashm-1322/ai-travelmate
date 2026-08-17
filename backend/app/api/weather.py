from fastapi import APIRouter, HTTPException

from app.tools.weather import get_weather


router = APIRouter(
    prefix="/weather",
    tags=["Weather"]
)


@router.get("/{city}")
async def weather(city: str):

    result = await get_weather(city)

    if not result["success"]:
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )

    return result