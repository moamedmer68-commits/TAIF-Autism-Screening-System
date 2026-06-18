"""Inference helpers for the numeric/questionnaire classification pipeline."""

from __future__ import annotations

import json
import logging
import pickle
from pathlib import Path
from typing import Any, Dict

import pandas as pd

try:
    import joblib
except ImportError:
    class _JoblibFallback:
        """Minimal joblib-compatible fallback using pickle."""

        @staticmethod
        def dump(obj: object, filename: Path) -> None:
            with open(filename, "wb") as file_pointer:
                pickle.dump(obj, file_pointer)

        @staticmethod
        def load(filename: Path) -> object:
            with open(filename, "rb") as file_pointer:
                return pickle.load(file_pointer)

    joblib = _JoblibFallback()

LOGGER = logging.getLogger(__name__)
DEFAULT_MODEL_PATH = Path("models/numeric/numeric_model.pkl")


def load_pipeline(model_path: Path = DEFAULT_MODEL_PATH) -> Any:
    """Load the saved sklearn pipeline from disk.

    Args:
        model_path: Path to the persisted joblib pipeline file.

    Returns:
        The deserialized sklearn pipeline.

    Raises:
        FileNotFoundError: If the model file does not exist.
    """
    if not model_path.exists():
        raise FileNotFoundError(
            f"Saved model pipeline not found at: {model_path}. Train the model first."
        )

    return joblib.load(model_path)


def predict(input_dict: Dict[str, Any], model_path: Path = DEFAULT_MODEL_PATH) -> Dict[str, Any]:
    """Run inference and return a standardized JSON-compatible result.

    Args:
        input_dict: Single questionnaire response payload keyed by feature name.
        model_path: Path to the saved full pipeline.

    Returns:
        A dictionary with the exact standardized output schema:
        ``{"score": float, "label": str, "confidence": float}``
    """
    pipeline = load_pipeline(model_path)
    input_frame = pd.DataFrame([input_dict])
    if hasattr(pipeline, "feature_names_in_"):
        input_frame = input_frame.reindex(columns=list(pipeline.feature_names_in_))

    predicted_class = pipeline.predict(input_frame)[0]
    probabilities = pipeline.predict_proba(input_frame)[0]
    positive_class_index = 1
    positive_score = float(probabilities[positive_class_index])
    confidence = float(max(probabilities))

    label = "high_risk" if predicted_class == pipeline.classes_[positive_class_index] else "low_risk"

    return {
        "score": positive_score,
        "label": label,
        "confidence": confidence,
    }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    example_input_dict = {
        "age": 42,
        "income": 65000,
        "stress_level": 8,
        "smoker": "yes",
    }

    try:
        result = predict(example_input_dict)
        print(json.dumps(result, indent=2))
    except FileNotFoundError as exc:
        LOGGER.error("%s", exc)
