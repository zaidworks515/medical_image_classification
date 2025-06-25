from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Patient, ProcessFile

routes = Blueprint("routes", __name__)


@routes.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        user_email = data.get("user_email")

        if not user_email:
            return jsonify({"error": "user_email is required"}), 400

        existing_user = User.query.filter_by(user_email=user_email).first()
        if existing_user:
            return (
                jsonify({"error": "User already exists", "id": existing_user.id}),
                409,
            )

        user = User(user_email=user_email)
        db.session.add(user)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "User created, Please use the same user_email to signin",
                    "id": user.id,
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify({"error": e}),
            500,
        )


@routes.route("/signin", methods=["POST"])
def sign_in():
    try:
        data = request.get_json()
        user_email = data.get("user_email")

        if not user_email:
            return jsonify({"error": "user_email is required"}), 400

        user = User.query.filter_by(user_email=user_email).first()
        if not user:
            return jsonify({"error": "User does not exist"}), 404

        return (
            jsonify(
                {
                    "message": "Sign-in successful",
                    "id": user.id,
                    "user_email": user.user_email,
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify({"error": e}),
            500,
        )


@routes.route("/create_patient", methods=["POST"])
def create_patient():
    try:
        data = request.get_json()
        name = data.get("patient_name")
        mr = data.get("mr_number")
        user_email = data.get("user_email")

        if not name or not mr:
            return jsonify({"error": "Missing patient name or MR number"}), 400
        elif not user_email:
            return jsonify({"error": "Missing user user_email/id."}), 400

        existing_patient = Patient.query.filter_by(mr_number=mr).first()
        if existing_patient:
            return (
                jsonify(
                    {
                        "message": "Patient with this MR number already exists.",
                        "id": existing_patient.id,
                    }
                ),
                200,
            )

        patient = Patient(patient_name=name, mr_number=mr, created_by=user_email)
        db.session.add(patient)
        db.session.commit()

        return jsonify({"message": "Patient created", "id": patient.id}), 200

    except Exception as e:
        return (
            jsonify({"error": e}),
            500,
        )


@routes.route("/get_patients", methods=["GET"])
def get_patients():
    try:
        # data = request.get_json()
        user_email = request.args.get("user_email")

        if not user_email:
            return jsonify({"error": "Missing user_email"}), 400

        patients = Patient.query.filter_by(created_by=user_email).all()
        if patients:

            return jsonify(
                [
                    {"id": p.id, "name": p.patient_name, "mr_number": p.mr_number}
                    for p in patients
                ]
            )
        else:
            return (
                jsonify({"error": "No associated patients found, please create one."}),
                404,
            )

    except Exception as e:
        return (
            jsonify({"error": e}),
            500,
        )


@routes.route("/get_all_process_files", methods=["GET"])
def get_all_process_files():
    try:
        data = request.get_json()
        user_email = data.get("user_email")
        mr_number = data.get("mr_number", None)

        if not user_email:
            return jsonify({"message": "user_email is required"}), 400

        user = User.query.filter_by(user_email=user_email).first()
        if not user:
            return jsonify({"message": "User not found"}), 404

        if mr_number:
            process_files = ProcessFile.query.filter_by(
                user_email=user.id, patient_mr_number=mr_number
            ).all()
        else:
            process_files = ProcessFile.query.filter_by(user_email=user.id).all()

        result = [
            {
                "id": pf.id,
                "filename": pf.filename,
                "patient_mr_number": pf.patient_mr_number,
                "processing_status": pf.processing_status,
                "hpv_percentage": pf.hpv_percentage,
                "no_hpv_percentage": pf.no_hpv_percentage,
                "timestamp": pf.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for pf in process_files
        ]

        return jsonify(result), 200

    except Exception as e:
        return (
            jsonify({"error": e}),
            500,
        )
