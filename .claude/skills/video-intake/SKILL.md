---
name: video-intake
description: >
  Ia cel mai vechi video neprocesat dintr-un folder Drive de intake
  (sincronizat local), îl mută în video-sursa/{slug}/video.mp4 și îl
  transcrie cu ElevenLabs Speech-to-Text (timestamp-uri per cuvânt),
  primul pas al pipeline-ului săptămânal de content pentru client.
  Triggere: "video nou de la client", "transcrie video", "procesează
  coada de video-uri", "video-intake", "ia următorul video din intake".
---

# Video Intake

## Scop

Primul pas al pipeline-ului: ia DOAR cel mai vechi video neprocesat din coada de intake (FIFO), îl mută în `video-sursa/{slug}/video.mp4`, și îl transcrie cu ElevenLabs Speech-to-Text. Restul video-urilor din coadă rămân neatinse pentru săptămânile viitoare.

Cine îl rulează: Adelina, manual, o dată pe săptămână, când primește notificare că clientul a urcat un video nou.

Limba dialogului (întrebări, mesaje) — română. Conținutul transcris rămâne exact ce a spus clientul, în engleză.

## Workflow

### Pas 1 — Folderul de intake

Verifică dacă `DRIVE_INTAKE_LOCAL_PATH` există în `.env` (caută fișierul urcând prin directoare, ca restul skill-urilor din proiect).

Dacă lipsește, folosește `AskUserQuestion`:
- "Care e calea locală către folderul Drive de intake (unde clientul urcă video-urile noi)?"

După ce primești răspunsul, oferă-te să-l salvezi în `.env` ca `DRIVE_INTAKE_LOCAL_PATH` (adaugă, fără să suprascrii variabilele existente), ca la rulările viitoare să nu mai fie nevoie să întrebi.

### Pas 2-4 — Scanează coada și mută cel mai vechi video

Rulează:
```bash
python3 .claude/skills/video-intake/scripts/scan_queue.py --intake-dir <cale> --video-sursa-dir video-sursa
```

Scriptul face totul automat:
- listează video-urile din intake (`.mp4 .mov .mkv .avi .m4v`), sortate FIFO (cel mai vechi primul)
- dacă folderul e gol, afișează "Coadă goală" — în acest caz, spune-i clar Adelinei „nimic nou" și oprește-te aici, nu continua la pașii următori
- altfel, mută cel mai vechi video în `video-sursa/{slug}/video.mp4` (slug = data video-ului, `YYYY-MM-DD`, cu `-2`/`-3`... dacă slug-ul există deja) și scrie `meta.json`
- afișează pe stdout linia `SLUG=<slug>` și câte video-uri au mai rămas în coadă

Extrage `<slug>` din output pentru pasul următor.

### Pas 5-6 — Transcrie cu ElevenLabs

Rulează:
```bash
python3 .claude/skills/video-intake/scripts/transcribe.py --slug <slug> --video-sursa-dir video-sursa
```

Scriptul citește `ELEVENLABS_API_KEY` din `.env`, trimite video-ul la ElevenLabs Speech-to-Text (`model_id=scribe_v2`, `language_code=en`, timestamp-uri per cuvânt), și scrie:
- `video-sursa/{slug}/transcript.json` — răspunsul brut, cu timestamp-uri per cuvânt
- `video-sursa/{slug}/transcript.md` — text curat, citibil (paragrafe noi la pauze mari între cuvinte, fără JSON)
- actualizează `duration_seconds` în `meta.json` cu durata reală a video-ului

**Atenție:** apelul ăsta costă bani reali pe contul ElevenLabs și poate dura câteva minute pentru un video lung — dacă rulezi pe un video de test, confirmă cu utilizatorul înainte.

Dacă scriptul eșuează, afișează eroarea exactă din output (mesaj `ERROR:` cu body-ul răspunsului API) — nu presupune succes și nu reîncerca manual peste retry-ul deja făcut de script.

### Pas 7 — Rezumat final

Afișează:
- slug-ul
- calea video-ului (`video-sursa/{slug}/video.mp4`)
- calea transcriptului (`video-sursa/{slug}/transcript.md`)
- câte video-uri au mai rămas în coadă (din output-ul Pas 2-4)
- sugerează pasul următor: skill-ul `substack-article-writer`, pentru articolul de Substack

## Dependențe

```bash
pip install requests python-dotenv
```
