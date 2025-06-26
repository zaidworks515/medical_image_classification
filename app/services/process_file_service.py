# app/services/process_file_service.py

from app import db
from app.models import ProcessFile
from sqlalchemy import or_


def create_process_file_record(filename, user_email, patient_mr_number):
    existing_file = (
        ProcessFile.query.filter_by(
            filename=filename, patient_mr_number=patient_mr_number
        )
        .filter(
            or_(
                ProcessFile.processing_status == "successful",
                ProcessFile.processing_status == "pending",
            )
        )
        .first()
    )

    if existing_file:
        return {
            "status": "exists",
            "message": "A process file with this filename and MR number already exists with status 'successful' or 'pending'.",
            "id": existing_file.id,
        }

    process_file = ProcessFile(
        filename=filename,
        user_email=user_email,
        patient_mr_number=patient_mr_number,
        processing_status="pending",
        hpv_percentage=None,
        no_hpv_percentage=None,
    )
    db.session.add(process_file)
    db.session.commit()

    return {
        "status": "created",
        "message": "Process file created successfully.",
        "id": process_file.id,
    }
