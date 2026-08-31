"""Utility helpers for URL parsing, path sanitization, and formatting."""

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote

# Domain mappings for mirror support
DOMAIN_ALIASES = {
    "kemono.party": "kemono.su",
    "kemono.cr": "kemono.su",
    "coomer.party": "coomer.su",
    "coomer.st": "coomer.su",
    "pawchive.pw": "kemono.su",
    "coomerfans.com": "coomer.su",
}

# Supported services
SERVICES = {
    "patreon", "fanbox", "fantia", "discord", "gumroad",
    "subscribestar", "dlsite", "boosty", "afdian",
    "onlyfans", "fansly", "candfans",
}


def normalize_domain(url: str) -> str:
    """Replace known mirror domains with canonical ones."""
    for alias, canonical in DOMAIN_ALIASES.items():
        url = url.replace(alias, canonical)
    return url


def parse_kemono_url(url: str) -> dict | None:
    """
    Parse a Kemono/Coomer URL and return components.
    Supports:
      - Post:  https://kemono.su/{service}/user/{user_id}/post/{post_id}
      - Profile: https://kemono.su/{service}/user/{user_id}
    """
    url = normalize_domain(url)
    parsed = urlparse(url)
    path = unquote(parsed.path).strip("/")
    parts = path.split("/")

    if len(parts) >= 4 and parts[1] == "user":
        service = parts[0]
        user_id = parts[2]
        if service not in SERVICES:
            return None
        result = {"domain": parsed.netloc, "service": service, "user_id": user_id}
        if len(parts) >= 5 and parts[3] == "post":
            result["post_id"] = parts[4]
            result["type"] = "post"
        else:
            result["type"] = "profile"
        return result
    return None


def sanitize_filename(name: str, max_len: int = 120) -> str:
    """Remove illegal filesystem characters and truncate."""
    name = re.sub(r'[<>:"/\|?*]', "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    if len(name) > max_len:
        name = name[:max_len].rsplit(" ", 1)[0] + "…"
    return name or "untitled"


def format_size(size_bytes: int) -> str:
    """Human-readable file size."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:3.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def ensure_dir(path: Path) -> Path:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_headers(user_agent: str | None = None) -> dict:
    """Return default HTTP headers."""
    return {
        "User-Agent": user_agent or "CoomerTool/1.0 (Python; https://github.com/GangTailorUpgrade/CoomeRtool)",
        "Accept": "application/json, text/html, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }


def print_error(msg: str) -> None:
    """Print to stderr."""
    print(f"[ERROR] {msg}", file=sys.stderr)


def print_info(msg: str) -> None:
    """Print info message."""
    print(f"[INFO] {msg}")
