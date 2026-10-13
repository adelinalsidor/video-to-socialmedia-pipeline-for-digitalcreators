---
name: frame-image-generator
description: >
  Extrage cadre REALE din video-sursa/{slug}/video.mp4 (nu generare AI) pentru
  caruselul Instagram și pin-ul Pinterest, pe baza citatelor-ancoră scrise de
  video-repurposer și content-repurposer, arde textul de slide/overlay peste
  cadru cu ffmpeg, și marchează postările image_status: ready. Triggere:
  generează imagini carusel, generează imagini pin Pinterest,
  frame-image-generator, imagini din footage, cadre din video.
---

# Frame Image Generator

Clientul e o persoană reală (makeup artist) — imaginile pentru carusel Instagram și pin Pinterest folosesc cadre reale din footage-ul clientului (`video-sursa/{slug}/video.mp4`), nu generare AI. Rulează **după** `video-repurposer` (carusel) și `content-repurposer` (pin Pinterest), care deja au scris un citat-ancoră verbatim per slide/pin.

**Fără gate de confirmare către utilizator** (nu `AskUserQuestion`) — dar asta NU înseamnă zero verificare. `blurdetect` (Pas 3) prinde doar claritatea optică generală a cadrului; NU detectează ochi închiși/clipit și poate rata blur localizat (o mână în mișcare rapidă lângă o față altfel clară scade media mai puțin decât ai crede). Din experiență directă: pe un caz real, cadrul „cel mai clar" ales automat avea ochii pe jumătate închiși ȘI o mână puternic blurată — a trecut nedetectat de `blurdetect`. **Verifică CE anume acoperă chenarul de text, nu doar CÂT de mare e.** Un chenar de 2 rânduri poate fi tehnic "mic" și tot să strice slide-ul dacă acoperă exact detaliul pe care textul îl descrie — ex. un slide cu textul "apply concealer in these areas" cu chenarul poziționat "bottom" a acoperit exact un patch de concealer de pe bărbie, ascunzând una din "aceste zone" despre care vorbea textul. Înainte de a alege `--position`, uită-te la ZONELE relevante ale cadrului (produs în mână, patch-uri de concealer, deget care arată ceva) și pune textul unde NU e nimic relevant — de obicei pe păr/frunte (`top`) dacă acțiunea e în partea de jos a feței, sau `bottom` dacă acțiunea e sus. Scurtează textul la 1-2 rânduri ori de câte ori poți (sub ~45 caractere wrapează de obicei la 2 rânduri) — un chenar de 4 rânduri aproape mereu acoperă ceva important, indiferent unde-l pui.

**Preferă gura închisă, ochii deschiși** — clientul vorbește continuu în video (tutorial narat), deci majoritatea cadrelor o prind mid-cuvânt, cu gura deschisă; arată neîngrijit ca imagine statică de carusel/pin, chiar dacă e sharp și bine încadrat. Caută în candidații deja extrași (sunt eșantionați des, ~3-4/secundă) un cadru unde gura e închisă (pauză naturală între cuvinte/propoziții) și ochii sunt deschiși — ca și cum ar poza, nu ca și cum ar fi surprinsă mid-frază. Nu întotdeauna există un candidat perfect în fereastra citatului — dacă niciunul din candidații extrași n-are gura închisă, ia cel mai aproape de asta (gură relaxată, nu larg deschisă) în loc să insiști pe un cadru mid-cuvânt.

**Înainte să salvezi cadrul final, uită-te efectiv la el** (Read pe imaginea rezultată din `overlay_text.py`, sau pe cadrul brut înainte de crop) — dacă ochii sunt închiși, mișcarea a prins blur vizibil, sau cadrul du-a tăiat-o greșit (vezi nota despre centrare din Pas 3 al `crop_resize_image.py`), alege alt candidat din același folder (`candidate_02.png`, `candidate_03.png`, ...) sau extrage un contact sheet la rezoluție mică (`ffmpeg -i candidate_%02d.png -vf "scale=280:-1,tile=NxM" contact.png`) ca să compari mai mulți deodată. Controlul de calitate manual de duminică e pentru client (aprobă/nu conținutul), nu un substitut pentru verificarea tehnică de bază a cadrului.

