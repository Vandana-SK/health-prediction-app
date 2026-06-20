"""Server-side input validation for patient records.

Validation is enforced on the backend (in addition to HTML5 client-side hints)
so that bad data can never reach the database, regardless of the client.
"""
from datetime import date, datetime
from email_validator import EmailNotValidError, validate_email


def validate_patient_form(form):
    """Validate raw form data.

    Returns a tuple ``(data, errors)`` where ``data`` is a dict of cleaned
    values and ``errors`` is a dict mapping field name -> error message.
    """
    data = {}
    errors = {}

    # Full name
    full_name = (form.get("full_name") or "").strip()
    if not full_name:
        errors["full_name"] = "Full name is required."
    elif len(full_name) < 2:
        errors["full_name"] = "Full name must be at least 2 characters."
    data["full_name"] = full_name

    # Date of birth — required, valid date, not in the future
    dob_raw = (form.get("date_of_birth") or "").strip()
    if not dob_raw:
        errors["date_of_birth"] = "Date of birth is required."
    else:
        try:
            dob = datetime.strptime(dob_raw, "%Y-%m-%d").date()
            if dob > date.today():
                errors["date_of_birth"] = "Date of birth cannot be in the future."
            else:
                data["date_of_birth"] = dob
        except ValueError:
            errors["date_of_birth"] = "Enter a valid date (YYYY-MM-DD)."

    # Email — must be a valid format
    email = (form.get("email") or "").strip()
    if not email:
        errors["email"] = "Email is required."
    else:
        try:
            validate_email(email, check_deliverability=False)
            data["email"] = email
        except EmailNotValidError:
            errors["email"] = "Enter a valid email address."

    # Numeric blood-test fields — must be numeric and within a sane range
    for field, label, low, high in [
        ("glucose", "Glucose", 20, 600),
        ("haemoglobin", "Haemoglobin", 2, 25),
        ("cholesterol", "Cholesterol", 50, 600),
    ]:
        raw = (form.get(field) or "").strip()
        if not raw:
            errors[field] = f"{label} is required."
            continue
        try:
            value = float(raw)
        except ValueError:
            errors[field] = f"{label} must be a number."
            continue
        if not (low <= value <= high):
            errors[field] = f"{label} must be between {low} and {high}."
        else:
            data[field] = value

    return data, errors
