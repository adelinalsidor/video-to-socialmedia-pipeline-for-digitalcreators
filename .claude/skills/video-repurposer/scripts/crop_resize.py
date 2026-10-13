#!/usr/bin/env python3
"""
Recadrează/redimensionează un clip la 9:16 (1080x1920) — formatul vertical
cerut de Reels/TikTok/Shorts. Pasul 2 din cele 3 ale video-repurposer.

Dacă sursa e mai lată decât 9:16 (cazul obișnuit, footage landscape/16:9),
face crop pe orizontală. Dacă e mai îngustă (deja mai verticală decât 9:16),
face crop central pe verticală. Apoi scalează la 1080x1920.

Poziționare orizontală: Clientul nu stă fixă în cadru pe tot parcursul
video-ului (se apleacă, gesticulează) — un crop central fix pe mijlocul
cadrului 16:9 o taie la unele momente. Detectăm unde e clientul eșantionând
câteva cadre din bandă față/umeri și măsurând TEXTURA (varianța verticală
de culoare) pe coloană, nu culoarea brută — peretele din fundal are un
gradient de lumină (nu e uniform gri), deci o simplă distanță de culoare
față de un eșantion din colț confundă zone umbrite ale peretelui cu
"subiect". Textura (păr, sprâncene, bijuterii, haine) are variație
verticală mult mai mare decât peretele, chiar și cu gradient. Alegem cel
mai lat bloc CONTIGUU de coloane cu textură ridicată — corpul clientului, nu o
mână ridicată izolată lângă margine. Fără dependințe Python noi — doar
ffmpeg (rawvideo) + stdlib.

Usage:
    python3 crop_resize.py --in clip.mp4 --out clip-916.mp4
"""

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

TARGET_W = 1080
TARGET_H = 1920

# Fereastra de rânduri (fracție din înălțime) folosită pentru detecția
# poziției orizontale — banda față/umeri, evită partea de sus a părului
# (uneori tunsă de cadru) și gesturile mâinilor (mai jos, spre piept).
FACE_BAND_TOP = 0.12
FACE_BAND_BOTTOM = 0.55

# Câte "rânduri" verticale eșantionăm în bandă pentru scorul de textură —
# suficient să prindă tranziții față/păr/bijuterii, fără să coste mult.
GRID_ROWS = 8

# Prag de varianță (sumă pe R/G/B a varianței populaționale pe coloană)
# peste care o coloană e considerată "clientul", nu perete.
TEXTURE_THRESHOLD = 100

SAMPLE_FRACTIONS = (0.15, 0.35, 0.5, 0.65, 0.85)


def check_tools():
    missing = [t for t in ("ffmpeg", "ffprobe") if shutil.which(t) is None]
    if missing:
        print(f"ERROR: lipsesc din PATH: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


def get_dimensions(video_path: Path):
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: ffprobe a eșuat:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    info = json.loads(result.stdout)
    stream = info["streams"][0]
    return stream["width"], stream["height"]


def get_duration(video_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        str(video_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return 0.0
    info = json.loads(result.stdout)
    try:
        return float(info["format"]["duration"])
    except (KeyError, ValueError, TypeError):
        return 0.0


def sample_texture_profile(video_path: Path, t: float, width: int, band_y0: int, band_h: int):
    """Extrage un grid width x GRID_ROWS al benzii față/umeri la momentul t
    (scris într-un fișier temporar, nu pipe:1 — pipe-ul de rawvideo către
    stdout se poate bloca/eșua sub Windows) și întoarce scorul de textură
    (varianță verticală de culoare) per coloană."""
    with tempfile.NamedTemporaryFile(suffix=".raw", delete=False) as f:
        raw_path = Path(f.name)

    try:
        cmd = [
            "ffmpeg", "-v", "error", "-y",
            "-i", str(video_path),
            "-ss", f"{t:.2f}",
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
    """Centrul celui mai lat bloc contiguu de True din is_fg, sau None."""
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


def estimate_subject_center_x(video_path: Path, width: int, height: int):
    """Estimează centrul orizontal al clientului (nu al cadrului) pe durata
    clipului, eșantionând câteva cadre. Întoarce None dacă detecția eșuează
    (fallback la centrare clasică pe mijlocul cadrului)."""
    duration = get_duration(video_path)
    if duration <= 0:
        return None

    band_y0 = int(height * FACE_BAND_TOP)
    band_y1 = int(height * FACE_BAND_BOTTOM)
    band_h = band_y1 - band_y0
    if band_h <= 0:
        return None

    centers = []
    for frac in SAMPLE_FRACTIONS:
        t = duration * frac
        scores = sample_texture_profile(video_path, t, width, band_y0, band_h)
        if not scores:
            continue

        is_fg = [s > TEXTURE_THRESHOLD for s in scores]
        center = largest_run_center(is_fg)
        if center is not None:
            centers.append(center)

    if not centers:
        return None

    return statistics.median(centers)


def crop_resize(in_path: Path, out_path: Path):
    width, height = get_dimensions(in_path)
    print(f"Sursă: {width}x{height}")

    crop_w = min(width, round(height * 9 / 16))
    crop_h = min(height, round(width * 16 / 9))

    x_offset = (width - crop_w) // 2
    y_offset = (height - crop_h) // 2

    if crop_w < width:
        # Crop orizontal (cazul obișnuit, sursă 16:9) — încearcă să centreze pe client
        center_x = estimate_subject_center_x(in_path, width, height)
        if center_x is not None:
            candidate = round(center_x - crop_w / 2)
            x_offset = max(0, min(width - crop_w, candidate))
            print(f"Subiect detectat la x≈{center_x:.0f} din {width} — crop offset x={x_offset}")
        else:
            print("Detecție poziție eșuată — folosesc crop central clasic.")

    vf = (
        f"crop={crop_w}:{crop_h}:{x_offset}:{y_offset},"
        f"scale={TARGET_W}:{TARGET_H},setsar=1"
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(in_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-c:a", "copy",
        str(out_path),
    ]

    print(f"Recadrez la {TARGET_W}x{TARGET_H} (9:16)...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: ffmpeg a eșuat:\n{result.stderr[-2000:]}", file=sys.stderr)
        sys.exit(1)

    print(f"Gata: {out_path}")
    print(f"\nCLIP_PATH={out_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="in_path", required=True)
    parser.add_argument("--out", dest="out_path", required=True)
    args = parser.parse_args()

    check_tools()

    in_path = Path(args.in_path)
    if not in_path.exists():
        print(f"ERROR: nu există {in_path}", file=sys.stderr)
        sys.exit(1)

    crop_resize(in_path, Path(args.out_path))


if __name__ == "__main__":
    main()
