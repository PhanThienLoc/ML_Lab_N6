from __future__ import annotations

import numpy as np
import pandas as pd

from src.predict import predict_scenarios
from src.prediction_policy import postprocess_sales_predictions
from src.preprocessing import fit_preprocessor


class NegativeModel:
    def predict(self, X):
        return np.array([-3.0] * len(X))


def test_count_prediction_policy_clips_negative_values() -> None:
    clipped = postprocess_sales_predictions(np.array([-2.5, 0.0, 4.0]))
    assert np.array_equal(clipped, np.array([0.0, 0.0, 4.0]))


def test_prediction_uses_saved_preprocessor_and_keeps_count_nonnegative() -> None:
    train = pd.DataFrame(
        {
            "sales_current": [1.0, 3.0],
            "product_category": ["a", "b"],
        }
    )
    preprocessor = fit_preprocessor(train, ["sales_current"], ["product_category"])
    bundle = {
        "model": NegativeModel(),
        "preprocessor": preprocessor,
        "feature_names": list(preprocessor.feature_names),
        "prediction_postprocessing": "clip_to_zero_for_nonnegative_sales_count",
    }
    new_scenario = pd.DataFrame(
        {"sales_current": [10.0], "product_category": ["new_category"]}
    )

    predictions = predict_scenarios(bundle, new_scenario)

    assert np.array_equal(predictions, np.array([0.0]))
