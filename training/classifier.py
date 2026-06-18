"""Model factory utilities for numeric/questionnaire classification."""

from __future__ import annotations

import logging
from typing import Any

from sklearn.ensemble import RandomForestClassifier

LOGGER = logging.getLogger(__name__)


def get_model(model_type: str = "rf") -> Any:
    """Return a configured classification model.

    Supported model types:
    - ``rf``: ``RandomForestClassifier``
    - ``xgb``: ``xgboost.XGBClassifier`` if xgboost is installed

    Args:
        model_type: Requested model identifier.

    Returns:
        A scikit-learn compatible classifier instance.

    Raises:
        ValueError: If the model type is unsupported or unavailable.
    """
    normalized_model_type = model_type.strip().lower()

    if normalized_model_type == "rf":
        return RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=1,
            class_weight="balanced_subsample",
        )

    if normalized_model_type == "xgb":
        try:
            from xgboost import XGBClassifier
        except ImportError as exc:
            raise ValueError(
                "XGBoost was requested but is not installed. Install `xgboost` or use `rf`."
            ) from exc

        LOGGER.info("Using XGBoost classifier.")
        return XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            n_jobs=1,
        )

    raise ValueError(f"Unsupported model_type '{model_type}'. Use 'rf' or 'xgb'.")
