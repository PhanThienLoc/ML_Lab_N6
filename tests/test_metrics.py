from __future__ import annotations

import numpy as np
import pytest

from src.metrics import regression_metrics, r2_score


def test_regression_metrics_match_known_values() -> None:
    metrics = regression_metrics(np.array([1.0, 3.0]), np.array([2.0, 1.0]))

    assert metrics["mae"] == 1.5
    assert metrics["mse"] == 2.5
    assert metrics["rmse"] == pytest.approx(np.sqrt(2.5))
    assert metrics["r2"] == -1.5


def test_r2_rejects_a_constant_target() -> None:
    with pytest.raises(ValueError, match="undefined"):
        r2_score(np.array([2.0, 2.0]), np.array([2.0, 2.0]))