---

## Pas 0 — Verificări

1. Cere `{slug}` dacă nu a fost dat (sau folosește cel mai recent folder din `video-sursa/`).
2. Verifică existența `video-sursa/{slug}/video.mp4` și `transcript.json`.
3. Verifică `ffmpeg -version` / `ffprobe -version` — dacă lipsesc, oprește-te cu mesaj clar (nu încerca instalare automată).
4. Verifică fontul implicit `C:\Windows\Fonts\arialbd.ttf` există — dacă nu, oprește-te și cere alt `--fontfile` (Windows-only, per mediul acestui proiect).

## Pas 1 — Scanează postările eligibile

Caută în `postari/{slug}/`:
- `03-instagram/carousel-{slug}.md` — dacă `image_status: pending`
- `05-pinterest/pin.md` — dacă `image_status: pending`

Dacă niciuna nu are `image_status: pending`, oprește-te și raportează (nimic de făcut).

## Pas 2 — Extrage citatele-ancoră

- **Carusel:** din `## Note Editoriale` → `### Slides`, extrage per slide textul „Citat sursă pentru cadru: '...'" (8-10 citate, unul per slide).
- **Pin Pinterest:** din frontmatter, câmpul `frame_source_quote`.

Dacă un citat lipsește sau pare parafrazat (nu apare identic în `transcript.md`), semnalează-l dar continuă cu restul — se rezolvă la Pas 3 (fallback).

**Coerență temporală text-imagine — verifică înainte să extragi:** textul unui slide (mai ales primele slide-uri, care adesea sunt o parafrază/hook scrisă de `video-repurposer`, nu un citat direct) trebuie să corespundă ca MOMENT din video cu citatul-ancoră folosit pentru cadru — nu doar tematic, ci și temporal. Exemplu real de greșeală: un slide cu textul „the more concealer you use, the worse it looks" (parafrază după o propoziție spusă la ~1:09 în video) a fost ancorat inițial la citatul de deschidere al video-ului (~0:03) — tematic înrudit (ambele despre „diferență"/rezultat), dar dintr-un moment complet diferit, deci cadrul nu avea nicio legătură reală cu ce ilustra textul. Dacă citatul-ancoră scris de `video-repurposer`/`content-repurposer` pare desprins de momentul unde ideea slide-ului chiar apare în transcript, caută în `transcript.md` fraza reală care a generat acel text și folosește timestamp-ul EI, nu al unui citat doar tematic apropiat.

**Caută întâi un freeze/pauză de 2-3s lângă citat** — de la 2026-08-08, clientul a fost rugată să facă o pauză de 2-3 secunde în care „pozează" esența fiecărui pas (gest static, gură închisă, privire spre cameră) exact ca să existe cadre clare de extras. Dacă `extract_candidates.py` găsește un grup de cadre aproape identice (subiect static) în fereastra citatului, acela e freeze-ul — folosește-l direct, sări peste căutarea largă/manuală descrisă mai jos (necesară doar pentru footage vechi, fără freeze-uri, ex. 2026-08-06).

## Pas 3 — Per citat: găsește timestamp, extrage, alege, recadrează, suprapune text

Pentru fiecare citat (8-10 pentru carusel + 1 pentru pin), rulează secvențial cele 4 scripturi, cu fișiere temporare într-un folder temp (șters la final):

