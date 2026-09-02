"""Outfit recommendation and management endpoints."""
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, OutfitDB, WardrobeItemDB
from app.models import (
    OutfitResponse, OutfitGenerateRequest, OutfitVisualizeRequest,
    Occasion, Season, StyleTag
)
from app.services.outfit_engine import OutfitEngine
from app.services.image_gen import ImageGenerationService

router = APIRouter()
engine = OutfitEngine()
img_gen = ImageGenerationService()


@router.post("/outfits/generate", response_model=List[OutfitResponse])
async def generate_outfits(
    request: OutfitGenerateRequest,
    db: Session = Depends(get_db),
):
    items = db.query(WardrobeItemDB).all()
    if len(items) < 3:
        raise HTTPException(400, "Need at least 3 wardrobe items to generate outfits")

    suggestions = engine.generate_outfits(
        items=items,
        occasion=request.occasion.value,
        season=request.season.value,
        weather_condition=request.weather_condition,
        temperature=request.temperature,
        style_preference=request.style_preference.value if request.style_preference else None,
        exclude_items=request.exclude_items or [],
        must_include=request.must_include or [],
        num_suggestions=request.num_suggestions,
    )

    responses = []
    for sugg in suggestions:
        outfit = OutfitDB(
            name=sugg["name"],
            occasion=sugg["occasion"],
            season=sugg["season"],
            style_tags=",".join(sugg.get("style_tags", [])),
            color_palette=json.dumps(sugg.get("color_palette", [])),
            reasoning=sugg.get("reasoning"),
        )
        # Link items
        for item_id in sugg["item_ids"]:
            item = db.query(WardrobeItemDB).filter(WardrobeItemDB.id == item_id).first()
            if item:
                outfit.items.append(item)

        db.add(outfit)
        db.commit()
        db.refresh(outfit)
        responses.append(_to_response(outfit))

    return responses


@router.get("/outfits/{outfit_id}", response_model=OutfitResponse)
async def get_outfit(outfit_id: int, db: Session = Depends(get_db)):
    outfit = db.query(OutfitDB).filter(OutfitDB.id == outfit_id).first()
    if not outfit:
        raise HTTPException(404, "Outfit not found")
    return _to_response(outfit)


@router.post("/outfits/{outfit_id}/visualize")
async def visualize_outfit(
    outfit_id: int,
    request: OutfitVisualizeRequest,
    db: Session = Depends(get_db),
):
    outfit = db.query(OutfitDB).filter(OutfitDB.id == outfit_id).first()
    if not outfit:
        raise HTTPException(404, "Outfit not found")

    # Build prompt from outfit items
    items_info = []
    for item in outfit.items:
        items_info.append(f"{item.category}: {item.name} ({item.style_tags})")

    prompt = f"Fashion editorial photo of a complete outfit. {outfit.occasion} style. "
    prompt += "Wearing: " + ", ".join(items_info) + ". "
    prompt += f"Color palette: {outfit.color_palette}. "
    prompt += f"{request.pose} pose, {request.background} background, {request.model_style} style. "
    prompt += "High quality, photorealistic, detailed fabric texture, professional fashion photography."

    image_path = img_gen.generate(prompt)

    outfit.visualization_path = str(image_path)
    db.commit()

    return {"visualization_url": f"/uploads/{image_path.name}", "prompt": prompt}


@router.post("/outfits/{outfit_id}/favorite")
async def favorite_outfit(outfit_id: int, db: Session = Depends(get_db)):
    outfit = db.query(OutfitDB).filter(OutfitDB.id == outfit_id).first()
    if not outfit:
        raise HTTPException(404, "Outfit not found")
    outfit.is_favorite = not outfit.is_favorite
    db.commit()
    return {"is_favorite": outfit.is_favorite}


@router.get("/outfits", response_model=List[OutfitResponse])
async def list_outfits(
    occasion: str = None,
    favorite_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(OutfitDB)
    if occasion:
        query = query.filter(OutfitDB.occasion == occasion)
    if favorite_only:
        query = query.filter(OutfitDB.is_favorite == True)

    outfits = query.offset(skip).limit(limit).all()
    return [_to_response(o) for o in outfits]


def _to_response(outfit: OutfitDB) -> OutfitResponse:
    from app.routers.wardrobe import _to_response as item_to_response
    return OutfitResponse(
        id=outfit.id,
        name=outfit.name,
        occasion=Occasion(outfit.occasion),
        season=Season(outfit.season),
        items=[item_to_response(item) for item in outfit.items],
        style_tags=outfit.style_tags.split(",") if outfit.style_tags else [],
        color_palette=json.loads(outfit.color_palette) if outfit.color_palette else [],
        reasoning=outfit.reasoning,
        visualization_url=f"/uploads/{outfit.visualization_path}" if outfit.visualization_path else None,
        is_favorite=outfit.is_favorite,
        created_at=outfit.created_at,
    )
