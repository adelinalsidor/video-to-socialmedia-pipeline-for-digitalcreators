#!/usr/bin/env python3
"""
Rulează filtrul ffmpeg `blurdetect` pe fiecare cadru candidat dintr-un folder
și alege pe cel mai clar (scor `lavfi.blur` cel mai mic — valoarea crește
odată cu blur-ul detectat). Pasul 2 din cele 4 ale frame-image-generator.

Usage:
    python3 pick_sharpest.py --candidates-dir tmp/candidates
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BLUR_RE = re.compile(r"lavfi\.blur=([\d.]+)")


def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        print("ERROR: ffmpeg nu e instalat sau nu e în PATH.", file=sys.stderr)
        sys.exit(1)


def blur_score(image_path: Path) -> float:
    cmd = [
        "ffmpeg", "-i", str(image_path),
        "-vf", "blurdetect,metadata=print:file=-",
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    match = BLUR_RE.search(result.stdout + result.stderr)
    if not match:
        print(f"ERROR: nu am găsit scor blur pentru {image_path.name}:\n{result.stderr[-500:]}", file=sys.stderr)
        sys.exit(1)
    return float(match.group(1))


def pick_sharpest(candidates_dir: Path) -> Path:
    candidates = sorted(candidates_dir.glob("candidate_*.png"))
    if not candidates:
        print(f"ERROR: niciun candidat în {candidates_dir}", file=sys.stderr)
        sys.exit(1)

    scored = [(blur_score(c), c) for c in candidates]
    for score, path in scored:
        print(f"{path.name}: blur={score:.4f}")

    best_score, best_path = min(scored, key=lambda pair: pair[0])
    print(f"\nCel mai clar: {best_path.name} (blur={best_score:.4f})")
    return best_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates-dir", required=True)
    args = parser.parse_args()

    check_ffmpeg()

    candidates_dir = Path(args.candidates_dir)
    if not candidates_dir.exists():
        print(f"ERROR: nu există {candidates_dir}", file=sys.stderr)
        sys.exit(1)

    best_path = pick_sharpest(candidates_dir)
    print(f"\nBEST_FRAME={best_path.resolve()}")


if __name__ == "__main__":
    main()
