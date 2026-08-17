from fastapi import APIRouter
from pydantic import BaseModel

from app.llm.provider import generate_response
from app.memory.conversation import memory
from app.rag.retriever import retrieve


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):

    message: str

    conversation_id: str = "default"


# ============================================================
# SOURCE MODEL
# ============================================================

class Source(BaseModel):

    source: str


# ============================================================
# RESPONSE MODEL
# ============================================================

class ChatResponse(BaseModel):

    response: str

    sources: list[Source] = []


# ============================================================
# CHAT ENDPOINT
# ============================================================

@router.post(
    "/",
    response_model=ChatResponse
)
async def chat(request: ChatRequest):

    # --------------------------------------------------------
    # 1. GET CONVERSATION HISTORY
    # --------------------------------------------------------

    history = memory.get_messages(
        request.conversation_id
    )


    # --------------------------------------------------------
    # 2. RETRIEVE RELEVANT KNOWLEDGE
    # --------------------------------------------------------

    retrieved_documents = retrieve(
        request.message,
        top_k=5
    )


    # --------------------------------------------------------
    # 3. GENERATE GROUNDED RESPONSE
    # --------------------------------------------------------

    response = await generate_response(

        prompt=request.message,

        conversation_history=history,

        retrieved_documents=retrieved_documents

    )


    # --------------------------------------------------------
    # 4. STORE USER MESSAGE
    # --------------------------------------------------------

    memory.add_message(

        request.conversation_id,

        "user",

        request.message

    )


    # --------------------------------------------------------
    # 5. STORE AI RESPONSE
    # --------------------------------------------------------

    memory.add_message(

        request.conversation_id,

        "assistant",

        response

    )


    # --------------------------------------------------------
    # 6. BUILD UNIQUE SOURCES
    # --------------------------------------------------------

    unique_sources = []

    seen_sources = set()


    for document in retrieved_documents:

        source = document.get(
            "metadata",
            {}
        ).get(
            "source",
            "unknown"
        )


        if source not in seen_sources:

            seen_sources.add(
                source
            )

            unique_sources.append(
                Source(
                    source=source
                )
            )


    # --------------------------------------------------------
    # 7. RETURN RESPONSE
    # --------------------------------------------------------

    return ChatResponse(

        response=response,

        sources=unique_sources

    )


# ============================================================
# CONVERSATION HISTORY
# ============================================================

@router.get(
    "/history/{conversation_id}"
)
async def get_history(
    conversation_id: str
):

    return {

        "conversation_id":
            conversation_id,

        "messages":
            memory.get_messages(
                conversation_id
            )

    }