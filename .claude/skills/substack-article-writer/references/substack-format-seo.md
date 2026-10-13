# Substack Format & SEO Guide

Substack isn't a generic blog CMS — it has its own mechanics for how title, headings, and previews work. This guide is the on-page format/SEO reference for this skill. It reflects how Substack actually works (verified via web research when this skill was built), not generic blog-SEO advice.

---

## Title

- Keep it **under 60 characters**. If it's too long, Google may truncate it with an ellipsis or rewrite it entirely.
- Put the relevant term (the technique or topic the client is teaching) early in the title, phrased as a concrete value statement — not a vague category.
  - Weak: "Concealer Tips"
  - Better: "The Concealer Mistake That Makes You Look Older"
- The title becomes the post's **H1 automatically** on Substack. Never add a manual `#` heading at the top of the body that repeats it.

## Subtitle

- Write **155-160 characters**. This field does double duty: it's the SEO meta description AND the teaser text shown in email and social previews.
- **Always set it explicitly.** If left blank, Substack auto-pulls the first sentence of the post — which is rarely the strongest hook.
- Include the core promise of the piece and, where natural, a soft nod to the reader taking action (reading on, trying it).

## Headings in the body

- **No manual H1** — the title already fills that role.
- Use `##` (H2) for each major section of the article.
- Use `###` (H3) only for sub-points within a section, if needed.
- Keep headings short and specific to what that section actually delivers — not generic labels like "Introduction" or "Conclusion."

## Opening ~100 words

- Place the core topic/technique in natural language early — this is what search engines and readers both use to judge relevance.
- Never keyword-stuff. One clear, well-placed mention beats three forced ones.

## Images (if/when used)

- If a preview image is added, Substack recommends **1200×630px, 14:10 aspect ratio**.
- Whatever image appears **first in the post body** automatically becomes the preview/share image, unless manually overridden in post settings before publishing.
- This skill doesn't generate images — if the client wants a header image for a given article, that's a separate step (not currently automated; `frame-image-generator` only covers the Instagram carousel and Pinterest pin).

## General formatting

- Short paragraphs — Substack's reading experience (web and, especially, email) punishes big text blocks.
- Moderate bold on key phrases, not entire sentences.
- Substack renders posts differently on **web vs. email** — avoid complex HTML or layout tricks; simple Markdown-equivalent formatting (headings, bold, italics, lists, blockquotes) is what survives both contexts reliably.

---

## Self-review checklist (Pas 5 of SKILL.md)

| # | Criterion | Requirement |
|---|-----------|-------------|
| 1 | Title length | Under 60 characters |
| 2 | Subtitle length | 155-160 characters, set explicitly |
| 3 | No manual H1 | Body starts with `##`, never `#` |
| 4 | Heading levels | `##` for major sections, `###` only for sub-points |
| 5 | Word count | 1200-2500 words (excluding frontmatter) |
| 6 | Keyword placement | Core topic named naturally in the first ~100 words, no stuffing |
| 7 | Paragraph length | Short — no dense text blocks |

Sources consulted when writing this guide: Substack's own SEO guide (on.substack.com), Substack's support documentation on image dimensions, and third-party Substack formatting guides. Substack's own product can change — if something here seems out of date, verify with a quick web search before trusting it blindly.
