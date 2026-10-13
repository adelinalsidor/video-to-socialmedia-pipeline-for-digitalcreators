# YouTube Long-Form — Metadata for an Existing Video

This is **not** a script. The client already filmed the video (real footage, under 10 minutes). This reference covers only the metadata wrapped around that existing video: title, description, chapters, tags, thumbnail text.

---

## Spec (from `strategy/repurposing-matrix.md`, section 2)

| Field | Requirement |
|---|---|
| **Title** | ≤70 characters, main keyword in the first 40 |
| **Description** | 200-300 words, main keyword in the first 2 sentences |
| **Chapters** | Required — 4-6 sections, real timestamps from `transcript.json` |
| **Tags** | 5-8, relevant to makeup/beauty niche |
| **Thumbnail text** | Short, high contrast, promises a concrete benefit |

**Golden rule:** the title and the first 2 sentences of the description are what the algorithm reads first — treat them as the highest-leverage words in the whole piece, not an afterthought.

---

## Title

- Specific beats clever. A title with a clear keyword ranks ~1.5 positions higher on average than one without.
- Lead with the concrete outcome or technique, not a vague tease.

**Good:**
- "Concealer Technique for Redness & Dark Circles (Women Over 40)"
- "5-Minute Everyday Makeup Routine for Mature Skin"

**Weak (avoid):**
- "You Won't Believe This Makeup Trick!"
- "My Makeup Secrets Revealed"

---

## Description

- First 2 sentences carry the main keyword — this is what displays under the video and in search snippets.
- 200-300 words total: what the viewer will learn, what products/techniques are covered, why it matters for the over-40 audience.
- Write it from what's actually in the transcript — don't invent products or claims the client didn't say on camera.

**Structure:**
1. Hook sentence with the main keyword (what this video teaches)
2. 1-2 sentences on why it matters for women 40+
3. Brief rundown of what's covered (mirrors the chapters)
4. Soft CTA: subscribe + related video mention

---

## Chapters

- Split the transcript into 4-6 logical sections by topic/technique (e.g., "Skin prep," "Covering redness," "Brightening the orbital bone," "Setting the look").
- For each section, find the real start time by matching the section's opening words against `transcript.json` → `words[]` (word-level `start` timestamps in seconds).
- Format as `MM:SS — Section name`.

**Example:**
```
00:00 — Intro & skin prep
01:12 — Covering redness and dark spots
04:30 — Technique: pack, don't spread
07:45 — Brightening the orbital bone
10:20 — Setting with blush, final look
```

---

## Tags

- 5-8 total, mixing niche staples (from `strategy/hashtags/youtube.json`) with 2-3 tags specific to this week's video content.
- Base niche tags: `makeup`, `makeup tutorial`, `beauty over 40`, `makeup artist tips`, `everyday makeup`.
- Video-specific tags: pull from what the client actually demonstrates (e.g., `concealer technique`, `covering redness`, `mature skin makeup`).

---

## Thumbnail text suggestion

- Short (3-5 words), high contrast, promises the concrete result.
- Examples: "Redness? Gone.", "5-Min Concealer Fix", "Makeup After 40: Less Is More"

---

## Anti-slop for YouTube metadata

Beyond the general list in `substack-article-writer/references/anti-slop.md`, watch for these YouTube-specific traps:

- "You won't believe..." / "This changed everything" → state the actual result
- "Watch till the end!" as a hook → the content itself should earn the watch-through, not a promise
- "In this video, I'm going to show you..." as an opener → cut straight to the promise instead
- Generic "welcome back to my channel" openers in the description — lead with the keyword and value instead
