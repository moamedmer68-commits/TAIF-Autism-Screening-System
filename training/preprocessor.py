"""Preprocessing utilities for numeric/questionnaire classification."""

from __future__ import annotations

import inspect
from typing import List

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def _build_one_hot_encoder() -> OneHotEncoder:
    """Create a compatible one-hot encoder across scikit-learn versions."""
    encoder_signature = inspect.signature(OneHotEncoder)
    if "sparse_output" in encoder_signature.parameters:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    return OneHotEncoder(handle_unknown="ignore", sparse=False)


def build_preprocessor(df: pd.DataFrame) -> ColumnTransformer:
    """Build a reusable preprocessing pipeline for a feature DataFrame.

    The returned transformer:
    - imputes missing numerical values with the mean
    - imputes missing categorical values with the most frequent value
    - one-hot encodes categorical features with safe handling for unseen values
    - standardizes numerical features

    Args:
        df: Feature-only pandas DataFrame used to infer column types.

    Returns:
        A fitted-ready ``ColumnTransformer`` that can be used inside an
        ``sklearn.pipeline.Pipeline``.
    """
    numeric_columns: List[str] = df.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_columns: List[str] = [column for column in df.columns if column not in numeric_columns]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="mean")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", _build_one_hot_encoder()),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_columns),
            ("cat", categorical_pipeline, categorical_columns),
        ],
    )
