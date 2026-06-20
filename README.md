# MIRA — Health Prediction Application

A small full-stack web application that stores patient blood-test results,
performs full **CRUD**, validates input, persists data in **SQLite**, and uses a
**custom machine-learning model** to generate an AI **"Remarks"** health-risk
prediction for each record.

Built as Task 1 for the Junior AI/ML Developer assessment (MIRA — Medical
Intelligence Robotic Automation scenario).

---

## Features

| Requirement          | Implementation                                                         |
|-----------------------|-------------------------------------------------------------------------|
| CRUD operations        | Create / Read / Update / Delete patient records                        |
| User interface          | Bootstrap 5 responsive UI, clean list + form + detail views            |
| Data validation         | Server-side validation (email format, no future DOB, numeric markers)  |
| Persistent storage       | SQLite via SQLAlchemy ORM                                              |
| AI/ML integration        | Custom scikit-learn RandomForest model fills the "Remarks" field       |

### Data captured per patient
Full Name · Date of Birth · Email · Glucose · Haemoglobin · Cholesterol · Remarks (AI-generated)

---

## Tech stack & why

- **Flask** — lightweight Python backend; clearly separates backend logic from
  the frontend templates, which makes both halves easy to assess.
- **SQLAlchemy + SQLite** — zero-config persistent storage; no DB server to set up.
- **Bootstrap 5** — clean, responsive UI without hand-writing much CSS.
- **scikit-learn (custom model)** — the task allows a custom ML model. A
  RandomForest is trained on a synthetic, clinically-grounded dataset to classify
  overall health risk (Low / Moderate / High). This avoids shipping any API keys
  while still demonstrating a real ML prediction pipeline.

---

## How the AI prediction works

1. On save, the patient's age (derived from DOB), glucose, haemoglobin and
   cholesterol are fed to the trained model (`ml/predict.py`).
2. The model predicts a risk category and confidence.
3. A human-readable remark is composed from the prediction plus per-marker
   interpretation (e.g. "glucose in the pre-diabetic range").
4. The result is stored in the `Remarks` column and shown in the UI.

The model is defined and trained in `ml/train_model.py` using reference ranges
for glucose, haemoglobin and cholesterol. It trains automatically on first run if
`ml/health_model.pkl` is missing — no separate build step needed.

> An optional external Health/AI API can be plugged in via the `HEALTH_API_URL`
> environment variable; the local model is the default and the fallback.

---

## Setup & run

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (optional) configure environment
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux

# 4. Run
python app.py
```

Then open <http://127.0.0.1:5000>.

To (re)train the model manually:

```bash
python -m ml.train_model
```

---

## Project structure

```
mira-health-prediction/
├── app.py              # Flask app + CRUD routes + JSON API
├── config.py            # Configuration (reads secrets from env vars)
├── models.py             # SQLAlchemy Patient model
├── validators.py          # Server-side input validation
├── ml/
│   ├── train_model.py      # Builds synthetic data + trains RandomForest
│   └── predict.py           # Loads model, generates the AI "Remarks"
├── templates/              # Jinja2 + Bootstrap views
├── static/style.css
├── requirements.txt
├── .env.example            # Template — copy to .env (never committed)
└── .gitignore
```

---

## Security notes

- No passwords or API keys are committed. Secrets are read from environment
  variables (`.env`, which is git-ignored). `.env.example` shows the expected keys.
- The local SQLite database and the trained model artifact are git-ignored.

## Disclaimer

This is a technical demo. The predictions are **not** medical advice and must not
be used for real clinical decisions.
