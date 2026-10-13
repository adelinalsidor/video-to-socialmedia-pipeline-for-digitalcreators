---
name: content-repurposer
description: >
  Generează metadata YouTube long-form (titlu, descriere, chapters, tags,
  thumbnail) și textul pin-ului Pinterest, direct din video-sursa/{slug}/transcript.md
  (+ transcript.json pentru timestamp-uri), respectând întocmai
  strategy/repurposing-matrix.md. Triggere: repurposează video, generează
  metadata YouTube, generează pin Pinterest, content-repurposer, chapters
  YouTube, titlu descriere video.
---

# Content Repurposer

Generează, dintr-un video săptămânal deja transcris, **2 piese de content**: metadata pentru video-ul YouTube long-form (titlu, descriere, chapters, tags, sugestie thumbnail) și textul pentru pin-ul static de Pinterest.

Nu generează script, nu taie video — video-ul brut ESTE conținutul de YouTube (vezi `CLAUDE.md` din rădăcina proiectului). Clipurile scurte (Reels/TikTok/Shorts) și articolul de Substack sunt scrise de alte skill-uri (`video-repurposer`, `substack-article-writer`).

---

## Workflow

Urmează **toți** pașii, în ordine. Nu sări pași.

---

### Pas 1: Identificare video sursă

Dacă utilizatorul a specificat slug-ul (ex: `2026-08-06`):
- Validează că `video-sursa/{slug}/transcript.md` și `video-sursa/{slug}/transcript.json` există
- Dacă lipsesc, oprește-te și explică: transcrierea trebuie făcută întâi de `video-intake`

Dacă NU a specificat:
- Scanează `video-sursa/*/` (foldere cu `transcript.md` prezent)
- Listează slug-urile disponibile cu `AskUserQuestion`

După identificare, citește complet `transcript.md`.

---

### Pas 2: Citire obligatorie a repurposing-matrix.md

**Înainte de orice generare**, citește `strategy/repurposing-matrix.md`:
- Secțiunea **2 — YouTube Long-form**
- Secțiunea **7 — Pinterest**

Structura „Structură livrabil" din fiecare secțiune e șablonul literal de urmat — nu doar inspirație. Reține exact câmpurile cerute (vezi Pas 4 și Pas 5 mai jos, care le reproduc).

---

### Pas 3: Extragere mesaj core

Extrage din transcript **mesajul core** — esența în 1-2 propoziții (Coherence Rule din matrice). Acest mesaj se transmite identic în ambele piese generate (YouTube + Pinterest).

Nu cere confirmare — afișează mesajul core ca informare și treci direct mai departe (viteză, la fel ca `video-repurposer`; verificarea reală se face la aprobarea clientului, nu ca pas intermediar).

---

### Pas 4: Generare metadata YouTube

Citește `references/youtube.md` pentru exemple și reguli anti-slop specifice.

Generează:

1. **Titlu** — ≤70 caractere, keyword principal (makeup/beauty) în primele 40 de caractere. Specific, nu „clever".
2. **Descriere** — 200-300 cuvinte, keyword principal în primele 2 propoziții, restul context (ce învață privitorul, produse/tehnici menționate).
3. **Chapters** — împarte transcript-ul în 4-6 secțiuni logice (pe temă/tehnică discutată de client). Pentru fiecare secțiune:
   - Alege propoziția/fraza de start
   - Caută acel text (cuvânt cu cuvânt) în `transcript.json` → `words[]` pentru a găsi timpul real (`start`, în secunde)
   - Formatează `MM:SS`
4. **Tags (5-8):**
   - Citește `strategy/hashtags/youtube.json` dacă există (tags de nișă stabile) — dacă lipsește, creează-l cu tags de bază: `makeup`, `makeup tutorial`, `beauty over 40`, `makeup artist tips`, `everyday makeup`
   - Adaugă 2-3 tags specifice extrase din transcript-ul curent (produse/tehnici menționate de client)
5. **Sugestie text thumbnail** — scurt, contrast puternic, promite beneficiul concret.

Salvează `postari/{slug}/02-youtube/metadata.md`:

```yaml
---
platform: youtube
type: long-form-metadata
title: "..."
tags: ["makeup", "beauty over 40", "..."]
source_video: video-sursa/{slug}/video.mp4
date_generated: YYYY-MM-DD
---

## Description
{descriere completă, 200-300 cuvinte}

## Chapters
00:00 — {secțiune 1}
02:14 — {secțiune 2}
...

## Thumbnail text suggestion
{sugestie scurtă}
```

---

### Pas 5: Generare pin Pinterest

Citește `references/pinterest.md` pentru exemple și reguli specifice.

