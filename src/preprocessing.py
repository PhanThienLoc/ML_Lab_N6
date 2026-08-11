"""Temporal splitting and train-only preprocessing without sklearn."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd


TARGET_NAME = "sales_next_month"
TARGET_MONTH_NAME = "target_month"


def temporal_split(
    data: pd.DataFrame,
    train_fraction: float = 0.70,
    validation_fraction: float = 0.15,
) -> dict[str, pd.DataFrame]:
    """Split whole target months into chronological train/validation/test sets."""

    if TARGET_MONTH_NAME not in data.columns:
        raise ValueError(f"Temporal split requires {TARGET_MONTH_NAME!r}.")
    if not 0 < train_fraction < 1 or not 0 < validation_fraction < 1:
        raise ValueError("Split fractions must be in (0, 1).")
    if train_fraction + validation_fraction >= 1:
        raise ValueError("train_fraction + validation_fraction must leave a test period.")

    values = data.copy()
    values[TARGET_MONTH_NAME] = pd.to_datetime(values[TARGET_MONTH_NAME])
    target_months = pd.DatetimeIndex(values[TARGET_MONTH_NAME].dropna().unique()).sort_values()
    if len(target_months) < 3:
        raise ValueError("At least three distinct target months are required for temporal train/val/test splits.")

    n_months = len(target_months)
    n_train = max(1, int(np.floor(n_months * train_fraction)))
    n_validation = max(1, int(np.floor(n_months * validation_fraction)))
    if n_train + n_validation >= n_months:
        n_train = n_months - 2
        n_validation = 1

    train_months = target_months[:n_train]
    validation_months = target_months[n_train : n_train + n_validation]
    test_months = target_months[n_train + n_validation :]
    splits = {
        "train": values.loc[values[TARGET_MONTH_NAME].isin(train_months)].copy(),
        "validation": values.loc[values[TARGET_MONTH_NAME].isin(validation_months)].copy(),
        "test": values.loc[values[TARGET_MONTH_NAME].isin(test_months)].copy(),
    }
    assert_temporal_split(splits)
    return splits


def _split_months(frame: pd.DataFrame) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(pd.to_datetime(frame[TARGET_MONTH_NAME]).unique()).sort_values()


def assert_temporal_split(splits: Mapping[str, pd.DataFrame]) -> None:
    """Assert strict chronological separation and no target-month overlap."""

    expected = {"train", "validation", "test"}
    missing = expected.difference(splits)
    if missing:
        raise ValueError(f"Missing temporal split(s): {sorted(missing)}")
    month_sets = {name: set(_split_months(frame)) for name, frame in splits.items()}
    if any(not months for months in month_sets.values()):
        raise AssertionError("Every temporal split must contain at least one target month.")
    if month_sets["train"] & month_sets["validation"]:
        raise AssertionError("Train and validation target months overlap.")
    if month_sets["train"] & month_sets["test"]:
        raise AssertionError("Train and test target months overlap.")
    if month_sets["validation"] & month_sets["test"]:
        raise AssertionError("Validation and test target months overlap.")
    if max(month_sets["train"]) >= min(month_sets["validation"]):
        raise AssertionError("Validation must follow the training target months.")
    if max(month_sets["validation"]) >= min(month_sets["test"]):
        raise AssertionError("Test must follow the validation target months.")


def temporal_split_metadata(splits: Mapping[str, pd.DataFrame]) -> dict[str, dict[str, str | int]]:
    """Return serialisable target-month boundaries and row counts."""

    metadata: dict[str, dict[str, str | int]] = {}
    for name, frame in splits.items():
        months = _split_months(frame)
        metadata[name] = {
            "target_month_start": months.min().strftime("%Y-%m"),
            "target_month_end": months.max().strftime("%Y-%m"),
            "target_month_count": int(len(months)),
            "rows": int(len(frame)),
        }
    return metadata


@dataclass(frozen=True)
class TrainOnlyPreprocessor:
    """One-hot encoder and standardiser whose learned values come from train only."""

    numerical_columns: tuple[str, ...]
    categorical_columns: tuple[str, ...]
    category_levels: dict[str, tuple[str, ...]]
    fill_values: dict[str, float]
    means: dict[str, float]
    stds: dict[str, float]
    feature_names: tuple[str, ...]

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Transform a split, safely ignoring categories unseen during training."""

        needed = set(self.numerical_columns).union(self.categorical_columns)
        missing = needed.difference(frame.columns)
        if missing:
            raise ValueError(f"Cannot transform data missing columns: {sorted(missing)}")

        transformed_numeric: dict[str, pd.Series] = {}
        for column in self.numerical_columns:
            values = pd.to_numeric(frame[column], errors="coerce").astype(float)
            values = values.fillna(self.fill_values[column])
            transformed_numeric[column] = (values - self.means[column]) / self.stds[column]
        numeric = pd.DataFrame(transformed_numeric, index=frame.index)

        encoded: dict[str, pd.Series] = {}
        for column in self.categorical_columns:
            values = frame[column].astype("string").fillna("__MISSING__")
            for level in self.category_levels[column]:
                encoded_name = f"{column}__{level}"
                encoded[encoded_name] = (values == level).astype(float)
        categorical = pd.DataFrame(encoded, index=frame.index)
        output = pd.concat([numeric, categorical], axis=1).reindex(columns=self.feature_names, fill_value=0.0)
        output = output.astype(float)
        if not np.isfinite(output.to_numpy()).all():
            raise ValueError("Preprocessing produced NaN or infinite model inputs.")
        return output

    def metadata(self) -> dict[str, Any]:
        """Return only JSON-safe parameters needed for reproducible inference."""

        return {
            "numerical_columns": list(self.numerical_columns),
            "categorical_columns": list(self.categorical_columns),
            "category_levels": {name: list(levels) for name, levels in self.category_levels.items()},
            "numeric_fill_values_train_median": self.fill_values,
            "numeric_train_means": self.means,
            "numeric_train_stds": self.stds,
            "feature_names": list(self.feature_names),
            "unknown_category_rule": "All-zero one-hot vector; transformation does not fail.",
        }


