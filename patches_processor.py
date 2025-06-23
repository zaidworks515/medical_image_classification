from models_loading import predict_image
import os

base_dir = "data"
sub_folders = os.listdir(base_dir)

for folder in sub_folders:
    all_files = os.listdir(os.path.join(base_dir, folder))
    for file in all_files:
        file_path = os.path.join(base_dir, folder, file)

        label, conf = predict_image(image_path=file_path)
        if label != 0:
            os.remove(file_path)
    print(f"category {folder} is filtered completely")
