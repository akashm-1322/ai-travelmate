import asyncio

from app.services.conversation_service import (
    ConversationService
)

from app.memory.conversation import (
    ConversationMemory
)


async def main():

    print("=" * 75)
    print("STEP 36D — UNIFIED CONVERSATION MEMORY TEST")
    print("=" * 75)

    # ========================================================
    # 1. CREATE ISOLATED MEMORY
    # ========================================================

    print()
    print("1. Creating isolated conversation memory...")

    test_memory = ConversationMemory()

    service = ConversationService(
        conversation_memory=test_memory
    )

    print("   ✅ Memory created")

    # ========================================================
    # 2. FIRST MESSAGE
    # ========================================================

    conversation_id = "step36d-test"

    print()
    print("2. Processing first message...")

    first_result = await service.process_message(

        conversation_id=conversation_id,

        message=(
            "I am planning a trip to Chennai. "
            "I like temples and food."
        ),

        top_k=5

    )

    assert first_result["response"]

    print("   ✅ First response generated")

    # ========================================================
    # 3. VERIFY FIRST MESSAGE
    # ========================================================

    print()
    print("3. Validating first conversation state...")

    history = test_memory.get_messages(
        conversation_id
    )

    assert len(history) == 2

    assert history[0]["role"] == "user"

    assert history[1]["role"] == "assistant"

    print("   ✅ User message stored")

    print("   ✅ Assistant response stored")

    # ========================================================
    # 4. SECOND MESSAGE
    # ========================================================

    print()
    print("4. Processing follow-up message...")

    second_result = await service.process_message(

        conversation_id=conversation_id,

        message=(
            "Can you make that a three-day itinerary?"
        ),

        top_k=5

    )

    assert second_result["response"]

    print("   ✅ Follow-up response generated")

    # ========================================================
    # 5. VERIFY CONTEXT RETENTION
    # ========================================================

    print()
    print("5. Validating conversation continuity...")

    history = test_memory.get_messages(
        conversation_id
    )

    assert len(history) == 4

    assert history[0]["role"] == "user"

    assert history[1]["role"] == "assistant"

    assert history[2]["role"] == "user"

    assert history[3]["role"] == "assistant"

    print("   ✅ Conversation history preserved")

    # ========================================================
    # 6. ISOLATION TEST
    # ========================================================

    print()
    print("6. Validating conversation isolation...")

    isolated_history = test_memory.get_messages(
        "different-conversation"
    )

    assert isolated_history == []

    print("   ✅ Separate conversation has no leaked context")

    # ========================================================
    # 7. VERIFY SHARED MEMORY COUNT
    # ========================================================

    print()
    print("7. Validating message count...")

    assert len(
        test_memory.get_messages(
            conversation_id
        )
    ) == 4

    print("   ✅ Four messages stored correctly")

    # ========================================================
    # FINAL
    # ========================================================

    print()
    print("=" * 75)
    print("STEP 36D VALIDATION SUMMARY")
    print("=" * 75)

    print(
        f"Conversation ID: {conversation_id}"
    )

    print(
        "Messages stored: 4"
    )

    print(
        "Context continuity: True"
    )

    print(
        "Conversation isolation: True"
    )

    print()
    print(
        "🎉 STEP 36D — UNIFIED CONVERSATION MEMORY TEST PASSED"
    )

    print("=" * 75)


if __name__ == "__main__":

    asyncio.run(main())