---
name: video-repurposer
description: >
  Taie video-sursa/{slug}/video.mp4 (footage brut al clientului) în clipuri
  scurte pentru Instagram Reels, TikTok și YouTube Shorts (taie segmentul,
  recadrează la 9:16, arde subtitrări, local cu ffmpeg), plus scrie textul
  caruselului Instagram din transcript. Triggere: taie video, generează
  Reels, generează clipuri TikTok, YouTube Shorts, video-repurposer,
  repurpose video, tăiere clipuri din footage, carusel Instagram din video.
---

# Video Repurposer

Transformă video-ul săptămânal al clientului (`video-sursa/{slug}/video.mp4` + `transcript.md` + `transcript.json`) în 15 clipuri scurte (5 momente × Instagram Reel + TikTok + YouTube Shorts) plus 1 carusel Instagram text-only, respectând `strategy/repurposing-matrix.md` și schema de foldere din `CLAUDE.md`.

**Regulă de aur:** toate cele 15 clipuri + caruselul transmit ACELAȘI mesaj core al video-ului (Coherence Rule) — ambalajul diferă per platformă, substanța nu. Tot textul generat e în ENGLEZĂ.

**Fără gate de confirmare:** selecția momentelor și tăierea sunt automate — nu opri fluxul cu `AskUserQuestion` pentru a confirma segmentele alese (controlul de calitate se face la review-ul manual de duminică seara).

---

## Pas 0 — Verificări

1. Cere `{slug}` dacă nu a fost dat (sau folosește cel mai recent folder din `video-sursa/`).
2. Verifică existența `video-sursa/{slug}/video.mp4`, `transcript.md`, `transcript.json`, `meta.json`. Dacă `transcript.md`/`transcript.json` lipsesc, oprește-te — rulează `video-intake` întâi.
3. Verifică `ffmpeg -version` și `ffprobe -version` — dacă lipsesc, oprește-te cu mesaj clar (nu încerca instalare automată).

## Pas 1 — Mesajul core

Citește `video-sursa/{slug}/transcript.md` integral (proză curată, fără marcaje de timp — e mic, ~5-10KB, se citește direct). Extrage mesajul core al video-ului în 1-2 propoziții (Coherence Rule din `strategy/repurposing-matrix.md`).

## Pas 2 — Alege 5 momente puternice

**Verifică întâi dacă `transcript.md` conține marcaje explicite de tip „Step 1", „Step 2" etc.** — de la 2026-08-08, clientul a fost rugată să filmeze după un scenariu clar (hook → pași numerotați cu voce tare → concluzie), tocmai ca segmentarea să fie mai fiabilă. Dacă aceste marcaje există, folosește-le direct ca puncte de start/final pentru momente — mult mai sigur decât inferarea din conținut (cazul video-urilor vechi, ex. 2026-08-06, care nu aveau structura asta). Dacă nu există marcaje explicite, continuă cu inferarea manuală de mai jos.

