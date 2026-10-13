#!/usr/bin/env python3
"""
Taie un segment din video-sursa/{slug}/video.mp4, între --start și --end
(secunde), și îl salvează la --out. Pasul 1 din cele 3 ale video-repurposer
(cut -> crop -> subtitrări).

Usage:
    python3 cut_segment.py --slug 2026-08-06 --start 12.5 --end 32.0 --out clip.mp4
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        print("ERROR: ffmpeg nu e instalat sau nu e în PATH.", file=sys.stderr)
        sys.exit(1)


def cut_segment(video_path: Path, start: float, end: float, out_path: Path):
    if end <= start:
        print(f"ERROR: end ({end}) trebuie să fie mai mare decât start ({start}).", file=sys.stderr)
        sys.exit(1)

    duration = end - start
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", str(video_path),
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        str(out_path),
    ]

    print(f"Tai segmentul {start:.2f}s - {end:.2f}s ({duration:.2f}s) din {video_path.name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: ffmpeg a eșuat:\n{result.stderr[-2000:]}", file=sys.stderr)
        sys.exit(1)

    print(f"Gata: {out_path}")
    print(f"\nCLIP_PATH={out_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--start", type=float, required=True, help="secunde")
    parser.add_argument("--end", type=float, required=True, help="secunde")
    parser.add_argument("--out", required=True, help="cale fișier .mp4 de output")
    parser.add_argument("--video-sursa-dir", default="video-sursa")
    args = parser.parse_args()

    check_ffmpeg()

    video_path = Path(args.video_sursa_dir).resolve() / args.slug / "video.mp4"
    if not video_path.exists():
        print(f"ERROR: nu există {video_path}", file=sys.stderr)
        sys.exit(1)

    cut_segment(video_path, args.start, args.end, Path(args.out))


if __name__ == "__main__":
    main()
