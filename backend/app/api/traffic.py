from fastapi import (
    APIRouter,
    HTTPException,
)

from pydantic import BaseModel


from app.services.traffic_routing_service import (
    get_traffic_route,
)


router = APIRouter(
    prefix="/traffic",
    tags=[
        "Traffic Routing"
    ],
)


class TrafficRouteRequest(
    BaseModel
):

    origin_latitude: float
    origin_longitude: float

    destination_latitude: float
    destination_longitude: float


@router.post(
    "/route"
)
async def calculate_traffic_route(
    request: TrafficRouteRequest
):

    result = (
        await get_traffic_route(

            origin_latitude=(
                request.origin_latitude
            ),

            origin_longitude=(
                request.origin_longitude
            ),

            destination_latitude=(
                request.destination_latitude
            ),

            destination_longitude=(
                request.destination_longitude
            ),

        )
    )


    if not result.get(
        "success"
    ):

        raise HTTPException(

            status_code=503,

            detail=(
                result.get(
                    "error"
                )
                or
                "Traffic routing unavailable."
            ),

        )


    return result