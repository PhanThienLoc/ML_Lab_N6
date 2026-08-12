import numpy as np


class Node:
    """
    A node used by the Decision Tree Regressor.
    """

    def __init__(
        self,
        feature_index=None,
        threshold=None,
        left=None,
        right=None,
        value=None,
    ):
        self.feature_index = feature_index
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value

    def is_leaf(self):
        return self.value is not None


class DecisionTreeRegressorScratch:
    """
    Decision Tree Regression implemented from scratch.

    Weighted Mean Squared Error is used to select the best split.
    """

    def __init__(
        self,
        max_depth=5,
        min_samples_split=2,
        min_impurity_decrease=1e-7,
    ):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_impurity_decrease = min_impurity_decrease
        self.root = None

    def _calculate_mse(self, y):
        if len(y) == 0:
            return 0.0

        return float(np.var(y))

    def _best_split(self, X, y):
        n_samples, n_features = X.shape

        best_feature = None
        best_threshold = None
        best_score = float("inf")

        current_mse = self._calculate_mse(y)

        for feature_idx in range(n_features):
            X_column = X[:, feature_idx]
            unique_values = np.unique(X_column)

            if len(unique_values) <= 1:
                continue

            thresholds = (
                unique_values[:-1] + unique_values[1:]
            ) / 2.0

            for threshold in thresholds:
                left_mask = X_column <= threshold
                right_mask = ~left_mask

                if not np.any(left_mask):
                    continue

                if not np.any(right_mask):
                    continue

                y_left = y[left_mask]
                y_right = y[right_mask]

                n_left = len(y_left)
                n_right = len(y_right)

                mse_left = self._calculate_mse(y_left)
                mse_right = self._calculate_mse(y_right)

                weighted_mse = (
                    (n_left / n_samples) * mse_left
                    + (n_right / n_samples) * mse_right
                )

                if weighted_mse < best_score:
                    best_score = weighted_mse
                    best_feature = feature_idx
                    best_threshold = threshold

        impurity_decrease = (
            current_mse - best_score
            if best_feature is not None
            else 0.0
        )

        return (
            best_feature,
            best_threshold,
            impurity_decrease,
        )

    def _build_tree(self, X, y, depth=0):
        n_samples = X.shape[0]

        variance_y = (
            np.var(y)
            if len(y) > 0
            else 0.0
        )

        if (
            depth >= self.max_depth
            or n_samples < self.min_samples_split
            or variance_y < 1e-12
        ):
            leaf_value = (
                float(np.mean(y))
                if len(y) > 0
                else 0.0
            )

            return Node(value=leaf_value)

        (
            best_feature,
            best_threshold,
            impurity_decrease,
        ) = self._best_split(X, y)

        if (
            best_feature is None
            or impurity_decrease < self.min_impurity_decrease
        ):
            leaf_value = float(np.mean(y))
            return Node(value=leaf_value)

        left_mask = X[:, best_feature] <= best_threshold
        right_mask = ~left_mask

        left_child = self._build_tree(
            X[left_mask],
            y[left_mask],
            depth + 1,
        )

        right_child = self._build_tree(
            X[right_mask],
            y[right_mask],
            depth + 1,
        )

        return Node(
            feature_index=best_feature,
            threshold=best_threshold,
            left=left_child,
            right=right_child,
        )

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
            raise ValueError(
                "Training data must not be empty."
            )

        self.root = self._build_tree(
            X,
            y,
            depth=0,
        )

        return self

    def _traverse_tree(self, x, node):
        if node.is_leaf():
            return node.value

        if x[node.feature_index] <= node.threshold:
            return self._traverse_tree(
                x,
                node.left,
            )

        return self._traverse_tree(
            x,
            node.right,
        )

    def predict(self, X):
        if self.root is None:
            raise ValueError(
                "The model has not been trained. Call fit() before predict()."
            )

        X = np.asarray(X, dtype=float)

        if X.ndim == 1:
            X = X.reshape(-1, 1)

        predictions = [
            self._traverse_tree(
                x,
                self.root,
            )
            for x in X
        ]

        return np.array(
            predictions,
            dtype=float,
        )

    def __repr__(self):
        return (
            "DecisionTreeRegressorScratch("
            f"max_depth={self.max_depth}, "
            f"min_samples_split={self.min_samples_split})"
        )