Sursă: **doar `transcript.md`** (nu articolul Substack — evită dependența de ordinea de rulare a skill-urilor; articolul poate să nu existe încă).

Generează:

1. **Titlu pin** — ≤100 caractere, keyword principal în primele 30. Clar, direct, fără jocuri de cuvinte.
2. **Descriere** — ton natural, „sales pitch" scurt: keyword principal + 1-2 secundare, rezumat al beneficiului concret.
3. **Sugestie text overlay** pentru imagine — font lizibil, NU cursiv/handwritten (Pinterest OCR are dificultăți cu scrisul de mână).
4. **Citat sursă pentru cadru** — citat exact de 3-6 cuvinte, verbatim din `transcript.md`, aproape de tehnica/momentul descris în pin. Ancora pe care `frame-image-generator` o caută cu `find_segment_time.py` pentru a extrage un cadru real din `video.mp4`.
5. **Board recomandat** + link către `postari/{slug}/01-substack/`.

**Fără câmp `hashtags`** — Pinterest folosește keywords, nu hashtag-uri.

Salvează `postari/{slug}/05-pinterest/pin.md`:

```yaml
---
platform: pinterest
type: pin
title: "..."
keywords: ["...", "..."]
link_target: postari/{slug}/01-substack/
source_video: video-sursa/{slug}/video.mp4
frame_source_quote: "..."
image_status: pending
date_generated: YYYY-MM-DD
---

## Description
{descriere completă}

## Overlay text suggestion
{text scurt pentru imagine}

## Recommended board
{nume board}
```

`image_status: pending` — imaginea o extrage `frame-image-generator` ulterior din footage-ul real, pe baza `frame_source_quote`. `upload-drive` sare peste postare până statusul devine `ready`.

---

### Pas 6: Self-review cu checklist explicit

Pentru **fiecare** piesă generată, verifică punct cu punct:

**Checklist YouTube** (din „Structură livrabil", secțiunea 2 a matricei):
- [ ] Titlu ≤70 caractere, keyword în primele 40?
- [ ] Descriere 200-300 cuvinte, keyword în primele 2 propoziții?
- [ ] Chapters cu timestamp-uri reale (verificate în `transcript.json`)?
- [ ] Sugestie text thumbnail prezentă?
- [ ] 5-8 tags prezente?

**Checklist Pinterest** (din „Structură livrabil", secțiunea 7 a matricei):
- [ ] Titlu pin ≤100 caractere, keyword în primele 30?
- [ ] Descriere cu keyword principal + 1-2 secundare, ton natural?
- [ ] Sugestie text overlay prezentă (font non-cursiv)?
- [ ] `frame_source_quote` e verbatim din transcript (nu parafrazat)?
- [ ] Board recomandat + link către Substack prezente?

**Criterii comune (ambele piese):**
- [ ] Zero expresii din `.claude/skills/substack-article-writer/references/anti-slop.md`?
- [ ] Acuratețe față de transcript — nu inventează produse/tehnici de makeup nemenționate de client?
- [ ] Mesajul core (Pas 3) e consistent între YouTube și Pinterest?

Dacă detectezi probleme → **corectează automat**, fără a întreba.

---

### Pas 7: Generare INDEX.md + raport final

Creează/actualizează `postari/{slug}/INDEX.md`:

```markdown
# Content Repurposing: {slug}

**Video sursă:** video-sursa/{slug}/video.mp4
**Mesaj core:** {mesajul core din Pas 3}
**Data generare:** {data}

## Postări Generate

| Platformă | Fișier | Status | Note |
|-----------|--------|--------|------|
| YouTube | 02-youtube/metadata.md | draft | |
| Pinterest | 05-pinterest/pin.md | draft | |
```

Afișează sumar final:

```
✅ Content repurposing complet!
📄 Video sursă: video-sursa/{slug}/video.mp4
📁 Output: postari/{slug}/
📊 Piese generate: 2 (YouTube metadata, Pinterest pin)
🔍 Self-review: checklist complet verificat, {N} corecții aplicate
```

---

## Referințe

| Fișier | Când se citește |
|--------|----------------|
| `strategy/repurposing-matrix.md` | Pas 2 — obligatoriu, înainte de orice generare |
| `references/youtube.md` | Pas 4 — la generare YouTube |
| `references/pinterest.md` | Pas 5 — la generare Pinterest |
| `.claude/skills/substack-article-writer/references/anti-slop.md` | Pas 6 — self-review, sursă unică de fraze interzise |
| `strategy/hashtags/youtube.json` | Pas 4 — tags de nișă (creat automat dacă lipsește) |
