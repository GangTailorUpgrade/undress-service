<div align="center">

<img src="https://raw.githubusercontent.com/GangTailorUpgrade/dress-ai-service/main/docs/logo.png" alt="Dress AI Service" width="180">

# 👗 Dress AI Service

**Self-Hosted AI Outfit Generator & Virtual Wardrobe Stylist**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/GangTailorUpgrade/dress-ai-service?style=social)](https://github.com/GangTailorUpgrade/undress-service)

🚀 **Turn your closet into an AI-powered fashion assistant.** Upload your wardrobe, get smart outfit recommendations for any occasion, and visualize your looks with generative AI — all self-hosted, private, and free.

[🎥 Demo Video](#) · [📖 Documentation](docs/) · [🐳 Quick Start](#quick-start) · [💬 Discord](#)

</div>

---

## ✨ What is Dress AI Service?

**Dress AI Service** is an open-source, self-hosted AI fashion platform that helps you:

- 📸 **Digitize your wardrobe** — Upload photos of your clothes; AI auto-tags them by category, color, style, and season
- 🧠 **Get smart outfit recommendations** — AI suggests perfect combinations based on occasion, weather, and your personal style
- 🎨 **Visualize outfits before wearing** — Generate AI renderings of how recommended outfits will look
- 🌤️ **Weather-aware styling** — Integrates real-time weather to suggest appropriate layers and fabrics
- 🏠 **100% self-hosted** — Your photos stay on your machine. No cloud uploads. No privacy concerns.

Whether you're a fashion enthusiast, a boutique owner, or a developer building the next generation of fashion tech, Dress AI Service gives you a complete, production-ready foundation.

---

## 🖼️ Screenshots

| Wardrobe Upload | AI Tagging | Outfit Recommendations | AI Visualization |
|---|---|---|---|
| ![Upload](docs/screenshots/upload.png) | ![Tagging](docs/screenshots/tagging.png) | ![Outfits](docs/screenshots/outfits.png) | ![Visualize](docs/screenshots/visualize.png) |

---
## 💖 Sponsors

Dress AI Service is made possible by our amazing sponsors. Support the project and get your logo here!

<div align="center">


<img width="1672" height="941" alt="5259cbc0-c12f-40e1-934b-d0f6802f745c" src="https://github.com/user-attachments/assets/43a0f5ad-c0b0-427d-9d24-0824c5bb8fa7" />


### Option 1: Docker (Recommended)

```bash
git clone https://github.com/GangTailorUpgrade/undress-service.git
cd dress-ai-service
cp .env.example .env
docker-compose up --build
```

Visit `http://localhost:8080` — your personal AI stylist is live! 🎉

### Option 2: Local Python

```bash
git clone https://github.com/GangTailorUpgrade/undress-service.git
cd dress-ai-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Download AI models (first run)
python scripts/download_models.py

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Dress AI Service                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Wardrobe   │  │   Outfit    │  │   AI Visualization  │ │
│  │   Upload    │  │   Engine    │  │      Pipeline       │ │
│  │  & Storage  │  │  (Rules +   │  │  (Stable Diffusion  │ │
│  │             │  │   LLM)      │  │   / FLUX / SDXL)    │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                     │            │
│  ┌──────▼────────────────▼─────────────────────▼──────────┐ │
│  │              FastAPI Backend (Python 3.11)             │ │
│  │  • SQLite / PostgreSQL  • CLIP Tagging  • Weather API │ │
│  └─────────────────────────┬──────────────────────────────┘ │
│                            │                                │
│  ┌─────────────────────────▼──────────────────────────────┐ │
│  │              Self-Hosted Frontend (HTML/JS)            │ │
│  │         • Drag & Drop Upload  • Live Preview          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI + Python 3.11 | High-performance async API |
| **AI/ML** | CLIP, Stable Diffusion XL, FLUX.1-schnell | Image understanding & generation |
| **Database** | SQLite (default) / PostgreSQL | Wardrobe & outfit storage |
| **Frontend** | Vanilla HTML5 + Tailwind CSS | Lightweight, zero-build UI |
| **Container** | Docker + Docker Compose | One-command deployment |
| **LLM** | Ollama (optional) | Local outfit reasoning & descriptions |

---

## 📦 Features

### Core Features
- ✅ **AI Auto-Tagging** — Upload a photo; AI detects category (top, bottom, shoes, accessory), dominant colors, fabric type, pattern, and season
- ✅ **Smart Outfit Generator** — Combines items based on color theory, occasion, weather, and fashion rules
- ✅ **Virtual Try-On Visualization** — Generate photorealistic images of recommended outfits on customizable avatars
- ✅ **Weather Integration** — Real-time weather-aware suggestions (rain coats, summer linens, winter layers)
- ✅ **Occasion Profiles** — Casual, Business, Date Night, Gym, Travel, Party presets
- ✅ **Favorites & Collections** — Save and organize your favorite looks
- ✅ **Export & Share** — Export outfit boards as PNG/PDF or shareable links
- ✅ **Batch Upload** — Drag & drop entire folders of clothing photos
- ✅ **Duplicate Detection** — AI prevents adding the same item twice

### Advanced Features
- 🔄 **Model Swap** — Choose different AI model styles (realistic, anime, sketch)
- 🎨 **Color Palette Extractor** — Builds seasonal color palettes from your wardrobe
- 📊 **Wardrobe Analytics** — Insights: most-worn colors, underutilized items, gap analysis
- 🔌 **Plugin System** — Extend with custom recommendation engines
- 🌍 **Multi-language** — i18n support for 12 languages
- 📱 **PWA Support** — Install as a mobile app

---

## ⚙️ Configuration

Create a `.env` file:

```env
# Server
HOST=0.0.0.0
PORT=8080
DEBUG=false

# Database
DATABASE_URL=sqlite:///data/wardrobe.db
# DATABASE_URL=postgresql://user:pass@localhost/dressai

# AI Models
USE_LOCAL_MODELS=true
SDXL_MODEL_PATH=models/sd-xl-base
FLUX_MODEL_PATH=models/flux-schnell
CLIP_MODEL=openai/clip-vit-large-patch14

# Optional: Ollama for LLM reasoning
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Optional: Weather API
OPENWEATHER_API_KEY=your_key_here

# Image Generation
IMAGE_WIDTH=1024
IMAGE_HEIGHT=1024
NUM_INFERENCE_STEPS=20
GUIDANCE_SCALE=7.5

# Storage
UPLOAD_DIR=data/uploads
MAX_UPLOAD_SIZE=20MB
```

---

## 🧪 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/wardrobe/upload` | Upload clothing item |
| `GET` | `/api/v1/wardrobe/items` | List all wardrobe items |
| `GET` | `/api/v1/wardrobe/items/{id}` | Get item details |
| `DELETE` | `/api/v1/wardrobe/items/{id}` | Remove item |
| `POST` | `/api/v1/outfits/generate` | Generate outfit recommendations |
| `GET` | `/api/v1/outfits/{id}` | Get outfit details |
| `POST` | `/api/v1/outfits/{id}/visualize` | Generate outfit visualization |
| `POST` | `/api/v1/outfits/{id}/favorite` | Save to favorites |
| `GET` | `/api/v1/analytics/wardrobe` | Wardrobe insights |
| `GET` | `/api/v1/health` | Health check |

**Full API docs:** `http://localhost:8080/docs` (Swagger UI) or `http://localhost:8080/redoc` (ReDoc)

---

## 🧠 How It Works

### 1. Wardrobe Digitization
When you upload a clothing photo:
1. **Image preprocessing** — Resize, normalize, background removal (optional)
2. **CLIP inference** — Classifies category, color, pattern, fabric
3. **Embedding storage** — Saves visual embedding for similarity search
4. **Metadata extraction** — Dominant colors, season tags, style classification

### 2. Outfit Recommendation Engine
The recommendation system uses a hybrid approach:
- **Rule-based layer** — Color theory (complementary, analogous, triadic), occasion appropriateness, weather matching
- **Embedding similarity** — CLIP embeddings find visually harmonious combinations
- **LLM reasoning** (optional) — Ollama-powered natural language outfit reasoning
- **User feedback loop** — Learns from your favorites and rejections

### 3. AI Visualization
For each recommended outfit:
1. **Prompt engineering** — Builds detailed prompt from item metadata
2. **Negative prompt** — Avoids common generation artifacts
3. **Stable Diffusion / FLUX** — Generates photorealistic outfit visualization
4. **Post-processing** — Upscaling, face restoration, background consistency

---

## 🐳 Docker Deployment

### Basic Deployment
```bash
docker-compose up -d
```

### With GPU (NVIDIA)
```bash
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

### With Ollama (Local LLM)
```bash
docker-compose -f docker-compose.yml -f docker-compose.ollama.yml up -d
```

### Environment Variables
All configuration is via environment variables. See `.env.example` for full reference.

---

## 🧑‍💻 Development

```bash
# Setup
git clone https://github.com/GangTailorUpgrade/undress-service.git
cd dress-ai-service
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=app

# Run linting
ruff check app/
black app/
mypy app/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

---

## 🗺️ Roadmap

- [ ] **Mobile App** — React Native / Flutter companion app
- [ ] **Social Features** — Share outfits, follow stylists, community boards
- [ ] **E-commerce Integration** — Import from Shopify, WooCommerce, Amazon
- [ ] **3D Avatars** — Realistic body scanning for accurate fit visualization
- [ ] **Calendar Integration** — Plan outfits for upcoming events
- [ ] **Sustainability Score** — Carbon footprint analysis of your wardrobe
- [ ] **AI Shopping Assistant** — Suggest items to complete your wardrobe gaps

---

## 🤝 Contributing

We love contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

### 🥇 Platinum Sponsors

<a href="#sponsor-platinum"><img src="https://via.placeholder.com/300x100/1a1a2e/FFFFFF?text=Your+Logo+Here+-+Platinum" alt="Platinum Sponsor" width="300"></a>

*Become a Platinum Sponsor — $500/month. Featured logo on README, website, and release notes.*

### 🥈 Gold Sponsors

<a href="#sponsor-gold"><img src="https://via.placeholder.com/200x80/16213e/FFFFFF?text=Gold+Sponsor+Slot" alt="Gold Sponsor" width="200"></a>
<a href="#sponsor-gold"><img src="https://via.placeholder.com/200x80/16213e/FFFFFF?text=Gold+Sponsor+Slot" alt="Gold Sponsor" width="200"></a>

*Become a Gold Sponsor — $200/month. Logo on README and website.*

### 🥉 Silver Sponsors

<a href="#sponsor-silver"><img src="https://via.placeholder.com/150x60/0f3460/FFFFFF?text=Silver" alt="Silver Sponsor" width="150"></a>
<a href="#sponsor-silver"><img src="https://via.placeholder.com/150x60/0f3460/FFFFFF?text=Silver" alt="Silver Sponsor" width="150"></a>
<a href="#sponsor-silver"><img src="https://via.placeholder.com/150x60/0f3460/FFFFFF?text=Silver" alt="Silver Sponsor" width="150"></a>

*Become a Silver Sponsor — $50/month. Name listed in README.*

</div>

**[→ Become a Sponsor](https://github.com/sponsors/GangTailorUpgrade)**

---

## 🙏 Acknowledgments

- [Stable Diffusion](https://stability.ai) by Stability AI
- [FLUX](https://blackforestlabs.ai) by Black Forest Labs
- [CLIP](https://openai.com/research/clip) by OpenAI
- [FastAPI](https://fastapi.tiangolo.com) by Sebastián Ramírez
- [Ollama](https://ollama.ai) for local LLM inference

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with 💜 by [GangTailorUpgrade](https://github.com/GangTailorUpgrade)

</div>
