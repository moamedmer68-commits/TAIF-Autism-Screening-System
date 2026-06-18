"""
Questionnaire Pipeline
- Age 1-3: numeric_model.pkl (16 named features)
- Age 3-12: model.pkl (18 ordered numeric features)

Important corrections:
1) The toddler model expects 16 features, not only the 10 A1-A10 answers.
2) The toddler model classes are ['high_risk', 'low_risk']; therefore the ASD-risk
   probability is the probability of 'high_risk', not column index 1.
"""

from __future__ import annotations

import os
from typing import Any

import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

_model_1_3 = None
_model_3_12 = None


def _load_models():
    global _model_1_3, _model_3_12

    model_1_3_path = os.path.join(MODELS_DIR, "numeric_model.pkl")
    model_3_12_path = os.path.join(MODELS_DIR, "model.pkl")

    if not os.path.exists(model_1_3_path):
        raise FileNotFoundError(
            f"numeric_model.pkl not found at: {model_1_3_path}\n"
            "Please place the model file in the models/ directory."
        )
    if not os.path.exists(model_3_12_path):
        raise FileNotFoundError(
            f"model.pkl not found at: {model_3_12_path}\n"
            "Please place the model file in the models/ directory."
        )

    if _model_1_3 is None:
        _model_1_3 = joblib.load(model_1_3_path)
    if _model_3_12 is None:
        _model_3_12 = joblib.load(model_3_12_path)


def _class_probability(model: Any, features, positive_class) -> float:
    """Return probability for an explicit class label instead of assuming column 1."""
    classes = list(model.classes_)
    if positive_class not in classes:
        raise ValueError(
            f"Expected positive class {positive_class!r}, but model classes are {classes!r}."
        )
    idx = classes.index(positive_class)
    return float(model.predict_proba(features)[0][idx])


def _normalise_yes_no(value: int | bool | str) -> str:
    if isinstance(value, str):
        return "yes" if value.strip().lower() in {"yes", "y", "1", "true"} else "no"
    return "yes" if int(bool(value)) else "no"


def _clip_probability(value: float) -> float:
    """Keep every score safely inside the 0-1 probability range."""
    return float(max(0.0, min(1.0, float(value))))


def fallback_questionnaire_score(
    age,
    answers,
    gender=0,
    jaundice=0,
    family_history=0,
    language_delay=0,
    social_interaction=0,
    communication=0,
    repetitive=0,
    ethnicity="Others",
    completed_by="Family member",
):
    """
    Transparent backup score used only when the trained questionnaire model fails.

    The 10 questionnaire answers are already risk-coded by the app:
    Yes = 0 concern, No = 1 concern.
    This fallback prevents a technical model-loading or prediction problem from
    being shown to the parent as a false 0% result.
    """
    if len(answers) != 10:
        raise ValueError(f"Expected 10 answers, got {len(answers)}")

    risk_answers = [1 if int(x) else 0 for x in answers[:10]]
    questionnaire_component = sum(risk_answers) / 10.0

    developmental_flags = [
        float(bool(int(jaundice))),
        float(bool(int(family_history))),
        float(bool(int(language_delay))),
    ]
    if float(age) > 3:
        developmental_flags.extend([
            _clip_probability(social_interaction),
            _clip_probability(communication),
            _clip_probability(repetitive),
        ])

    developmental_component = sum(developmental_flags) / len(developmental_flags)

    # The questionnaire carries most of the weight. Medical/developmental flags
    # add context without overpowering the child's direct behavioural answers.
    fallback = 0.78 * questionnaire_component + 0.22 * developmental_component
    return _clip_probability(fallback)


def predict_questionnaire(
    age,
    answers,
    gender=0,
    jaundice=0,
    family_history=0,
    language_delay=0,
    social_interaction=0,
    communication=0,
    repetitive=0,
    ethnicity="Others",
    completed_by="Family member",
):
    """
    Predict ASD-screening risk probability from questionnaire data.

    The 10 displayed questions are protective behaviours and are passed as
    risk-coded indicators: Yes=0 concern, No=1 concern.
    """
    _load_models()

    if len(answers) != 10:
        raise ValueError(f"Expected 10 answers, got {len(answers)}")

    risk_answers = [int(x) for x in answers[:10]]

    if age <= 3:
        # numeric_model.pkl was audited locally and expects these exact 16 columns.
        # Age_Mons is derived from the age slider because the UI collects years.
        row = {
            **{f"A{i + 1}": risk_answers[i] for i in range(10)},
            "Age_Mons": int(round(float(age) * 12)),
            "Sex": "m" if int(gender) == 1 else "f",
            "Ethnicity": str(ethnicity or "Others"),
            "Jaundice": _normalise_yes_no(jaundice),
            "Family_mem_with_ASD": _normalise_yes_no(family_history),
            "Who completed the test": str(completed_by or "Family member"),
        }
        features = pd.DataFrame([row])
        return _clip_probability(_class_probability(_model_1_3, features, "high_risk"))

    # The 3-12 model was audited locally: class 0 behaves as healthy-like and
    # class 1 behaves as risk-like on the supplied test vectors.
    features = [
        age,
        gender,
        jaundice,
        family_history,
        language_delay,
        social_interaction,
        communication,
        repetitive,
    ] + risk_answers
    features = np.array(features, dtype=float).reshape(1, -1)
    return _clip_probability(_class_probability(_model_3_12, features, 1))


def check_models_exist():
    return {
        "numeric_model": os.path.exists(os.path.join(MODELS_DIR, "numeric_model.pkl")),
        "questionnaire_model": os.path.exists(os.path.join(MODELS_DIR, "model.pkl")),
    }
