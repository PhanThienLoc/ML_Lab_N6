import os
import sys

import numpy as np


sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
        )
    ),
)


from src.models.baseline import MeanBaseline
from src.models.linear_regression import LinearRegressionScratch
from src.models.decision_tree import DecisionTreeRegressorScratch


def test_linear_toy_line():
    """
    Verify that Linear Regression learns y approximately equal to 2x + 3.
    """
    np.random.seed(42)

    X = np.linspace(
        0,
        10,
        100,
    ).reshape(-1, 1)

    y = (
        2 * X.ravel()
        + 3
        + np.random.normal(
            0,
            0.01,
            size=100,
        )
    )

    model = LinearRegressionScratch(
        learning_rate=0.01,
        epochs=3000,
    )

    model.fit(X, y)

    weight = model.weights[0]
    bias = model.bias

    assert np.isclose(
        weight,
        2.0,
        atol=0.1,
    )

    assert np.isclose(
        bias,
        3.0,
        atol=0.1,
    )


def test_loss_trend():
    """
    Verify that Gradient Descent reduces the loss.
    """
    np.random.seed(42)

    X = np.random.rand(
        50,
        3,
    )

    y = (
        X
        @ np.array(
            [1.5, -2.0, 3.0]
        )
        + 0.5
    )

    model = LinearRegressionScratch(
        learning_rate=0.05,
        epochs=200,
    )

    model.fit(X, y)

    loss_history = model.loss_history

    assert len(loss_history) >= 2

    assert (
        loss_history[-1]
        < loss_history[0]
    )


def test_tree_simple_split():
    """
    Verify that the Decision Tree separates two simple target regions.
    """
    X = np.array(
        [
            [1],
            [2],
            [3],
            [10],
            [11],
            [12],
        ],
        dtype=float,
    )

    y = np.array(
        [
            10.0,
            10.0,
            10.0,
            100.0,
            100.0,
            100.0,
        ],
        dtype=float,
    )

    tree = DecisionTreeRegressorScratch(
        max_depth=2,
        min_samples_split=2,
    )

    tree.fit(X, y)

    preds_low = tree.predict(
        [
            [1.5],
            [2.5],
        ]
    )

    preds_high = tree.predict(
        [
            [10.5],
            [11.5],
        ]
    )

    assert np.allclose(
        preds_low,
        10.0,
    )

    assert np.allclose(
        preds_high,
        100.0,
    )


def test_shape_test():
    """
    Verify the output shape of all models.
    """
    np.random.seed(42)

    X_train = np.random.randn(
        20,
        4,
    )

    y_train = np.random.randn(20)

    X_test = np.random.randn(
        5,
        4,
    )

    models = [
        MeanBaseline(),

        LinearRegressionScratch(
            learning_rate=0.01,
            epochs=10,
        ),

        DecisionTreeRegressorScratch(
            max_depth=3,
        ),
    ]

    for model in models:
        model.fit(
            X_train,
            y_train,
        )

        predictions = model.predict(
            X_test
        )

        assert predictions.ndim == 1

        assert predictions.shape[0] == 5


def test_constant_target():
    """
    Verify stable predictions when all target values are identical.
    """
    X = np.array(
        [
            [1, 2],
            [3, 4],
            [5, 6],
            [7, 8],
        ],
        dtype=float,
    )

    y = np.array(
        [
            7.5,
            7.5,
            7.5,
            7.5,
        ],
        dtype=float,
    )

    models = [
        MeanBaseline(),

        LinearRegressionScratch(
            learning_rate=0.01,
            epochs=3000,
        ),

        DecisionTreeRegressorScratch(
            max_depth=3,
        ),
    ]

    for model in models:
        model.fit(
            X,
            y,
        )

        predictions = model.predict(X)

        assert np.allclose(
            predictions,
            7.5,
            atol=0.02,
        )
