"""AI-powered clothing image analysis and tagging."""
import json
from pathlib import Path
from typing import Dict, List
from PIL import Image
import numpy as np

from app.config import settings


class AITaggingService:
    """Analyzes clothing images and extracts metadata using CLIP and heuristics."""

    def __init__(self):
        self._clip_loaded = False
        self._processor = None
        self._model = None

    def _load_clip(self):
        if self._clip_loaded:
            return
        try:
            from transformers import CLIPProcessor, CLIPModel
            self._processor = CLIPProcessor.from_pretrained(settings.clip_model)
            self._model = CLIPModel.from_pretrained(settings.clip_model)
            self._clip_loaded = True
        except Exception as e:
            print(f"CLIP load warning: {e}")

    def analyze_image(self, image_path: str) -> Dict:
        """Analyze a clothing image and return structured metadata."""
        img = Image.open(image_path).convert("RGB")

        # Extract dominant colors
        colors = self._extract_colors(img)

        # Determine category via CLIP or heuristics
        category = self._detect_category(image_path, img)

        # Detect season from colors
        season = self._detect_season(colors)

        # Style tags
        style_tags = self._detect_style(img, colors)

        # Fabric detection (basic heuristic)
        fabric = self._detect_fabric(img)

        # Pattern detection
        pattern = self._detect_pattern(img)

        suggested_name = self._suggest_name(category, colors[0]["name"] if colors else "unknown", fabric)

        return {
            "suggested_name": suggested_name,
            "category": category,
            "colors": colors,
            "season": season,
            "style_tags": style_tags,
            "fabric": fabric,
            "pattern": pattern,
        }

    def _extract_colors(self, img: Image.Image, num_colors: int = 3) -> List[Dict]:
        """Extract dominant colors using k-means clustering on resized image."""
        img_small = img.resize((100, 100))
        pixels = np.array(img_small).reshape(-1, 3)

        # Simple quantization
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)

        colors = []
        for center, count in zip(kmeans.cluster_centers_, np.bincount(kmeans.labels_)):
            hex_color = "#{:02x}{:02x}{:02x}".format(int(center[0]), int(center[1]), int(center[2]))
            colors.append({
                "hex": hex_color,
                "name": self._hex_to_name(hex_color),
                "percentage": round(count / len(pixels) * 100, 1),
            })

        colors.sort(key=lambda x: x["percentage"], reverse=True)
        return colors

    def _hex_to_name(self, hex_color: str) -> str:
        """Map hex color to approximate name."""
        color_map = {
            "#000000": "Black", "#FFFFFF": "White", "#FF0000": "Red",
            "#00FF00": "Green", "#0000FF": "Blue", "#FFFF00": "Yellow",
            "#FFA500": "Orange", "#800080": "Purple", "#FFC0CB": "Pink",
            "#A52A2A": "Brown", "#808080": "Gray", "#C0C0C0": "Silver",
            "#FFD700": "Gold", "#40E0D0": "Turquoise", "#FA8072": "Salmon",
            "#800000": "Maroon", "#008000": "Dark Green", "#000080": "Navy",
            "#F5F5DC": "Beige", "#D2691E": "Chocolate", "#B22222": "Firebrick",
        }
        # Find closest
        from sklearn.metrics import pairwise_distances
        target = np.array([[int(hex_color[i:i+2], 16) for i in (1, 3, 5)]])
        candidates = np.array([[int(h[i:i+2], 16) for i in (1, 3, 5)] for h in color_map.keys()])
        distances = pairwise_distances(target, candidates)
        closest_idx = distances.argmin()
        return list(color_map.values())[closest_idx]

    def _detect_category(self, image_path: str, img: Image.Image) -> str:
        """Detect clothing category using CLIP or fallback heuristics."""
        self._load_clip()

        if self._model and self._processor:
            categories = [
                "a photo of a shirt or top", "a photo of pants or trousers",
                "a photo of a dress", "a photo of a jacket or coat",
                "a photo of shoes", "a photo of a bag or accessory",
                "a photo of athletic wear", "a photo of swimwear",
                "a photo of loungewear", "a photo of formal wear"
            ]
            cat_map = ["top", "bottom", "dress", "outerwear", "shoes", 
                      "accessory", "activewear", "swimwear", "loungewear", "formal"]

            inputs = self._processor(text=categories, images=img, return_tensors="pt", padding=True)
            outputs = self._model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1)
            best_idx = probs.argmax().item()
            return cat_map[best_idx]

        # Fallback: use filename hints
        name = Path(image_path).stem.lower()
        if any(w in name for w in ["shirt", "top", "blouse", "t-shirt", "sweater"]):
            return "top"
        elif any(w in name for w in ["pant", "trouser", "jean", "short", "skirt"]):
            return "bottom"
        elif "dress" in name:
            return "dress"
        elif any(w in name for w in ["jacket", "coat", "blazer", "cardigan"]):
            return "outerwear"
        elif any(w in name for w in ["shoe", "boot", "sneaker", "heel", "sandal"]):
            return "shoes"
        elif any(w in name for w in ["bag", "belt", "hat", "scarf", "jewelry", "watch"]):
            return "accessory"
        return "top"

    def _detect_season(self, colors: List[Dict]) -> str:
        """Infer season from color palette."""
        warm_colors = ["Red", "Orange", "Yellow", "Gold", "Brown", "Beige", "Maroon"]
        cool_colors = ["Blue", "Navy", "Green", "Turquoise", "Purple", "Gray", "Silver"]

        warm_score = sum(1 for c in colors if c["name"] in warm_colors)
        cool_score = sum(1 for c in colors if c["name"] in cool_colors)

        if warm_score > cool_score:
            return "autumn,spring"
        elif cool_score > warm_score:
            return "winter,summer"
        return "all_season"

    def _detect_style(self, img: Image.Image, colors: List[Dict]) -> List[str]:
        """Detect style tags from image characteristics."""
        tags = ["casual"]

        # Brightness-based
        img_gray = img.convert("L")
        brightness = np.mean(np.array(img_gray))
        if brightness > 200:
            tags.append("minimalist")
        elif brightness < 80:
            tags.append("luxury")

        # Color-based
        color_names = [c["name"] for c in colors]
        if "Black" in color_names and len(color_names) <= 2:
            tags.append("classic")
        if any(c in color_names for c in ["Red", "Orange", "Yellow", "Pink"]):
            tags.append("trendy")
        if "Blue" in color_names or "Navy" in color_names:
            tags.append("preppy")

        return list(set(tags))

    def _detect_fabric(self, img: Image.Image) -> str:
        """Basic fabric detection from texture analysis."""
        # Placeholder: would use texture classification model
        return "cotton"

    def _detect_pattern(self, img: Image.Image) -> str:
        """Detect pattern type."""
        # Placeholder: would use pattern classification
        return "solid"

    def _suggest_name(self, category: str, color: str, fabric: str) -> str:
        """Generate a human-readable item name."""
        return f"{color} {fabric} {category}".title()
