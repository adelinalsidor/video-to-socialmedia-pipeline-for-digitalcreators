#!/usr/bin/env python3
"""
Extrage cadre PNG candidate dintr-o fereastră scurtă de timp din video.mp4,
în jurul intervalului [start, end] al citatului-ancoră (rezultat din
find_segment_time.py). Pasul 1 din cele 4 ale frame-image-generator.

Fereastra e [start - pad, end + pad], eșantionată la `fps` cadre/secundă —
mai mulți candidați decât o singură captură, ca pick_sharpest.py să aibă din
ce alege (evită cadre cu clipit/mișcare neclară exact pe punctul de start).

Usage:
    python3 extract_candidates.py --video video-sursa/2026-08-06/video.mp4 \
        --start 12.5 --end 14.0 --out-dir tmp/candidates --pad 0.5 --fps 4
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


def extract_candidates(video_path: Path, start: float, end: float, out_dir: Path,
                        pad: float, fps: float):
    window_start = max(0.0, start - pad)
    duration = (end - start) + 2 * pad
    if duration <= 0:
        duration = pad * 2 or 1.0

    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = str(out_dir / "candidate_%02d.png")

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{window_start:.3f}",
        "-i", str(video_path),
        "-t", f"{duration:.3f}",
        "-vf", f"fps={fps}",
        "-frames:v", "20",
        pattern,
    ]

    print(f"Extrag candidați din fereastra {window_start:.2f}s - {window_start + duration:.2f}s...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: ffmpeg a eșuat:\n{result.stderr[-2000:]}", file=sys.stderr)
        sys.exit(1)

    candidates = sorted(out_dir.glob("candidate_*.png"))
    if not candidates:
        print("ERROR: niciun cadru extras — verifică start/end/pad.", file=sys.stderr)
        sys.exit(1)

    print(f"Gata: {len(candidates)} candidați în {out_dir}")
    print(f"\nCANDIDATES_DIR={out_dir}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True)
    parser.add_argument("--start", type=float, required=True, help="secunde, START din find_segment_time.py")
    parser.add_argument("--end", type=float, required=True, help="secunde, END din find_segment_time.py")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--pad", type=float, default=0.5, help="secunde adăugate înainte/după interval")
    parser.add_argument("--fps", type=float, default=4.0, help="cadre candidate pe secundă")
    args = parser.parse_args()

    check_ffmpeg()

    video_path = Path(args.video)
    if not video_path.exists():
        print(f"ERROR: nu există {video_path}", file=sys.stderr)
        sys.exit(1)

    extract_candidates(
        video_path, args.start, args.end, Path(args.out_dir), args.pad, args.fps,
    )


if __name__ == "__main__":
    main()
