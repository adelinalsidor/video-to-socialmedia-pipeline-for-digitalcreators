---
name: upload-drive
description: >
  Uploadează postările din postari/ pe Google Drive într-o structură flat
  cu config.json per postare. Propune timpi de postare și triggerează n8n.
  Triggere: "uploadează pe drive", "upload drive", "pune pe drive",
  "upload postări", "programează postări pe drive".
---

# Upload Drive

## Scop
Uploadează postările generate din `postari/` pe Google Drive într-o structură flat pe care n8n o poate citi. Fiecare postare primește un `config.json` cu interfață fixă care dictează ce, când și cum se postează.

## Cum să invoci

```
uploadează pe drive
upload drive postari/claude-code-vs-chatgpt-automatizari/
pune pe drive
upload postări
programează postări pe drive
```

## Workflow

### ETAPA 1: Validare .env

Verifică prezența celor 4 variabile în `.env`:

1. **GOOGLE_DRIVE_FOLDER_ID** — Dacă lipsește, folosește `AskUserQuestion`:
   - "Care e ID-ul folderului din Google Drive unde vrei să uploadez postările?"
   - Ajutor: "Îl găsești în URL-ul folderului: https://drive.google.com/drive/folders/FOLDER_ID"

2. **N8N_WEBHOOK_URL** — Dacă lipsește, folosește `AskUserQuestion`:
   - "Care e URL-ul webhook-ului n8n? (opțional — lasă gol dacă nu folosești)"

3. **GOOGLE_CREDENTIALS_PATH** — Dacă lipsește, folosește `AskUserQuestion`:
   - "Unde se află fișierul credentials.json pentru Google Drive API?"
   - Ajutor: "Creează-l din Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client ID (Desktop app)"

4. **TIMEZONE** — Dacă lipsește, setează default `Europe/Bucharest`. Folosește `AskUserQuestion` doar dacă utilizatorul a menționat alt timezone.

După ce primește răspunsurile, **adaugă variabilele în `.env`** (fără a le suprascrie pe cele existente).

### ETAPA 2: Autentificare Google Drive

1. Citește `GOOGLE_CREDENTIALS_PATH` din `.env`
2. Verifică dacă `token.json` există lângă `credentials.json`
3. Dacă nu există sau e expirat, rulează:
   ```bash
   python3 .claude/skills/upload-drive/scripts/setup_drive_auth.py
   ```
4. Dacă auth eșuează, folosește `AskUserQuestion` să ghideze utilizatorul prin setup-ul OAuth2:
   - "Autentificarea Google Drive a eșuat. Ai configurat OAuth2 în Google Cloud Console?"
   - Opțiuni: "Da, am credentials.json" | "Nu, trebuie să configurez" | "Am altă problemă"

### ETAPA 3: Scanare postari/

Rulează scanarea automată a tuturor topic-urilor din `postari/`:
- Parcurge recursiv fiecare topic → platformă → post .md
- Parsează frontmatter YAML
- Extrage caption (ZONA A — text între end-of-frontmatter și `## Note Editoriale`)
- Colectează fișierele media din folderul corespunzător slug-ului

### ETAPA 4: Filtrare

Skip postări care NU sunt ready:
- `image_status` != `ready` (pentru posturi cu imagini)
- `video_status` != `ready` (pentru posturi video)
- `audio_status` != `ready` (pentru posturi audio)
- Fără niciun fișier media în folder

### ETAPA 5: Parsare caption

Pentru fiecare post eligibil, extrage **ZONA A** din MD:
- Textul între sfârșitul frontmatter-ului (`---`) și `## Note Editoriale`
- Include hashtag-urile din text (nu doar din frontmatter)
- Acesta devine câmpul `caption` din config.json

### ETAPA 6: Calcul scheduling

Propune timpi de postare pe baza regulilor din `references/scheduling-rules.md`:
1. Grupează postările pe platformă
2. Atribuie sloturi respectând:
   - Ore optime weekday/weekend per platformă
   - Spacing minim între postări pe aceeași platformă
   - Max postări/zi/platformă
   - Max total postări/zi (8)
