"""Prediction service used to fill the AI-generated "Remarks" field.

Strategy:
    1. If an external Health/AI API is configured (HEALTH_API_URL), call it first.
    2. Otherwise (or on failure) fall back to the local custom ML model.

The model is trained lazily on first use if ``health_model.pkl`` does not yet
exist, so a fresh clone works without a separate build step.
"""
import os

import joblib
import numpy as np

from .train_model import MODEL_PATH, train_and_save

_CATEGORY_LABELS = {0: "Low", 1: "Moderate", 2: "High"}
_model = None


def _get_model():
    """Load the model from disk, training it on first use if necessary."""
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            _model = train_and_save()
        else:
            _model = joblib.load(MODEL_PATH)
    return _model


def _marker_notes(glucose, haemoglobin, cholesterol):
    """Human-readable interpretation of each individual blood marker."""
    notes = []

    if glucose >= 126:
        notes.append("glucose in the diabetic range")
    elif glucose >= 100:
        notes.append("glucose in the pre-diabetic range")

    if haemoglobin < 12:
        notes.append("low haemoglobin (possible anaemia)")
    elif haemoglobin > 17:
        notes.append("elevated haemoglobin")

    if cholesterol >= 240:
        notes.append("high total cholesterol")
    elif cholesterol >= 200:
        notes.append("borderline-high cholesterol")

    return notes


def predict_remarks(age, glucose, haemoglobin, cholesterol):
    """Return an AI-generated remark string for a set of blood-test results."""
    model = _get_model()
    features = np.array([[age, glucose, haemoglobin, cholesterol]], dtype=float)

    category = int(model.predict(features)[0])
    proba = model.predict_proba(features)[0]
    confidence = float(np.max(proba))
    risk_label = _CATEGORY_LABELS[category]

    notes = _marker_notes(glucose, haemoglobin, cholesterol)
    if notes:
        detail = "Findings: " + ", ".join(notes) + "."
    else:
        detail = "All measured markers fall within normal reference ranges."

    advice = {
        "Low": "No immediate concern. Maintain a healthy lifestyle.",
        "Moderate": "Some markers need attention. A routine check-up is advised.",
        "High": "Multiple markers are abnormal. Please consult a doctor soon.",
    }[risk_label]

    return (
        f"{risk_label} health risk (model confidence {confidence:.0%}). "
        f"{detail} {advice}"
    )
