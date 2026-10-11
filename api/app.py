from pathlib import Path
from io import BytesIO
import os

import numpy as np
import torch
from PIL import Image
from flask import Flask, jsonify, request
from torchvision import transforms

from model_def import CIFAR10CNN

CLASSES = (
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck"
)

MODEL_PATH = Path(os.getenv("MODEL_PATH", "/app/cifar10_cnn.pth"))
APP_VERSION = os.getenv("APP_VERSION", "v1")
DEVICE = torch.device("cpu")

model = CIFAR10CNN().to(DEVICE)
if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
model.load_state_dict(checkpoint["state_dict"])
model.eval()

preprocess = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize(
        (0.4914, 0.4822, 0.4465),
        (0.2470, 0.2435, 0.2616),
    ),
])

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


@app.get("/")
def index():
    return jsonify({
        "success": True,
        "application": "CIFAR-10 PyTorch CNN API",
        "version": APP_VERSION,
        "endpoints": ["/health", "/predict"],
    })


@app.get("/health")
def health():
    return jsonify({
        "success": True,
        "status": "healthy",
        "model_loaded": True,
        "version": APP_VERSION,
    })


@app.post("/predict")
def predict():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "Use form field 'file'."}), 400

    uploaded = request.files["file"]
    if not uploaded.filename:
        return jsonify({"success": False, "error": "No file selected."}), 400

    try:
        image = Image.open(BytesIO(uploaded.read())).convert("RGB")
        tensor = preprocess(image).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            probabilities = torch.softmax(model(tensor), dim=1)[0]
            index = int(torch.argmax(probabilities).item())
            confidence = float(probabilities[index].item())

        return jsonify({
            "success": True,
            "version": APP_VERSION,
            "predicted_class": CLASSES[index],
            "predicted_index": index,
            "confidence": confidence,
            "confidence_percent": round(confidence * 100, 2),
            "probabilities": {
                name: float(probabilities[i].item())
                for i, name in enumerate(CLASSES)
            },
        })
    except Exception as exc:
        app.logger.exception("Prediction failed")
        return jsonify({"success": False, "error": str(exc)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
