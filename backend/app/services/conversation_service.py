import time

from app.llm.provider import generate_response
from app.memory.conversation import memory
from app.rag.retriever import retrieve


class ConversationService:
    """
    Shared conversation orchestration layer.

    Both text chat and voice chat use this service so that
    conversation memory, RAG retrieval and LLM generation
    behave consistently across interfaces.
    """

    def __init__(
        self,
        conversation_memory=memory
    ):

        self.memory = (
            conversation_memory
        )

    async def process_message(
        self,
        conversation_id: str,
        message: str,
        top_k: int = 5
    ) -> dict:

        total_start = (
            time.perf_counter()
        )

        message = (
            message.strip()
        )

        if not message:

            raise ValueError(
                "Message cannot be empty"
            )

        # ====================================================
        # 1. CONVERSATION HISTORY
        # ====================================================

        history_start = (
            time.perf_counter()
        )

        history = (
            self.memory.get_messages(
                conversation_id
            )
        )

        history_end = (
            time.perf_counter()
        )

        # ====================================================
        # 2. RAG RETRIEVAL
        # ====================================================

        rag_start = (
            time.perf_counter()
        )

        retrieved_documents = retrieve(
            message,
            top_k=top_k
        )

        rag_end = (
            time.perf_counter()
        )

        # ====================================================
        # 3. LLM GENERATION
        # ====================================================

        llm_start = (
            time.perf_counter()
        )

        response = await generate_response(

            prompt=message,

            conversation_history=history,

            retrieved_documents=(
                retrieved_documents
            )

        )

        llm_end = (
            time.perf_counter()
        )

        # ====================================================
        # 4. STORE MEMORY
        # ====================================================

        memory_start = (
            time.perf_counter()
        )

        self.memory.add_message(

            conversation_id,

            "user",

            message

        )

        self.memory.add_message(

            conversation_id,

            "assistant",

            response

        )

        memory_end = (
            time.perf_counter()
        )

        # ====================================================
        # 5. UNIQUE SOURCE LIST
        # ====================================================

        unique_sources = []
        seen_sources = set()

        for document in (
            retrieved_documents
        ):

            source = (
                document
                .get(
                    "metadata",
                    {}
                )
                .get(
                    "source",
                    "unknown"
                )
            )

            if (
                source
                not in seen_sources
            ):

                seen_sources.add(
                    source
                )

                unique_sources.append(
                    source
                )

        # ====================================================
        # 6. TIMINGS
        # ====================================================

        total_end = (
            time.perf_counter()
        )

        timings = {

            "history_seconds":
                round(
                    history_end
                    - history_start,
                    4
                ),

            "rag_seconds":
                round(
                    rag_end
                    - rag_start,
                    4
                ),

            "llm_seconds":
                round(
                    llm_end
                    - llm_start,
                    4
                ),

            "memory_seconds":
                round(
                    memory_end
                    - memory_start,
                    4
                ),

            "total_seconds":
                round(
                    total_end
                    - total_start,
                    4
                )

        }

        # ====================================================
        # 7. LOG LATENCY
        # ====================================================

        print()
        print(
            "=" * 70
        )

        print(
            "CONVERSATION LATENCY REPORT"
        )

        print(
            "=" * 70
        )

        print(
            f"History: "
            f"{timings['history_seconds']:.2f} sec"
        )

        print(
            f"RAG:     "
            f"{timings['rag_seconds']:.2f} sec"
        )

        print(
            f"LLM:     "
            f"{timings['llm_seconds']:.2f} sec"
        )

        print(
            f"Memory:  "
            f"{timings['memory_seconds']:.2f} sec"
        )

        print(
            f"TOTAL:   "
            f"{timings['total_seconds']:.2f} sec"
        )

        print(
            "=" * 70
        )

        print()

        # ====================================================
        # 8. RETURN STRUCTURED RESULT
        # ====================================================

        return {

            "conversation_id":
                conversation_id,

            "message":
                message,

            "response":
                response,

            "sources":
                unique_sources,

            "timings":
                timings

        }


conversation_service = (
    ConversationService()
)