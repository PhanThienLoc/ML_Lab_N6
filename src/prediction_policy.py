"""Inference policy for the non-negative product-sales target."""

from __future__ import annotations

import numpy as np


PREDICTION_POLICY_NAME = "clip_to_zero_for_nonnegative_sales_count"


def postprocess_sales_predictions(predictions) -> np.ndarray:
    """Return finite product-sales count predictions constrained to zero or above.

    The scratch Linear Regression model is unconstrained and can return a
    negative number even though ``sales_next_month`` is an order-item count.
    The same post-processing is therefore applied during validation, final
    test evaluation, and CLI inference.
    """

    values = np.asarray(predictions, dtype=float)
    if values.ndim != 1:
        raise ValueError("Predictions must be a one-dimensional array.")
    if not np.isfinite(values).all():
        raise ValueError("Predictions contain NaN or infinite values.")
    return np.maximum(values, 0.0)
