#!/usr/bin/env python3
"""
Upload postări social media pe Google Drive într-o structură flat cu config.json.
Propune timpi de postare pe baza regulilor de scheduling și triggerează n8n webhook.

Usage:
    python3 upload_to_drive.py --postari-dir ./postari
    python3 upload_to_drive.py --postari-dir ./postari --dry-run
    python3 upload_to_drive.py --postari-dir ./postari --auto-post
    python3 upload_to_drive.py --postari-dir ./postari --auto-post --scheduled-times '{"slug": "2026-03-03T09:00:00+02:00"}'
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import zoneinfo

    ZoneInfo = zoneinfo.ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo


# ─── ENV ────────────────────────────────────────────────────────────────────────


def find_env_file():
    """Walk up directories to find .env file."""
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        env_path = os.path.join(d, ".env")
        if os.path.exists(env_path):
            return env_path
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


def load_env():
    """Load .env file into os.environ."""
    env_path = find_env_file()
    if env_path:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())
    return env_path


def check_env_vars():
    """Check required environment variables. Returns list of missing ones."""
    required = [
        "GOOGLE_DRIVE_FOLDER_ID",
        "GOOGLE_CREDENTIALS_PATH",
    ]
    missing = [v for v in required if not os.environ.get(v)]
    return missing


# ─── FRONTMATTER PARSING ───────────────────────────────────────────────────────


def parse_frontmatter(text):
    """Parse YAML frontmatter from markdown text. Returns (metadata_dict, body)."""
    if not text.startswith("---"):
        return {}, text

    end = text.find("---", 3)
    if end == -1:
        return {}, text

    fm_text = text[3:end].strip()
    body = text[end + 3 :].strip()

    metadata = {}
    current_key = None
    list_mode = False

    for line in fm_text.split("\n"):
        stripped = line.strip()

        # List item
        if stripped.startswith("- ") and current_key and list_mode:
            val = stripped[2:].strip().strip('"').strip("'")
            if current_key not in metadata:
                metadata[current_key] = []
            metadata[current_key].append(val)
            continue

        # Key: value
        match = re.match(r"^(\w[\w_-]*)\s*:\s*(.*)", line)
        if match:
            key = match.group(1)
            value = match.group(2).strip()

            if value == "" or value == ">":
                current_key = key
                list_mode = value == ""
                if value == ">":
                    metadata[key] = ""
                continue

            # Array on same line: ["a", "b"]
            if value.startswith("["):
                try:
                    metadata[key] = json.loads(value.replace("'", '"'))
                except json.JSONDecodeError:
                    items = re.findall(r'"([^"]*)"', value)
                    metadata[key] = items
                current_key = key
                list_mode = False
                continue

            # Boolean / null
            if value.lower() in ("true", "false"):
                metadata[key] = value.lower() == "true"
            elif value.lower() == "null" or value == "~":
                metadata[key] = None
            else:
                metadata[key] = value.strip('"').strip("'")

            current_key = key
            list_mode = value == ""
        elif current_key and not list_mode and stripped:
            # Multi-line string continuation (for > blocks)
            if current_key in metadata and isinstance(metadata[current_key], str):
                metadata[current_key] += (" " if metadata[current_key] else "") + stripped

    return metadata, body


def extract_caption(body):
    """Extract ZONA A from body — text between end-of-frontmatter and '## Note Editoriale'."""
    marker = "## Note Editoriale"
    idx = body.find(marker)
    if idx != -1:
        caption = body[:idx].strip()
    else:
        caption = body.strip()
    return caption


# ─── SCANNING & COLLECTION ─────────────────────────────────────────────────────

FOLDER_TO_PLATFORM = {
    "01-linkedin": "linkedin",
    "02-instagram": "instagram",
    "03-x": "x",
    "04-newsletter": "newsletter",
    "05-youtube": "youtube",
    "06-podcast": "podcast",
    "07-tiktok-reels": "tiktok-reels",
}

MEDIA_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mp3", ".wav"}


def collect_media_files(media_dir):
    """Collect final media files from a directory, excluding prompt-*.json."""
    if not os.path.isdir(media_dir):
        return []
    files = []
    for f in sorted(os.listdir(media_dir)):
        ext = os.path.splitext(f)[1].lower()
        if ext in MEDIA_EXTENSIONS and not f.startswith("prompt-"):
            files.append(f)
    return files


def determine_post_type(media_files):
    """Determine post_type from media files: single-image|carousel|video|audio."""
    has_video = any(f.endswith(".mp4") for f in media_files)
    has_audio = any(f.endswith((".mp3", ".wav")) for f in media_files)
    image_files = [f for f in media_files if any(f.endswith(e) for e in (".png", ".jpg", ".jpeg", ".webp"))]
    num_images = len(image_files)

    if has_video:
        return "video"
    if has_audio and num_images <= 1:
        return "audio"
    if num_images > 1:
        return "carousel"
    return "single-image"


def scan_posts(postari_dir):
    """Scan all topics in postari/, return list of post dicts."""
    posts = []
    postari_path = Path(postari_dir)

    if not postari_path.exists():
        print(f"ERROR: postari directory not found: {postari_dir}")
        return posts

    # Walk topic directories
    for topic_dir in sorted(postari_path.iterdir()):
        if not topic_dir.is_dir() or topic_dir.name.startswith("."):
            continue

        topic_name = topic_dir.name

        # Walk platform directories within topic
        for platform_dir in sorted(topic_dir.iterdir()):
            if not platform_dir.is_dir() or platform_dir.name.startswith("."):
                continue

            platform_folder = platform_dir.name
            platform = FOLDER_TO_PLATFORM.get(platform_folder)
            if not platform:
                continue

            # Find all .md files in this platform dir
            for md_file in sorted(platform_dir.glob("*.md")):
                if md_file.name.startswith("INDEX") or md_file.name.startswith("."):
                    continue

                slug = md_file.stem
                media_dir = platform_dir / slug

                # Parse the MD file
                text = md_file.read_text(encoding="utf-8")
                metadata, body = parse_frontmatter(text)
                caption = extract_caption(body)

                # Check media readiness
                image_status = metadata.get("image_status")
                video_status = metadata.get("video_status")
                audio_status = metadata.get("audio_status")

                # Skip if not ready
                has_ready_media = False
                if image_status == "ready":
                    has_ready_media = True
                if video_status == "ready":
                    has_ready_media = True
                if audio_status == "ready":
                    has_ready_media = True

                if not has_ready_media:
                    continue

                # Collect media files
                media_files = collect_media_files(media_dir)
                if not media_files:
                    continue

                post_type = determine_post_type(media_files)

                # Determine cover image
                cover_image = None
                for candidate in ["cover.png", "cover.jpg", "cover.jpeg", "cover.webp"]:
                    if candidate in media_files:
                        cover_image = candidate
                        break

                # Separate media by type
                video_file = None
                audio_file = None
                extra_media = []

                for f in media_files:
                    if f.endswith(".mp4") and not video_file:
                        video_file = f
                    elif f.endswith((".mp3", ".wav")) and not audio_file:
                        audio_file = f
                    elif f != cover_image:
                        extra_media.append(f)

                post = {
                    "topic": topic_name,
                    "platform_folder": platform_folder,
                    "platform": platform,
                    "slug": slug,
                    "md_path": str(md_file),
                    "media_dir": str(media_dir),
                    "metadata": metadata,
                    "caption": caption,
                    "post_type": post_type,
                    "cover_image": cover_image,
                    "media_files": extra_media,
                    "video_file": video_file,
                    "audio_file": audio_file,
                    "hashtags": metadata.get("hashtags", []),
                }
                posts.append(post)

    return posts


# ─── SCHEDULING ─────────────────────────────────────────────────────────────────

# Mapping day names (Romanian-friendly) to weekday numbers
DAY_NAMES_RO = {
    "luni": 0,
    "marți": 1,
    "miercuri": 2,
    "joi": 3,
    "vineri": 4,
    "sâmbătă": 5,
    "duminică": 6,
}

# Default scheduling rules (used if parsing fails)
DEFAULT_RULES = {
    "linkedin": {
        "weekday_slots": [(8, 0), (12, 0)],
        "weekend_slots": [(10, 0)],
        "optimal_days": [1, 2, 3],
        "avoid_days": [6],
        "spacing_hours": 6,
        "max_per_day": 2,
    },
    "instagram": {
        "weekday_slots": [(11, 0), (19, 0)],
        "weekend_slots": [(10, 0), (18, 0)],
        "optimal_days": [2, 3, 4],
        "avoid_days": [0],
        "spacing_hours": 4,
        "max_per_day": 3,
    },
    "x": {
        "weekday_slots": [(9, 0), (12, 0)],
        "weekend_slots": [(10, 0)],
        "optimal_days": [1, 2],
        "avoid_days": [6],
        "spacing_hours": 2,
        "max_per_day": 5,
    },
    "tiktok-reels": {
        "weekday_slots": [(12, 0), (19, 0)],
        "weekend_slots": [(11, 0)],
        "optimal_days": [3, 4, 5],
        "avoid_days": [0],
        "spacing_hours": 3,
        "max_per_day": 3,
    },
    "newsletter": {
        "weekday_slots": [(9, 0)],
        "weekend_slots": [],
        "optimal_days": [1, 2],
        "avoid_days": [4, 5, 6],
        "spacing_hours": 24,
        "max_per_day": 1,
    },
    "youtube": {
        "weekday_slots": [(14, 0)],
        "weekend_slots": [(10, 0)],
        "optimal_days": [3, 4],
        "avoid_days": [0],
        "spacing_hours": 24,
        "max_per_day": 1,
    },
    "podcast": {
        "weekday_slots": [(7, 0)],
        "weekend_slots": [(9, 0)],
        "optimal_days": [0, 1],
        "avoid_days": [4, 5],
        "spacing_hours": 48,
        "max_per_day": 1,
    },
}

MAX_TOTAL_PER_DAY = 8


def get_current_datetime(tz_name=None):
    """Get current datetime with timezone from .env or default."""
    tz_name = tz_name or os.environ.get("TIMEZONE", "Europe/Bucharest")
    tz = ZoneInfo(tz_name)
    return datetime.now(tz)


def calculate_schedule(posts, now):
    """Calculate scheduled times for posts respecting scheduling rules."""
    rules = DEFAULT_RULES

    # Group by platform
    by_platform = {}
    for post in posts:
        plat = post["platform"]
        by_platform.setdefault(plat, []).append(post)

    # Track assigned slots per day and per platform per day
    day_counts = {}  # date -> total count
    platform_day_counts = {}  # (platform, date) -> count
    platform_last_time = {}  # platform -> last scheduled datetime

    scheduled = []

    # Start scheduling from tomorrow to avoid same-day rush
    current_date = (now + timedelta(days=1)).date()

    for platform, platform_posts in sorted(by_platform.items()):
        rule = rules.get(platform, rules.get("linkedin"))
        slot_idx = 0

        for post in platform_posts:
            assigned = False
            search_date = current_date
            attempts = 0

            while not assigned and attempts < 60:
                attempts += 1
                weekday = search_date.weekday()

                # Skip avoided days
                if weekday in rule.get("avoid_days", []):
                    search_date += timedelta(days=1)
                    continue

                # Check max total per day
                if day_counts.get(search_date, 0) >= MAX_TOTAL_PER_DAY:
                    search_date += timedelta(days=1)
                    continue

                # Check max per platform per day
                key = (platform, search_date)
                if platform_day_counts.get(key, 0) >= rule["max_per_day"]:
                    search_date += timedelta(days=1)
                    continue

                # Pick time slot
                is_weekend = weekday >= 5
                slots = rule["weekend_slots"] if is_weekend else rule["weekday_slots"]
                if not slots:
                    search_date += timedelta(days=1)
                    continue

                # Cycle through available slots
                slot_h, slot_m = slots[slot_idx % len(slots)]
                tz = now.tzinfo
                candidate = datetime(
                    search_date.year,
                    search_date.month,
                    search_date.day,
                    slot_h,
                    slot_m,
                    tzinfo=tz,
                )

                # Check spacing from last post on same platform
                last = platform_last_time.get(platform)
                if last and (candidate - last).total_seconds() < rule["spacing_hours"] * 3600:
                    slot_idx += 1
                    if slot_idx % len(slots) == 0:
                        search_date += timedelta(days=1)
                        slot_idx = 0
                    continue

                # Assign
                post["scheduled_time"] = candidate.isoformat()
                platform_last_time[platform] = candidate
                day_counts[search_date] = day_counts.get(search_date, 0) + 1
                platform_day_counts[key] = platform_day_counts.get(key, 0) + 1
                scheduled.append(post)
                assigned = True
                slot_idx += 1

            if not assigned:
                # Fallback: assign anyway
                tz = now.tzinfo
                fallback_date = current_date + timedelta(days=attempts)
                candidate = datetime(
                    fallback_date.year,
                    fallback_date.month,
                    fallback_date.day,
                    9,
                    0,
                    tzinfo=tz,
                )
                post["scheduled_time"] = candidate.isoformat()
                scheduled.append(post)

    return scheduled


# ─── DRIVE OPERATIONS ───────────────────────────────────────────────────────────


def authenticate(creds_path):
    """Authenticate with Google Drive API. Returns service object."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    SCOPES = ["https://www.googleapis.com/auth/drive"]
    token_path = os.path.join(os.path.dirname(creds_path), "token.json")

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, "w") as f:
                f.write(creds.to_json())
        else:
            print("ERROR: No valid token. Run setup_drive_auth.py first.")
            sys.exit(1)

    return build("drive", "v3", credentials=creds)


