import os
import requests


BASE_URL = "http://127.0.0.1:8000"
VOICE_URL = f"{BASE_URL}/voice/"

AUDIO_FILE = "step36c_input.mp3"
CONVERSATION_ID = "step36d-conversation-test"


# Disable environment proxy handling for localhost testing.
SESSION = requests.Session()
SESSION.trust_env = False


def call_voice(audio_path: str, conversation_id: str):

    with open(audio_path, "rb") as audio:

        response = SESSION.post(
            VOICE_URL,
            files={
                "audio": (
                    os.path.basename(audio_path),
                    audio,
                    "audio/mpeg"
                )
            },
            data={
                "conversation_id": conversation_id
            },
            timeout=180
        )

    return response


def main():

    print("=" * 75)
    print("STEP 36D — VOICE CONVERSATION PIPELINE TEST")
    print("=" * 75)

    # ========================================================
    # 1. CHECK INPUT AUDIO
    # ========================================================

    print()
    print("1. Checking voice input...")

    if not os.path.exists(AUDIO_FILE):

        raise FileNotFoundError(
            f"Audio file not found: {AUDIO_FILE}"
        )

    print("   ✅ Voice input found")


    # ========================================================
    # 2. CHECK BACKEND
    # ========================================================

    print()
    print("2. Checking backend...")

    health = SESSION.get(
    f"{BASE_URL}/health",
    timeout=10
)

    assert health.status_code == 200

    print("   ✅ Backend reachable")


    # ========================================================
    # 3. FIRST VOICE TURN
    # ========================================================

    print()
    print("3. Sending first voice turn...")

    response_1 = call_voice(
        AUDIO_FILE,
        CONVERSATION_ID
    )

    print(
        f"   HTTP status: {response_1.status_code}"
    )

    assert response_1.status_code == 200

    assert response_1.headers.get(
        "content-type",
        ""
    ).startswith("audio/mpeg")

    print("   ✅ First voice turn completed")


    # ========================================================
    # 4. SAVE FIRST RESPONSE
    # ========================================================

    response_1_path = "step36d_response_1.mp3"

    with open(
        response_1_path,
        "wb"
    ) as output:

        output.write(
            response_1.content
        )

    assert os.path.getsize(
        response_1_path
    ) > 0

    print(
        f"   ✅ First response saved: "
        f"{response_1_path}"
    )


    # ========================================================
    # 5. SECOND VOICE TURN
    # ========================================================

    print()
    print(
        "4. Sending second voice turn "
        "using SAME conversation ID..."
    )

    response_2 = call_voice(
        AUDIO_FILE,
        CONVERSATION_ID
    )

    print(
        f"   HTTP status: {response_2.status_code}"
    )

    assert response_2.status_code == 200

    assert response_2.headers.get(
        "content-type",
        ""
    ).startswith("audio/mpeg")

    print("   ✅ Second voice turn completed")


    # ========================================================
    # 6. SAVE SECOND RESPONSE
    # ========================================================

    response_2_path = "step36d_response_2.mp3"

    with open(
        response_2_path,
        "wb"
    ) as output:

        output.write(
            response_2.content
        )

    assert os.path.getsize(
        response_2_path
    ) > 0

    print(
        f"   ✅ Second response saved: "
        f"{response_2_path}"
    )


    # ========================================================
    # 7. CHECK CONVERSATION HISTORY
    # ========================================================

    print()
    print(
        "5. Checking conversation memory..."
    )

    history_response = SESSION.get(
        f"{BASE_URL}/chat/history/"
        f"{CONVERSATION_ID}",
        timeout=10
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert (
        history.get("conversation_id")
        == CONVERSATION_ID
    )

    messages = history.get(
        "messages",
        []
    )

    print(
        f"   Messages stored: {len(messages)}"
    )

    assert len(messages) >= 4

    print(
        "   ✅ Conversation history preserved"
    )


    # ========================================================
    # 8. VALIDATE MESSAGE ROLES
    # ========================================================

    print()
    print(
        "6. Validating conversation roles..."
    )

    roles = [
        message.get("role")
        for message in messages
    ]

    assert "user" in roles
    assert "assistant" in roles

    print(
        "   ✅ User/assistant messages present"
    )


    # ========================================================
    # 9. VALIDATE NON-EMPTY CONTENT
    # ========================================================

    print()
    print(
        "7. Validating stored message content..."
    )

    for message in messages:

        assert message.get(
            "content"
        )

    print(
        "   ✅ All stored messages contain content"
    )


    # ========================================================
    # 10. FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 75)
    print("STEP 36D VALIDATION SUMMARY")
    print("=" * 75)

    print(
        f"Conversation ID: {CONVERSATION_ID}"
    )

    print(
        f"Conversation messages: {len(messages)}"
    )

    print(
        f"First response bytes: "
        f"{os.path.getsize(response_1_path)}"
    )

    print(
        f"Second response bytes: "
        f"{os.path.getsize(response_2_path)}"
    )

    print()
    print(
        "🎉 STEP 36D — VOICE CONVERSATION "
        "PIPELINE TEST PASSED"
    )

    print(
        "Voice → STT → Memory → RAG → LLM "
        "→ TTS → Voice response is working."
    )

    print("=" * 75)


if __name__ == "__main__":
    main()