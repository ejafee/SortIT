# SortIt ♻️ — AI-Powered Waste Classification Web App

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)](https://ai.google.dev/)

> **"Scan your waste. Save the planet."**  
> A mobile-friendly web application that accurately identifies waste types from camera captures using Google Gemini Vision, providing localized disposal and recycling instructions for communities across Malaysia and Indonesia.

---

## Problem & Impact

Improper waste management in Southeast Asia leads to recyclable materials filling up landfills. Everyday consumers often lack accessible, instant guidance on correct segregation. **SortIt** bridges this gap by turning any smartphone camera into an intelligent recycling assistant aligned with:

- **SDG 11:** Sustainable Cities and Communities
- **SDG 12:** Responsible Consumption and Production
- **SDG 13:** Climate Action

---

## Key Features

- **Camera-Only Capture:** Live camera capture flow designed to encourage real-world waste scanning.
- **Gemini AI Classification:** Vision-based classification across 7 categories (`plastic`, `paper`, `glass`, `organic`, `ewaste`, `hazardous`, `unknown`).
- **Confidence Scoring & Threshold Alerts:** Transparent model-reported accuracy percentage, displaying warning banners if below threshold (<60%).
- **Manual Correction & Feedback Loop:** Users can suggest corrections which are logged to an audit trail (`POST /correct`) for dataset improvement.
- **Scan History & Stats Dashboard:** Client-side scan log and breakdown chart (backed by an abstracted storage interface).
- **Production-Grade Architecture:** Custom exception hierarchy, typed Python backend, structured rotating file logging, and comprehensive `pytest` test suite.

---

## Architecture & Folder Structure

```
SortIT/
├── LICENSE
├── README.md
├── .gitignore                      # Ignores internal docs/ and cache
├── frontend/
│   ├── index.html                  # Semantic UI shell with tab navigation
│   ├── css/
│   │   └── style.css               # Responsive design & gamified styles
│   └── js/
│       ├── app.js                  # Application bootstrap & event listeners
│       ├── api.js                  # Fetch wrapper for /analyze and /correct
│       ├── ui.js                   # DOM rendering, state & error handling
│       ├── storage.js              # Storage interface & localStorage adapter
│       └── stats.js                # History log and dynamic category charts
└── backend/
    ├── app.py                      # Flask routes (/analyze, /correct, /)
    ├── classifier.py               # Gemini Vision client & schema validation
    ├── exceptions.py               # Typed custom exception hierarchy
    ├── logging_config.py           # RotatingFileHandler logging setup
    ├── storage_interface.py        # Abstract Base Class for audit backends
    ├── requirements.txt            # Pinned dependencies
    ├── pytest.ini                  # Test configuration
    ├── .env.example                # Configuration template
    ├── .env                        # Local secrets (gitignored)
    ├── logs/                       # Rotating app logs & audit trail (gitignored)
    └── tests/
        ├── test_exceptions.py      # Exception hierarchy tests
        ├── test_classifier.py      # Schema parser & normalization tests
        └── test_app_routes.py      # Route integration tests (mocked Gemini)
```

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- A modern browser with camera permissions enabled
- A [Google AI Studio Gemini API Key](https://aistudio.google.com/)

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Edit `backend/.env` with your API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Run the backend server:
```bash
python app.py
# Backend runs on http://localhost:5000
```

### 2. Frontend Setup

Since the frontend is built with vanilla HTML/CSS and ES modules, open `frontend/index.html` directly in your browser, or serve it using any static server:

```bash
# Using Python
cd frontend
python -m http.server 3000
# Visit http://localhost:3000
```

---

## Running Tests

SortIt includes unit and integration tests covering the classification parser, typed exception hierarchy, and API routes.

```bash
cd backend
pytest
```

---

## API Contract

### `POST /analyze`
Analyzes a waste image via Gemini Vision.
- **Request:** `multipart/form-data` containing `image` (binary file)
- **Response (200 OK):**
  ```json
  {
    "waste_type": "plastic",
    "waste_name": "PET Bottle",
    "waste_detail": "Type 1 Recyclable Plastic",
    "confidence": 92,
    "instructions": [
      "Rinse bottle thoroughly.",
      "Remove cap and crush.",
      "Place in blue recycling bin."
    ],
    "tip": "Crushing plastic bottles saves space in recycling bins!",
    "below_threshold": false
  }
  ```

### `POST /correct`
Logs an audit record of user-suggested classification overrides.
- **Request (200 OK):**
  ```json
  {
    "original_result": { "waste_type": "plastic", "waste_name": "Bottle" },
    "corrected_waste_type": "glass",
    "note": "Item is actually a glass bottle",
    "timestamp": "2026-09-04T12:00:00Z"
  }
  ```

### `GET /`
Health check and configuration status.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
