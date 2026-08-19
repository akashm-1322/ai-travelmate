import os
import requests


BASE_URL = "http://127.0.0.1:8000"

CONVERSATION_ID = "step36e-cross-modal"

AUDIO_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "step36c_input.mp3"
)


def print_header(title):
    print("=" * 75)
    print(title)
    print("=" * 75)


def main():

    print_header(
        "STEP 36E — CROSS-MODAL TEXT ↔ VOICE CONVERSATION TEST"
    )

    # ============================================================
    # 1. VERIFY INPUT AUDIO
    # ============================================================

    print()
    print("1. Checking voice input...")

    if not os.path.exists(AUDIO_FILE):

        raise FileNotFoundError(
            f"Voice input not found: {AUDIO_FILE}"
        )

    print(
        f"   ✅ Voice input found: {AUDIO_FILE}"
    )

    # ============================================================
    # 2. CHECK BACKEND
    # ============================================================

    print()
    print("2. Checking backend...")

    health = requests.get(
        f"{BASE_URL}/health",
        timeout=10
    )

    assert health.status_code == 200

    print(
        "   ✅ Backend reachable"
    )

    # ============================================================
    # 3. TEXT TURN
    # ============================================================

    print()
    print("3. Sending TEXT turn...")

    text_message = (
        "I am planning a 3-day trip to Chennai. "
        "I like temples, food and beaches. "
        "Help me plan it."
    )

    text_payload = {
        "message": text_message,
        "conversation_id": CONVERSATION_ID
    }

    text_response = requests.post(
        f"{BASE_URL}/chat/",
        json=text_payload,
        timeout=120
    )

    print(
        f"   HTTP status: {text_response.status_code}"
    )

    assert text_response.status_code == 200

    text_data = text_response.json()

    assert "response" in text_data
    assert text_data["response"]

    print(
        "   ✅ Text turn completed"
    )

    print()
    print("   TEXT RESPONSE:")
    print(
        "   " + text_data["response"][:500]
    )

    # ============================================================
    # 4. VOICE TURN
    # ============================================================

    print()
    print(
        "4. Sending VOICE turn using SAME conversation ID..."
    )

    with open(
        AUDIO_FILE,
        "rb"
    ) as audio_file:

        files = {
            "audio": (
                os.path.basename(AUDIO_FILE),
                audio_file,
                "audio/mpeg"
            )
        }

        data = {
            "conversation_id": CONVERSATION_ID
        }

        voice_response = requests.post(
            f"{BASE_URL}/voice/",
            files=files,
            data=data,
            timeout=180
        )

    print(
        f"   HTTP status: {voice_response.status_code}"
    )

    assert voice_response.status_code == 200

    content_type = voice_response.headers.get(
        "content-type",
        ""
    )

    assert "audio/mpeg" in content_type

    print(
        "   ✅ Voice turn completed"
    )

    print(
        f"   Response audio bytes: "
        f"{len(voice_response.content):,}"
    )

    assert len(voice_response.content) > 0

    # ============================================================
    # 5. SECOND TEXT TURN
    # ============================================================

    print()
    print(
        "5. Sending SECOND TEXT turn using SAME conversation ID..."
    )

    second_text_message = (
        "From the trip we were discussing, "
        "which places should I prioritize if I especially "
        "want to visit temples?"
    )

    second_text_payload = {
        "message": second_text_message,
        "conversation_id": CONVERSATION_ID
    }

    second_text_response = requests.post(
        f"{BASE_URL}/chat/",
        json=second_text_payload,
        timeout=120
    )

    print(
        f"   HTTP status: "
        f"{second_text_response.status_code}"
    )

    assert second_text_response.status_code == 200

    second_text_data = (
        second_text_response.json()
    )

    assert "response" in second_text_data
    assert second_text_data["response"]

    print(
        "   ✅ Second text turn completed"
    )

    print()
    print("   SECOND TEXT RESPONSE:")

    print(
        "   "
        + second_text_data["response"][:500]
    )

    # ============================================================
    # 6. CHECK SHARED CONVERSATION MEMORY
    # ============================================================

    print()
    print(
        "6. Checking shared conversation memory..."
    )

    history_response = requests.get(
        f"{BASE_URL}/chat/history/{CONVERSATION_ID}",
        timeout=30
    )

    print(
        f"   HTTP status: "
        f"{history_response.status_code}"
    )

    assert history_response.status_code == 200

    history_data = history_response.json()

    assert (
        history_data["conversation_id"]
        == CONVERSATION_ID
    )

    messages = history_data.get(
        "messages",
        []
    )

    print(
        f"   Messages stored: {len(messages)}"
    )

    assert len(messages) >= 6

    print(
        "   ✅ Shared conversation history preserved"
    )

    # ============================================================
    # 7. VALIDATE MESSAGE ROLES
    # ============================================================

    print()
    print(
        "7. Validating cross-modal message roles..."
    )

    roles = [
        message.get("role")
        for message in messages
    ]

    user_count = roles.count(
        "user"
    )

    assistant_count = roles.count(
        "assistant"
    )

    print(
        f"   User messages: {user_count}"
    )

    print(
        f"   Assistant messages: {assistant_count}"
    )

    assert user_count >= 3
    assert assistant_count >= 3

    print(
        "   ✅ User/assistant roles valid"
    )

    # ============================================================
    # 8. VALIDATE ORIGINAL TEXT MESSAGE
    # ============================================================

    print()
    print(
        "8. Validating original TEXT message..."
    )

    user_messages = [
        message.get(
            "content",
            ""
        )
        for message in messages
        if message.get("role") == "user"
    ]

    assert any(
        "3-day trip to Chennai" in message
        for message in user_messages
    )

    print(
        "   ✅ Original text turn preserved"
    )

    # ============================================================
    # 9. VALIDATE VOICE TRANSCRIPT
    # ============================================================

    print()
    print(
        "9. Validating VOICE transcript..."
    )

    voice_transcript_fragment = (
        "What are the best places to visit in Chennai"
    )

    voice_found = any(
        voice_transcript_fragment.lower()
        in message.lower()
        for message in user_messages
    )

    assert voice_found

    print(
        "   ✅ Voice transcript preserved in shared memory"
    )

    # ============================================================
    # 10. VALIDATE SECOND TEXT TURN
    # ============================================================

    print()
    print(
        "10. Validating SECOND TEXT turn..."
    )

    second_text_found = any(
        (
            "temples" in message.lower()
            and
            (
                "prioritize" in message.lower()
                or
                "places" in message.lower()
            )
        )
        for message in user_messages
    )

    assert second_text_found

    print(
        "   ✅ Second text turn preserved"
    )

    # ============================================================
    # 10A. VALIDATE CROSS-MODAL ORDER
    # ============================================================

    print()
    print(
        "10A. Validating cross-modal conversation order..."
    )

    assert len(messages) >= 6

    expected_roles = [
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
        "assistant"
    ]

    actual_roles = [
        message.get("role")
        for message in messages[:6]
    ]

    assert actual_roles == expected_roles

    print(
        "   ✅ Conversation order is correct"
    )

    # ============================================================
    # 11. PRINT COMPLETE CONVERSATION
    # ============================================================

    print()
    print("=" * 75)
    print("CROSS-MODAL CONVERSATION")
    print("=" * 75)

    for index, message in enumerate(
        messages,
        start=1
    ):

        role = message.get(
            "role",
            "unknown"
        )

        content = message.get(
            "content",
            ""
        )

        print()
        print(
            f"{index}. {role.upper()}"
        )

        print(
            f"   {content[:300]}"
        )

    # ============================================================
    # 12. FINAL SUMMARY
    # ============================================================

    print()
    print("=" * 75)
    print("STEP 36E VALIDATION SUMMARY")
    print("=" * 75)

    print(
        f"Conversation ID: {CONVERSATION_ID}"
    )

    print(
        f"Total messages: {len(messages)}"
    )

    print(
        f"User messages: {user_count}"
    )

    print(
        f"Assistant messages: {assistant_count}"
    )

    print()
    print(
        "Text → Voice → Text: PASSED"
    )

    print(
        "Shared conversation memory: PASSED"
    )

    print(
        "Voice transcript persistence: PASSED"
    )

    print()
    print(
        "🎉 STEP 36E — CROSS-MODAL CONVERSATION TEST PASSED"
    )

    print(
        "Text and voice successfully operate "
        "within the same AI TravelMate conversation."
    )

    print("=" * 75)


if __name__ == "__main__":
    main()