3. Distribuie pe mai multe zile (nu totul în aceeași zi)
4. Începe schedulingul de mâine

Rulează dry-run pentru preview:
```bash
python3 .claude/skills/upload-drive/scripts/upload_to_drive.py \
  --postari-dir ./postari --dry-run
```

### ETAPA 7: Confirmare auto_post

Folosește `AskUserQuestion` pentru a întreba:
- **Întrebare:** "Vrei auto_post activat pe toate postările?"
- **Opțiuni:**
  - **Da (automat)** — n8n postează automat la ora programată
  - **Nu (cu confirmare)** — n8n trimite notificare și așteaptă aprobare
  - **Mixt** — setează auto_post per platformă (întreabă separat)

### ETAPA 8: Preview + confirmare

Afișează tabel sumar cu toate postările, timpii propuși și media:

```
┌──────────────┬────────────────────────────────────────┬──────────────┬────────┬─────────────────────┐
│ Platformă    │ Slug                                   │ Tip          │ Media  │ Scheduled           │
├──────────────┼────────────────────────────────────────┼──────────────┼────────┼─────────────────────┤
│ linkedin     │ chatgpt-tool-gresit-automatizari       │ single-image │ 1      │ 2026-03-03T08:00    │
│ instagram    │ carousel-4-pasi-chatgpt-la-claude-code │ carousel     │ 5      │ 2026-03-03T11:00    │
│ tiktok-reels │ 4-ore-vs-10-minute-inventar            │ video        │ 1      │ 2026-03-04T12:00    │
└──────────────┴────────────────────────────────────────┴──────────────┴────────┴─────────────────────┘
```

Folosește `AskUserQuestion`:
- **Întrebare:** "Confirmi upload-ul pe Google Drive?"
- **Opțiuni:**
  - **Confirmă upload** — pornește upload-ul
  - **Vreau să ajustez timpii** — întreabă care postări trebuie mutate
  - **Anulează** — oprește procesul

### ETAPA 9: Upload + Webhook

Rulează upload-ul efectiv:
```bash
python3 .claude/skills/upload-drive/scripts/upload_to_drive.py \
  --postari-dir ./postari --auto-post
```

Scriptul:
1. Se autentifică cu Google Drive
2. Listează folderele existente → calculează next counter (NNNNN)
3. Pentru fiecare post:
   - Verifică duplicate (skip dacă slug+platform există deja)
   - Creează folder `NNNNN-slug-platform`
   - Uploadează `config.json` cu schema fixă
   - Uploadează `cover.png` + media adițională
4. Trimite webhook POST la N8N_WEBHOOK_URL cu `{"drive_folder_id": "..."}`
5. Afișează raport final JSON

## Schema config.json (interfață fixă)

```json
{
  "platform": "linkedin",
  "post_type": "single-image",
  "status": "pending",
  "auto_post": false,
  "scheduled_time": "2026-03-03T09:00:00+02:00",
  "posted_at": null,
  "caption": "Textul complet al postării...",
  "hashtags": ["#ClaudeCode", "#ChatGPT"],
  "cover_image": "cover.png",
  "media_files": [],
  "video_file": null,
  "audio_file": null
}
```

**post_type:** `single-image` | `carousel` | `video` | `audio`
**status:** `pending` | `posted` | `failed`

## Structura pe Drive (flat)

```
[GOOGLE_DRIVE_FOLDER_ID]/
├── 00001-chatgpt-tool-gresit-automatizari-linkedin/
│   ├── config.json
│   └── cover.png
├── 00002-carousel-4-pasi-chatgpt-la-claude-code-instagram/
│   ├── config.json
│   ├── cover.png
│   ├── 01.png ... 04.png
├── 00003-4-ore-vs-10-minute-inventar-tiktok-reels/
│   ├── config.json
│   ├── cover.png
│   └── video.mp4
```

## Dependențe

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

## Re-run Behavior

La re-run pe aceleași postări:
1. Listează folderele existente pe Drive
2. Skip postări care au deja folder (slug+platform match)
3. Uploadează doar postările noi
4. Counter-ul continuă de la max(existent) + 1
