from fastapi import APIRouter , HTTPException

from app.tools.places import search_places


router = APIRouter(
    prefix="/places",
    tags=["Places"]
)


@router.get("/{city}")
async def places(city: str):

    result = await search_places(city)

    if not result["success"]:
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )

    return result