```bash
python scripts/find_segment_time.py --slug {slug} --phrase "citatul exact"
# → START=... END=...

python scripts/extract_candidates.py --video video-sursa/{slug}/video.mp4 \
  --start {START} --end {END} --out-dir {tmp}/candidates --pad 0.5 --fps 4

python scripts/pick_sharpest.py --candidates-dir {tmp}/candidates
# → BEST_FRAME=...

python scripts/crop_resize_image.py --in {BEST_FRAME} --out {tmp}/cropped.png \
  --width {W} --height {H}

python scripts/overlay_text.py --in {tmp}/cropped.png --out {final_path} \
  --text "{textul slide-ului / overlay-ul pin-ului}" --position {top|center|bottom}
```

**Dimensiuni țintă (`--width`/`--height`) per `strategy/repurposing-matrix.md`:**

| Piesă | Raport | Dimensiuni |
|---|---|---|
| Carusel Instagram (fiecare slide) | 4:5 | 1080×1350 |
| Pinterest | 2:3 | 1000×1500 |

**Dacă `find_segment_time.py` nu găsește citatul exact** (fraza a fost parafrazată în `.md`, nu verbatim): folosește cuvintele apropiate sugerate de script pentru a ajusta citatul și încearcă din nou. Dacă tot nu găsește, sare peste acel slide/pin, marchează-l în raportul final, nu opri tot fluxul.

`{final_path}` e direct calea finală din structura de foldere (Pas 4) — nu mai muta fișierul după.

## Pas 4 — Structura de foldere

```
postari/{slug}/
├── 03-instagram/carousel-{slug}/01.png ... 09-10.png    (câte slide-uri are caruselul)
└── 05-pinterest/pin-{slug}.png
```

## Pas 5 — Update frontmatter

Pentru fiecare `.md` procesat complet (toate citatele găsite):
- `image_status: pending` → `ready`
- adaugă `image_path:` — pentru carusel, indică doar primul slide (`01.png`); pentru pin, `pin-{slug}.png`.

Dacă unul sau mai multe slide-uri au fost sărite (citat negăsit), lasă `image_status: pending` și notează în raport care slide-uri lipsesc — nu marca `ready` parțial.

## Pas 6 — Validare cu ffprobe

Pentru fiecare imagine generată:

```bash
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of default=noprint_wrappers=1 {imagine.png}
```

Confirmă dimensiunile exacte din tabelul de la Pas 3. Afișează un tabel sumar; flag orice imagine în afara țintelor.

## Pas 7 — Raport final

```
Imagini generate: {N}/{total}
Sărite (citat negăsit): {listă, dacă există}
postari/{slug}/03-instagram/carousel-{slug}/: {status}
postari/{slug}/05-pinterest/pin-{slug}.png: {status}
```

---

## Scripturi

| Script | Rol |
|---|---|
| `scripts/find_segment_time.py` | Caută citatul în `transcript.json`, întoarce `START`/`END` (identic cu versiunea din `video-repurposer`, copiat pentru autonomie) |
| `scripts/extract_candidates.py` | Extrage ~6-8 cadre PNG candidate dintr-o fereastră de ~2s în jurul citatului |
| `scripts/pick_sharpest.py` | Rulează filtrul ffmpeg `blurdetect` pe fiecare candidat, alege cel mai clar (scor minim) |
| `scripts/crop_resize_image.py` | Crop + scale la raportul cerut de platformă — centrat automat pe client (detecție de textură pe coloană, nu crop central fix pe cadru; vezi nota din `video-repurposer/SKILL.md`), cu fallback la crop central clasic dacă detecția eșuează |
| `scripts/overlay_text.py` | Arde text static peste imagine cu `drawtext` (font sans-serif bold, alb/contur negru) — **notă tehnică:** acest build de ffmpeg NU interpretează `\n` ca linie nouă în `drawtext`; scriptul unește liniile cu un caracter real de linie nouă (`\n` Python, nu secvență escape în filtru) |

## De ce nu OpenCV / Pillow

Fără dependințe Python noi — totul rulează cu ffmpeg (`blurdetect`, `drawtext`), la fel ca `video-repurposer`. Consecvent cu restul pipeline-ului: un singur tool extern de întreținut.
