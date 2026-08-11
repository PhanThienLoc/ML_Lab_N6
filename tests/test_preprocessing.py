from __future__ import annotations

import numpy as np
import pandas as pd

from src.preprocessing import fit_preprocessor, temporal_split, transform_splits


def test_preprocessing_statistics_are_fit_on_train_only() -> None:
    train = pd.DataFrame({"sales_current": [1.0, 3.0], "product_category": ["a", "b"]})
    preprocessor = fit_preprocessor(train, ["sales_current"], ["product_category"])
    assert preprocessor.means["sales_current"] == 2.0


def test_unknown_category_is_safe_at_transformation_time() -> None:
    train = pd.DataFrame({"sales_current": [1.0, 3.0], "product_category": ["a", "b"]})
    preprocessor = fit_preprocessor(train, ["sales_current"], ["product_category"])
    validation = pd.DataFrame({"sales_current": [100.0], "product_category": ["new_category"]})
    transformed = preprocessor.transform(validation)
    assert transformed.loc[0, "sales_current"] == 98.0
    assert transformed.filter(like="product_category__").iloc[0].sum() == 0.0


def _transformed_temporal_splits() -> tuple[dict[str, pd.DataFrame], dict[str, pd.Series]]:
    months = pd.date_range("2020-01-01", periods=10, freq="MS")
    data = pd.DataFrame(
        {
            "target_month": months,
            "sales_current": np.arange(10, dtype=float),
            "product_category": ["a"] * 7 + ["unseen_later"] * 3,
            "sales_next_month": np.arange(1, 11, dtype=float),
        }
    )
    splits = temporal_split(data)
    preprocessor = fit_preprocessor(splits["train"], ["sales_current"], ["product_category"])
    matrices, targets = transform_splits(preprocessor, splits)
    return matrices, targets


def test_temporal_splits_have_an_aligned_feature_schema() -> None:
    matrices, _ = _transformed_temporal_splits()
    assert list(matrices["train"].columns) == list(matrices["validation"].columns)
    assert list(matrices["train"].columns) == list(matrices["test"].columns)


def test_model_matrices_are_finite_after_preprocessing() -> None:
    matrices, targets = _transformed_temporal_splits()
    assert np.isfinite(matrices["test"].to_numpy()).all()
    assert len(targets["test"]) == len(matrices["test"])
