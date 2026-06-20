"""Database models for the MIRA Health Prediction application."""
from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Patient(db.Model):
    """A single patient record with blood-test results and an AI remark."""

    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), nullable=False)

    # Blood-test results
    glucose = db.Column(db.Float, nullable=False)       # mg/dL
    haemoglobin = db.Column(db.Float, nullable=False)    # g/dL
    cholesterol = db.Column(db.Float, nullable=False)    # mg/dL

    # AI-generated prediction text
    remarks = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @property
    def age(self):
        """Age in whole years, derived from the date of birth."""
        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "date_of_birth": self.date_of_birth.isoformat(),
            "email": self.email,
            "glucose": self.glucose,
            "haemoglobin": self.haemoglobin,
            "cholesterol": self.cholesterol,
            "remarks": self.remarks,
        }

    def __repr__(self):
        return f"<Patient {self.id} {self.full_name}>"
