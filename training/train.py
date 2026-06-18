"""Training script for the numeric/questionnaire classification pipeline."""

from __future__ import annotations

import argparse
import logging
import pickle
import sys
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

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

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from classifier import get_model
from preprocessor import build_preprocessor

LOGGER = logging.getLogger(__name__)
DEFAULT_DATA_DIR = Path("data/raw/questionnaire")
DEFAULT_MODEL_PATH = Path("models/numeric/numeric_model.pkl")


def configure_logging() -> None:
    """Configure application logging for training."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def load_dataset(data_dir: Path) -> pd.DataFrame:
    """Load and concatenate CSV files from the questionnaire data directory.

    Args:
        data_dir: Directory containing one or more CSV files.

    Returns:
        A concatenated pandas DataFrame.

    Raises:
        FileNotFoundError: If the directory does not exist or has no CSV files.
        ValueError: If the loaded dataset is empty.
    """
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    csv_files = sorted(data_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in: {data_dir}")

    dataframes = [pd.read_csv(csv_file) for csv_file in csv_files]
    dataset = pd.concat(dataframes, ignore_index=True)

    if dataset.empty:
        raise ValueError(f"No rows found after loading CSV files from: {data_dir}")

    LOGGER.info("Loaded %s rows from %s CSV file(s).", len(dataset), len(csv_files))
    return dataset


def infer_target_column(df: pd.DataFrame, target_column: Optional[str] = None) -> str:
    """Infer the target column, defaulting to the last column.

    Args:
        df: Full dataset including features and target.
        target_column: Optional user-provided target column name.

    Returns:
        The resolved target column name.

    Raises:
        ValueError: If the requested target is missing or the inferred target is invalid.
    """
    if target_column is not None:
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataset.")
        return target_column

    if df.shape[1] < 2:
        raise ValueError("Dataset must contain at least one feature column and one target column.")

    inferred_target = df.columns[-1]
    LOGGER.info("No target column supplied. Using the last column: %s", inferred_target)
    return inferred_target


def prepare_features_and_target(
    df: pd.DataFrame, target_column: str
) -> Tuple[pd.DataFrame, pd.Series]:
    """Split a DataFrame into features and target, validating binary classification.

    Args:
        df: Full dataset.
        target_column: Name of the target column.

    Returns:
        A tuple of ``(X, y)``.

    Raises:
        ValueError: If the target is missing or does not contain exactly two classes.
    """
    X = df.drop(columns=[target_column]).copy()
    y = df[target_column].copy()

    if X.empty:
        raise ValueError("Feature matrix is empty after removing the target column.")

    unique_classes = pd.Series(y).dropna().unique()
    if len(unique_classes) != 2:
        raise ValueError(
            "This pipeline expects binary classification data with exactly two target classes."
        )

    return X, y


def build_training_pipeline(model_type: str, X_train: pd.DataFrame) -> Pipeline:
    """Create the full sklearn pipeline for preprocessing and classification.

    Args:
        model_type: Requested classifier type.
        X_train: Training features used to infer preprocessing behavior.

    Returns:
        A complete sklearn ``Pipeline``.
    """
    preprocessor = build_preprocessor(X_train)
    model = get_model(model_type=model_type)

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def save_pipeline(pipeline: Pipeline, output_path: Path) -> None:
    """Persist the full training pipeline to disk using joblib.

    Args:
        pipeline: Trained sklearn pipeline.
        output_path: Destination file path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, output_path)
    LOGGER.info("Saved trained pipeline to %s", output_path)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the training script."""
    parser = argparse.ArgumentParser(description="Train a numeric questionnaire classifier.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Directory containing questionnaire CSV files.",
    )
    parser.add_argument(
        "--target-column",
        type=str,
        default=None,
        help="Optional target column name. Defaults to the last column in the dataset.",
    )
    parser.add_argument(
        "--model-type",
        type=str,
        default="rf",
        choices=["rf", "xgb"],
        help="Classifier type to train.",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=DEFAULT_MODEL_PATH,
        help="Destination for the saved full pipeline.",
    )
    return parser.parse_args()


def main() -> None:
    """Train, evaluate, and save the full numeric classification pipeline."""
    configure_logging()
    args = parse_args()

    dataset = load_dataset(args.data_dir)
    target_column = infer_target_column(dataset, args.target_column)
    X, y = prepare_features_and_target(dataset, target_column)

    stratify_target = y if y.nunique(dropna=True) > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=stratify_target,
    )

    positive_ratio = y_train.value_counts(normalize=True).max()
    if positive_ratio >= 0.8:
        LOGGER.warning(
            "Class imbalance detected in the training split. Largest class ratio: %.2f",
            positive_ratio,
        )

    pipeline = build_training_pipeline(args.model_type, X_train)
    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    f1 = f1_score(y_test, predictions, pos_label=pipeline.named_steps["model"].classes_[1])

    print("Evaluation Metrics")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1 Score: {f1:.4f}")

    save_pipeline(pipeline, args.output_path)


if __name__ == "__main__":
    main()
