import numpy as np


class MeanBaseline:
    """
    Model 0 - Mean Baseline Regressor.

    Predicts every sample using the mean value of y_train.
    """

    def __init__(self):
        self.mean_value = None

    def fit(self, X, y):
        y = np.asarray(y, dtype=float).ravel()

        if len(y) == 0:
            raise ValueError("y_train must not be empty.")

        self.mean_value = float(np.mean(y))
        return self

    def predict(self, X):
        if self.mean_value is None:
            raise ValueError(
                "The model has not been trained. Call fit() before predict()."
            )

        X = np.asarray(X)
        n_samples = X.shape[0] if X.ndim > 0 else 1

        return np.full(
            shape=(n_samples,),
            fill_value=self.mean_value,
            dtype=float,
        )

    def __repr__(self):
        return f"MeanBaseline(mean_value={self.mean_value})"
