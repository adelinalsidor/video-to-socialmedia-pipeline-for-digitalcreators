# Frontmatter Schema — video-repurposer

Toate câmpurile sunt obligatorii, cu excepția celor marcate `(opțional)`. Toate valorile text (hook, caption, cta, slide text) sunt în ENGLEZĂ.

## Clip video (Reel / TikTok / Shorts)

```yaml
---
platform: instagram          # instagram | tiktok | youtube
type: reel                   # reel | tiktok | shorts
hook: "..."                  # text hook overlay pt. primele 2-3s, cuvinte identice cu audio-ul (Contextual Continuity)
cta: "Save this"             # per matrice: Reel "Save this"/"Link in bio"; TikTok "Follow for more"; Shorts "Watch the full video"
hashtags: ["#...", "#...", "#..."]   # 3-5, din strategy/hashtags/{instagram,tiktok-reels,youtube}.json + nișă makeup
video_path: "{N}-{topic-slug}.mp4"   # relativ la folderul acestui .md; N=1-5, poziția cronologică a momentului în video
video_status: ready
source_video_slug: "{slug}"
video_source_segment: "MM:SS-MM:SS"  # timecode în video-sursa/{slug}/video.mp4
date_generated: YYYY-MM-DD
---

{caption text — scurt, cu cuvinte cheie repetate din clip, conversation starter unde se potrivește platforma}

## Note Editoriale

### Segment sursă
- Timecode: MM:SS-MM:SS din video-sursa/{slug}/video.mp4
- Mesaj core: {mesajul core al video-ului, 1-2 propoziții}

### Variantă hook alternativă
{o a doua variantă de hook, pentru A/B testing manual}
```

`upload-drive` extrage caption-ul ca textul dintre sfârșitul frontmatter-ului și heading-ul `## Note Editoriale` — secțiunea trebuie să existe mereu, chiar dacă notele sunt scurte.

## Carusel Instagram (text-only, fără video)

```yaml
---
platform: instagram
type: carousel
hook: "..."                  # întrebarea/hook-ul de pe slide 1 ("open loop")
cta: "Save this for later"
hashtags: ["#...", "#...", "#..."]   # 3-5
image_status: pending        # NU "ready" — frame-image-generator extrage cadrele ulterior
source_video_slug: "{slug}"
date_generated: YYYY-MM-DD
---

{caption 80-150 cuvinte — hook în prima propoziție, CTA "Save"-type la final}

## Note Editoriale

### Slides
1. **Slide 1 (Hook):** {text scurt pe slide} — Citat sursă pentru cadru: "{citat exact 3-6 cuvinte din transcript.md}"
2. **Slide 2:** {...} — Citat sursă pentru cadru: "{...}"
3. **Slide 3:** {...} — Citat sursă pentru cadru: "{...}"
...
8-9. **Payoff:** {răspunsul la întrebarea din slide 1} — Citat sursă pentru cadru: "{...}"
10. **Slide final (CTA):** Save this for later — Citat sursă pentru cadru: "{...}"
```

Fiecare „Citat sursă pentru cadru" trebuie să fie **verbatim din `transcript.md`** (identic la literă, ca și hook-urile celor 5 momente din secțiunea de mai sus) — `frame-image-generator` îl caută cu `find_segment_time.py` ca să localizeze un cadru real din `video.mp4` pentru acel slide. Nu descrie o imagine, nu inventa text — alege o frază care chiar apare în transcript, aproape de ideea slide-ului.

`image_status: pending` (nu `ready`) e intenționat — `upload-drive` sare peste postare până `frame-image-generator` extrage cadrele reale din video pe baza citatelor-ancoră și schimbă statusul.

## De ce `video_path` e relativ

`video_path` e calea fișierului `.mp4` relativ la folderul unde stă `.md`-ul (nu la rădăcina proiectului) — la fel cum `video-sursa/{slug}/video.mp4` e mereu colocat cu `meta.json`/`transcript.md` în aceeași convenție de proiect.
