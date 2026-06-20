# MIRA Health Prediction — Full Procedure

A complete, step-by-step account of how this project was designed, built, and
how to run it. Written so the solution can be understood and explained end to end.

---

## 1. Problem statement (Task 1)

Build a Health Prediction application that:

1. Collects per patient: Full Name, Date of Birth, Email, Glucose, Haemoglobin,
   Cholesterol, and an AI-generated **Remarks** value.
2. Supports full **CRUD** (Create, Read, Update, Delete).
3. Has a clean, user-friendly **UI**.
4. **Validates** input (valid email, no future DOB, numeric blood values).
5. Uses **persistent storage** (a database).
6. Calls an **AI/ML model/API** to predict a health condition and writes the
   result into the **Remarks** field.

---

## 2. Technology choices (and why)

| Layer     | Choice                       | Why                                                                |
|-----------|-------------------------------|----------------------------------------------------------------------|
| Backend    | **Flask** (Python)             | Lightweight; clear split between backend logic and templates.       |
| Database    | **SQLite + SQLAlchemy ORM**     | Zero-config persistence; no DB server to install.                  |
| Frontend     | **Bootstrap 5 + Jinja2**         | Clean responsive UI with minimal custom CSS.                       |
| AI / ML       | **scikit-learn (custom model)**   | Task allows a custom model; needs no API key (nothing secret to leak). |

A hook for an external Health API is also included (`HEALTH_API_URL`): if set, it
is tried first and the local model is the fallback.

---

## 3. Architecture / data flow

```
Browser (Bootstrap UI)
        | submits form
        v
Flask routes (app.py)
        | raw form data
        v
validators.py  --->  rejects bad input, returns clean data
        | valid data
        v
ml/predict.py  --->  loads RandomForest model, returns Remarks text
        | Patient object (+ remarks)
        v
SQLAlchemy (models.py)  --->  SQLite database (instance/patients.db)
```

---

## 4. How each requirement is met

- **CRUD** — routes in `app.py`:
  - Create: `GET/POST /patient/new`
  - Read: `GET /` (list) and `GET /patient/<id>` (detail) + `GET /api/patients` (JSON)
  - Update: `GET/POST /patient/<id>/edit`
  - Delete: `POST /patient/<id>/delete`
- **UI** — `templates/` with a shared `base.html`, a list table, an add/edit form,
  and a detail page; styled with Bootstrap 5 + `static/style.css`.
- **Validation** — `validators.py` runs on the server for every Create/Update:
  required fields, email format (`email-validator`), DOB not in the future and a
  real date, blood values numeric and within sane medical ranges.
- **Persistent storage** — `models.py` defines the `Patient` table; SQLAlchemy
  stores it in SQLite at `instance/patients.db`.
- **AI/ML prediction** — `ml/train_model.py` trains a RandomForest on a synthetic,
  clinically-grounded dataset; `ml/predict.py` runs it and composes a readable
  remark; `app.py` saves that text into the `Remarks` column.

---

## 5. How the ML model works

1. **Training data** (`ml/train_model.py`): 6,000 synthetic patients are generated
   with realistic value distributions. Each is labelled Low / Moderate / High risk
   using transparent clinical rules:
   - Glucose ≥126 diabetic, 100–125 pre-diabetic.
   - Haemoglobin <12 anaemia, >17 elevated.
   - Cholesterol ≥240 high, 200–239 borderline.
   - Age ≥60 adds mild risk.
   A little label noise (5%) is added so the model generalises.
2. **Model**: a `RandomForestClassifier` (200 trees) is trained; ~95% hold-out
   accuracy. Saved to `ml/health_model.pkl`.
3. **Prediction** (`ml/predict.py`): given age + the three blood markers, the model
   returns a risk category and confidence; the code adds per-marker notes and
   advice to build the final Remarks string.
4. The model trains automatically on first run if the `.pkl` file is missing.

---

## 6. Setup & run procedure

```powershell
# 1. Go to the project folder
cd C:\Users\<you>\mira-health-prediction

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate it (Windows PowerShell)
.\.venv\Scripts\activate
# If activation is blocked, run once:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 4. Install dependencies
pip install -r requirements.txt

# 5. (optional) copy the env template
copy .env.example .env

# 6. Run the app
python app.py

# 7. Open in a browser
# http://127.0.0.1:5000

# 8. Stop the server: press Ctrl + C
```

To (re)train the ML model manually:

```powershell
python -m ml.train_model
```

---

## 7. How to use the app

1. Open http://127.0.0.1:5000 — you see the patient list (empty at first).
2. Click **+ New Patient**, fill the form, click **Create & Analyse**.
3. The AI Remarks are generated and the record appears in the list.
4. Click a name to **view** details, **Edit** to update (Remarks re-calculate),
   or **Delete** to remove (with a confirm prompt).

---

## 8. Security / submission notes

- No passwords or API keys are committed. Secrets come from environment variables
  (`.env`, which is git-ignored). `.env.example` documents the expected keys.
- The SQLite DB and the trained model artifact are git-ignored.
- This is a technical demo — predictions are **not** medical advice.
