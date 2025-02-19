from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from ultralytics import YOLO
import tensorflow as tf
from PIL import Image

app = Flask(__name__)
CORS(app)

@app.route('/predict/<plant>', methods=['POST'])
def predict(plant):
    model = YOLO(f'{plant}.pt')

    if 'image' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    results = model.predict(img)

    result_dict = []
    for result in results:
        if result.boxes is None:
            class_idx = int(results[0].probs.top1)
            class_name = model.names[class_idx]
            result_dict.append(class_name)
        else:
            for box in result.boxes:
                class_idx = box.cls.item()
                class_name = model.names[int(class_idx)]
                result_dict.append(class_name)

    return jsonify({'prediction': result_dict[0]})

@app.route('/predict/Identify', methods=['POST'])
def Identify():
    model = tf.keras.models.load_model('Identifythecrop.h5')
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    img = Image.open(file.stream)
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0

    input_data = np.expand_dims(img_array, axis=0)

    class_names = {
        0: 'Cucumber',
        1: 'Pepper',
        2: 'Zucchini'
    }

    predictions = model.predict(input_data)
    predictions = predictions.tolist()

    predicted_class = np.argmax(predictions, axis=1)

    predicted_label = class_names[predicted_class[0]]
    return jsonify({'predictions': predicted_label})

if __name__ == '__main__':
    app.run(debug=True)
