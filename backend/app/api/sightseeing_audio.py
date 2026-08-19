import os
import tempfile

from fastapi import (
    APIRouter,
    HTTPException,
)

from fastapi.responses import FileResponse

from pydantic import BaseModel

from app.services.voice_service import (
    text_to_speech,
)


router = APIRouter(
    prefix="/sightseeing-audio",
    tags=["Sightseeing Audio Guide"],
)


class SightseeingAudioRequest(BaseModel):

    place_name: str = ""

    summary: str = ""

    history: str = ""

    travel_tip: str = ""


@router.post("/")
async def generate_sightseeing_audio(
    request: SightseeingAudioRequest
):

    # ========================================================
    # 1. BUILD NATURAL AUDIO GUIDE
    # ========================================================

    sections = []


    if request.place_name.strip():

        sections.append(
            f"You are looking at {request.place_name.strip()}."
        )


    if request.summary.strip():

        sections.append(
            request.summary.strip()
        )


    if request.history.strip():

        sections.append(
            f"Here is a little history. "
            f"{request.history.strip()}"
        )


    if request.travel_tip.strip():

        sections.append(
            f"TravelMate tip. "
            f"{request.travel_tip.strip()}"
        )


    speech_text = " ".join(
        sections
    ).strip()


    if not speech_text:

        raise HTTPException(
            status_code=400,
            detail=(
                "There is no sightseeing information "
                "available to speak."
            ),
        )


    # Keep audio guides reasonably concise.

    MAX_CHARS = 1800

    if len(speech_text) > MAX_CHARS:

        shortened = (
            speech_text[:MAX_CHARS]
        )

        last_period = (
            shortened.rfind(".")
        )

        if last_period > 500:

            shortened = (
                shortened[
                    :last_period + 1
                ]
            )


        speech_text = shortened


    # ========================================================
    # 2. GENERATE TEMPORARY MP3
    # ========================================================

    output_file = (
        tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3",
        )
    )

    output_path = (
        output_file.name
    )

    output_file.close()


    try:

        await text_to_speech(
            text=speech_text,
            output_path=output_path,
        )


        return FileResponse(

            output_path,

            media_type="audio/mpeg",

            filename=(
                "travelmate_sightseeing_guide.mp3"
            ),

        )


    except Exception as exc:

        if os.path.exists(
            output_path
        ):

            os.remove(
                output_path
            )


        print(
            "Sightseeing audio error: "
            f"{type(exc).__name__}: {exc}"
        )


        raise HTTPException(
            status_code=500,
            detail=(
                "TravelMate could not generate "
                "the sightseeing audio guide."
            ),
        )