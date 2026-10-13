---
name: substack-article-writer
description: Scrie articolul de Substack al clientului (engleză, 1200-2500 cuvinte) direct din video-sursa/{slug}/transcript.md, aplicând stilul de scriere al clientului (tone/stil-scris-client.md) și cerințele de format/SEO Substack. Articolul generat ESTE postarea de Substack, salvată în postari/{slug}/01-substack/. Triggere - scrie articolul de Substack, generează articol Substack, articolul săptămânii, substack article, articol din transcript.
---

# Substack Article Writer

Scrie articolul de Substack al clientului direct din transcriptul video-ului săptămânal — nu dintr-un brief scris de utilizator. Articolul generat **este** postarea de Substack, gata de publicat (după aprobarea clientului), nu un draft intermediar.

**Limbă obligatorie: engleză.** Publicul clientului e vorbitor de engleză, 40+. Instrucțiunile din acest SKILL.md și întrebările către Adelina rămân în română — asta e doar uz intern.

---

## Workflow

Urmează toți pașii, în ordine. Nu sări pași.

---

### Pas 1: Alege slug-ul video-ului

Scanează folderele `video-sursa/*/` care au un `transcript.md`. Pentru fiecare candidat, verifică dacă există deja `postari/{slug}/01-substack/article.md` (semn că a fost procesat).

Dacă nu găsești niciun `video-sursa/*/transcript.md` → oprește și spune Adelinei că trebuie rulat întâi skill-ul `video-intake`.

Altfel, pune **întotdeauna** o întrebare (`AskUserQuestion`) cu slug-urile găsite ca opțiuni — chiar dacă există un singur candidat evident. Marchează în descrierea fiecărei opțiuni dacă are deja articol scris (util ca Adelina să nu suprascrie din greșeală).

---

### Pas 2: Verifică prerechizitele

- Verifică `tone/stil-scris-client.md` există. **Dacă lipsește, oprește-te** — nu inventa un stil de scriere. Spune clar Adelinei că trebuie rulat întâi skill-ul `writing-style-client`, care produce acest fișier.
- Citește integral `video-sursa/{slug}/transcript.md`. E text brut, fără frontmatter — doar proza vorbită a clientului, paragrafe separate la pauzele mari din discurs.
- Citește integral `tone/stil-scris-client.md`.

---

### Pas 3: Citește referințele obligatorii

Înainte de a scrie:
1. `references/anti-slop.md` — reguli anti-slop, în engleză
2. `references/substack-format-seo.md` — mecanica de format/SEO specifică Substack

---

### Pas 4: Scrie articolul

**Reguli:**
- **Limbă:** engleză, întotdeauna.
- **Lungime:** 1200-2500 cuvinte (fără frontmatter). Nu forța la 3000+ — nu umple cu content generic doar ca să atingi un număr; lungimea vine din ce chiar a spus clientul.
- **Structură:** urmează fluxul narativ deja definit în `tone/stil-scris-client.md` (secțiunea "Cum leagă ideile"): mit greșit → corectare → de ce contează (pentru femei 40+, concret) → cum se face (pași/tehnică) → concluzie-principiu quotabilă → invitație caldă la acțiune. Nu alege între structuri SEO generice (skyscraper/how-to/listicle) — nu se mai folosesc aici.
- **Fidelitate față de transcript:** orice tehnică, produs sau exemplu menționat trebuie să existe în `transcript.md`. Nu inventa statistici, studii sau surse externe — dacă clientul citează ceva concret în video, păstrează-l; altfel nu adăuga citări false. Articolul e o transformare a vorbirii spontane a clientului în proză scrisă, nu un articol de research nou.
- **CTA:** invitație caldă, non-agresivă de abonare la Substack (implicit, per stilul din `stil-scris-client.md`). Folosește alt CTA doar dacă Adelina l-a cerut explicit în prompt.
- **Formatare body:** titlul devine automat H1 pe Substack — **nu** pune `#` manual în body. Folosește `##` (H2) pentru secțiuni majore și `###` (H3) pentru sub-secțiuni. Paragrafe scurte (max 4-5 rânduri). Bold moderat pe idei cheie.
- **Termeni cheie:** plasează natural termenii relevanți temei (ex. numele tehnicii de machiaj) în primele ~100 de cuvinte — fără keyword stuffing.

**Frontmatter YAML obligatoriu:**

```yaml
---
title: "..."            # <60 caractere, termen cheie devreme — devine automat H1, nu-l repeta cu # în body
subtitle: "..."         # 155-160 caractere — dublează ca meta description ȘI teaser de email, setează-l mereu explicit
slug: "..."
source_video_slug: "{slug}"
date: YYYY-MM-DD
cta: "subscribe"        # sau CTA custom dacă a fost cerut explicit de Adelina
---
```

---

### Pas 5: Self-review automat

Verifică articolul contra criteriilor din `references/substack-format-seo.md` și `references/anti-slop.md`:

- **Format tehnic:** title <60 caractere, subtitle 155-160 caractere, zero `#` manual în body, `##`/`###` folosite corect, lungime 1200-2500 cuvinte.
- **Anti-slop:** zero fraze din lista interzisă, fiecare paragraf conține ceva concret (nu generalități goale).
- **Fidelitate:** fiecare afirmație/exemplu se regăsește în transcript — nimic inventat.
- **Ton:** se potrivește cu exemplele din `tone/stil-scris-client.md`.

Generează un tabel de raportare:

```
| Criteriu | Status | Detalii |
|----------|--------|---------|
| Title | ✅ OK | "..." (54 car) |
| Subtitle | ✅ OK | "..." (158 car) |
| Word count | ✅ OK | 1847 cuvinte |
| ... | ... | ... |
```

Dacă un criteriu e FAIL → corectează articolul înainte de salvare și notează corecția în tabel.

---

### Pas 6: Salvare

1. Creează folderul `postari/{slug}/01-substack/` dacă nu există.
2. Salvează articolul în `postari/{slug}/01-substack/article.md`.
3. **Exportă și un `.docx`** — clientul citește și aprobă articolul, nu vrea să deschidă un fișier `.md` brut. Rulează:
   ```bash
   python .claude/skills/substack-article-writer/scripts/export_docx.py \
     --in postari/{slug}/01-substack/article.md \
     --out postari/{slug}/01-substack/article.docx
   ```
   Scriptul citește frontmatter-ul (titlu → Heading 1, subtitle → paragraf italic sub titlu), `##`/`###` devin Heading 2/3, `**bold**` devine bold. Nu necesită dependințe noi dincolo de `python-docx` (verifică `python3 -c "import docx"` — dacă lipsește, instaleaz-o cu `pip install python-docx` înainte de a rula scriptul).
4. Afișează sumar final:
   ```
   ✅ Articol salvat: postari/{slug}/01-substack/article.md
   📄 Versiune Word: postari/{slug}/01-substack/article.docx
   📊 Word count: {N} cuvinte
   🎬 Video sursă: video-sursa/{slug}/transcript.md
   ```
5. Sugerează pasul următor: `content-repurposer` (YouTube + Pinterest) sau `upload-drive`, conform pipeline-ului din `CLAUDE.md`.

---

## Referințe

| Fișier | Când se citește |
|--------|----------------|
| `references/anti-slop.md` | Pas 3 și Pas 5 — întotdeauna, înainte de scriere și la self-review |
| `references/substack-format-seo.md` | Pas 3 și Pas 5 — întotdeauna, înainte de scriere și la self-review |