Din `transcript.md`, alege 5 momente distincte, fiecare cu potențial de hook (o afirmație surprinzătoare, o greșeală comună, un „before/after", un sfat concret). Pentru fiecare moment, notează:
- un **citat exact de 3-6 cuvinte** care marchează începutul (hook-ul) — va fi folosit pentru lookup de timp
- un **topic-slug** descriptiv de 2-4 cuvinte (ex. `color-correcting-tip`), NU generic

**Ordine cronologică + arc narativ:** alege cele 5 momente astfel încât, în ordinea lor din video (aceeași ordine cu timestamp-urile crescătoare), să formeze un arc problemă → soluție → concluzie: momentul 1 stabilește problema/mitul greșit, momentele 2-4 sunt tehnicile/soluțiile concrete, momentul 5 e concluzia/rezultatul final. Numerele 1-5 din numele fișierelor (Pas 6) reflectă exact această ordine — nu ordinea în care le-ai identificat citind transcript-ul, ci ordinea lor reală în video.

**Nu parsa niciodată `transcript.json` direct** (~300KB, per-cuvânt) — e mult prea mare pentru context. Pentru fiecare citat, rulează:

```bash
python scripts/find_segment_time.py --slug {slug} --phrase "citatul exact"
```

Scriptul face fuzzy-match (case/punctuație-insensitive) și returnează `START=...`/`END=...` în secunde. Dacă nu găsește fraza exact, sugerează cuvinte apropiate — ajustează citatul și încearcă din nou.

`START` = hook-ul comun al celor 3 variante ale momentului respectiv (Reel/TikTok/Shorts folosesc ACELAȘI punct de plecare — doar durata diferă).

## Pas 3 — Alege durata (end-ul) per platformă

**Regulă de aur, mai importantă decât tabelul de mai jos: fiecare clip e o idee dusă până la capăt, nu o fereastră de N secunde.** Un clip care se oprește în mijlocul unei propoziții (ex. "...instead of putting foundation all over the face." — și atât, fără să spună ce faci în loc) e un clip stricat, chiar dacă durata lui pică perfect în fereastra recomandată. Nu tăia niciodată la un timp fix doar ca să nimerești un interval de durată — găsește întâi finalul natural al propoziției/ideii (verifică în `transcript.md` ce urmează după punctul unde ai vrea să tai), și abia apoi verifică unde pică durata rezultată.

Ca reper orientativ (nu literă de lege):

| Platformă | Fereastră durată orientativă | Notă |
|---|---|---|
| Instagram Reel | 15-20s (reach) SAU 45-60s (saves) | **singura regulă dură: evită 30-40s** — "dead zone" de retenție |
| TikTok | 15-34s | |
| YouTube Shorts | 15-34s | matricea nu dă interval separat dincolo de "hook <3s"; tratăm identic cu TikTok |

Procedură practică:
1. Din `transcript.md`, găsește unde ideea se încheie natural (punct, nu virgulă de pauză) după `start`-ul hook-ului.
2. Verifică cu `find_segment_time.py` timpul acelei fraze complete (nu al unei fraze intermediare care doar "sună a final" — citește propoziția întreagă până la punct).
3. Dacă durata rezultată nimerește o fereastră din tabel, perfect. Dacă e puțin mai lungă (ex. 23s pentru un Reel în loc de 15-20s), las-o așa — o idee completă la 23s bate o idee ruptă la 19s.
4. Dacă durata rezultată pică exact în 30-40s pentru Reel (singura interdicție reală), și există un punct de propoziție anterior care tot completează ideea (chiar dacă mai scurt), folosește-l pe acela; dacă nu există, acceptă cele 30-40s — o idee completă e mai importantă decât dead zone-ul, care e doar o eurizare de retenție, nu o interdicție absolută.
5. **Reel poate (și de obicei ar trebui) să aibă un `end` diferit de TikTok/Shorts pentru ACELAȘI moment** — asta e diferențierea reală de platformă la nivel de video, nu doar text. Reel se oprește la finalul primei propoziții complete (scurt, direct — se potrivește ferestrei 15-20s de reach); TikTok/Shorts continuă până la finalul unei propoziții următoare, mai lungi, care adaugă context/detaliu real (exemplu concret, pasul următor al tehnicii) — nu doar padding ca să umpli timp. Fiecare variantă, individual, tot trebuie să se oprească la un final natural de idee, nu la jumătatea uneia.

**Atenție, capcană verificată din experiență:** dacă la Pas 3 ajustezi un `end` pentru că tăia ideea la jumătate, verifică separat DACĂ acea corecție chiar trebuie aplicată identic pe toate cele 3 platforme, sau dacă Reel avea deja un punct de oprire mai scurt care era el însuși complet (doar mai concis). Unificarea automată a `end`-ului pe toate 3 platforme "ca să fie mai simplu" produce clipuri Reel/TikTok/Shorts vizual IDENTICE (aceeași durată, același crop, aceleași subtitrări) — pierzi diferențierea de platformă complet, chiar dacă hashtag-urile/caption-urile din `.md` diferă. Text diferit peste video identic nu e optimizare per-platformă, doar metadata diferită.

## Pas 4 — Taie, recadrează, subtitrează (×15)

Pentru fiecare din cele 15 combinații (5 momente × 3 platforme), rulează cele 3 scripturi ffmpeg în secvență, cu fișiere temporare intermediare într-un folder temp (șterse la final):

```bash
python scripts/cut_segment.py --slug {slug} --start {start} --end {end} --out {tmp}/1-cut.mp4
python scripts/crop_resize.py --in {tmp}/1-cut.mp4 --out {tmp}/2-crop.mp4
python scripts/burn_subtitles.py --slug {slug} --start {start} --end {end} --in {tmp}/2-crop.mp4 --out {final_path}
```

`{final_path}` e direct calea finală din structura de foldere (Pas 6) — nu mai muta fișierul după.

Fiecare script printează `CLIP_PATH=...` pe ultima linie — folosește-l ca să confirmi calea, nu presupune.

**Centrare automată pe client (`crop_resize.py`):** clientul nu stă fix în cadru pe tot parcursul video-ului sursă (se apleacă, gesticulează) — un crop central fix pe mijlocul cadrului 16:9 o taie la unele momente (verificat vizual: la unele segmente ajungea aproape în afara cadrului pe o parte, cu mult perete gol pe cealaltă). `crop_resize.py` detectează automat unde e clientul — eșantionează câteva cadre din banda față/umeri a clipului și găsește cel mai lat bloc contiguu de coloane cu textură ridicată (păr/sprâncene/bijuterii au variație verticală de culoare mult mai mare decât peretele din fundal, chiar dacă peretele are gradient de lumină, nu e perfect uniform). Nu necesită nicio acțiune manuală — rulează automat la fiecare apel al scriptului. Dacă detecția eșuează (clip fără destul contrast), scriptul cade automat pe crop central clasic și afișează un mesaj — nu se oprește din eroare.

## Pas 5 — Hashtag-uri

Citește `strategy/hashtags/instagram.json`, `strategy/hashtags/tiktok-reels.json`, `strategy/hashtags/youtube-shorts.json` (format `{"general": [...], "niche": [...]}` — `general` = lista fixă a clientului, identică pe toate platformele; `niche` = specific de platformă + idei per conținut). Combină 2-3 din `general` + 1-2 din `niche`.

**Atenție, nu confunda cu `strategy/hashtags/youtube.json`** — acela e fișierul lui `content-repurposer`, cu tag-uri simple fără `#` pentru câmpul „tags" din spate al YouTube long-form (concept diferit). `video-repurposer` folosește DOAR `youtube-shorts.json` (hashtag-uri cu `#`, pentru descrierea clipurilor Shorts).

**Libertate de topic:** dacă subiectul momentului cere un hashtag specific care nu există în `niche` (ex. un produs/tehnică menționată explicit în clip, gen `#CreamBlush` sau `#BakingMethod`), poți adăuga 1-2 hashtag-uri noi, relevante strict conținutului — nu trebuie să vină doar din fișierele JSON. Total tot 3-5 hashtag-uri per clip (general + niche + eventual topic-specific, nu adăuga peste 5).

**Excepție YouTube Shorts:** per `strategy/repurposing-matrix.md`, hashtag-ul `#Shorts` e obligatoriu (regulă de platformă YouTube, nu vine din lista clientului) — adaugă-l mereu, în plus față de cele 3-5 de mai sus.

## Pas 6 — Scrie fișierele `.md`

Structura de foldere (per `CLAUDE.md`, NU cea din documentul vechi `strategie-adaptare-video-social.md`):

**Numerotare obligatorie:** fiecare nume de fișier are prefix `{N}-` (1-5), unde `N` e poziția momentului în ordinea cronologică din video (Pas 2) — `1-{topic-slug}.md`/`.mp4`, nu doar `{topic-slug}.md`. Asta face vizibilă instant, în orice file explorer sau pe Drive, ordinea narativă (1 = problemă, 2-4 = soluții, 5 = concluzie) fără să deschizi fiecare fișier ca să afli unde se încadrează.

```
postari/{slug}/
├── 02-youtube/shorts/{N}-{topic-slug}.md + .mp4        (×5, N=1-5)
├── 03-instagram/{N}-{topic-slug}-reel.md + .mp4         (×5, N=1-5)
├── 03-instagram/carousel-{slug}.md                  (×1, Pas 7, fără video)
└── 04-tiktok/{N}-{topic-slug}.md + .mp4                 (×5, N=1-5)
```

Frontmatter exact + convenția `## Note Editoriale` (obligatorie — `upload-drive` extrage caption-ul din textul dintre frontmatter și acest heading): vezi **`references/frontmatter-schema.md`**.

Câmpuri cheie de reținut: `video_path` relativ la folderul `.md`-ului, `video_status: ready`, `video_source_segment: "MM:SS-MM:SS"`, `cta` conform tabelului din matrice (Reel: "Save this"/"Link in bio"; TikTok: "Follow for more"; Shorts: "Watch the full video").

## Pas 7 — Caruselul Instagram (text-only)

Din transcript-ul integral (nu dintr-un singur moment), scrie caruselul: 8-10 slide-uri, tehnica „open loop" (întrebare pe slide 1, răspuns pe slide 5-6+), caption 80-150 cuvinte, CTA „Save this for later". Frontmatter + structură slide-uri: vezi secțiunea Carusel din `references/frontmatter-schema.md`. Pentru fiecare slide, alege un **citat exact de 3-6 cuvinte, verbatim din `transcript.md`**, aproape de ideea slide-ului — e ancora pe care `frame-image-generator` o va căuta ca să extragă un cadru real din video pentru acel slide. **`image_status: pending`** (nu `ready` — cadrele reale le extrage `frame-image-generator` ulterior, pe baza citatelor-ancoră).

**Atenție, coerență temporală — nu doar tematică:** textul unui slide e adesea o parafrază/hook (mai ales slide 1, care rezumă mesajul core), nu un citat direct. Citatul-ancoră trebuie ales din locul din transcript unde ACEA idee chiar e spusă, nu dintr-un citat doar înrudit tematic aflat în altă parte a video-ului (ex. deschiderea video-ului sună generic potrivită pentru orice slide de hook, dar poate fi la minute distanță de unde ideea slide-ului chiar apare). Exemplu real de greșeală: slide 1 avea textul „the more concealer you use, the worse it looks" — parafrază după o propoziție spusă la ~1:09 — dar citatul-ancoră folosit inițial era din deschiderea video-ului (~0:03), tematic înrudit dar dintr-un moment complet diferit. Cadrul extras arăta bine izolat, dar nu ilustra de fapt ce spunea textul de deasupra lui. Verifică: unde din transcript a apărut de fapt ideea pe care ai parafrazat-o pe slide? Ancorează acolo.

Salvează în `postari/{slug}/03-instagram/carousel-{slug}.md`.

## Pas 8 — Validare cu ffprobe

Pentru fiecare din cele 15 clipuri:

```bash
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration -of default=noprint_wrappers=1 {clip.mp4}
```

Confirmă rezoluție 1080x1920 și durata în fereastra platformei (±10%). Afișează un tabel sumar la final; flag orice clip în afara țintelor.

## Pas 9 — Self-review scurt

Verifică pe toate cele 16 piese (15 clipuri + carusel):
1. **Mesaj core consistent** — toate transmit aceeași substanță din Pas 1?
2. **Zero text românesc** — tot conținutul generat (hook, caption, cta, hashtags, slide text) e în engleză?
3. **Hashtag-uri din fișierele existente** — nu inventate, din `strategy/hashtags/*.json` + relevanță de nișă?
4. **`## Note Editoriale` prezent** în toate cele 16 fișiere?

Raportează un sumar scurt: câte piese generate, câte clipuri validate cu ffprobe, orice problemă corectată automat.
