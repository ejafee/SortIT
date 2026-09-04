# SortIt — AI-Powered Waste Classification

> *Scan your waste. Save the planet. ♻️*

Mobile-friendly web app that identifies waste from a camera photo and tells you how to dispose of it properly. Hackathon submission — team of 4, Sep 1–20.

---

## What it is

Web-based app where you point your camera at a waste item and get instant AI classification + disposal instructions. Built for Malaysia & Indonesia.

## Problem

Improper waste disposal → recyclables end up in landfills. No simple tool guides everyday users on correct sorting.

## Target Users

- General public in Malaysia & Indonesia
- Language: English
- Platform: web, mobile-friendly

## How it works

1. Take photo via camera
2. AI classifies waste (`plastic` / `paper` / `glass` / `organic` / `ewaste` / `hazardous` / `unknown`)
3. Show disposal steps + tip + confidence + gamified XP/badges

## SDG Alignment

- **SDG 11** Sustainable Cities & Communities
- **SDG 12** Responsible Consumption & Production
- **SDG 13** Climate Action

## Features

**MVP (built):**

- Camera-only capture (upload disabled to prevent fake photos)
- Gemini Vision classification
- Result: name, type, detail, confidence bar, instructions, tip
- Playful UI with XP bar & badges
- Disclaimer: guidance only

**Bonus (planned):**

- Nearby recycling centers map (Google Maps API)
- Per-user scan history
- Stats dashboard
- Result caching to save quota

## Tech Stack (as built)

**Frontend:** plain `frontend/index.html` — HTML/CSS/JS, no framework, `fetch('http://localhost:5000/analyze')`

**Backend:** Python Flask — `backend/app.py`, `google-genai` (`from google import genai`, model `gemini-3.6-flash`), `POST /analyze` + `GET /`

**Packages:** `flask`, `flask-cors`, `google-genai`, `python-dotenv`

**Planned originally:** React or plain HTML/CSS/JS, Flask or Node.js, Gemini Vision free tier, Google Maps API, Vercel/Netlify + Render, GitHub.

## Folder Structure

```
sortit/
├── frontend/
│   └── index.html
├── backend/
│   ├── app.py
│   └── .env              # GEMINI_API_KEY — gitignored, never commit
├── .gitignore
└── README.md
```

## Gemini JSON Response

```json
{
  "waste_type": "plastic|paper|glass|organic|ewaste|hazardous|unknown",
  "waste_name": "Plastic Bottle",
  "waste_detail": "Type 2 HDPE Plastic",
  "confidence": 91,
  "instructions": ["step 1", "step 2", "step 3"],
  "tip": "one useful tip"
}
```

## Run Locally

```bash
cd backend
# create .env with GEMINI_API_KEY=...
python app.py          # http://localhost:5000
# open frontend/index.html in browser
```

> Correct import is `from google import genai` (not `google.generativeai` — deprecated). `.env` is gitignored.

## Team Roles (4)

1. AI Integration & Prompt Engineering (AI major)
2. AI Testing, Accuracy & Waste Content DB (AI major)
3. Research, DB & Recycling Center Data (IS major)
4. Lead Frontend & Backend (SE major)

## Risks & Mitigations

- API rate limit → use free tier wisely, cache repeats
- Low accuracy → manual override option
- Time crunch → MVP first, bonus optional

## Evaluation Criteria

Innovation, Technical Implementation, UX (one-click scan), SDG alignment, Impact in SEA.

## What's Left

Deploy (Vercel/Netlify + Render), Maps integration, history, dashboard, caching.

---

*SortIt Team | Hackathon | Sep 2026*
