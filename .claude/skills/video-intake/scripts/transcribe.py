#!/usr/bin/env python3
"""
Transcrie video-sursa/{slug}/video.mp4 cu ElevenLabs Speech-to-Text
(timestamp-uri per cuvânt), și scrie transcript.json (răspunsul brut)
+ transcript.md (text curat, cu paragrafe noi la pauze mari).

Usage:
    python3 transcribe.py --slug 2026-08-06 --video-sursa-dir video-sursa
    python3 transcribe.py --slug 2026-08-06 --video-sursa-dir video-sursa --paragraph-gap-s 1.5
"""

import argparse
import json
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

API_URL = "https://api.elevenlabs.io/v1/speech-to-text"
MODEL_ID = "scribe_v2"
LANGUAGE_CODE = "en"
REQUEST_TIMEOUT = 1800  # 30 min — video-uri lungi pot dura la procesare
MAX_RETRIES = 1
DEFAULT_PARAGRAPH_GAP_S = 1.5


def find_env_file(start_dir: str) -> Path:
    """Caută .env: start_dir, apoi urcă prin directoare (max 10 niveluri)."""
    env_path = Path(start_dir) / ".env"
    if env_path.exists():
        return env_path

    current = Path(start_dir).resolve()
    for _ in range(10):
        candidate = current / ".env"
        if candidate.exists():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent

    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        return cwd_env

    return Path(".env")


def call_elevenlabs_stt(api_key: str, video_path: Path) -> dict:
    """Trimite video-ul la ElevenLabs STT, returnează JSON-ul de răspuns."""
    headers = {"xi-api-key": api_key}
    data = {
        "model_id": MODEL_ID,
        "language_code": LANGUAGE_CODE,
        "timestamps_granularity": "word",
    }

    with open(video_path, "rb") as f:
        files = {"file": (video_path.name, f, "application/octet-stream")}
        resp = requests.post(
            API_URL, headers=headers, data=data, files=files, timeout=REQUEST_TIMEOUT
        )

    if resp.status_code != 200:
        raise RuntimeError(f"ElevenLabs API error {resp.status_code}: {resp.text}")

    return resp.json()


def build_transcript_md(words: list, paragraph_gap_s: float) -> str:
    """Reconstruiește text citibil din array-ul `words`, cu paragrafe noi la pauze mari."""
    parts = []
    prev_end = None

    for w in words:
        w_type = w.get("type")
        text = w.get("text", "")

        if w_type == "spacing":
            start = w.get("start")
            if prev_end is not None and start is not None and (start - prev_end) > paragraph_gap_s:
                parts.append("\n\n")
            else:
                parts.append(text or " ")
        else:  # "word" sau "audio_event"
            parts.append(text)

        end = w.get("end")
        if end is not None:
            prev_end = end

    md = "".join(parts)
    # curăță spații multiple rămase și linii goale în exces
    lines = [line.strip() for line in md.split("\n\n")]
    return "\n\n".join(line for line in lines if line)


def transcribe(slug: str, video_sursa_dir: Path, paragraph_gap_s: float):
    slug_dir = video_sursa_dir / slug
    video_path = slug_dir / "video.mp4"

    if not video_path.exists():
        print(f"ERROR: video-ul nu există: {video_path}", file=sys.stderr)
        sys.exit(1)

    env_path = find_env_file(str(slug_dir))
    load_dotenv(env_path)
    api_key = os.getenv("ELEVENLABS_API_KEY")

    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY nu a fost găsit în .env", file=sys.stderr)
        sys.exit(1)

    last_error = None
    result = None
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            print(f"Trimit {video_path.name} la ElevenLabs STT (încercarea {attempt})...")
            result = call_elevenlabs_stt(api_key, video_path)
            break
        except requests.exceptions.RequestException as e:
            last_error = e
            if attempt <= MAX_RETRIES:
                print(f"Eroare de rețea la încercarea {attempt}: {e}. Reîncerc...", file=sys.stderr)
                time.sleep(5)
            else:
                print(f"ERROR: eșec după {attempt} încercări: {last_error}", file=sys.stderr)
                sys.exit(1)
        except RuntimeError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

    transcript_json_path = slug_dir / "transcript.json"
    transcript_json_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    words = result.get("words", [])
    transcript_md = build_transcript_md(words, paragraph_gap_s)
    transcript_md_path = slug_dir / "transcript.md"
    transcript_md_path.write_text(transcript_md, encoding="utf-8")

    # actualizează meta.json cu durata reală (end-ul ultimului cuvânt)
    meta_path = slug_dir / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        word_ends = [w.get("end") for w in words if w.get("end") is not None]
        meta["duration_seconds"] = max(word_ends) if word_ends else None
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Gata: {transcript_json_path}")
    print(f"Gata: {transcript_md_path}")
    print(f"\nTRANSCRIPT_MD={transcript_md_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--video-sursa-dir", default="video-sursa")
    parser.add_argument("--paragraph-gap-s", type=float, default=DEFAULT_PARAGRAPH_GAP_S)
    args = parser.parse_args()

    transcribe(args.slug, Path(args.video_sursa_dir).resolve(), args.paragraph_gap_s)


if __name__ == "__main__":
    main()
