import os
import openslide
import numpy as np
import cv2
from tqdm import tqdm

WSI_DIR = "data_svs"
OUTPUT_PATCHES_DIR = "data"
PATCH_SIZE = 1024
LEVEL = 0  # no downgrading/downsampling..


def extract_patches(slide_path, patch_size=PATCH_SIZE, save_dir=OUTPUT_PATCHES_DIR):
    """Extracts the given dimension patches from the highest resolution level of an .svs file."""
    os.makedirs(save_dir, exist_ok=True)

    slide = openslide.OpenSlide(slide_path)
    w, h = slide.level_dimensions[LEVEL]
    slide_name = os.path.splitext(os.path.basename(slide_path))[0]
    count = 0

    print(f"Processing {slide_name} with dimensions {w}x{h}")

    for x in tqdm(range(0, w, patch_size), desc=f"Rows for {slide_name}"):
        for y in range(0, h, patch_size):
            if x + patch_size > w or y + patch_size > h:
                continue  # Skip incomplete patches at the edges

            patch = slide.read_region((x, y), LEVEL, (patch_size, patch_size)).convert(
                "RGB"
            )
            patch_np = np.array(patch)

            if np.mean(patch_np) < 240:
                patch_filename = os.path.join(save_dir, f"{slide_name}_x{x}_y{y}.png")
                cv2.imwrite(patch_filename, cv2.cvtColor(patch_np, cv2.COLOR_RGB2BGR))
                count += 1

    print(f"Saved {count} patches for {slide_name}")


all_processed_files = []


def svs_to_png(base_dir):
    for sub_folder in os.listdir(base_dir):
        complete_path = os.path.join(base_dir, sub_folder)
        if not os.path.isdir(complete_path):
            continue

        for file in os.listdir(complete_path):
            file_path = os.path.join(complete_path, file)

            if file_path.endswith(".svs"):
                if sub_folder.lower() == "hpv":
                    target_dir = os.path.join(OUTPUT_PATCHES_DIR, "hpv")

                elif sub_folder.lower() == "no_hpv":
                    target_dir = os.path.join(OUTPUT_PATCHES_DIR, "no_hpv")

                else:
                    continue  # skip unrelated folders

                print(f"Extracting patches from: {file_path}")
                extract_patches(
                    slide_path=file_path, patch_size=PATCH_SIZE, save_dir=target_dir
                )
                all_processed_files.append(file_path)
                print(f"Extraction complete: {file_path}")


svs_to_png(WSI_DIR)

print("No of processed files: ", len(all_processed_files))
