"""Multi-threaded download engine with resume, filtering, and progress tracking."""

import os
import time
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Callable

import requests
from tqdm import tqdm

from coomertool.utils import ensure_dir, sanitize_filename, format_size, print_error, print_info
from coomertool.database import DownloadDB


class DownloadEngine:
    """
    Concurrent download manager with:
      - Resume support (Range headers)
      - File-type filtering
      - Size filtering
      - SQLite deduplication
      - Exponential backoff retries
    """

    def __init__(
        self,
        output_dir: Path,
        db: DownloadDB,
        threads: int = 32,
        timeout: int = 30,
        retries: int = 5,
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None,
        include_exts: Optional[list[str]] = None,
        exclude_exts: Optional[list[str]] = None,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        chunk_size: int = 8192,
        rate_limit: float = 0.0,
    ):
        self.output_dir = ensure_dir(output_dir)
        self.db = db
        self.threads = threads
        self.timeout = timeout
        self.retries = retries
        self.proxy = proxy
        self.user_agent = user_agent
        self.include_exts = set((e.lower().lstrip(".") for e in (include_exts or [])))
        self.exclude_exts = set((e.lower().lstrip(".") for e in (exclude_exts or [])))
        self.min_size = min_size
        self.max_size = max_size
        self.chunk_size = chunk_size
        self.rate_limit = rate_limit

        self.session = requests.Session()
        from coomertool.utils import get_headers
        self.session.headers.update(get_headers(user_agent))
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}

        self._stats = {
            "downloaded": 0,
            "skipped": 0,
            "failed": 0,
            "bytes": 0,
        }

    def _should_download(self, file_info: dict) -> bool:
        """Check filters before downloading."""
        name = file_info.get("name", "")
        ext = Path(name).suffix.lower().lstrip(".")
        size = file_info.get("size", 0) or 0

        if self.include_exts and ext not in self.include_exts:
            return False
        if self.exclude_exts and ext in self.exclude_exts:
            return False
        if self.min_size is not None and size > 0 and size < self.min_size:
            return False
        if self.max_size is not None and size > 0 and size > self.max_size:
            return False
        return True

    def _download_file(
        self,
        url: str,
        dest: Path,
        file_size: int = 0,
        post_id: Optional[str] = None,
        creator_id: Optional[str] = None,
        service: Optional[str] = None,
        domain: Optional[str] = None,
        pbar: Optional[tqdm] = None,
    ) -> bool:
        """Download a single file with resume support. Returns True on success."""
        if self.db.is_downloaded(url):
            self._stats["skipped"] += 1
            if pbar:
                pbar.update(1)
            return True

        # Check if partial file exists for resume
        existing_size = dest.stat().st_size if dest.exists() else 0
        headers = {}
        if existing_size > 0:
            headers["Range"] = f"bytes={existing_size}-"

        for attempt in range(self.retries):
            try:
                resp = self.session.get(
                    url,
                    headers=headers,
                    stream=True,
                    timeout=self.timeout,
                )

                if resp.status_code == 416:  # Range not satisfiable — file already complete
                    self.db.record_download(
                        url, str(dest), existing_size, None,
                        post_id, creator_id, service, domain, "completed",
                    )
                    self._stats["downloaded"] += 1
                    self._stats["bytes"] += existing_size
                    if pbar:
                        pbar.update(1)
                    return True

                resp.raise_for_status()

                mode = "ab" if existing_size > 0 and resp.status_code == 206 else "wb"
                downloaded = existing_size if mode == "ab" else 0

                with open(dest, mode) as f:
                    for chunk in resp.iter_content(chunk_size=self.chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                self.db.record_download(
                    url, str(dest), downloaded, None,
                    post_id, creator_id, service, domain, "completed",
                )
                self._stats["downloaded"] += 1
                self._stats["bytes"] += downloaded
                if pbar:
                    pbar.update(1)
                return True

            except requests.exceptions.RequestException as e:
                wait = (2 ** attempt) + random.uniform(0, 1)
                if attempt < self.retries - 1:
                    time.sleep(wait)
                else:
                    self.db.record_download(
                        url, str(dest), None, None,
                        post_id, creator_id, service, domain, "failed",
                    )
                    self._stats["failed"] += 1
                    if pbar:
                        pbar.update(1)
                    print_error(f"Failed after {self.retries} retries: {url} — {e}")
                    return False

        return False

    def download_post(
        self,
        post: dict,
        service: str,
        creator_id: str,
        domain: str,
        files: list[dict],
        metadata_format: str = "md",
    ) -> None:
        """Download all files for a single post."""
        post_id = str(post.get("id", "unknown"))
        title = sanitize_filename(post.get("title", "untitled"))
        post_dir = ensure_dir(self.output_dir / sanitize_filename(creator_id) / f"{post_id} - {title}")

        # Save metadata
        if metadata_format in ("md", "json"):
            self._save_metadata(post, post_dir, metadata_format)

        if not files:
            return

        # Filter files
        to_download = [f for f in files if self._should_download(f)]
        if not to_download:
            return

        with tqdm(
            total=len(to_download),
            desc=f"Post {post_id}",
            unit="file",
            leave=False,
        ) as pbar:
            for finfo in to_download:
                filename = sanitize_filename(finfo.get("name", "file"))
                dest = post_dir / filename
                self._download_file(
                    finfo["url"],
                    dest,
                    finfo.get("size", 0),
                    post_id,
                    creator_id,
                    service,
                    domain,
                    pbar,
                )

    def download_posts_concurrent(
        self,
        posts: list[dict],
        service: str,
        creator_id: str,
        domain: str,
        get_files_fn: Callable[[dict], list[dict]],
        metadata_format: str = "md",
    ) -> None:
        """Download multiple posts concurrently using thread pool."""
        total_files = 0
        post_file_map = {}

        for post in posts:
            files = [f for f in get_files_fn(post) if self._should_download(f)]
            if files:
                post_file_map[post["id"]] = (post, files)
                total_files += len(files)

        if not post_file_map:
            print_info("No files match current filters.")
            return

        print_info(f"Downloading {total_files} files across {len(post_file_map)} posts ({self.threads} threads)")

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {}
            for post_id, (post, files) in post_file_map.items():
                post_id_str = str(post_id)
                title = sanitize_filename(post.get("title", "untitled"))
                post_dir = ensure_dir(
                    self.output_dir / sanitize_filename(creator_id) / f"{post_id_str} - {title}"
                )

                # Save metadata
                if metadata_format in ("md", "json"):
                    self._save_metadata(post, post_dir, metadata_format)

                for finfo in files:
                    filename = sanitize_filename(finfo.get("name", "file"))
                    dest = post_dir / filename
                    future = executor.submit(
                        self._download_file,
                        finfo["url"],
                        dest,
                        finfo.get("size", 0),
                        post_id_str,
                        creator_id,
                        service,
                        domain,
                        None,
                    )
                    futures[future] = finfo["url"]

            with tqdm(total=len(futures), desc="Total Progress", unit="file") as pbar:
                for future in as_completed(futures):
                    future.result()
                    pbar.update(1)

    def _save_metadata(self, post: dict, post_dir: Path, fmt: str) -> None:
        """Save post metadata to file."""
        if fmt == "md":
            path = post_dir / "info.md"
            if path.exists():
                return
            content = self._format_md(post)
        elif fmt == "json":
            path = post_dir / "info.json"
            if path.exists():
                return
            import json
            content = json.dumps(post, indent=2, ensure_ascii=False)
        else:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as e:
            print_error(f"Could not write metadata: {e}")

    def _format_md(self, post: dict) -> str:
        """Format post data as Markdown."""
        lines = [
            f"# {post.get('title', 'Untitled')}",
            "",
            f"- **Post ID:** {post.get('id', 'N/A')}",
            f"- **Published:** {post.get('published', 'N/A')}",
            f"- **Edited:** {post.get('edited', 'N/A')}",
            f"- **Service:** {post.get('service', 'N/A')}",
            f"- **Creator ID:** {post.get('user', 'N/A')}",
            "",
            "## Content",
            "",
            post.get("content", "*No content.*"),
            "",
        ]
        embed = post.get("embed", {})
        if embed:
            lines.extend([
                "## Embed",
                "",
                f"```json",
                f"{embed}",
                f"```",
                "",
            ])
        return "\n".join(lines)

    def print_summary(self) -> None:
        """Print final download statistics."""
        print_info("=" * 50)
        print_info(f"Downloaded : {self._stats['downloaded']}")
        print_info(f"Skipped    : {self._stats['skipped']} (already in DB)")
        print_info(f"Failed     : {self._stats['failed']}")
        print_info(f"Total Size : {format_size(self._stats['bytes'])}")
        print_info("=" * 50)
