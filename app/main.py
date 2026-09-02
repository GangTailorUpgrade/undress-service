"""Dress AI Service — Main FastAPI application."""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

from app.config import settings
from app.database import init_db
from app.routers import wardrobe, outfits, generate, health

start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.models_dir).mkdir(parents=True, exist_ok=True)
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Dress AI Service",
    description="Self-Hosted AI Outfit Generator & Virtual Wardrobe Stylist",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")

# Routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(wardrobe.router, prefix="/api/v1", tags=["Wardrobe"])
app.include_router(outfits.router, prefix="/api/v1", tags=["Outfits"])
app.include_router(generate.router, prefix="/api/v1", tags=["Generation"])


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dress AI Service</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>body { font-family: 'Inter', sans-serif; }</style>
    </head>
    <body class="bg-slate-900 text-white min-h-screen">
        <div class="max-w-6xl mx-auto px-6 py-12">
            <div class="text-center mb-16">
                <h1 class="text-5xl font-bold mb-4 bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
                    Dress AI Service
                </h1>
                <p class="text-xl text-slate-400 mb-8">Self-Hosted AI Outfit Generator & Virtual Wardrobe</p>
                <div class="flex justify-center gap-4">
                    <a href="/static/index.html" class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-medium transition">
                        Open App
                    </a>
                    <a href="/docs" class="px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition">
                        API Docs
                    </a>
                </div>
            </div>
            <div class="grid md:grid-cols-3 gap-8">
                <div class="bg-slate-800 p-6 rounded-xl">
                    <div class="text-3xl mb-3">📸</div>
                    <h3 class="text-lg font-semibold mb-2">Digitize Wardrobe</h3>
                    <p class="text-slate-400">Upload photos of your clothes. AI auto-tags category, color, style, and season.</p>
                </div>
                <div class="bg-slate-800 p-6 rounded-xl">
                    <div class="text-3xl mb-3">🧠</div>
                    <h3 class="text-lg font-semibold mb-2">Smart Recommendations</h3>
                    <p class="text-slate-400">Get outfit suggestions based on occasion, weather, and your personal style.</p>
                </div>
                <div class="bg-slate-800 p-6 rounded-xl">
                    <div class="text-3xl mb-3">🎨</div>
                    <h3 class="text-lg font-semibold mb-2">AI Visualization</h3>
                    <p class="text-slate-400">Generate photorealistic images of recommended outfits before you wear them.</p>
                </div>
            </div>
            <div class="mt-16 text-center text-slate-500">
                <p>Self-hosted. Private. Free forever.</p>
            </div>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
