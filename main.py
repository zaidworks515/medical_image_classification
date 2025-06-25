from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import shutil
import pandas as pd
from config import port, server_ip
from wsi_processing import wsi_processor
from concurrent.futures import ThreadPoolExecutor
from app import create_app, db
from app.services.process_file_service import create_process_file_record
from app.models import ProcessFile

app = create_app()
CORS(app)

BASE_URL = f"http://{server_ip}:{port}/local"
executor = ThreadPoolExecutor(max_workers=4)

CHUNKS_DIR = "temp_chunks"
MERGED_DIR = "svs_data"

os.makedirs(CHUNKS_DIR, exist_ok=True)
os.makedirs(MERGED_DIR, exist_ok=True)


def background_process_wsi(
    folder, user_email, filename, output_path, chunk_folder, patient_mr_number
):
    try:
        with open(output_path, "wb") as output_file:
            chunks = sorted(os.listdir(chunk_folder))
            for chunk_name in chunks:
                chunk_path = os.path.join(chunk_folder, chunk_name)
                with open(chunk_path, "rb") as chunk_file:
                    output_file.write(chunk_file.read())

        shutil.rmtree(os.path.join(CHUNKS_DIR, user_email))

        hpv_count, no_hpv_count, status = wsi_processor(
            folder=folder, user_email=user_email, filename=filename
        )

        hpv_count, no_hpv_count, status = 12, 12, "successful"

        with app.app_context():
            process_file = ProcessFile.query.filter_by(
                filename=filename, patient_mr_number=patient_mr_number
            ).first()

            print("===" * 10)
            print(process_file)
            print("===" * 10)

            if process_file:
                if (hpv_count or no_hpv_count) and (status == "successful"):
                    total_images = hpv_count + no_hpv_count
                    hpv_percentage = (hpv_count / total_images) * 100
                    no_hpv_percentage = (no_hpv_count / total_images) * 100
                    print("======" * 10)
                    print("HPV PERCENTAGE: ", hpv_percentage)
                    print("No HPV PERCENTAGE: ", no_hpv_percentage)
                    print("======" * 10)
                    process_file.hpv_percentage = hpv_percentage
                    process_file.no_hpv_percentage = no_hpv_percentage
                    process_file.processing_status = "completed"
                else:
                    process_file.processing_status = "failed"

                db.session.commit()

    except Exception as e:
        print(f"[ERROR] Background processing failed: {e}")


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "server is up and running."})


@app.route("/upload_chunk", methods=["POST"])
def upload_chunk():
    try:
        file = request.files["file"]
        user_email = request.form["user_email"]
        file_id = request.form["file_id"]
        chunk_index = int(request.form["chunk_index"])

        chunk_folder = os.path.join(CHUNKS_DIR, user_email, file_id)
        os.makedirs(chunk_folder, exist_ok=True)

        chunk_path = os.path.join(chunk_folder, f"{chunk_index:06d}")
        file.save(chunk_path)

        return jsonify({"message": f"Chunk {chunk_index} received."}), 200
    except Exception as e:
        return (
            jsonify({"error": e}),
            500,
        )


@app.route("/process_svs", methods=["POST"])
def process_svs():
    try:
        data = request.get_json()
        user_email = data["user_email"]
        file_id = data["file_id"]
        filename = data["filename"]
        patient_mr_number = data["mr_number"]

        chunk_folder = os.path.join(CHUNKS_DIR, user_email, file_id)
        user_output_dir = os.path.join(MERGED_DIR, user_email)
        os.makedirs(user_output_dir, exist_ok=True)

        output_path = os.path.join(user_output_dir, filename)

        result = create_process_file_record(filename, user_email, patient_mr_number)
        if result["status"] == "exists":
            return (
                jsonify(
                    {
                        "error": "The file you're trying to upload is already processed or in process with the given MR Number"
                    }
                ),
                409,
            )
        else:
            executor.submit(
                background_process_wsi,
                "svs_data",
                user_email,
                filename,
                output_path,
                chunk_folder,
                patient_mr_number,
            )

            return (
                jsonify(
                    {
                        "message": "File uploaded successfully, Please wait for the predictions."
                    }
                ),
                200,
            )

    except Exception as e:
        return (
            jsonify({"error": e}),
            500,
        )


# @app.route("/get_biological_data", methods=["GET"])
# def get_biological_data():
#     try:
#         image_dir = os.path.join("static", "dataset_sample", "biological")
#         all_images = [
#             f"{BASE_URL}/dataset_sample/biological/{img}"
#             for img in os.listdir(image_dir)
#             if img.lower().endswith(".png")
#         ]
#         return jsonify({"image_list": all_images}), 200

#     except FileNotFoundError:
#         return jsonify({"status": "image not found"}), 404


# @app.route("/get_non_biological_data", methods=["GET"])
# def get_non_biological_data():
#     try:
#         image_dir = os.path.join("static", "dataset_sample", "non_biological")
#         all_images = [
#             f"{BASE_URL}/dataset_sample/non_biological/{img}"
#             for img in os.listdir(image_dir)
#             if img.lower().endswith(".png")
#         ]
#         return jsonify({"image_list": all_images}), 200

#     except FileNotFoundError:
#         return jsonify({"status": "image not found"}), 404


@app.route("/get_performance_metrics", methods=["GET"])
def get_performance_metrics():
    try:
        image_dir = os.path.join("static", "performance_metrics")

        all_images = [
            f"{BASE_URL}/performance_metrics/{img}"
            for img in os.listdir(image_dir)
            if img.lower().endswith(".png")
        ]

        return (
            jsonify({"image_list": all_images}),
            200,
        )

    except FileNotFoundError:
        return jsonify({"status": "image not found"}), 404


if __name__ == "__main__":
    ip = "0.0.0.0"
    port = port
    app.run(host=ip, port=port, debug=False, use_reloader=False)
