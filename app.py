from flask import Flask, request, render_template, jsonify
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import img_to_array
import joblib
import cv2
from PIL import Image
from io import BytesIO
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

TEMP_UPLOAD_FOLDER = './uploads'
os.makedirs(TEMP_UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = TEMP_UPLOAD_FOLDER

model = load_model("model.keras")
class_names = joblib.load("class_names.pkl")

def predict_image(model, img_path, class_names, img_size=64):
    img = tf.io.read_file(img_path)
    img = tf.io.decode_image(img, channels=3)
    img = tf.image.resize(img, [img_size, img_size])
    img = tf.expand_dims(img, 0)
    
    predictions = model.predict(img, verbose=0)
    predicted_class_index = np.argmax(predictions[0])
    confidence = predictions[0][predicted_class_index]
    predicted_class = class_names[predicted_class_index]
    
    return predicted_class, confidence

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if 'image' not in request.files:
            return jsonify({"error": "No image in request"})

        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No file selected"})
 
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            predicted_class, confidence = predict_image(
                model, file_path, class_names
            )
        except Exception as e:
            return jsonify({"error": f"Prediction failed: {str(e)}"})

        os.remove(file_path)

        return jsonify({
            "prediction": predicted_class,
            "confidence": f"{confidence:.2f}"
        })

    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)