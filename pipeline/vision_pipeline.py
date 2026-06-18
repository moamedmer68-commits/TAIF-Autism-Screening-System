"""
Vision Pipeline - ResNet50 image analysis
Input: image file
Output: ASD-screening probability [0-1]

Correction:
The local audit returned raw sigmoid output 1.0 for a file from the
Non_Autistic folder. With the original training folder order
Autistic=0 and Non_Autistic=1, raw output is the non-autistic probability.
Therefore ASD probability = 1 - raw output.
"""

from __future__ import annotations

import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

_vision_model = None


def _load_model():
    global _vision_model
    if _vision_model is not None:
        return _vision_model

    model_path = os.path.join(MODELS_DIR, "resnet50.h5")
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"resnet50.h5 not found at: {model_path}\n"
            "Please place the model file in the models/ directory."
        )

    from tensorflow.keras.models import load_model

    _vision_model = load_model(model_path)
    return _vision_model


def predict_image_with_details(image_file):
    """Return both raw model output and corrected ASD probability."""
    from PIL import Image

    model = _load_model()

    img = Image.open(image_file).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    pred = model.predict(img_array, verbose=0)
    raw_non_autistic_probability = float(pred[0][0])
    raw_non_autistic_probability = max(0.0, min(1.0, raw_non_autistic_probability))
    autism_probability = 1.0 - raw_non_autistic_probability

    return {
        "raw_non_autistic_probability": raw_non_autistic_probability,
        "autism_probability": autism_probability,
        "mapping": "raw sigmoid class 1 = Non_Autistic; ASD risk = 1 - raw",
    }


def predict_image(image_file):
    return float(predict_image_with_details(image_file)["autism_probability"])


def check_model_exists():
    return os.path.exists(os.path.join(MODELS_DIR, "resnet50.h5"))
