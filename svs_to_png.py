import os
import openslide
import numpy as np
import cv2
from tqdm import tqdm

# WSI_DIR = "data_svs"
# OUTPUT_PATCHES_DIR = "data"
# PATCH_SIZE = 1024
# LEVEL = 0  # no downgrading/downsampling..


def extract_patches(
    save_dir="png_data",
    user_email=None,
    slide_path=None,
    LEVEL=0,
    patch_size=1024,
):
    """Extracts the given dimension patches from the highest resolution level of an .svs file."""
    try:
        save_dir = os.path.join(os.getcwd(), save_dir, user_email)
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

                patch = slide.read_region(
                    (x, y), LEVEL, (patch_size, patch_size)
                ).convert("RGB")
                patch_np = np.array(patch)

                if np.mean(patch_np) < 240:
                    patch_filename = os.path.join(
                        save_dir, f"{slide_name}_x{x}_y{y}.png"
                    )
                    cv2.imwrite(
                        patch_filename, cv2.cvtColor(patch_np, cv2.COLOR_RGB2BGR)
                    )
                    count += 1

        print(f"Saved {count} patches for {slide_name}")

        return True

    except Exception as e:
        return False