def get_existing_folders(service, parent_id):
    """List existing folders in the Drive parent folder."""
    folders = []
    page_token = None

    while True:
        results = (
            service.files()
            .list(
                q=f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
                fields="nextPageToken, files(id, name)",
                pageSize=1000,
                pageToken=page_token,
            )
            .execute()
        )
        folders.extend(results.get("files", []))
        page_token = results.get("nextPageToken")
        if not page_token:
            break

    return folders


def get_next_counter(existing_folders):
    """Get next counter value from existing folder names (NNNNN-slug format)."""
    max_counter = 0
    for folder in existing_folders:
        match = re.match(r"^(\d{5})-", folder["name"])
        if match:
            counter = int(match.group(1))
            max_counter = max(max_counter, counter)
    return max_counter + 1


def check_duplicate(post, existing_folders):
    """Check if a post already exists on Drive (by slug+platform suffix)."""
    target_suffix = f"-{post['slug']}-{post['platform']}"
    for folder in existing_folders:
        if folder["name"].endswith(target_suffix):
            return folder
    return None


def create_drive_folder(service, name, parent_id):
    """Create a folder on Google Drive."""
    file_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=file_metadata, fields="id").execute()
    return folder.get("id")


def upload_file(service, local_path, folder_id, filename=None):
    """Upload a file to a Google Drive folder."""
    from googleapiclient.http import MediaFileUpload

    fname = filename or os.path.basename(local_path)
    file_metadata = {"name": fname, "parents": [folder_id]}

    # Determine MIME type
    ext = os.path.splitext(local_path)[1].lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".mp4": "video/mp4",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".json": "application/json",
    }
    mime_type = mime_types.get(ext, "application/octet-stream")

    media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    return file.get("id")


