"""Kemono / Coomer API client with retry logic and proxy support."""

import json
import time
import random
from typing import Optional, Iterator
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from coomertool.utils import get_headers, print_error, print_info


class KemonoAPI:
    """
    Client for Kemono/Coomer public API.
    Endpoints:
      - GET /api/v1/{service}/user/{creator_id}
      - GET /api/v1/{service}/user/{creator_id}/posts-legacy?o={offset}
      - GET /api/v1/{service}/user/{creator_id}/post/{post_id}
    """

    def __init__(
        self,
        domain: str = "kemono.su",
        timeout: int = 30,
        retries: int = 5,
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None,
        rate_limit: float = 0.0,
    ):
        self.domain = domain
        self.base_url = f"https://{domain}"
        self.api_base = f"{self.base_url}/api/v1"
        self.timeout = timeout
        self.rate_limit = rate_limit
        self._last_request_time = 0.0

        self.session = requests.Session()
        self.session.headers.update(get_headers(user_agent))

        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}

        # Retry strategy: exponential backoff for 429, 502, 503, 504
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=50)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _rate_limit_wait(self) -> None:
        """Enforce minimum delay between requests."""
        if self.rate_limit > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.rate_limit:
                time.sleep(self.rate_limit - elapsed + random.uniform(0, 0.1))
        self._last_request_time = time.time()

    def _get(self, endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
        """Make a GET request with rate limiting and error handling."""
        self._rate_limit_wait()
        url = urljoin(self.api_base, endpoint)
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 404:
                print_error(f"Not found: {url}")
            elif resp.status_code == 403:
                print_error(f"Forbidden (403) — try a proxy or reduce threads: {url}")
            else:
                print_error(f"HTTP {resp.status_code}: {url}")
            return None
        except requests.exceptions.RequestException as e:
            print_error(f"Request failed: {e}")
            return None
        except json.JSONDecodeError:
            print_error(f"Invalid JSON from {url}")
            return None

    def get_creator(self, service: str, creator_id: str) -> Optional[dict]:
        """Fetch creator profile."""
        return self._get(f"/{service}/user/{creator_id}")

    def get_post(self, service: str, creator_id: str, post_id: str) -> Optional[dict]:
        """Fetch a single post."""
        return self._get(f"/{service}/user/{creator_id}/post/{post_id}")

    def get_posts(self, service: str, creator_id: str, offset: int = 0) -> Optional[list]:
        """Fetch a page of posts (50 per page)."""
        data = self._get(f"/{service}/user/{creator_id}/posts-legacy", params={"o": offset})
        if isinstance(data, list):
            return data
        # Some endpoints return dict with posts key
        if isinstance(data, dict) and "posts" in data:
            return data["posts"]
        return None

    def iter_all_posts(self, service: str, creator_id: str) -> Iterator[dict]:
        """Iterate through all posts for a creator, paginated."""
        offset = 0
        while True:
            posts = self.get_posts(service, creator_id, offset)
            if not posts:
                break
            for post in posts:
                yield post
            if len(posts) < 50:
                break
            offset += 50

    def get_post_files(self, post: dict) -> list[dict]:
        """Extract downloadable file entries from a post object."""
        files = []
        # Main file
        if post.get("file") and post["file"].get("path"):
            files.append({
                "name": post["file"].get("name", "file"),
                "path": post["file"]["path"],
                "url": f"https://{self.domain}/data{post['file']['path']}",
                "size": post["file"].get("size", 0),
            })
        # Attachments
        for att in post.get("attachments", []):
            if att.get("path"):
                files.append({
                    "name": att.get("name", "attachment"),
                    "path": att["path"],
                    "url": f"https://{self.domain}/data{att['path']}",
                    "size": att.get("size", 0),
                })
        return files
