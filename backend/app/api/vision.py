from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from app.services.vision_services import (
    analyze_travel_image,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(

    prefix="/vision",

    tags=[
        "Sightseeing Lens"
    ]

)


# ============================================================
# LIMITS
# ============================================================

MAX_IMAGE_SIZE = (
    10
    * 1024
    * 1024
)


ALLOWED_IMAGE_TYPES = {

    "image/jpeg",

    "image/jpg",

    "image/png",

    "image/webp",

}


# ============================================================
# ANALYZE IMAGE
# ============================================================

@router.post(
    "/analyze"
)
async def analyze_image(

    image: UploadFile = File(...)

):

    # ========================================================
    # 1. VALIDATE CONTENT TYPE
    # ========================================================

    content_type = (

        image.content_type
        or ""

    ).lower()


    if (
        content_type
        not in ALLOWED_IMAGE_TYPES
    ):

        raise HTTPException(

            status_code=400,

            detail=(

                "Unsupported image format. "
                "Please use JPEG, PNG or WebP."

            )

        )


    # ========================================================
    # 2. READ IMAGE
    #
    # The image remains request-scoped.
    # We do not save it to the filesystem or database.
    # ========================================================

    try:

        image_bytes = (
            await image.read()
        )


    except Exception as exc:

        print(
            "Image read error: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )


        raise HTTPException(

            status_code=400,

            detail=(
                "TravelMate could not read "
                "the supplied image."
            )

        )


    # ========================================================
    # 3. VALIDATE IMAGE CONTENT
    # ========================================================

    if not image_bytes:

        raise HTTPException(

            status_code=400,

            detail=(
                "The captured image is empty."
            )

        )


    if (
        len(image_bytes)
        > MAX_IMAGE_SIZE
    ):

        raise HTTPException(

            status_code=413,

            detail=(

                "The image is too large. "
                "Maximum supported size is 10 MB."

            )

        )


    # ========================================================
    # 4. ANALYZE IMAGE
    # ========================================================

    try:

        analysis = (
            await analyze_travel_image(

                image_bytes=(
                    image_bytes
                ),

                mime_type=(
                    content_type
                )

            )
        )


    except ValueError as exc:

        # ----------------------------------------------------
        # INVALID INPUT
        # ----------------------------------------------------

        print(
            "Sightseeing validation error: "
            f"{exc}"
        )


        raise HTTPException(

            status_code=400,

            detail=str(
                exc
            )

        )


    except RuntimeError as exc:

        error_text = str(
            exc
        )


        print(
            "Sightseeing analysis error: "
            f"{error_text}"
        )


        # ----------------------------------------------------
        # QUOTA / RATE LIMIT
        # ----------------------------------------------------

        if (
            "VISION_QUOTA_EXHAUSTED"
            in error_text
        ):

            raise HTTPException(

                status_code=429,

                detail=(

                    "Sightseeing Lens AI is temporarily "
                    "rate-limited. Your captured photo "
                    "is still available in the session "
                    "album. Please try analysis again later."

                )

            )


        # ----------------------------------------------------
        # ALL MODEL FALLBACKS FAILED
        # ----------------------------------------------------

        raise HTTPException(

            status_code=503,

            detail=(

                "Sightseeing Lens AI is temporarily "
                "unavailable. Please try again later."

            )

        )


    except Exception as exc:

        # ----------------------------------------------------
        # UNEXPECTED ERROR
        # ----------------------------------------------------

        print(

            "Unexpected sightseeing analysis error: "

            f"{type(exc).__name__}: "

            f"{exc}"

        )


        raise HTTPException(

            status_code=500,

            detail=(

                "TravelMate encountered an unexpected "
                "error while analyzing this image."

            )

        )


    # ========================================================
    # 5. RETURN STRUCTURED RESULT
    # ========================================================

    return {

        "success":
            True,

        "analysis":
            analysis,

    }