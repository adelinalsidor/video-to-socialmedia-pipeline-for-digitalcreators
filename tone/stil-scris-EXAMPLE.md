---
name: stil-scris-EXAMPLE
scope: EXEMPLU / TEMPLATE — nu date reale. Arată formatul așteptat de skill-ul `substack-article-writer`.
  Pentru un client nou: copiază acest fișier ca `tone/stil-scris-<nume-client>.md`, umple secțiunile
  cu tiparele reale din scrisul/vorbirea clientului, apoi actualizează referința în
  `.claude/skills/substack-article-writer` să pointeze spre noul fișier.
sursa:
  - "acest fișier e generat manual, doar ca ilustrare — într-un proiect real e generat de skill-ul `writing-style-client`"
persona_fictiva: "Jane Doe — skincare & makeup creator, audiență: femei 40+"
status: EXEMPLU, nu se folosește în producție
---

# Stil de scriere — Jane Doe (EXEMPLU FICTIV)

> Acest fișier e o mostră cu date inventate. Arată STRUCTURA pe care trebuie să o completezi
> pentru clientul tău real — nu conținutul propriu-zis.

Ghid scurt de STIL (nu de personalitate/psihologie). Spune cum scrie persoana, nu cine e.
Articolul de Substack e locul unde transformăm vorbire spontană (transcript) în proză scrisă —
de-aia are nevoie de un reper persistent. Pentru orice altceva (Instagram, TikTok, YouTube,
Pinterest), sursa vocii ar trebui să fie transcript-ul curent, nu acest fișier.

---

## 1. Deschiderea

Cum își deschide de obicei materialele? (mit greșit corectat? o întrebare retorică? o statistică?)

**Formula (exemplu fictiv):** "Everyone tells you to buy more products… here's why that's the opposite of what your skin needs."

**Aplicare:** primul paragraf trebuie să urmeze acest tipar de deschidere, nu un rezumat generic tip "In this article we'll talk about...".

---

## 2. Sursa de autoritate

Vorbește din experiență personală directă? Citează studii? Citează clienți?

**Aplicare:** persoana I / III, în funcție de ce ai identificat în sample-urile reale.

---

## 3. Legătura tehnică → filozofie

Sfaturile concrete se leagă de un principiu mai mare, repetat?

**Tagline fix (exemplu fictiv):** *"Simple skin. Real glow."* — dacă persoana ta reală are o frază-semnătură, notează-o aici exact cum o spune, nu parafrazată.

---

## 4. Adresare

Persoana I, a II-a, a III-a? Formal sau casual?

---

## 5. Ritmul propozițiilor

- Propoziții scurte / lungi — ce pattern domină?
- Punctuație caracteristică (puncte de suspensie, exclamări, liste)?
- Lungimea tipică a paragrafelor?

---

## 6. Structura tipică a unei piese de conținut

Exemplu fictiv: **problemă → de ce nu funcționează varianta veche → soluție pas cu pas → concluzie-principiu → invitație caldă la acțiune**

---

## 7. Vocabular preferat

Cuvinte/expresii care revin des, termeni tehnici pe care îi folosește firesc.

## 8. Ce evită

Superlative goale, vânzare agresivă, generalizări abstracte, orice cadru care nu se potrivește vocii clientului.

---

## Cum se folosește acest fișier

1. Copiază-l: `tone/stil-scris-<nume-client>.md`
2. Umple fiecare secțiune cu tipare reale, extrase din sample-uri de scris/vorbire ale clientului (poți folosi skill-ul `writing-style-client` ca punct de plecare — el a fost construit pentru client, dar logica de extragere e reutilizabilă)
3. În `.claude/skills/substack-article-writer`, actualizează calea către noul fișier
4. Fișierul cu date reale rămâne local, exclus din Git (vezi `.gitignore`)
