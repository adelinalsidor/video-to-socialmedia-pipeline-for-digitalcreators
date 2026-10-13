# Repurposing Matrix — Proiect Client

> Dintr-un video săptămânal (footage real, sub 10 minute, engleză) → 7 piese de content, fiecare adaptată nativ platformei ei.

**Principiu central — Coherence Rule:** Toate variațiile transmit ACELAȘI mesaj core din video-ul săptămânii. Ambalajul diferă. Substanța NU.

**Atenție — notă structurală importantă:** clientul nu scrie scripturi separate pentru fiecare platformă. Ea filmează UN SINGUR video (footage real) care **este** conținutul de YouTube Long-form. Shorts-urile, Reel-ul de Instagram și clipul de TikTok sunt **tăiate din același footage** local, cu ffmpeg (skill `video-repurposer`) — nu sunt scripturi generate de la zero. Deci pentru acele 3 formate, ce generăm e **metadata + hook text overlay + caption + hashtags** pentru un clip deja existent, NU un script video. Singurele formate unde textul chiar se scrie de la zero din transcript sunt **Substack** (articol), **Instagram Carousel** (slide-uri) și **Pinterest** (pin copy).

Tot conținutul generat (titluri, caption-uri, hook-uri, hashtag-uri, descrieri) e în **ENGLEZĂ** — publicul clientului e vorbitor de engleză, 40+ ani.

---

## Tabel Rezumat

| # | Platformă / Format | Sursă conținut | Output | Lungime | Ton | CTA |
|---|---|---|---|---|---|---|
| 1 | Substack | Generat din transcript (articol) | 1 articol | 1200-2500 cuvinte | Personal, scris (vezi `tone/stil-scris-client.md`) | Comment / Reply / Subscribe |
| 2 | YouTube Long-form | Metadata pt. video-ul brut | Titlu + descriere + tags + chapters | Titlu ≤70 car., descriere 200-300 cuv. | Informativ, cald | Subscribe + video recomandat |
| 3 | YouTube Shorts | Metadata pt. clip tăiat | Titlu + descriere + hook overlay | Clip 15-60s, descriere scurtă | Direct, energic | "Watch the full video" |
| 4 | Instagram Carousel | Generat din transcript (slide-uri) | 8-10 slide-uri + caption | Caption 80-150 cuvinte | Cald, conversațional | Save / Share |
| 5 | Instagram Reel | Metadata pt. clip tăiat | Caption + hook overlay + hashtags | Clip 15-60s, caption scurt | Energic, personal | "Save this" / "Link in bio" |
| 6 | TikTok | Metadata pt. clip tăiat | Caption + hook overlay + hashtags | Clip 15-34s | Direct, autentic | "Follow for more" |
| 7 | Pinterest | Generat din transcript/articol (pin copy) | Titlu + descriere + keywords | Titlu ≤100 car. (keyword în primele 30) | Clar, orientat spre beneficiu | Click către articolul Substack |

**Total:** 7 piese de content per video săptămânal.

---

## Specificații Detaliate per Platformă

### 1. Substack — „Articolul"

- **Sursă:** `video-sursa/{slug}/transcript.md`, procesat de skill-ul `substack-article-writer`, aplicând `tone/stil-scris-client.md`.
- **Lungime:** 1200-2500 cuvinte.
- **SEO intern + extern:** optimizează atât pentru căutare internă Substack, cât și pentru Google/Bing — titlu și primul paragraf cu cuvinte cheie clare despre subiectul makeup-ului discutat în video.
- **SEO pentru AI search (nou în 2026):** newsletter-ele apar tot mai des citate de instrumente ca ChatGPT/Perplexity — scrie paragrafe auto-conținute, cu afirmații clare și structurate, ușor de citat.
- **Poziționare de nișă:** rămâi specific pe subiectul makeup — nișa clară performează mai bine decât conținutul generic.
- **Creștere:** Recommendations + Notes (funcțiile native Substack) sunt motorul principal de creștere sub 10.000 de abonați — nu SEO extern pur.
- **CTA:** un singur CTA clar — comentariu, share, sau (după aprobare) subscribe.
- **Regulă de aur:** articolul E postarea de Substack, nu un rezumat al ei — vezi skill-ul `substack-article-writer` pentru format complet.

### 2. YouTube Long-form — „Videoclipul Săptămânii"

- **Sursă:** video-ul brut filmat de client (footage real, sub 10 min) — NU se generează script, doar metadata.
- **Titlu:** cuvântul cheie principal în primele 40 de caractere. Specific, nu „clever" — un titlu cu keyword clar se poziționează în medie cu 1.5 poziții mai sus decât unul fără.
- **Descriere:** cuvântul cheie principal în primele 2 propoziții. 200-300 cuvinte de context — YouTube folosește textul ăsta ca să înțeleagă despre ce e video-ul.
- **Chapters:** obligatorii, cu timestamp-uri — ajută navigarea și SEO-ul deopotrivă.
- **Transcript/captions:** activează sau încarcă subtitrări — extra acoperire de cuvinte cheie și accesibilitate.
- **Thumbnail text:** text scurt, cu contrast puternic, care promite beneficiul concret al video-ului.
- **Regulă de aur:** titlul + primele 2 propoziții din descriere sunt ce vede algoritmul întâi — nu le trata ca detaliu.
- **Structură livrabil:**
  1. Titlu (≤70 car., keyword în primele 40)
  2. Descriere (200-300 cuv., keyword în primele 2 propoziții)
  3. Chapters cu timestamp-uri
  4. Sugestie text thumbnail
  5. Tags (5-8, relevante)

