from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.weather import router as weather_router
from app.api.places import router as places_router
from app.api.itinerary import router as itinerary_router
from app.api.voice import router as voice_router
from app.api.vision import (router as vision_router)
from app.api.sightseeing_audio import (router as sightseeing_audio_router)
from app.api.disruptions import (router as disruptions_router)
from app.api.traffic import (router as traffic_router,)


app = FastAPI(
    title="AI TravelMate",
    description="LLM + RAG + Voice Travel Planning Assistant",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,

    allow_origin_regex=(
        r"^http://"
        r"(localhost|127\.0\.0\.1)"
        r":\d+$"
    ),

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router)
app.include_router(itinerary_router)
app.include_router(weather_router)
app.include_router(places_router)
app.include_router(voice_router)
app.include_router(vision_router)
app.include_router(sightseeing_audio_router)
app.include_router(disruptions_router)
app.include_router(
    traffic_router
)


@app.get("/")
def root():
    return {
        "message": "AI TravelMate API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }