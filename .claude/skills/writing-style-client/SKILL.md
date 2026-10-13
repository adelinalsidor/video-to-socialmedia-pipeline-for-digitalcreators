---
name: writing-style-client
description: Extrage ghidul scurt de stil de scriere al clientului (nu fișă de personalitate) din scriptul video EN al clientului + opțional un text mai lung scris de client, în altă limbă (doar ritm/structură), și scrie tone/stil-scris-client.md. Folosit o singură dată / rar, doar când apar sample-uri noi de scris ale clientului. Output-ul e citit EXCLUSIV de substack-article-writer. Triggere - extrage stilul clientului, actualizează stil-scris-client, regenerează ghidul de stil.
---

# Writing Style Client

Produce `tone/stil-scris-client.md` — un ghid SCURT de stil de scriere (vocabular, ritm, cum leagă ideile, ce evită), NU o fișă de personalitate/psihologie de tip "brand voice" generică.

**De ce există separat de restul pipeline-ului:** vocea vorbită a clientului există deja, proaspătă, în `transcript.md` al fiecărui video săptămânal — `content-repurposer` și `video-repurposer` citesc transcript-ul curent direct pentru caption-uri/hook-uri, nu au nevoie de acest fișier. Singurul loc unde un ghid persistent chiar ajută e **articolul de Substack**, pentru că acolo transformăm vorbire spontană în proză scrisă.

---

## Când se rulează

- O singură dată, la Faza 1 a pipeline-ului (bootstrap).
- Din nou, doar dacă clientul trimite sample-uri noi de scris (alt script, un text mai lung în altă limbă, un articol scris de client) și stilul curent pare depășit sau insuficient.

**Nu** se rulează săptămânal — nu ține pasul cu transcript-urile, acelea au propriul flux.

---

## Input-uri

1. **Obligatoriu:** un script scurt în ENGLEZĂ scris/vorbit de client (ex. descriere de video, un email, un draft al clientului). Aceasta e sursa PRIMARĂ — vocea reală a clientului, în limba în care scriem conținutul final.
2. **Opțional:** pagini dintr-un text mai lung scris de client, într-o altă limbă. Se folosesc **DOAR** pentru ritm de frază și structură de idei (cum deschide, cum leagă tehnica de un principiu, cum încheie) — **niciodată** pentru traducere literală de conținut sau vocabular RO→EN.

Dacă lipsește input-ul obligatoriu (scriptul EN), **nu inventa** un stil — oprește-te și cere-l cursantei/Adelinei via `AskUserQuestion`.

---

## Workflow

### Pas 1 — Citește sursele
Citește scriptul EN cuvânt cu cuvânt. Dacă există și un text mai lung în altă limbă, citește-l doar pentru tipare structurale, nu pentru conținut de tradus.

### Pas 2 — Identifică tiparele, nu doar cuvintele
Caută răspunsuri la:
- **Cum deschide?** (context general vs. corectare de mit/presupunere greșită — verifică ambele surse pentru confirmare încrucișată)
- **De unde vine autoritatea clientului?** (experiență personală vs. citate din "experți")
- **Cum leagă tehnica de ceva mai mare** (un principiu, o filozofie, o emoție)?
- **Cum se adresează cititoarei** (persoana I/II, ton)?
- **Ritmul propozițiilor** — scurte/lungi, punctuație distinctivă (puncte de suspensie, liste)?
- **Cum leagă ideile între ele** — ce vine după ce, structura tipică a unui text?
- **Vocabular preferat** — cuvinte care revin, termeni tehnici folosiți firesc?
- **Ce evită** — ce NU face (superlative goale, vânzare agresivă, jargon de marketing)?

### Pas 3 — Scrie `tone/stil-scris-client.md`
Format: secțiuni scurte, fiecare cu un exemplu concret citat din script (nu inventat). Include o secțiune finală care notează explicit că sursa română a fost folosită doar pentru ritm/structură, nu pentru conținut tradus.

Ține fișierul **scurt** — e un ghid de stil, nu o fișă de personaj de 2 pagini. Dacă depășește ~1 pagină, tunde.

### Pas 4 — Validare cu Adelina
Prezintă un rezumat scurt al regulilor extrase și întreabă (via `AskUserQuestion` sau direct) dacă se potrivesc cu ce știe clientul despre propria voce, înainte ca fișierul să fie considerat final. Notează în frontmatter `status: draft` până la confirmare, apoi `status: validated`.

---

## Output

`tone/stil-scris-client.md` — citit exclusiv de `substack-article-writer` la scrierea articolului de Substack.

**Nu** atinge alte fișiere din `tone/` sau din alte skill-uri.
