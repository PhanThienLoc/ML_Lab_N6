import numpy as np
import pytest

from src.metrics import (
    mean_absolute_error,
    mean_squared_error,
    root_mean_squared_error,
    r2_score,
    regression_metrics,
)


def test_mean_absolute_error():
    y_true = np.array([100.0, 200.0, 300.0])
    y_pred = np.array([110.0, 190.0, 280.0])

    result = mean_absolute_error(y_true, y_pred)

    assert np.isclose(result, 13.3333333333)


def test_mean_squared_error():
    y_true = np.array([100.0, 200.0, 300.0])
    y_pred = np.array([110.0, 190.0, 280.0])

    result = mean_squared_error(y_true, y_pred)

    assert np.isclose(result, 200.0)


def test_root_mean_squared_error():
    y_true = np.array([100.0, 200.0, 300.0])
    y_pred = np.array([110.0, 190.0, 280.0])

    result = root_mean_squared_error(y_true, y_pred)

    assert np.isclose(result, np.sqrt(200.0))


def test_r2_score():
    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    y_pred = np.array([1.0, 2.0, 3.0, 4.0])

    result = r2_score(y_true, y_pred)

    assert np.isclose(result, 1.0)


def test_regression_metrics():
    y_true = np.array([100.0, 200.0, 300.0])
    y_pred = np.array([110.0, 190.0, 280.0])

    result = regression_metrics(y_true, y_pred)

    assert set(result.keys()) == {"mae", "mse", "rmse", "r2"}

    assert np.isclose(result["mae"], 13.3333333333)
    assert np.isclose(result["mse"], 200.0)
    assert np.isclose(result["rmse"], np.sqrt(200.0))


def test_perfect_prediction():
    y_true = np.array([10.0, 20.0, 30.0])
    y_pred = np.array([10.0, 20.0, 30.0])

    assert np.isclose(mean_absolute_error(y_true, y_pred), 0.0)
    assert np.isclose(mean_squared_error(y_true, y_pred), 0.0)
    assert np.isclose(root_mean_squared_error(y_true, y_pred), 0.0)
    assert np.isclose(r2_score(y_true, y_pred), 1.0)


def test_mismatched_shapes():
    y_true = np.array([1.0, 2.0, 3.0])
    y_pred = np.array([1.0, 2.0])

    with pytest.raises(ValueError):
        mean_absolute_error(y_true, y_pred)


def test_empty_input():
    y_true = np.array([])
    y_pred = np.array([])

    with pytest.raises(ValueError):
        mean_squared_error(y_true, y_pred)


def test_nan_input():
    y_true = np.array([1.0, np.nan, 3.0])
    y_pred = np.array([1.0, 2.0, 3.0])

    with pytest.raises(ValueError):
        mean_absolute_error(y_true, y_pred)


def test_constant_target_r2():
    y_true = np.array([5.0, 5.0, 5.0])
    y_pred = np.array([5.0, 5.0, 5.0])

    with pytest.raises(ValueError):
        r2_score(y_true, y_pred)