def fit_preprocessor(
    train_frame: pd.DataFrame,
    numerical_columns: Sequence[str],
    categorical_columns: Sequence[str],
) -> TrainOnlyPreprocessor:
    """Fit imputation, category space, and scaling parameters on train only."""

    if TARGET_NAME in numerical_columns or TARGET_NAME in categorical_columns:
        raise ValueError(f"{TARGET_NAME} must never be passed as a model feature.")
    numerical = tuple(numerical_columns)
    categorical = tuple(categorical_columns)
    required = set(numerical).union(categorical)
    missing = required.difference(train_frame.columns)
    if missing:
        raise ValueError(f"Cannot fit preprocessor; train data lacks {sorted(missing)}")

    fill_values: dict[str, float] = {}
    means: dict[str, float] = {}
    stds: dict[str, float] = {}
    for column in numerical:
        values = pd.to_numeric(train_frame[column], errors="coerce").astype(float)
        median = values.median(skipna=True)
        fill_value = 0.0 if pd.isna(median) else float(median)
        filled = values.fillna(fill_value)
        mean = float(filled.mean())
        std = float(filled.std(ddof=0))
        fill_values[column] = fill_value
        means[column] = mean
        stds[column] = 1.0 if not np.isfinite(std) or std == 0 else std

    category_levels: dict[str, tuple[str, ...]] = {}
    for column in categorical:
        levels = tuple(sorted(train_frame[column].astype("string").fillna("__MISSING__").unique().tolist()))
        if not levels:
            raise ValueError(f"Categorical training column {column!r} has no levels.")
        category_levels[column] = levels

    feature_names = tuple(numerical) + tuple(
        f"{column}__{level}"
        for column in categorical
        for level in category_levels[column]
    )
    return TrainOnlyPreprocessor(
        numerical_columns=numerical,
        categorical_columns=categorical,
        category_levels=category_levels,
        fill_values=fill_values,
        means=means,
        stds=stds,
        feature_names=feature_names,
    )


def transform_splits(
    preprocessor: TrainOnlyPreprocessor, splits: Mapping[str, pd.DataFrame]
) -> tuple[dict[str, pd.DataFrame], dict[str, pd.Series]]:
    """Return identically ordered X matrices and target vectors for each split."""

    matrices: dict[str, pd.DataFrame] = {}
    targets: dict[str, pd.Series] = {}
    for name in ("train", "validation", "test"):
        frame = splits[name]
        if TARGET_NAME not in frame.columns:
            raise ValueError(f"{name} split has no {TARGET_NAME} column.")
        matrices[name] = preprocessor.transform(frame)
        targets[name] = pd.to_numeric(frame[TARGET_NAME], errors="raise").astype(float).reset_index(drop=True)
        matrices[name] = matrices[name].reset_index(drop=True)
    expected_columns = list(matrices["train"].columns)
    if any(list(matrix.columns) != expected_columns for matrix in matrices.values()):
        raise AssertionError("Train, validation, and test matrices do not share the same feature schema.")
    return matrices, targets
