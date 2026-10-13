#!/usr/bin/env python3
"""
Arde text static peste o imagine (slide de carusel sau pin Pinterest) cu
filtrul ffmpeg `drawtext` — echivalentul static al burn_subtitles.py din
video-repurposer (acolo textul e cronometrat per cuvânt; aici e un singur
bloc de text fix). Pasul 4 (ultimul) din cele 4 ale frame-image-generator.

Font sans-serif bold, alb cu contur negru, cu o bandă semi-transparentă în
spate pentru lizibilitate pe orice fundal — respectă cerința explicită a
Pinterest ("NU cursiv/handwritten", OCR-ul pierde discoverability).

Usage:
    python3 overlay_text.py --in cover.png --out cover.png --text "Fix Redness Without Caking" --position bottom
"""

import argparse
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Fallback hardcodat — la fel ca FONT_NAME="Arial" din burn_subtitles.py, dar
# drawtext (spre deosebire de libass) cere un path explicit către fișierul de
# font pe build-urile ffmpeg pentru Windows.
DEFAULT_FONTFILE = r"C:\Windows\Fonts\arialbd.ttf"

MAX_CHARS_PER_LINE = 22
FONT_SIZE_RATIO = 0.055  # din înălțimea imaginii


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
        print(f"ERROR: ffprobe a eșuat:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    width, height = result.stdout.strip().split(",")
    return int(width), int(height)


def escape_drawtext(text: str) -> str:
    """Escapează caractere speciale pentru filtrul drawtext (: ' \\ %).

    Apostroful e un caz special: `\\'` în interiorul unui `text='...'` NU
    se randează corect pe acest build de ffmpeg — apostroful (și uneori tot
    ce urmează) dispare din text în loc să apară literal. Soluție robustă,
    fără escapare: înlocuim apostroful drept cu apostroful tipografic (’),
    care nu are niciun sens special pentru parser-ul de filtre ffmpeg.
    """
    text = text.replace("\\", "\\\\")
    text = text.replace(":", r"\:")
    text = text.replace("'", "’")
    text = text.replace("%", r"\%")
    return text


def build_filter(text: str, width: int, height: int, position: str, fontfile: str) -> str:
    wrapped_lines = textwrap.wrap(text, width=MAX_CHARS_PER_LINE) or [text]
    escaped_lines = [escape_drawtext(line) for line in wrapped_lines]
    # drawtext nu interpretează secvența escape "\n" ca linie nouă — vrea un
    # caracter real de linie nouă (0x0A) direct în valoarea text=.
    combined = "\n".join(escaped_lines)

    font_size = max(24, round(height * FONT_SIZE_RATIO))
    fontfile_escaped = fontfile.replace("\\", "/").replace(":", r"\:")

    y_expr = {
        "top": "h*0.08",
        "center": "(h-text_h)/2",
        "bottom": "h*0.85-text_h",
    }.get(position, "h*0.85-text_h")

    return (
        f"drawtext=fontfile='{fontfile_escaped}':text='{combined}':"
        f"fontsize={font_size}:fontcolor=white:"
        f"borderw=4:bordercolor=black:"
        f"box=1:boxcolor=black@0.35:boxborderw=20:"
        f"x=(w-text_w)/2:y={y_expr}:line_spacing=10"
    )


def overlay_text(in_path: Path, out_path: Path, text: str, position: str, fontfile: str):
    width, height = get_dimensions(in_path)
    vf = build_filter(text, width, height, position, fontfile)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(in_path),
        "-vf", vf,
        "-frames:v", "1",
        str(out_path),
    ]

    print(f"Ard text peste {in_path.name}: \"{text}\"")
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
    parser.add_argument("--text", required=True)
    parser.add_argument("--position", choices=["top", "center", "bottom"], default="bottom")
    parser.add_argument("--fontfile", default=DEFAULT_FONTFILE)
    args = parser.parse_args()

    check_ffmpeg()

    in_path = Path(args.in_path)
    if not in_path.exists():
        print(f"ERROR: nu există {in_path}", file=sys.stderr)
        sys.exit(1)

    if not Path(args.fontfile).exists():
        print(f"ERROR: fontul {args.fontfile} nu există — dă alt --fontfile.", file=sys.stderr)
        sys.exit(1)

    overlay_text(in_path, Path(args.out_path), args.text, args.position, args.fontfile)


if __name__ == "__main__":
    main()
