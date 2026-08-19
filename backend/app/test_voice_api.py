import os
import sys

import requests


BASE_URL = "http://127.0.0.1:8000"


def main():

    print("=" * 75)

    print(
        "STEP 36C — LIVE VOICE HTTP API TEST"
    )

    print("=" * 75)


    # ========================================================
    # 1. AUDIO FILE
    # ========================================================

    audio_path = input(
        "\nEnter path to a real WAV/MP3 audio file: "
    ).strip().strip('"')


    if not os.path.exists(audio_path):

        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )


    print()

    print(
        "1. Audio file..."
    )

    print(
        f"   ✅ Found: {audio_path}"
    )


    # ========================================================
    # 2. HEALTH
    # ========================================================

    print()

    print(
        "2. Checking backend..."
    )


    response = requests.get(

        f"{BASE_URL}/health",

        timeout=10

    )


    assert response.status_code == 200


    print(
        "   ✅ Backend is reachable"
    )


    # ========================================================
    # 3. OPEN AUDIO
    # ========================================================

    print()

    print(
        "3. Loading audio..."
    )


    extension = os.path.splitext(
        audio_path
    )[1].lower()


    content_types = {

        ".wav": "audio/wav",

        ".mp3": "audio/mpeg",

        ".m4a": "audio/mp4",

        ".ogg": "audio/ogg",

        ".webm": "audio/webm",

        ".flac": "audio/flac",

        ".mp4": "audio/mp4"

    }


    content_type = content_types.get(

        extension,

        "application/octet-stream"

    )


    print(
        f"   Format: {extension}"
    )

    print(
        f"   Content-Type: {content_type}"
    )


    # ========================================================
    # 4. SEND VOICE REQUEST
    # ========================================================

    print()

    print(
        "4. Sending POST /voice/..."
    )


    with open(

        audio_path,

        "rb"

    ) as audio_file:

        files = {

            "audio": (

                os.path.basename(audio_path),

                audio_file,

                content_type

            )

        }

        data = {

            "conversation_id":
                "step36c-live-test"

        }


        response = requests.post(

            f"{BASE_URL}/voice/",

            files=files,

            data=data,

            timeout=180

        )


    print()

    print(
        f"   HTTP status: "
        f"{response.status_code}"
    )


    # ========================================================
    # 5. ERROR DETAILS
    # ========================================================

    if response.status_code != 200:

        print()

        print(
            "❌ Voice API returned an error"
        )

        print(
            "Response:"
        )

        print(
            response.text
        )

        sys.exit(1)


    print(
        "   ✅ Voice endpoint returned 200"
    )


    # ========================================================
    # 6. RESPONSE TYPE
    # ========================================================

    content_type = response.headers.get(

        "Content-Type",

        ""

    )


    print()

    print(
        "6. Validating response..."
    )


    assert "audio/mpeg" in content_type


    print(
        "   ✅ Response contains audio/mpeg"
    )


    # ========================================================
    # 7. TRANSCRIPT
    # ========================================================

    transcript = response.headers.get(

        "X-Transcript",

        ""

    )


    if transcript:

        print()

        print(
            "7. Transcript"
        )

        print(
            f"   🗣️ {transcript}"
        )

        print(
            "   ✅ Transcript returned"

        )

    else:

        print()

        print(
            "   ⚠️ Transcript header unavailable"
        )


    # ========================================================
    # 8. CONVERSATION
    # ========================================================

    conversation_id = response.headers.get(

        "X-Conversation-Id",

        ""

    )


    assert (

        conversation_id

        ==

        "step36c-live-test"

    )


    print()

    print(
        "8. Conversation ID..."
    )

    print(
        f"   {conversation_id}"
    )

    print(
        "   ✅ Conversation ID preserved"
    )


    # ========================================================
    # 9. AUDIO RESPONSE
    # ========================================================

    audio_size = len(

        response.content

    )


    print()

    print(
        "9. Generated response audio..."
    )

    print(
        f"   Size: {audio_size:,} bytes"
    )


    assert audio_size > 0


    print(
        "   ✅ MP3 response is non-empty"
    )


    # ========================================================
    # 10. SAVE RESPONSE
    # ========================================================

    output_path = (

        "step36c_voice_response.mp3"

    )


    with open(

        output_path,

        "wb"

    ) as output_file:

        output_file.write(

            response.content

        )


    print()

    print(
        f"10. Saved response:"
    )

    print(
        f"   {os.path.abspath(output_path)}"
    )

    print(
        "   ✅ Audio response saved"
    )


    # ========================================================
    # FINAL
    # ========================================================

    print()

    print("=" * 75)

    print(
        "STEP 36C VALIDATION SUMMARY"
    )

    print("=" * 75)

    print(
        f"Input audio: {audio_path}"
    )

    print(
        f"Transcript: {transcript or 'N/A'}"
    )

    print(
        f"Response content type: {content_type}"
    )

    print(
        f"Response audio bytes: {audio_size:,}"
    )

    print(
        f"Conversation ID: {conversation_id}"
    )

    print()

    print(
        "🎉 STEP 36C — LIVE VOICE HTTP API TEST PASSED"
    )

    print("=" * 75)


if __name__ == "__main__":

    main()