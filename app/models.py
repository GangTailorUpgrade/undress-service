"""Pydantic models for API requests/responses."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ClothingCategory(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    DRESS = "dress"
    OUTERWEAR = "outerwear"
    SHOES = "shoes"
    ACCESSORY = "accessory"
    ACTIVEWEAR = "activewear"
    SWIMWEAR = "swimwear"
    LOUNGEWEAR = "loungewear"
    FORMAL = "formal"


class Season(str, Enum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"
    ALL_SEASON = "all_season"


class Occasion(str, Enum):
    CASUAL = "casual"
    BUSINESS = "business"
    FORMAL = "formal"
    DATE_NIGHT = "date_night"
    GYM = "gym"
    TRAVEL = "travel"
    PARTY = "party"
    OUTDOOR = "outdoor"
    LOUNGE = "lounge"


class StyleTag(str, Enum):
    MINIMALIST = "minimalist"
    STREETWEAR = "streetwear"
    CLASSIC = "classic"
    BOHEMIAN = "bohemian"
    PREPPY = "preppy"
    VINTAGE = "vintage"
    SPORTY = "sporty"
    LUXURY = "luxury"
    CASUAL = "casual"
    TRENDY = "trendy"


class ColorInfo(BaseModel):
    hex: str
    name: str
    percentage: float


class WardrobeItemCreate(BaseModel):
    name: Optional[str] = None
    category: Optional[ClothingCategory] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = []


class WardrobeItemResponse(BaseModel):
    id: int
    name: str
    category: ClothingCategory
    colors: List[ColorInfo]
    season: List[Season]
    style_tags: List[StyleTag]
    fabric: Optional[str] = None
    pattern: Optional[str] = None
    image_path: str
    thumbnail_path: str
    embedding_id: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OutfitItem(BaseModel):
    item_id: int
    position: int = Field(ge=0, le=10)


class OutfitGenerateRequest(BaseModel):
    occasion: Optional[Occasion] = Occasion.CASUAL
    season: Optional[Season] = Season.ALL_SEASON
    weather_condition: Optional[str] = None
    temperature: Optional[float] = None
    style_preference: Optional[StyleTag] = None
    exclude_items: Optional[List[int]] = []
    must_include: Optional[List[int]] = []
    num_suggestions: int = Field(default=3, ge=1, le=10)


class OutfitResponse(BaseModel):
    id: int
    name: str
    occasion: Occasion
    season: Season
    items: List[WardrobeItemResponse]
    style_tags: List[StyleTag]
    color_palette: List[str]
    reasoning: Optional[str] = None
    visualization_url: Optional[str] = None
    is_favorite: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class OutfitVisualizeRequest(BaseModel):
    model_style: Optional[str] = "realistic"
    background: Optional[str] = "studio"
    pose: Optional[str] = "standing"


class WardrobeAnalytics(BaseModel):
    total_items: int
    category_breakdown: dict
    color_distribution: List[ColorInfo]
    season_coverage: dict
    most_worn_colors: List[str]
    style_distribution: dict
    gap_suggestions: List[str]
    sustainability_score: Optional[float] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: dict
    database_connected: bool
    ollama_connected: Optional[bool] = None
    weather_api_connected: Optional[bool] = None
    uptime_seconds: float
