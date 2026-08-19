import os
import tempfile
import time
import shutil

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form
)

from fastapi.responses import FileResponse

from app.services.voice_service import (
    speech_to_text,
    text_to_speech
)

from app.services.conversation_service import (
    conversation_service
)


router = APIRouter(
    prefix="/voice",
    tags=["Voice Assistant"]
)


@router.post("/")
async def voice_assistant(

    audio: UploadFile = File(...),

    conversation_id: str = Form("default")

):

    # ========================================================
    # REQUEST TIMER
    # ========================================================

    request_start = time.perf_counter()

    # ========================================================
    # 1. VALIDATE INPUT
    # ========================================================

    if not audio.filename:

        return {
            "success": False,
            "error": "Audio file is required"
        }

    # ========================================================
    # 2. SAVE INPUT AUDIO
    # ========================================================

    suffix = (
        os.path.splitext(
            audio.filename
        )[1]
        or ".wav"
    )

    input_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    )

    audio_path = input_file.name

    try:

        content = await audio.read()

        input_file.write(content)

        input_file.close()

        # ====================================================
        # TEMPORARY STEP 47 DEBUG AUDIO COPY
        # ====================================================

        debug_audio_directory = os.path.join(os.getcwd(),"debug_audio")

        os.makedirs(debug_audio_directory,exist_ok=True)

        debug_extension = (os.path.splitext(audio.filename)[1]or ".webm")

        debug_audio_path = os.path.join(debug_audio_directory,f"latest_voice_input{debug_extension}")

        shutil.copyfile(audio_path,debug_audio_path)

        print(f"Voice debug audio saved: "f"{debug_audio_path}")
        # ====================================================
        # 3. SPEECH TO TEXT
        # ====================================================

        stt_start = time.perf_counter()

        transcript = speech_to_text(
            audio_path
        )

        stt_end = time.perf_counter()

        if not transcript:

            return {
                "success": False,
                "error": "Could not understand the audio"
            }

        # ====================================================
        # 4. SHARED CONVERSATION PIPELINE
        # ====================================================

        conversation_start = time.perf_counter()

        result = await conversation_service.process_message(

            conversation_id=conversation_id,

            message=transcript,

            top_k=5

        )

        conversation_end = time.perf_counter()

        response = result["response"]

        # ====================================================
        # 5. TEXT TO SPEECH
        # ====================================================

        output_path = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3"
        ).name

        tts_start = time.perf_counter()

        # ====================================================
        # SHORTEN SPOKEN RESPONSE
        # ====================================================

        spoken_response = response

        MAX_SPEECH_CHARS = 650

        if len(spoken_response) > MAX_SPEECH_CHARS:

            shortened = spoken_response[:MAX_SPEECH_CHARS]

            last_period = shortened.rfind(".")

            if last_period > 300:
                shortened = shortened[:last_period + 1]

            spoken_response = (
            shortened
            + " You can ask me to explain any part in more detail."
        )

        await text_to_speech(
        text=spoken_response,
        output_path=output_path
        )

        tts_end = time.perf_counter()

        # ====================================================
        # 6. TOTAL
        # ====================================================

        request_end = time.perf_counter()

        stt_seconds = (
            stt_end
            - stt_start
        )

        conversation_seconds = (
            conversation_end
            - conversation_start
        )

        tts_seconds = (
            tts_end
            - tts_start
        )

        total_seconds = (
            request_end
            - request_start
        )

        # ====================================================
        # LATENCY REPORT
        # ====================================================

        print()
        print("=" * 70)
        print("VOICE LATENCY REPORT")
        print("=" * 70)

        print(
            f"Transcript: {transcript}"
        )

        print(
            f"STT:            "
            f"{stt_seconds:.2f} sec"
        )

        print(
            f"Conversation:   "
            f"{conversation_seconds:.2f} sec"
        )

        print(
            f"TTS:            "
            f"{tts_seconds:.2f} sec"
        )

        print(
            f"TOTAL:          "
            f"{total_seconds:.2f} sec"
        )

        print("=" * 70)
        print()

        # ====================================================
        # 7. RETURN AUDIO
        # ====================================================

        return FileResponse(

            output_path,

            media_type="audio/mpeg",

            filename="travelmate_response.mp3",

            headers={

                "X-Conversation-ID":
                    conversation_id,

                "X-Transcript":
                    transcript,

                "X-STT-Time":
                    f"{stt_seconds:.3f}",

                "X-Conversation-Time":
                    f"{conversation_seconds:.3f}",

                "X-TTS-Time":
                    f"{tts_seconds:.3f}",

                "X-Total-Time":
                    f"{total_seconds:.3f}"

            }

        )

    finally:

        # ====================================================
        # 8. CLEAN INPUT FILE
        # ====================================================

        if os.path.exists(audio_path):

            os.remove(audio_path)