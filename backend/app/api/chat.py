from fastapi import APIRouter
from pydantic import BaseModel

from app.memory.conversation import memory
from app.services.conversation_service import (
    conversation_service
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):

    message: str

    conversation_id: str = "default"


class Source(BaseModel):

    source: str


class ChatResponse(BaseModel):

    response: str

    sources: list[Source] = []


@router.post(
    "/",
    response_model=ChatResponse
)
async def chat(request: ChatRequest):

    result = await conversation_service.process_message(

        conversation_id=request.conversation_id,

        message=request.message,

        top_k=5

    )

    return ChatResponse(

        response=result["response"],

        sources=[
            Source(source=source)
            for source in result["sources"]
        ]

    )


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