#!/usr/bin/env python3
"""
Recadrează/redimensionează o imagine statică (cadru extras din video) la
raportul de aspect cerut de platformă. Pasul 3 din cele 4 ale
frame-image-generator.

Poziționare orizontală: Clientul nu stă fixă în cadru pe tot parcursul
video-ului (se apleacă, gesticulează) — un crop central fix pe mijlocul
cadrului 16:9 o poate tăia la unele momente. Detectăm unde e clientul pe acest
cadru specific măsurând TEXTURA (varianță verticală de culoare) pe coloană
în banda față/umeri — peretele din fundal are un gradient de lumină (nu e
uniform gri), deci o simplă distanță de culoare ar confunda zone umbrite
ale peretelui cu "subiect". Alegem cel mai lat bloc CONTIGUU de coloane cu
textură ridicată (păr/sprâncene/bijuterii), nu o mână ridicată izolată
lângă margine. Aceeași tehnică ca `crop_resize.py` din `video-repurposer`,
adaptată la un singur cadru (nu la eșantioane pe durata unui clip). Fără
dependințe Python noi — doar ffmpeg (rawvideo) + stdlib.

Rapoarte folosite în acest proiect:
    Carusel Instagram: --width 1080 --height 1350   (4:5)
    Pinterest:          --width 1000 --height 1500   (2:3)

Usage:
    python3 crop_resize_image.py --in frame.png --out cover.png --width 1080 --height 1350
"""

import argparse
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

FACE_BAND_TOP = 0.12
FACE_BAND_BOTTOM = 0.55
GRID_ROWS = 8
TEXTURE_THRESHOLD = 100


def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        print("ERROR: ffmpeg nu e instalat sau nu e în PATH.", file=sys.stderr)
        sys.exit(1)


def get_dimensions(image_path: Path):
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0",
        str(image_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    try:
        w, h = result.stdout.strip().split(",")
        return int(w), int(h)
    except ValueError:
        return None


def sample_texture_profile(image_path: Path, width: int, band_y0: int, band_h: int):
    with tempfile.NamedTemporaryFile(suffix=".raw", delete=False) as f:
        raw_path = Path(f.name)

    try:
        cmd = [
            "ffmpeg", "-v", "error", "-y",
            "-i", str(image_path),
            "-frames:v", "1",
            "-vf", f"crop={width}:{band_h}:0:{band_y0},scale={width}:{GRID_ROWS}:flags=area",
            "-f", "rawvideo", "-pix_fmt", "rgb24",
            str(raw_path),
        ]
        result = subprocess.run(cmd, capture_output=True)
        expected = width * GRID_ROWS * 3
        data = raw_path.read_bytes() if raw_path.exists() else b""
        if result.returncode != 0 or len(data) != expected:
            return None
    finally:
        raw_path.unlink(missing_ok=True)

    scores = []
    for x in range(width):
        total = 0.0
        for k in range(3):
            vals = [data[(r * width + x) * 3 + k] for r in range(GRID_ROWS)]
            total += statistics.pvariance(vals)
        scores.append(total)
    return scores


def largest_run_center(is_fg: list):
    best = None
    start = None
    for i, v in enumerate(is_fg + [False]):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if best is None or (i - start) > (best[1] - best[0]):
                best = (start, i)
            start = None
    if best is None:
        return None
    return (best[0] + best[1] - 1) / 2


def estimate_subject_center_x(image_path: Path, width: int, height: int):
    band_y0 = int(height * FACE_BAND_TOP)
    band_y1 = int(height * FACE_BAND_BOTTOM)
    band_h = band_y1 - band_y0
    if band_h <= 0:
        return None

    scores = sample_texture_profile(image_path, width, band_y0, band_h)
    if not scores:
        return None

    is_fg = [s > TEXTURE_THRESHOLD for s in scores]
    return largest_run_center(is_fg)


def crop_resize_image(in_path: Path, out_path: Path, width: int, height: int):
    src_dims = get_dimensions(in_path)

    x_offset = None
    if src_dims:
        src_w, src_h = src_dims
        crop_w = min(src_w, round(src_h * width / height))
        crop_h = min(src_h, round(src_w * height / width))
        if crop_w < src_w:
            center_x = estimate_subject_center_x(in_path, src_w, src_h)
            if center_x is not None:
                candidate = round(center_x - crop_w / 2)
                x_offset = max(0, min(src_w - crop_w, candidate))
                print(f"Subiect detectat la x≈{center_x:.0f} din {src_w} — crop offset x={x_offset}")
            else:
                print("Detecție poziție eșuată — folosesc crop central clasic.")
        crop_filter = f"crop={crop_w}:{crop_h}:{x_offset if x_offset is not None else (src_w - crop_w) // 2}:{(src_h - crop_h) // 2}"
    else:
        # fallback dacă ffprobe eșuează pe imagine: formula centrată clasică, calculată de ffmpeg
        crop_filter = f"crop=min(iw\\,ih*{width}/{height}):min(ih\\,iw*{height}/{width})"

    vf = f"{crop_filter},scale={width}:{height},setsar=1"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(in_path),
        "-vf", vf,
        "-frames:v", "1",
        str(out_path),
    ]

    print(f"Recadrez la {width}x{height}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: ffmpeg a eșuat:\n{result.stderr[-2000:]}", file=sys.stderr)
        sys.exit(1)

    print(f"Gata: {out_path}")
    print(f"\nIMAGE_PATH={out_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="in_path", required=True)
    parser.add_argument("--out", dest="out_path", required=True)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    args = parser.parse_args()

    check_ffmpeg()

    in_path = Path(args.in_path)
    if not in_path.exists():
        print(f"ERROR: nu există {in_path}", file=sys.stderr)
        sys.exit(1)

    crop_resize_image(in_path, Path(args.out_path), args.width, args.height)


if __name__ == "__main__":
    main()
