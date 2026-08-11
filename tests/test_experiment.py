import numpy as np

from src.experiment import run_experiment


class DummyModel:

    def fit(self, X, y):
        pass

    def predict(self, X):
        return np.ones(len(X)) * 100


def test_run_experiment():

    X_train = np.array([
        [1],
        [2],
        [3]
    ])

    y_train = np.array([
        100,
        120,
        140
    ])

    X_validation = np.array([
        [4],
        [5]
    ])

    y_validation = np.array([
        150,
        160
    ])

    model = DummyModel()

    result = run_experiment(
        model=model,
        model_name="DummyModel",
        X_train=X_train,
        y_train=y_train,
        X_validation=X_validation,
        y_validation=y_validation,
        run_id="TEST_001"
    )

    assert "train_metrics" in result
    assert "validation_metrics" in result
