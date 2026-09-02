"""Wardrobe item management endpoints."""
import json
import uuid
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from sqlalchemy.orm import Session
from PIL import Image

from app.database import get_db, WardrobeItemDB
from app.models import WardrobeItemResponse, WardrobeItemCreate, ClothingCategory
from app.config import settings
from app.services.ai_tagging import AITaggingService

router = APIRouter()
tagging_service = AITaggingService()


def save_upload_file(upload_file: UploadFile) -> tuple[Path, Path]:
    ext = Path(upload_file.filename).suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(400, "Only JPG, PNG, WebP images allowed")

    item_id = str(uuid.uuid4())
    image_path = settings.upload_dir / f"{item_id}{ext}"
    thumb_path = settings.upload_dir / f"{item_id}_thumb{ext}"

    content = upload_file.file.read()
    if len(content) > settings.max_upload_size:
        raise HTTPException(400, f"File too large. Max {settings.max_upload_size // 1024 // 1024}MB")

    with open(image_path, "wb") as f:
        f.write(content)

    # Create thumbnail
    with Image.open(image_path) as img:
        img.thumbnail((400, 400), Image.LANCZOS)
        img.save(thumb_path, quality=85)

    return image_path, thumb_path


@router.post("/wardrobe/upload", response_model=WardrobeItemResponse)
async def upload_item(
    file: UploadFile = File(...),
    name: str = Form(None),
    category: str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db),
):
    image_path, thumb_path = save_upload_file(file)

    # AI tagging
    tags = tagging_service.analyze_image(str(image_path))

    item = WardrobeItemDB(
        name=name or tags.get("suggested_name", "Untitled Item"),
        category=category or tags.get("category", "top"),
        colors=json.dumps(tags.get("colors", [])),
        season=tags.get("season", "all_season"),
        style_tags=",".join(tags.get("style_tags", [])),
        fabric=tags.get("fabric"),
        pattern=tags.get("pattern"),
        image_path=str(image_path),
        thumbnail_path=str(thumb_path),
        notes=notes,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return _to_response(item)


@router.get("/wardrobe/items", response_model=List[WardrobeItemResponse])
async def list_items(
    category: str = None,
    season: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(WardrobeItemDB)
    if category:
        query = query.filter(WardrobeItemDB.category == category)
    if season:
        query = query.filter(WardrobeItemDB.season.contains(season))

    items = query.offset(skip).limit(limit).all()
    return [_to_response(item) for item in items]


@router.get("/wardrobe/items/{item_id}", response_model=WardrobeItemResponse)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(WardrobeItemDB).filter(WardrobeItemDB.id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")
    return _to_response(item)


@router.delete("/wardrobe/items/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(WardrobeItemDB).filter(WardrobeItemDB.id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")

    # Delete files
    Path(item.image_path).unlink(missing_ok=True)
    Path(item.thumbnail_path).unlink(missing_ok=True)

    db.delete(item)
    db.commit()
    return {"message": "Item deleted"}


def _to_response(item: WardrobeItemDB) -> WardrobeItemResponse:
    colors = json.loads(item.colors) if item.colors else []
    return WardrobeItemResponse(
        id=item.id,
        name=item.name,
        category=ClothingCategory(item.category),
        colors=colors,
        season=item.season.split(",") if item.season else ["all_season"],
        style_tags=item.style_tags.split(",") if item.style_tags else [],
        fabric=item.fabric,
        pattern=item.pattern,
        image_path=f"/uploads/{Path(item.image_path).name}",
        thumbnail_path=f"/uploads/{Path(item.thumbnail_path).name}",
        embedding_id=item.embedding_id,
        notes=item.notes,
        tags=[],
        created_at=item.created_at,
        updated_at=item.updated_at,
    )
