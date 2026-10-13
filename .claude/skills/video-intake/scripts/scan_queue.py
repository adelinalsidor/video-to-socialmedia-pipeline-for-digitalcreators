#!/usr/bin/env python3
"""
Scanează folderul de intake (Drive comun, descărcat local) și procesează
DOAR cel mai vechi video neprocesat (FIFO). Restul rămân în coadă.

Un video e "neprocesat" atâta timp cât stă în intake/ — odată mutat în
video-sursa/{slug}/, iese din coadă. Nu există alt tracking separat.

Usage:
    python3 scan_queue.py --intake-dir ./intake --video-sursa-dir ./video-sursa
    python3 scan_queue.py --dry-run
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".m4v"}


def find_queue(intake_dir: Path):
    """Video-urile din intake, sortate FIFO (cel mai vechi primul, după mtime)."""
    videos = [
        p for p in intake_dir.iterdir()
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS
    ]
    return sorted(videos, key=lambda p: p.stat().st_mtime)


def make_slug(date: datetime, video_sursa_dir: Path) -> str:
    """Slug = data video-ului (YYYY-MM-DD); dacă exista deja, adaugă -2, -3, ..."""
    base = date.strftime("%Y-%m-%d")
    slug = base
    n = 2
    while (video_sursa_dir / slug).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intake-dir", default="intake")
    parser.add_argument("--video-sursa-dir", default="video-sursa")
    parser.add_argument("--dry-run", action="store_true", help="Arată ce s-ar întâmpla, fără să mute nimic")
    args = parser.parse_args()

    intake_dir = Path(args.intake_dir).resolve()
    video_sursa_dir = Path(args.video_sursa_dir).resolve()

    if not intake_dir.exists():
        print(f"Folderul de intake nu există: {intake_dir}", file=sys.stderr)
        sys.exit(1)

    queue = find_queue(intake_dir)

    if not queue:
        print("Coadă goală — niciun video nou de procesat în intake/.")
        sys.exit(0)

    print(f"Video-uri în coadă ({len(queue)}), ordine FIFO:")
    for v in queue:
        mtime = datetime.fromtimestamp(v.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"  - {v.name} (încărcat: {mtime})")

    oldest = queue[0]
    mtime_dt = datetime.fromtimestamp(oldest.stat().st_mtime, tz=timezone.utc)
    slug = make_slug(mtime_dt, video_sursa_dir)

    print(f"\nProcesăm cel mai vechi: {oldest.name} -> video-sursa/{slug}/video.mp4")

    if args.dry_run:
        print("(--dry-run: nu am mutat nimic)")
        sys.exit(0)

    dest_dir = video_sursa_dir / slug
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_video = dest_dir / "video.mp4"

    shutil.move(str(oldest), str(dest_video))

    meta = {
        "slug": slug,
        "original_filename": oldest.name,
        "intake_mtime": mtime_dt.isoformat(),
        "moved_at": datetime.now(timezone.utc).isoformat(),
        "video_size_bytes": dest_video.stat().st_size,
        "duration_seconds": None,
    }
    (dest_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    print(f"Gata: {dest_video}")
    print(f"meta.json scris în {dest_dir / 'meta.json'}")
    print(f"\nSLUG={slug}")
    if len(queue) > 1:
        print(f"({len(queue) - 1} video(uri) rămase în coadă pentru săptămânile viitoare)")


if __name__ == "__main__":
    main()
