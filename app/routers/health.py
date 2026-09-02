"""Health check endpoint."""
import time
from fastapi import APIRouter
from app.models import HealthResponse
from app.config import settings

start_time = time.time()

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        models_loaded={"clip": True, "sdxl": settings.use_local_models},
        database_connected=True,
        ollama_connected=settings.enable_ollama,
        weather_api_connected=settings.enable_weather and bool(settings.openweather_api_key),
        uptime_seconds=round(time.time() - start_time, 2),
    )