def upload_config_json(service, config_data, folder_id):
    """Upload config.json content to a Drive folder."""
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
        tmp_path = f.name

    try:
        file_id = upload_file(service, tmp_path, folder_id, "config.json")
    finally:
        os.unlink(tmp_path)

    return file_id


def build_config_json(post, auto_post=False):
    """Build config.json with the fixed schema."""
    return {
        "platform": post["platform"],
        "post_type": post["post_type"],
        "status": "pending",
        "auto_post": auto_post,
        "scheduled_time": post.get("scheduled_time"),
        "posted_at": None,
        "caption": post["caption"],
        "hashtags": post["hashtags"],
        "cover_image": post["cover_image"],
        "media_files": post["media_files"],
        "video_file": post["video_file"],
        "audio_file": post["audio_file"],
    }


# ─── WEBHOOK ────────────────────────────────────────────────────────────────────


def send_webhook(webhook_url, drive_folder_id):
    """Send POST webhook to n8n with the drive folder ID."""
    import urllib.request

    data = json.dumps({"drive_folder_id": drive_folder_id}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"  WARNING: Webhook failed: {e}")
        return False


# ─── MAIN ───────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Upload postări pe Google Drive cu config.json"
    )
    parser.add_argument(
        "--postari-dir",
        default="./postari",
        help="Directorul cu postări (default: ./postari)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview fără upload efectiv",
    )
    parser.add_argument(
        "--auto-post",
        action="store_true",
        help="Set auto_post=true pe toate postările",
    )
    parser.add_argument(
        "--scheduled-times",
        type=str,
        default=None,
        help='JSON dict cu slug->scheduled_time overrides (ex: \'{"slug": "2026-03-03T09:00:00+02:00"}\')',
    )
    args = parser.parse_args()

    # Load environment
    load_env()
    missing = check_env_vars()
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        print("Set them in .env or run the skill workflow for guided setup.")
        sys.exit(1)

    folder_id = os.environ["GOOGLE_DRIVE_FOLDER_ID"]
    creds_path = os.path.expanduser(os.environ["GOOGLE_CREDENTIALS_PATH"])
    webhook_url = os.environ.get("N8N_WEBHOOK_URL")
    tz_name = os.environ.get("TIMEZONE", "Europe/Bucharest")

    # Parse scheduled time overrides
    time_overrides = {}
    if args.scheduled_times:
        try:
            time_overrides = json.loads(args.scheduled_times)
        except json.JSONDecodeError:
            print(f"ERROR: Invalid JSON for --scheduled-times: {args.scheduled_times}")
            sys.exit(1)

    # ── Step 1: Scan posts ──
    print("Scanning posts...")
    posts = scan_posts(args.postari_dir)
    if not posts:
        print("No ready posts found.")
        sys.exit(0)

    print(f"Found {len(posts)} ready posts.\n")

    # ── Step 2: Calculate schedule ──
    now = get_current_datetime(tz_name)
    posts = calculate_schedule(posts, now)

    # Apply time overrides
    for post in posts:
        if post["slug"] in time_overrides:
            post["scheduled_time"] = time_overrides[post["slug"]]

    # ── Step 3: Dry-run output ──
    print(f"{'Platformă':<16} {'Slug':<45} {'Tip':<14} {'Media':<8} {'Scheduled'}")
    print("─" * 110)
    for post in posts:
        media_count = 1  # cover
        if post["media_files"]:
            media_count += len(post["media_files"])
        sched = post.get("scheduled_time", "TBD")
        if isinstance(sched, str) and len(sched) > 19:
            sched = sched[:19]
        print(
            f"{post['platform']:<16} {post['slug'][:44]:<45} {post['post_type']:<14} {media_count:<8} {sched}"
        )
    print(f"\nTotal: {len(posts)} posts\n")

    if args.dry_run:
        # Output JSON summary for dry-run
        summary = {
            "mode": "dry-run",
            "total_posts": len(posts),
            "posts": [
                {
                    "platform": p["platform"],
                    "slug": p["slug"],
                    "post_type": p["post_type"],
                    "scheduled_time": p.get("scheduled_time"),
                    "cover_image": p["cover_image"],
                    "media_files": p["media_files"],
                    "video_file": p["video_file"],
                    "audio_file": p["audio_file"],
                }
                for p in posts
            ],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    # ── Step 4: Authenticate & upload ──
    print("Authenticating with Google Drive...")
    service = authenticate(creds_path)

    print("Fetching existing folders...")
    existing = get_existing_folders(service, folder_id)
    counter = get_next_counter(existing)
    print(f"Next counter: {counter:05d}\n")

    uploaded = []
    skipped = []
    failed = []

    for i, post in enumerate(posts, 1):
        slug = post["slug"]
        platform = post["platform"]
        prefix = f"[{i}/{len(posts)}]"

        # Check duplicate
        dup = check_duplicate(post, existing)
        if dup:
            print(f"{prefix} SKIP (exists): {dup['name']}")
            skipped.append({"slug": slug, "platform": platform, "reason": "duplicate"})
            continue

        # Build folder name
        folder_name = f"{counter:05d}-{slug}-{platform}"
        print(f"{prefix} Uploading: {folder_name}")

        try:
            # Create folder
            drive_folder_id = create_drive_folder(service, folder_name, folder_id)

            # Upload config.json
            config = build_config_json(post, auto_post=args.auto_post)
            upload_config_json(service, config, drive_folder_id)

            # Upload media files
            media_dir = post["media_dir"]

            # Upload cover
            if post["cover_image"] and os.path.exists(
                os.path.join(media_dir, post["cover_image"])
            ):
                upload_file(
                    service,
                    os.path.join(media_dir, post["cover_image"]),
                    drive_folder_id,
                )

            # Upload additional media (carousel slides)
            for mf in post["media_files"]:
                fpath = os.path.join(media_dir, mf)
                if os.path.exists(fpath):
                    upload_file(service, fpath, drive_folder_id)

            # Upload video
            if post["video_file"]:
                vpath = os.path.join(media_dir, post["video_file"])
                if os.path.exists(vpath):
                    upload_file(service, vpath, drive_folder_id)

            # Upload audio
            if post["audio_file"]:
                apath = os.path.join(media_dir, post["audio_file"])
                if os.path.exists(apath):
                    upload_file(service, apath, drive_folder_id)

            print(f"  SUCCESS: {folder_name}")
            uploaded.append(
                {
                    "slug": slug,
                    "platform": platform,
                    "folder_name": folder_name,
                    "drive_folder_id": drive_folder_id,
                }
            )
            counter += 1

        except Exception as e:
            print(f"  FAILED: {e}")
            failed.append({"slug": slug, "platform": platform, "error": str(e)})

    # ── Step 5: Webhook ──
    webhook_status = None
    if webhook_url and uploaded:
        print(f"\nSending webhook to n8n...")
        webhook_status = send_webhook(webhook_url, folder_id)
        print(f"Webhook: {'OK' if webhook_status else 'FAILED'}")

    # ── Step 6: Summary ──
    print(f"\n{'═' * 50}")
    print(f"  Upload complet!")
    print(f"{'═' * 50}")
    print(f"  Uploaded: {len(uploaded)}/{len(posts)}")
    print(f"  Skipped:  {len(skipped)}/{len(posts)}")
    print(f"  Failed:   {len(failed)}/{len(posts)}")
    if webhook_url:
        print(f"  Webhook:  {'OK' if webhook_status else 'FAILED' if webhook_status is not None else 'N/A'}")
    print(f"{'═' * 50}\n")

    # Output JSON summary
    result = {
        "uploaded": uploaded,
        "skipped": skipped,
        "failed": failed,
        "webhook_status": webhook_status,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
