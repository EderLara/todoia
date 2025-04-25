from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import tensorflow as tf
import io
import os

app = Flask(__name__)

# Cargar el modelo (asegúrate de que la ruta sea correcta dentro del contenedor)
MODEL_PATH = 'model/best_mnist_model.h5'
if not os.path.exists(MODEL_PATH):
    print(f"Error: Modelo no encontrado en {MODEL_PATH}")
    exit()
model = tf.keras.models.load_model(MODEL_PATH)

def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert('L')
    img = img.resize((28, 28))
    img_array = np.array(img) / 255.0
    img_array = img_array.reshape(1, 784)
    return img_array

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    image_bytes = image_file.read()
    processed_image = preprocess_image(image_bytes)
    predictions = model.predict(processed_image)
    predicted_class = np.argmax(predictions[0])
    confidence = np.max(predictions[0]) * 100

    return jsonify({'predicted_class': int(predicted_class), 'confidence': float(confidence)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)