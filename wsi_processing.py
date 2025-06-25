import os
from svs_to_png import extract_patches
from models_loading import hpv_model
import shutil


def wsi_processor(folder="svs_data", user_email=None, filename=None):
    try:
        current_working_dir = os.getcwd()
        all_files = os.listdir(os.path.join(current_working_dir, folder, user_email))
        hpv_count = 0
        no_hpv_count = 0
        patch_completion_status = False
        status = "failed"
        print("ALL FILES:", all_files)

        for file in all_files:
            print("SVS FILE FOUND: ", file)
            if file == filename:
                svs_file_path = os.path.join(
                    current_working_dir, folder, user_email, file
                )
                patch_completion_status = extract_patches(
                    user_email=user_email, slide_path=svs_file_path
                )

            patch_completion_status = True
            if patch_completion_status:
                print("EXTRACTION COMPLETED, NOW PROCESSING PNG FILES")
                os.remove(svs_file_path)
                all_images = os.listdir(
                    os.path.join(current_working_dir, "png_data", user_email)
                )
                for image in all_images:
                    image_path = os.path.join(
                        current_working_dir, "png_data", user_email, image
                    )
                    hpv_model(image_path, model_type="biological_filter")
                print("1st filteration completed")

                all_images = os.listdir(
                    os.path.join(current_working_dir, "png_data", user_email)
                )
                for image in all_images:
                    image_path = os.path.join(
                        current_working_dir, "png_data", user_email, image
                    )
                    label, conf = hpv_model(image_path, model_type="hpv_classifier")

                    if label == 0:
                        hpv_count += 1
                    else:
                        no_hpv_count += 1

                print("2nd filteration completed")
                status = "successful"
                print(
                    "PNG PATH: ",
                    os.path.join(current_working_dir, "png_data", user_email),
                )
                dir_path = os.path.join(current_working_dir, "png_data", user_email)
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    shutil.rmtree(dir_path)

        return hpv_count, no_hpv_count, status
    except Exception as e:
        print("ENTERED IN EXCEPTION:", e)
        return None, None, e
