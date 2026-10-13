# Pinterest — Static Pin Copy

Pinterest gets **no video** in this pipeline — just a static pin (a real frame extracted later from `video-sursa/{slug}/video.mp4` by `frame-image-generator`) with title, description, and overlay text written here, from the transcript.

---

## Spec (from `strategy/repurposing-matrix.md`, section 7)

| Field | Requirement |
|---|---|
| **Visual format** | Vertical, 2:3 ratio, fresh image (never reuse a prior pin's image) |
| **Title** | ≤100 characters, main keyword in the first 30 |
| **Description** | Natural, benefit-driven, main keyword + 1-2 secondary keywords |
| **Overlay text** | Readable font, NOT cursive/handwritten — Pinterest's OCR struggles with script fonts |
| **Board** | Must share the same keyword cluster as the pin |
| **Link** | Points to this week's Substack article (`postari/{slug}/01-substack/`) |

**No hashtags.** Pinterest ranks on keyword match, not hashtags — don't add a `hashtags` field to the frontmatter.

---

## Title

- The most valuable real estate on the pin is the first 30 characters — put the main keyword there.
- Clear and direct, not clever. Pinterest search behaves more like Google than like a social feed.

**Good:**
- "Concealer Technique for Redness (Women Over 40 Makeup)"
- "5-Minute Everyday Makeup for Mature Skin"

**Weak (avoid):**
- "You Have to See This!"
- "My Little Makeup Secret"

---

## Description

- Written like a short, natural sales pitch — not a keyword list.
- Combine the main keyword with 1-2 secondary keywords, framed around the concrete benefit (what the reader gets, not what the client did).
- Source it from the transcript only — don't pull from the Substack article, since it may not exist yet when this runs.

**Structure:** benefit-first sentence with main keyword → 1 sentence of context/technique → soft mention of the full guide on Substack.

---

## Overlay text suggestion

- Short, legible, sans-serif style font — flag this explicitly for `frame-image-generator` since Pinterest's AI-driven OCR loses discoverability on handwritten/cursive fonts.
- 3-6 words max, states the benefit or the technique.

**Example:** "Fix Redness Without Caking", "Concealer Trick After 40"

### Citat sursă pentru cadru

Alege și un **citat exact de 3-6 cuvinte, verbatim din `video-sursa/{slug}/transcript.md`**, cât mai aproape de momentul/tehnica descrisă în pin. Nu descrie o imagine — `frame-image-generator` caută acest citat cu `find_segment_time.py` ca să localizeze un cadru real în `video.mp4`, apoi arde overlay-ul de mai sus peste el.

Adaugă-l în frontmatter ca `frame_source_quote: "..."`.

---

## Recommended board

- Name it around the same keyword cluster as the pin title/description (e.g., "Makeup Tips for Women Over 40," "Everyday Beauty Routines") — a mismatched board confuses Pinterest's ranking signals.

---

## Anti-slop for Pinterest copy

Beyond the general list in `substack-article-writer/references/anti-slop.md`:

- "Pin this for later!" as the entire CTA — pair it with the actual benefit instead of using it as filler
- Vague board names like "Beauty" or "Tips" — always tie the board to the specific keyword cluster
- Keyword-stuffed descriptions that don't read as a real sentence — natural phrasing still needs to win
