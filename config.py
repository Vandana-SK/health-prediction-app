"""Application configuration.

All sensitive values are read from environment variables so that no secrets
are committed to source control. Sensible local-development defaults are used
when the variables are not set.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # SECRET_KEY is used by Flask for session / flash-message signing.
    # Override it in production via an environment variable.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")

    # SQLite database stored under the instance/ folder.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "patients.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Optional: URL of an external Health/AI API. If set, the app will try it
    # first and fall back to the local ML model when it is unavailable.
    HEALTH_API_URL = os.environ.get("HEALTH_API_URL")
