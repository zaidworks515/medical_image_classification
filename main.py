from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import shutil
import pandas as pd
from config import port, server_ip
from wsi_processing import wsi_processor
from concurrent.futures import ThreadPoolExecutor
from app import create_app

app = create_app()
CORS(app)

BASE_URL = f"http://{server_ip}:{port}/local"
executor = ThreadPoolExecutor(max_workers=4)

CHUNKS_DIR = "temp_chunks"
MERGED_DIR = "svs_data"

os.makedirs(CHUNKS_DIR, exist_ok=True)
os.makedirs(MERGED_DIR, exist_ok=True)


def background_process_wsi(
    folder, session_id, filename, output_path, chunk_folder, user_id
):
    try:
        with open(output_path, "wb") as output_file:
            chunks = sorted(os.listdir(chunk_folder))
            for chunk_name in chunks:
                chunk_path = os.path.join(chunk_folder, chunk_name)
                with open(chunk_path, "rb") as chunk_file:
                    output_file.write(chunk_file.read())

        shutil.rmtree(os.path.join(CHUNKS_DIR, user_id))

        wsi_processor(folder=folder, session_id=session_id, filename=filename)

    except Exception as e:
        print(f"[ERROR] Background processing failed: {e}")


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "server is up and running."})


@app.route("/upload_chunk", methods=["POST"])
def upload_chunk():
    file = request.files["file"]
    user_id = request.form["user_id"]
    file_id = request.form["file_id"]
    chunk_index = int(request.form["chunk_index"])

    chunk_folder = os.path.join(CHUNKS_DIR, user_id, file_id)
    os.makedirs(chunk_folder, exist_ok=True)

    chunk_path = os.path.join(chunk_folder, f"{chunk_index:06d}")
    file.save(chunk_path)

    return jsonify({"message": f"Chunk {chunk_index} received."})


@app.route("/process_svs", methods=["POST"])
def process_svs():
    data = request.get_json()
    user_id = data["user_id"]
    file_id = data["file_id"]
    filename = data["filename"]

    chunk_folder = os.path.join(CHUNKS_DIR, user_id, file_id)
    user_output_dir = os.path.join(MERGED_DIR, user_id)
    os.makedirs(user_output_dir, exist_ok=True)

    output_path = os.path.join(user_output_dir, filename)

    executor.submit(
        background_process_wsi,
        "svs_data",
        user_id,
        filename,
        output_path,
        chunk_folder,
        user_id,
    )

    return (
        jsonify({"message": "File uploaded successfully"}),
        200,
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

        training_history_df = pd.read_excel(
            "static/performance_metrics/training_history.xlsx"
        )
        training_history = training_history_df.to_dict(orient="records")

        return (
            jsonify({"image_list": all_images, "training_history": training_history}),
            200,
        )

    except FileNotFoundError:
        return jsonify({"status": "image not found"}), 404


if __name__ == "__main__":
    ip = "0.0.0.0"
    port = port
    app.run(host=ip, port=port, debug=False, use_reloader=False)
