"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    log_level: str = "info"
    secret_key: str = "change-me-in-production"

    # Database
    database_url: str = "sqlite:///data/wardrobe.db"

    # AI Models
    use_local_models: bool = True
    models_dir: Path = Path("./models")
    clip_model: str = "openai/clip-vit-large-patch14"
    image_gen_model: str = "sdxl"
    sdxl_model_path: str = "stabilityai/stable-diffusion-xl-base-1.0"
    flux_model_path: str = "black-forest-labs/FLUX.1-schnell"

    # Image Generation
    image_width: int = 1024
    image_height: int = 1024
    num_inference_steps: int = 20
    guidance_scale: float = 7.5
    max_concurrent_generations: int = 2

    # Ollama
    enable_ollama: bool = False
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout: int = 30

    # Weather
    enable_weather: bool = False
    openweather_api_key: str = ""
    openweather_units: str = "metric"

    # Storage
    upload_dir: Path = Path("data/uploads")
    max_upload_size: int = 20 * 1024 * 1024
    allowed_image_types: list[str] = ["image/jpeg", "image/png", "image/webp"]

    # Security
    cors_origins: list[str] = ["http://localhost:8080", "http://localhost:3000"]
    rate_limit_per_minute: int = 60

    # Features
    enable_background_removal: bool = True
    enable_duplicate_detection: bool = True
    enable_analytics: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
