import os

from app.services.voice_service import speech_to_text


def main():

    print("=" * 75)
    print("STEP 36A — SPEECH TO TEXT TEST")
    print("=" * 75)

    audio_path = input(
        "\nEnter path to a WAV/MP3 audio file: "
    ).strip()

    if not os.path.exists(audio_path):

        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    print()
    print("1. Loading audio...")
    print("   ✅ Audio file found")

    print()
    print("2. Running Whisper...")

    transcript = speech_to_text(
        audio_path
    )

    print()
    print("3. TRANSCRIPT")
    print("-" * 75)

    print(transcript)

    print("-" * 75)

    if transcript:

        print()
        print(
            "🎉 STEP 36A PASSED"
        )

    else:

        print()
        print(
            "❌ STEP 36A FAILED"
        )


if __name__ == "__main__":
    main()