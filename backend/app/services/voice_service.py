import os
import re

import edge_tts
from faster_whisper import WhisperModel


# ============================================================
# WHISPER CONFIGURATION
# ============================================================

WHISPER_MODEL = os.getenv(
    "WHISPER_MODEL",
    "base.en"
)

WHISPER_DEVICE = os.getenv(
    "WHISPER_DEVICE",
    "cpu"
)

WHISPER_COMPUTE_TYPE = os.getenv(
    "WHISPER_COMPUTE_TYPE",
    "int8"
)


# ============================================================
# SUPPORTED AUDIO
# ============================================================

SUPPORTED_AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".ogg",
    ".webm",
    ".flac",
    ".mp4",
}


# ============================================================
# LOAD WHISPER ONCE
# ============================================================

whisper_model = WhisperModel(
    WHISPER_MODEL,
    device=WHISPER_DEVICE,
    compute_type=WHISPER_COMPUTE_TYPE
)


# ============================================================
# AUDIO VALIDATION
# ============================================================

def validate_audio_extension(
    filename: str
) -> bool:

    if not filename:
        return False

    extension = os.path.splitext(
        filename
    )[1].lower()

    return extension in SUPPORTED_AUDIO_EXTENSIONS


# ============================================================
# SPEECH TO TEXT
# ============================================================

def speech_to_text(
    audio_path: str
) -> str:

    segments, info = whisper_model.transcribe(

        audio_path,

        language="en",

        task="transcribe",

        beam_size=1,

        best_of=1,

        temperature=0.0,

        vad_filter=True,

        vad_parameters=dict(
            min_silence_duration_ms=350,
            speech_pad_ms=500
        ),

        condition_on_previous_text=False,

        # Reject likely silence / hallucination
        no_speech_threshold=0.6,

        log_prob_threshold=-1.0,

        compression_ratio_threshold=2.4,

        initial_prompt=(
            "English speech to AI TravelMate. "
            "The user is asking a travel-related question. "
            "Common words include Chennai, Bengaluru, temples, "
            "beaches, restaurants, hotels, flights, weather, "
            "places to visit and itinerary."
        )
    )

    collected_text = []

    valid_speech_found = False

    for segment in segments:

        text = segment.text.strip()

        if not text:
            continue

        # ----------------------------------------------------
        # Reject extremely low-confidence segments
        # ----------------------------------------------------

        if (
            segment.no_speech_prob > 0.75
            and
            segment.avg_logprob < -1.0
        ):
            continue

        valid_speech_found = True

        collected_text.append(
            text
        )

    if not valid_speech_found:
        return ""

    transcript = " ".join(
        collected_text
    )

    return transcript.strip()


def clean_text_for_speech(
    text: str
) -> str:

    if not text:
        return ""

    cleaned = text

    # --------------------------------------------------------
    # REMOVE MARKDOWN HEADINGS
    # ### Day 1 -> Day 1
    # --------------------------------------------------------

    cleaned = re.sub(
        r"^\s*#{1,6}\s*",
        "",
        cleaned,
        flags=re.MULTILINE
    )

    # --------------------------------------------------------
    # REMOVE MARKDOWN BOLD / ITALICS
    # **Chennai** -> Chennai
    # *Chennai*   -> Chennai
    # __Chennai__ -> Chennai
    # --------------------------------------------------------

    cleaned = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        cleaned
    )

    cleaned = re.sub(
        r"__(.*?)__",
        r"\1",
        cleaned
    )

    cleaned = re.sub(
        r"\*(.*?)\*",
        r"\1",
        cleaned
    )

    cleaned = re.sub(
        r"_(.*?)_",
        r"\1",
        cleaned
    )

    # --------------------------------------------------------
    # MARKDOWN LINKS
    # [Marina Beach](url) -> Marina Beach
    # --------------------------------------------------------

    cleaned = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        cleaned
    )

    # --------------------------------------------------------
    # RAW URLS
    # --------------------------------------------------------

    cleaned = re.sub(
        r"https?://\S+",
        "",
        cleaned
    )

    # --------------------------------------------------------
    # BULLET CHARACTERS
    # --------------------------------------------------------

    cleaned = re.sub(
        r"^\s*[-*•]\s+",
        "",
        cleaned,
        flags=re.MULTILINE
    )

    # --------------------------------------------------------
    # MARKDOWN HORIZONTAL LINES
    # --------------------------------------------------------

    cleaned = re.sub(
        r"^\s*[-*_]{3,}\s*$",
        "",
        cleaned,
        flags=re.MULTILINE
    )

    # --------------------------------------------------------
    # BACKTICKS
    # --------------------------------------------------------

    cleaned = cleaned.replace(
        "`",
        ""
    )

    # --------------------------------------------------------
    # CLEAN EXCESS SPACES
    # --------------------------------------------------------

    cleaned = re.sub(
        r"[ \t]+",
        " ",
        cleaned
    )

    # Preserve natural pauses between paragraphs.
    cleaned = re.sub(
        r"\n{3,}",
        "\n\n",
        cleaned
    )

    return cleaned.strip()

# ============================================================
# TEXT TO SPEECH
# ============================================================

async def text_to_speech(
    text: str,
    output_path: str,
    voice: str = "en-IN-NeerjaNeural"
):

    speech_text = clean_text_for_speech(
        text
    )

    communicate = edge_tts.Communicate(
        text=speech_text,
        voice=voice
    )

    await communicate.save(
        output_path
    )

    return output_path