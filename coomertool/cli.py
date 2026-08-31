"""Command-line interface for CoomerTool."""

import argparse
import sys
from pathlib import Path

from coomertool import __version__
from coomertool.api import KemonoAPI
from coomertool.config import Config
from coomertool.database import DownloadDB
from coomertool.downloader import DownloadEngine
from coomertool.utils import parse_kemono_url, print_info, print_error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="coomertool",
        description="Fast multi-threaded CLI downloader for Kemono & Coomer archives.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m coomertool "https://kemono.su/patreon/user/123/post/456"
  python -m coomertool "https://coomer.su/onlyfans/user/name" --all --threads 64
  python -m coomertool "URL" --all --include mp4,png --output ./archive
  python -m coomertool --batch urls.txt --threads 128
        """,
    )
    parser.add_argument("url", nargs="?", help="Kemono/Coomer post or creator URL")
    parser.add_argument("-a", "--all", action="store_true", help="Download all posts from creator profile")
    parser.add_argument("-o", "--output", default="./downloads", help="Output directory (default: ./downloads)")
    parser.add_argument("-t", "--threads", type=int, default=32, help="Max concurrent downloads (default: 32)")
    parser.add_argument("--include", help="Comma-separated extensions to include (e.g., jpg,png,mp4)")
    parser.add_argument("--exclude", help="Comma-separated extensions to exclude")
    parser.add_argument("--min-size", type=int, help="Minimum file size in bytes")
    parser.add_argument("--max-size", type=int, help="Maximum file size in bytes")
    parser.add_argument("--resume", action="store_true", help="Resume interrupted downloads (enabled by default via DB)")
    parser.add_argument("--metadata", choices=["md", "json", "none"], default="md", help="Save post metadata format (default: md)")
    parser.add_argument("--proxy", help="Proxy URL (http://host:port or socks5://host:port)")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds (default: 30)")
    parser.add_argument("--retries", type=int, default=5, help="Max retry attempts (default: 5)")
    parser.add_argument("--db", default="./coomertool.db", help="SQLite database path (default: ./coomertool.db)")
    parser.add_argument("--config", default="./config.json", help="Config file path (default: ./config.json)")
    parser.add_argument("--update-config", action="store_true", help="Save current args to config file and exit")
    parser.add_argument("--batch", help="Path to text file containing URLs (one per line)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def process_url(url: str, args: argparse.Namespace, config: Config, db: DownloadDB) -> bool:
    """Process a single URL. Returns True on success."""
    parsed = parse_kemono_url(url)
    if not parsed:
        print_error(f"Could not parse URL: {url}")
        return False

    domain = parsed["domain"]
    service = parsed["service"]
    user_id = parsed["user_id"]

    api = KemonoAPI(
        domain=domain,
        timeout=config["timeout"],
        retries=config["retries"],
        proxy=config["proxy"],
        user_agent=config.get("user_agent"),
        rate_limit=config.get("rate_limit", 0.0),
    )

    engine = DownloadEngine(
        output_dir=Path(config["output"]),
        db=db,
        threads=config["threads"],
        timeout=config["timeout"],
        retries=config["retries"],
        proxy=config["proxy"],
        user_agent=config.get("user_agent"),
        include_exts=config.get("include") or [],
        exclude_exts=config.get("exclude") or [],
        min_size=config.get("min_size"),
        max_size=config.get("max_size"),
        rate_limit=config.get("rate_limit", 0.0),
    )

    if parsed.get("type") == "post":
        post_id = parsed["post_id"]
        print_info(f"Fetching post {post_id} from {service}/{user_id}")
        post = api.get_post(service, user_id, post_id)
        if not post:
            print_error(f"Post not found: {post_id}")
            return False
        files = api.get_post_files(post)
        engine.download_post(post, service, user_id, domain, files, config["metadata"])
        engine.print_summary()
        return True

    elif args.all or parsed.get("type") == "profile":
        print_info(f"Fetching profile {user_id} from {service} on {domain}")
        creator = api.get_creator(service, user_id)
        if not creator:
            print_error(f"Creator not found: {user_id}")
            return False

        print_info(f"Creator: {creator.get('name', 'Unknown')} — fetching posts...")
        posts = list(api.iter_all_posts(service, user_id))
        print_info(f"Found {len(posts)} posts")

        if not posts:
            print_info("No posts found.")
            return True

        engine.download_posts_concurrent(
            posts, service, user_id, domain, api.get_post_files, config["metadata"]
        )
        engine.print_summary()
        return True
    else:
        print_error("URL must be a post or creator profile. Use --all for profiles.")
        return False


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # Load config
    config = Config(args.config)
    config.merge_args(args)

    if args.update_config:
        config.save()
        return 0

    # Collect URLs
    urls = []
    if args.batch:
        batch_path = Path(args.batch)
        if not batch_path.exists():
            print_error(f"Batch file not found: {batch_path}")
            return 1
        with open(batch_path, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    elif args.url:
        urls = [args.url]
    else:
        parser.print_help()
        return 1

    # Init database
    db = DownloadDB(config["db_path"])

    print_info(f"CoomerTool v{__version__} — {len(urls)} URL(s) queued")
    print_info(f"Output: {config['output']} | Threads: {config['threads']} | DB: {config['db_path']}")

    success_count = 0
    for url in urls:
        if process_url(url, args, config, db):
            success_count += 1

    stats = db.get_stats()
    print_info(f"\nAll done. {success_count}/{len(urls)} URLs processed successfully.")
    print_info(f"Database: {stats['completed']} completed, {stats['failed']} failed, {stats['total']} total records.")
    return 0 if success_count == len(urls) else 1


if __name__ == "__main__":
    sys.exit(main())