### 3. YouTube Shorts — „Clipul Rapid"

- **Sursă:** clip deja tăiat din footage-ul săptămânii (`video-repurposer`) — se generează doar metadata + hook text.
- **Hook:** primele 3 secunde sunt critice; ideal sub 0.5s pentru „jolt"-ul vizual care oprește swipe-ul. Text pe ecran ajută să dai context înainte ca privitorul să proceseze audio.
- **Retenție:** rewatch-ul (privitorul revede clipul) e semnalul #1 de algoritm — dacă poți crea un moment „prea rapid ca să-l prinzi din prima", mai bine.
- **Hashtags:** 3-5 — #Shorts + 2 hashtag-uri de nișă + 1 semantic/viral. Primul hashtag intră în primele 100 de caractere din descriere (are pondere dublă acolo).
- **Regulă de aur:** hook-ul și retenția contează de 100x mai mult decât hashtag-urile (care sunt ~5% din discoverability) — nu optimiza exagerat hashtag-urile în detrimentul primelor 3 secunde.
- **Structură livrabil:**
  1. Titlu scurt cu keyword
  2. Text hook overlay (ce apare pe ecran în primele 2-3s)
  3. Descriere scurtă cu hashtag principal în primele 100 car.
  4. 3-5 hashtags (#Shorts + nișă + semantic)

### 4. Instagram Carousel — „Micro-Blogul"

- **Sursă:** generat de la zero din transcript — cel mai „scris" format după Substack.
- **Format câștigător 2026:** carusel-urile ating 1.92% engagement mediu — aproape 4x mai mult decât Reels (0.50%) și single-image (0.45%).
- **Număr de slide-uri:** 8-10, format 4:5 (1080x1350px), un singur idei pe slide.
- **Tehnica „open loop":** pui o întrebare pe slide 1, răspunsul vine abia pe slide 5-6 — ține atenția până la capăt.
- **Re-servire de algoritm:** dacă userii ajung la slide 3+, Instagram re-servește carusel-ul la 24-48h după postare — un al doilea val de impresii gratuit.
- **Media mixtă:** 1-2 slide-uri video (sub 15s, cu subtitrări — 85% urmăresc fără sunet), restul statice.
- **Muzică:** adăugarea unei piese pe carusel îl împinge în feed-ul de Reels — reach de Reel, cu profunzimea de engagement a caruselului.
- **Caption:** 80-150 cuvinte, hook în prima propoziție, CTA de tip „Save" la final (cel mai eficient CTA pentru conținut educațional).
- **Structură livrabil:**
  1. Slide 1: Hook / întrebare care creează curiozitate
  2. Slide 2-7: Un idei/pas per slide, aceeași ratie de aspect
  3. Slide 8-9: Payoff-ul întrebării din slide 1
  4. Slide final: Rezumat + CTA „Save this for later"
  5. Caption (80-150 cuv.) + 3-5 hashtags

### 5. Instagram Reel — „Clipul Personal"

- **Sursă:** clip tăiat din footage-ul săptămânii (`video-repurposer`) — se generează caption + hook overlay + hashtags.
- **Lungime optimă:** 15-20s pentru reach/completion rate, SAU 45-60s pentru saves/shares. Evită zona 30-40s („dead zone" cu scădere de retenție la mijloc).
- **Hook:** primele 3 secunde decid — hook-ul trebuie să „încarce" instant, nu să se construiască treptat.
- **Hashtags:** 3-5, foarte relevante — Instagram în 2026 se bazează mai mult pe „interest node mapping" decât pe volum de hashtag-uri.
- **Semnale de algoritm:** completion rate, replay-uri și share-uri către DM/Stories cântăresc mai mult decât like-urile.
- **„Contextual Continuity" (regula #1 din 2026):** audio-ul, textul de pe ecran și caption-ul trebuie să folosească aceleași cuvinte cheie semantice — alinierea asta crește discoverability-ul cu până la 50%.
- **Structură livrabil:**
  1. Text hook overlay (0-3s) — aceleași cuvinte cheie ca în audio
  2. Caption cu cuvintele cheie repetate din video (Contextual Continuity)
  3. CTA: „Save this" / „Link in bio" / „Which one is your favorite?"
  4. 3-5 hashtags de nișă

### 6. TikTok — „Clipul Autentic"

- **Sursă:** clip tăiat din footage-ul săptămânii (`video-repurposer`) — se generează caption + hook overlay + hashtags.
- **Lungime:** 15-34 secunde tipic; format vertical 1080x1920 (9:16).
- **Hook:** primele 2 secunde — vizual puternic + mesaj clar, fără introducere lentă.
- **Semnale de algoritm (ordine 2026):** rewatch/loop rate > completion rate > shares > comentarii relevante > like-uri (like-urile cântăresc cel mai puțin).
- **Hashtags:** 3-5, mix de trending + evergreen de nișă.
- **Cuvinte cheie peste tot:** nu doar în caption — și în textul de pe ecran (on-video text), TikTok le folosește pe toate pentru discovery.
- **Regulă de aur:** sistem dual — un strat construit pentru swipe (hook, ritm, packaging), un strat construit pentru query (keyword-uri în caption + on-video text).
- **Structură livrabil:**
  1. Text hook overlay (0-2s)
  2. Caption cu keyword-uri relevante + conversation starter
  3. 3-5 hashtags (trending + evergreen)
  4. CTA: „Follow for more" / „Which tip surprised you?"

### 7. Pinterest — „Pin-ul Static"

- **Sursă:** textul (titlu, descriere, overlay) generat din articolul Substack / transcript de `content-repurposer`; imaginea e un cadru real extras din `video.mp4` de `frame-image-generator` (nu grafică generată AI — clientul e o persoană reală).
- **Format vizual:** vertical, ratio 2:3, imagine nouă („fresh pin" — re-postarea aceleiași imagini e o strategie moartă în 2026).
- **Titlu pin:** cuvântul cheie principal în primele 30 de caractere — cea mai valoroasă zonă de pe pin. Clar și direct, fără jocuri de cuvinte.
- **Descriere:** scrisă natural, ca „un sales pitch" — combină cuvântul cheie principal + 1-2 secundare într-un rezumat scurt al beneficiului.
- **Text overlay pe imagine:** font lizibil, NU cursiv/handwritten — OCR-ul AI al Pinterest are dificultăți cu fonturile scrise de mână și pierzi din discoverability.
- **Board:** titlul și descrierea board-ului trebuie să folosească același cluster de cuvinte cheie ca pin-ul — altfel confuzi algoritmul.
- **Link:** către articolul din `01-substack/` al săptămânii respective.
- **Structură livrabil:**
  1. Titlu pin (≤100 car., keyword în primele 30)
  2. Descriere (keyword principal + 1-2 secundare, ton natural)
  3. Sugestie text overlay pentru imagine + citat sursă pentru cadru (pt. `frame-image-generator`)
  4. Board recomandat + link către articol

---

## Proces de Execuție

### Pas 1 — Video-ul săptămânii e sursa unică
Nu pornim de la un brief scris. Sursa e `video-sursa/{slug}/transcript.md` (produs de `video-intake`) + footage-ul brut pentru clipurile tăiate.

### Pas 2 — Mesajul core
Înainte de orice repurposing, extrage mesajul core al video-ului în 1-2 propoziții. Fiecare piesă de content trebuie să-l transmită (Coherence Rule).

### Pas 3 — Generare
Fiecare piesă se generează cu skill-ul dedicat (`substack-article-writer` pentru articol; restul urmează să fie construite/adaptate) și se salvează în `postari/{slug}/0X-platformă/`, conform hărții de foldere din `CLAUDE.md`.

### Pas 4 — Review (3 întrebări)
1. **Mesajul core e consistent?** — Deschide toate cele 7 piese. Transmit ACELAȘI mesaj?
2. **Tonul e ok?** — Sună ca clientul (vezi transcript-ul original)? Sau sună ca un AI generic?
3. **Faptele sunt corecte?** — Verifică fiecare afirmație despre produse/tehnici de makeup față de transcript.

### Pas 5 — Aprobare
Toate postările primesc `review_status` în `config.json` (`pending_review` → `approved`, scris de `upload-drive`). Substack cere aprobarea explicită a clientului; restul au termen duminică seara.

---

## Date Cheie per Platformă (Referință Rapidă, 2026)

| Platformă | Semnal #1 de algoritm | Lungime/Dimensiune optimă | Hashtags |
|---|---|---|---|
| Substack | Recommendations + Notes (sub 10k abonați) | 1200-2500 cuvinte | — |
| YouTube Long-form | CTR + watch time | Titlu ≤70 car., keyword în primele 40 | 5-8 tags |
| YouTube Shorts | Rewatch rate | Hook <3s (ideal <0.5s) | 3-5 (#Shorts + nișă) |
| Instagram Carousel | Swipe-through (slide 3+) | 8-10 slide-uri, 4:5 (1080x1350) | 3-5 |
| Instagram Reel | Completion + shares/DM | 15-20s (reach) sau 45-60s (saves) | 3-5 |
| TikTok | Rewatch/loop rate | 15-34s, 9:16 (1080x1920) | 3-5 (trending + evergreen) |
| Pinterest | Fresh pin + keyword match | Titlu ≤100 car., keyword în primele 30 | — (keywords, nu hashtags) |

---

*Repurposing Matrix v2.0 — Proiect Client, actualizat 2026-08-07, cu date de optimizare/SEO din research web 2026 per platformă.*
