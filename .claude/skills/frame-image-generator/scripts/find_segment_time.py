#!/usr/bin/env python3
"""
Caută o frază (citat exact de 3-6 cuvinte) în video-sursa/{slug}/transcript.json
și returnează timpul de start/end în secunde, ca să nu fie nevoie să încarci
cei ~300KB de JSON direct în context.

Identic cu scripts/find_segment_time.py din video-repurposer — copiat aici ca
skill-ul frame-image-generator să rămână autonom (nu depinde de path-uri din
alt folder de skill).

Usage:
    python3 find_segment_time.py --slug 2026-08-06 --phrase "the difference is enormous"
    python3 find_segment_time.py --slug 2026-08-06 --phrase "let's see how" --video-sursa-dir video-sursa
"""

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def normalize(text: str) -> str:
    """Lowercase, fără punctuație — pentru comparație tolerantă la formatare."""
    return re.sub(r"[^\w\s]", "", text.lower()).strip()


def find_phrase(words: list, phrase: str):
    """Caută secvența de tokeni ai frazei printre cuvintele de tip 'word'.

    Returnează (start, end, matched_text) al primei potriviri, sau None.
    """
    tokens = normalize(phrase).split()
    if not tokens:
        return None

    word_entries = [w for w in words if w.get("type") == "word" and w.get("text", "").strip()]
    normalized = [normalize(w["text"]) for w in word_entries]

    n = len(tokens)
    for i in range(len(normalized) - n + 1):
        if normalized[i:i + n] == tokens:
            start = word_entries[i]["start"]
            end = word_entries[i + n - 1]["end"]
            matched = " ".join(word_entries[i:i + n][j]["text"] for j in range(n))
            return start, end, matched

    return None


def suggest_closest(words: list, phrase: str, top_n: int = 3):
    """Dacă nu găsește potrivire exactă, sugerează cele mai apropiate fraze (primul cuvânt al frazei)."""
    import difflib

    word_entries = [w for w in words if w.get("type") == "word" and w.get("text", "").strip()]
    all_text = [normalize(w["text"]) for w in word_entries]
    first_token = normalize(phrase).split()[0] if normalize(phrase).split() else ""
    close = difflib.get_close_matches(first_token, all_text, n=top_n, cutoff=0.6)
    return close


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--phrase", required=True, help="Citat exact (3-6 cuvinte) din transcript.md")
    parser.add_argument("--video-sursa-dir", default="video-sursa")
    args = parser.parse_args()

    transcript_path = Path(args.video_sursa_dir).resolve() / args.slug / "transcript.json"
    if not transcript_path.exists():
        print(f"ERROR: nu există {transcript_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(transcript_path.read_text(encoding="utf-8"))
    words = data.get("words", [])

    result = find_phrase(words, args.phrase)
    if result is None:
        suggestions = suggest_closest(words, args.phrase)
        print(f"ERROR: fraza '{args.phrase}' nu a fost găsită exact în transcript.", file=sys.stderr)
        if suggestions:
            print(f"Cuvinte apropiate găsite: {suggestions}", file=sys.stderr)
        sys.exit(1)

    start, end, matched = result
    print(f"Găsit: \"{matched}\" @ {start:.2f}s - {end:.2f}s")
    print(f"\nSTART={start:.2f}")
    print(f"END={end:.2f}")


if __name__ == "__main__":
    main()
