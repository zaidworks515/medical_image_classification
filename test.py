from models_loading import hpv_model

image_path = r"static\dataset_sample\biological\6_27_105333_patch_73.png"

label, conf = hpv_model(
    image_path=image_path, model_type="hpv_classifier", threshold=0.75
)

print(label, conf)
