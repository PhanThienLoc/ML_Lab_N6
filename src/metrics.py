import numpy as np


def _validate_inputs(y_true, y_pred):
    """
    Validate and convert the input arrays.

    Parameters
    ----------
    y_true : array-like
        True target values.
    y_pred : array-like
        Predicted target values.

    Returns
    -------
    tuple
        Validated NumPy arrays with the same shape.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    if y_true.shape != y_pred.shape:
        raise ValueError("y_true and y_pred must have the same shape.")

    if y_true.ndim != 1:
        raise ValueError("y_true and y_pred must be one-dimensional arrays.")

    if len(y_true) == 0:
        raise ValueError("y_true and y_pred must not be empty.")

    if not np.all(np.isfinite(y_true)):
        raise ValueError("y_true contains NaN or infinite values.")

    if not np.all(np.isfinite(y_pred)):
        raise ValueError("y_pred contains NaN or infinite values.")

    return y_true, y_pred


def mean_absolute_error(y_true, y_pred):
    """
    Calculate Mean Absolute Error (MAE).

    MAE = mean(abs(y_true - y_pred))
    """
    y_true, y_pred = _validate_inputs(y_true, y_pred)

    return float(np.mean(np.abs(y_true - y_pred)))


def mean_squared_error(y_true, y_pred):
    """
    Calculate Mean Squared Error (MSE).

    MSE = mean((y_true - y_pred) ** 2)
    """
    y_true, y_pred = _validate_inputs(y_true, y_pred)

    return float(np.mean((y_true - y_pred) ** 2))


def root_mean_squared_error(y_true, y_pred):
    """
    Calculate Root Mean Squared Error (RMSE).

    RMSE = sqrt(MSE)
    """
    mse = mean_squared_error(y_true, y_pred)

    return float(np.sqrt(mse))


def r2_score(y_true, y_pred):
    """
    Calculate the coefficient of determination (R²).

    R² = 1 - SS_res / SS_tot
    """
    y_true, y_pred = _validate_inputs(y_true, y_pred)

    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)

    if np.isclose(ss_tot, 0.0):
        raise ValueError(
            "R² is undefined when all true target values are identical."
        )

    return float(1.0 - (ss_res / ss_tot))


def regression_metrics(y_true, y_pred):
    """
    Calculate all required regression metrics.

    Returns
    -------
    dict
        Dictionary containing MAE, MSE, RMSE, and R².
    """
    return {
        "mae": mean_absolute_error(y_true, y_pred),
        "mse": mean_squared_error(y_true, y_pred),
        "rmse": root_mean_squared_error(y_true, y_pred),
        "r2": r2_score(y_true, y_pred),
    }
