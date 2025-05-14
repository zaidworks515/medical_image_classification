from flask import Flask, jsonify
from flask_cors import CORS
import os
import pandas as pd
from config import port, server_ip


app = Flask(__name__, static_url_path='/local', static_folder='static')
CORS(app)

BASE_URL = f"http://{server_ip}:{port}/local" 
    
@app.route("/get_biological_data", methods=['GET'])
def get_biological_data():
    try:
        image_dir = os.path.join("static", "dataset_sample", "biological")
        all_images = [
            f"{BASE_URL}/dataset_sample/biological/{img}"
            for img in os.listdir(image_dir)
            if img.lower().endswith('.png')
        ]
        return jsonify({'image_list': all_images}), 200

    except FileNotFoundError:
        return jsonify({'status': 'image not found'}), 404


@app.route("/get_non_biological_data", methods=['GET'])
def get_non_biological_data():
    try:
        image_dir = os.path.join("static", "dataset_sample", "non_biological")
        all_images = [
            f"{BASE_URL}/dataset_sample/non_biological/{img}"
            for img in os.listdir(image_dir)
            if img.lower().endswith('.png')
        ]
        return jsonify({'image_list': all_images}), 200

    except FileNotFoundError:
        return jsonify({'status': 'image not found'}), 404


@app.route("/get_performance_metrics", methods=['GET'])
def get_performance_metrics():
    try:
        image_dir = os.path.join("static", "performance_metrics")
        
        all_images = [
            f"{BASE_URL}/performance_metrics/{img}"
            for img in os.listdir(image_dir)
            if img.lower().endswith('.png')
        ]
        
        training_history_df = pd.read_excel("static/performance_metrics/training_history.xlsx")
        training_history = training_history_df.to_dict(orient='records')
        
        
        return jsonify({'image_list': all_images,
                        "training_history": training_history}), 200

    except FileNotFoundError:
        return jsonify({'status': 'image not found'}), 404





if __name__ == '__main__':
    ip = "0.0.0.0"
    port = port
    app.run(host=ip, port=port, debug=True)
