import numpy as np


class LinearRegressionScratch:
    """
    Linear Regression implemented from scratch using Gradient Descent.
    """

    def __init__(self, learning_rate=0.01, epochs=1000, tol=1e-6):
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.tol = tol

        self.weights = None
        self.bias = None
        self.loss_history = []

    def fit(self, X, y):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float).ravel()

        if X.ndim == 1:
            X = X.reshape(-1, 1)

        if X.shape[0] != y.shape[0]:
            raise ValueError(
                "X and y must contain the same number of samples."
            )

        if X.shape[0] == 0:
            raise ValueError("Training data must not be empty.")

        n_samples, n_features = X.shape

        self.weights = np.zeros(n_features, dtype=float)
        self.bias = 0.0
        self.loss_history = []

        for epoch in range(self.epochs):
            y_hat = np.dot(X, self.weights) + self.bias

            error = y_hat - y

            loss = float(np.mean(error ** 2))
            self.loss_history.append(loss)

            if (
                epoch > 0
                and abs(self.loss_history[-2] - loss) < self.tol
            ):
                break

            dw = (2.0 / n_samples) * np.dot(X.T, error)
            db = (2.0 / n_samples) * np.sum(error)

            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db

        return self

    def predict(self, X):
        if self.weights is None or self.bias is None:
            raise ValueError(
                "The model has not been trained. Call fit() before predict()."
            )

        X = np.asarray(X, dtype=float)

        if X.ndim == 1:
            X = X.reshape(-1, 1)

        if X.shape[1] != len(self.weights):
            raise ValueError(
                "X must contain the same number of features used during training."
            )

        return np.dot(X, self.weights) + self.bias

    def __repr__(self):
        return (
            "LinearRegressionScratch("
            f"learning_rate={self.learning_rate}, "
            f"epochs={self.epochs})"
        )
