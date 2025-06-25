from datetime import datetime
from app import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), unique=True, nullable=False)
    process_files = db.relationship(
        "ProcessFile", backref="user", cascade="all, delete"
    )


class Patient(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(120), nullable=False)
    mr_number = db.Column(db.String(50), unique=True, nullable=False)
    created_by = db.Column(db.String(120), nullable=False)
    process_files = db.relationship(
        "ProcessFile", backref="patient", cascade="all, delete"
    )


class ProcessFile(db.Model):
    __tablename__ = "process_files"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)

    user_email = db.Column(
        db.String(120), db.ForeignKey("users.user_email"), nullable=False
    )

    patient_mr_number = db.Column(
        db.String(50), db.ForeignKey("patients.mr_number"), nullable=False
    )

    processing_status = db.Column(db.String(50), default="pending")
    hpv_percentage = db.Column(db.Float)
    no_hpv_percentage = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.now)
