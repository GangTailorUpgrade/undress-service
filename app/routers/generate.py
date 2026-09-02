"""Direct image generation endpoints."""
from fastapi import APIRouter
from app.services.image_gen import ImageGenerationService

router = APIRouter()
img_gen = ImageGenerationService()


@router.post("/generate/outfit-image")
async def generate_outfit_image(prompt: str, negative_prompt: str = ""):
    image_path = img_gen.generate(prompt, negative_prompt)
    return {"image_url": f"/uploads/{image_path.name}", "prompt": prompt}
