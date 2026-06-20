"""Train the custom health-risk ML model.

The task allows a "custom ML model" for the prediction step. Because real
labelled patient data is not available (and would be sensitive), we generate a
synthetic dataset grounded in well-known clinical reference ranges, then train a
RandomForest classifier to predict an overall health-risk category:

    0 = Low risk, 1 = Moderate risk, 2 = High risk

The clinical scoring used to label the synthetic data is intentionally simple
and transparent so the model's behaviour is easy to reason about.

Run directly to (re)generate ``health_model.pkl``:

    python -m ml.train_model
"""
import os

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "health_model.pkl")

# Reference ranges used to build the synthetic labels (typical adult values).
# Glucose (fasting, mg/dL): normal < 100, prediabetes 100-125, diabetes >= 126
# Haemoglobin (g/dL): low (anaemia) < 12, normal 12-17, high > 17
# Cholesterol (total mg/dL): desirable < 200, borderline 200-239, high >= 240


def _risk_score(age, glucose, haemoglobin, cholesterol):
    """Return an integer risk score from individual clinical markers."""
    score = 0

    # Glucose
    if glucose >= 126:
        score += 2
    elif glucose >= 100:
        score += 1

    # Haemoglobin (anaemia or polycythaemia both add risk)
    if haemoglobin < 11 or haemoglobin > 18:
        score += 2
    elif haemoglobin < 12 or haemoglobin > 17:
        score += 1

    # Cholesterol
    if cholesterol >= 240:
        score += 2
    elif cholesterol >= 200:
        score += 1

    # Age is a mild compounding factor
    if age >= 60:
        score += 1

    return score


def _score_to_category(score):
    if score >= 4:
        return 2  # High
    if score >= 2:
        return 1  # Moderate
    return 0  # Low


def generate_dataset(n_samples=6000, seed=42):
    """Create a synthetic, clinically-grounded training dataset."""
    rng = np.random.default_rng(seed)

    age = rng.integers(18, 90, n_samples)
    glucose = rng.normal(105, 30, n_samples).clip(60, 300)
    haemoglobin = rng.normal(14, 2.2, n_samples).clip(6, 22)
    cholesterol = rng.normal(195, 40, n_samples).clip(110, 350)

    X = np.column_stack([age, glucose, haemoglobin, cholesterol])
    y = np.array(
        [
            _score_to_category(_risk_score(a, g, h, c))
            for a, g, h, c in X
        ]
    )

    # Add a little label noise so the model has to generalise rather than
    # memorise the exact thresholds.
    flip = rng.random(n_samples) < 0.05
    y[flip] = rng.integers(0, 3, flip.sum())

    return X, y


def train_and_save():
    X, y = generate_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200, max_depth=8, random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    joblib.dump(model, MODEL_PATH)

    print(f"Model trained. Hold-out accuracy: {acc:.3f}")
    print(f"Saved to: {MODEL_PATH}")
    return model


if __name__ == "__main__":
    train_and_save()
