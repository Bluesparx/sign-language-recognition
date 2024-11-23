from flask import Flask, request, render_template, jsonify
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import img_to_array
import joblib
import cv2
from PIL import Image
from io import BytesIO
import base64

app = Flask(__name__)

model = load_model("model.keras")
class_names = joblib.load("class_names.pkl")

def preprocess_image(img_bytes, target_size=(64, 64)):
    img_data = base64.b64decode(img_bytes)
    img = Image.open(BytesIO(img_data))
    img = img.resize(target_size)
    img_array = img_to_array(img)
    # normalise
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array
    
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        img_data = request.form.get("image_data")
        
        if img_data:
            img_array = preprocess_image(img_data)
            if img_array is not None:
                prediction = model.predict(img_array)
                predicted_class_index = np.argmax(prediction, axis=1)[0]
                predicted_class_label = class_names[predicted_class_index]
                return jsonify({"prediction": predicted_class_label})
            else:
                return jsonify({"error": "Image preprocessing failed"})
        return jsonify({"error": "No image data received"})
    
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)