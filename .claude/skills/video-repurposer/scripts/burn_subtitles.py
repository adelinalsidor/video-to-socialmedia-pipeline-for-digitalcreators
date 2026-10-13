#!/usr/bin/env python3
"""
Generează un .ass din felia relevantă a video-sursa/{slug}/transcript.json
(offset recalculat la 0:00 al clipului) și arde subtitrările peste clip cu
filtrul ffmpeg `subtitles=`. Pasul 3 (ultimul) din cele 3 ale video-repurposer.

Stil standard, lizibil: font sans-serif bold, alb cu contur negru, aliniat
jos-centru — decis pentru toate clipurile (nu brand kit specific).

Folosim .ass (nu .srt) cu un header propriu (PlayResX/PlayResY = dimensiunea
reală a clipului) pentru că filtrul `subtitles=` al ffmpeg randează un .srt
la o rezoluție de script implicită mică (384x288, moștenită din SSA/ASS) —
un FontSize „normal" ar ieși de câteva ori mai mare decât ar trebui. Un .ass
cu PlayRes explicit elimină ambiguitatea.

Usage:
    python3 burn_subtitles.py --slug 2026-08-06 --start 12.5 --end 32.0 --in clip-916.mp4 --out clip-final.mp4
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

MAX_WORDS_PER_LINE = 4

# Trebuie să corespundă cu TARGET_W/TARGET_H din crop_resize.py — burn_subtitles.py
# rulează mereu pe clipul deja recadrat la 9:16, deci rezoluția e fixă.
PLAY_RES_X = 1080
PLAY_RES_Y = 1920

FONT_NAME = "Arial"
FONT_SIZE = 78          # ~4% din înălțime — lizibil fără să acopere cadrul
MARGIN_V = 130           # distanță de la marginea de jos


def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        print("ERROR: ffmpeg nu e instalat sau nu e în PATH.", file=sys.stderr)
        sys.exit(1)


def ass_timestamp(seconds: float) -> str:
    """Format ASS: H:MM:SS.cc (centizecimi, nu milisecunde)."""
    if seconds < 0:
        seconds = 0
    cs = round(seconds * 100)
    h, cs = divmod(cs, 360_000)
    m, cs = divmod(cs, 6_000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def group_words(words: list, clip_start: float, clip_end: float):
    """Filtrează cuvintele din interval, decalează la 0:00, grupează în linii scurte."""
    in_range = [
        w for w in words
        if w.get("type") == "word"
        and w.get("start") is not None
        and w["start"] >= clip_start
        and w["end"] <= clip_end
    ]

    lines = []
    current = []
    for w in in_range:
        current.append(w)
        text = w.get("text", "")
        ends_sentence = text.strip().endswith((".", "!", "?", ","))
        if len(current) >= MAX_WORDS_PER_LINE or ends_sentence:
            lines.append(current)
            current = []
    if current:
        lines.append(current)

    return lines


def build_ass(lines: list, clip_start: float) -> str:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {PLAY_RES_X}
PlayResY: {PLAY_RES_Y}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{FONT_NAME},{FONT_SIZE},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,3,0,2,60,60,{MARGIN_V},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for line_words in lines:
        start = line_words[0]["start"] - clip_start
        end = line_words[-1]["end"] - clip_start
        text = " ".join(w["text"].strip() for w in line_words)
        events.append(
            f"Dialogue: 0,{ass_timestamp(start)},{ass_timestamp(end)},Default,,0,0,0,,{text}"
        )
    return header + "\n".join(events) + "\n"


def escape_for_filter(path: Path) -> str:
    """Escapează calea pentru filtrul ffmpeg subtitles= (probleme cu ':' pe Windows)."""
    p = str(path.resolve()).replace("\\", "/")
    p = p.replace(":", r"\:")
    return p


def burn_subtitles(slug: str, video_sursa_dir: Path, start: float, end: float,
                    in_path: Path, out_path: Path):
    transcript_path = video_sursa_dir / slug / "transcript.json"
    if not transcript_path.exists():
        print(f"ERROR: nu există {transcript_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(transcript_path.read_text(encoding="utf-8"))
    words = data.get("words", [])

    lines = group_words(words, start, end)
    if not lines:
        print("ERROR: niciun cuvânt găsit în intervalul dat — verifică start/end.", file=sys.stderr)
        sys.exit(1)

    ass_content = build_ass(lines, start)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ass", delete=False, encoding="utf-8") as f:
        f.write(ass_content)
        ass_path = Path(f.name)

    try:
        escaped_ass = escape_for_filter(ass_path)
        vf = f"subtitles='{escaped_ass}'"

        out_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-i", str(in_path),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-c:a", "copy",
            str(out_path),
        ]

        print(f"Ard {len(lines)} linii de subtitrare peste {in_path.name}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR: ffmpeg a eșuat:\n{result.stderr[-2000:]}", file=sys.stderr)
            sys.exit(1)
    finally:
        ass_path.unlink(missing_ok=True)

    print(f"Gata: {out_path}")
    print(f"\nCLIP_PATH={out_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--start", type=float, required=True, help="secunde, în timpul video-ului sursă")
    parser.add_argument("--end", type=float, required=True, help="secunde, în timpul video-ului sursă")
    parser.add_argument("--in", dest="in_path", required=True, help="clipul deja tăiat + recadrat")
    parser.add_argument("--out", dest="out_path", required=True)
    parser.add_argument("--video-sursa-dir", default="video-sursa")
    args = parser.parse_args()

    check_ffmpeg()

    in_path = Path(args.in_path)
    if not in_path.exists():
        print(f"ERROR: nu există {in_path}", file=sys.stderr)
        sys.exit(1)

    burn_subtitles(
        args.slug,
        Path(args.video_sursa_dir).resolve(),
        args.start,
        args.end,
        in_path,
        Path(args.out_path),
    )


if __name__ == "__main__":
    main()
