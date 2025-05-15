import base64
import io
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array



loaded_model = load_model("models/best_model.h5")

def predict_image(file):
    image = Image.open(file).convert('RGB')
    image = image.resize((256, 256))  

    image_array = img_to_array(image)
    image_array = image_array / 255.0 
    image_array = np.expand_dims(image_array, axis=0)

    y_pred = loaded_model.predict(image_array)
    
    print("PREDICTIONS: ", y_pred)
    label = "Biological Features Found" if y_pred < 0.5 else "No Biological Features Found"
    return label