"""SQLAlchemy database setup and ORM models."""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association tables
outfit_items = Table(
    "outfit_items",
    Base.metadata,
    Column("outfit_id", Integer, ForeignKey("outfits.id"), primary_key=True),
    Column("wardrobe_item_id", Integer, ForeignKey("wardrobe_items.id"), primary_key=True),
    Column("position", Integer, default=0),
)

item_tags = Table(
    "item_tags",
    Base.metadata,
    Column("item_id", Integer, ForeignKey("wardrobe_items.id"), primary_key=True),
    Column("tag", String(50), primary_key=True),
)


class WardrobeItemDB(Base):
    __tablename__ = "wardrobe_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    colors = Column(Text, default="[]")  # JSON list of colors
    season = Column(String(100), default="all_season")
    style_tags = Column(String(255), default="")
    fabric = Column(String(100), nullable=True)
    pattern = Column(String(100), nullable=True)
    image_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500), nullable=False)
    embedding_id = Column(String(100), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    outfits = relationship("OutfitDB", secondary=outfit_items, back_populates="items")


class OutfitDB(Base):
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    occasion = Column(String(50), nullable=False, index=True)
    season = Column(String(50), nullable=False)
    style_tags = Column(String(255), default="")
    color_palette = Column(Text, default="[]")
    reasoning = Column(Text, nullable=True)
    visualization_path = Column(String(500), nullable=True)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("WardrobeItemDB", secondary=outfit_items, back_populates="outfits")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
