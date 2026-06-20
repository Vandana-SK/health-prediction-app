"""MIRA Health Prediction — Flask application.

A small full-stack CRUD application that stores patient blood-test results and
uses a custom ML model to generate an AI "Remarks" health-risk prediction.
"""
import os

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from config import Config
from models import Patient, db
from validators import validate_patient_form
from ml.predict import predict_remarks


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


def _generate_remarks(patient):
    """Call the prediction service and store the result on the patient."""
    try:
        patient.remarks = predict_remarks(
            patient.age, patient.glucose, patient.haemoglobin, patient.cholesterol
        )
    except Exception as exc:  # never let prediction failure block a save
        patient.remarks = f"Prediction unavailable ({exc.__class__.__name__})."


def register_routes(app):
    # ---- Read: list all patients ----------------------------------------
    @app.route("/")
    def index():
        patients = Patient.query.order_by(Patient.created_at.desc()).all()
        return render_template("index.html", patients=patients)

    # ---- Read: single patient detail ------------------------------------
    @app.route("/patient/<int:patient_id>")
    def detail(patient_id):
        patient = db.session.get(Patient, patient_id) or abort(404)
        return render_template("detail.html", patient=patient)

    # ---- Create ---------------------------------------------------------
    @app.route("/patient/new", methods=["GET", "POST"])
    def create():
        if request.method == "POST":
            data, errors = validate_patient_form(request.form)
            if errors:
                return render_template(
                    "form.html", errors=errors, form=request.form, mode="create"
                )
            patient = Patient(**data)
            _generate_remarks(patient)
            db.session.add(patient)
            db.session.commit()
            flash("Patient record created and analysed successfully.", "success")
            return redirect(url_for("index"))
        return render_template("form.html", errors={}, form={}, mode="create")

    # ---- Update ---------------------------------------------------------
    @app.route("/patient/<int:patient_id>/edit", methods=["GET", "POST"])
    def update(patient_id):
        patient = db.session.get(Patient, patient_id) or abort(404)
        if request.method == "POST":
            data, errors = validate_patient_form(request.form)
            if errors:
                return render_template(
                    "form.html",
                    errors=errors,
                    form=request.form,
                    mode="edit",
                    patient=patient,
                )
            for key, value in data.items():
                setattr(patient, key, value)
            _generate_remarks(patient)  # re-run prediction on updated values
            db.session.commit()
            flash("Patient record updated and re-analysed.", "success")
            return redirect(url_for("index"))

        # Pre-fill the form with the existing record.
        form = patient.to_dict()
        return render_template(
            "form.html", errors={}, form=form, mode="edit", patient=patient
        )

    # ---- Delete ---------------------------------------------------------
    @app.route("/patient/<int:patient_id>/delete", methods=["POST"])
    def delete(patient_id):
        patient = db.session.get(Patient, patient_id) or abort(404)
        db.session.delete(patient)
        db.session.commit()
        flash("Patient record deleted.", "info")
        return redirect(url_for("index"))

    # ---- Simple JSON API (handy for the demo / testing) -----------------
    @app.route("/api/patients")
    def api_patients():
        return {"patients": [p.to_dict() for p in Patient.query.all()]}


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
