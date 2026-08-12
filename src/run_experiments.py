import json
import pickle
from pathlib import Path

import numpy as np

from src.analyze_logs import get_best_run
from src.experiment import run_experiment
from src.logger import initialise_experiment_log
from src.metrics import regression_metrics

from src.models import (
    MeanBaseline,
    LinearRegressionScratch,
    DecisionTreeRegressorScratch,
)
from src.prediction_policy import PREDICTION_POLICY_NAME, postprocess_sales_predictions

from src.pipeline import prepare_data


EXPERIMENT_LOG = Path("logs/experiments.csv")
FINAL_TEST_PATH = Path("logs/final_test.json")
BEST_MODEL_PATH = Path("logs/best_model.pkl")


def build_model(model_type, params):
    if model_type == "baseline":
        return MeanBaseline()

    if model_type == "linear_regression":
        return LinearRegressionScratch(**params)

    if model_type == "decision_tree":
        return DecisionTreeRegressorScratch(**params)

    raise ValueError(
        f"Unknown model type: {model_type}"
    )


def get_period(
    metadata,
    split_name,
    fallback,
):
    direct_key = f"{split_name}_period"

    if direct_key in metadata:
        return str(metadata[direct_key])

    for container_name in (
        "temporal_split",
        "time_split_boundaries",
        "split_periods",
        "splits",
    ):
        container = metadata.get(container_name)

        if not isinstance(container, dict):
            continue

        value = container.get(split_name)

        if value is None:
            continue

        if isinstance(value, dict):
            start = value.get(
                "start",
                value.get("start_month", value.get("target_month_start")),
            )

            end = value.get(
                "end",
                value.get("end_month", value.get("target_month_end")),
            )

            if start is not None and end is not None:
                return f"{start}..{end}"

        return str(value)

    return fallback


def main():
    print("=" * 70)
    print("OLIST PRODUCT SALES - FULL EXPERIMENT PIPELINE")
    print("=" * 70)

    print("\n[1] Loading and preparing data...")

    prepared = prepare_data(
        raw_dir="data/raw"
    )

    X_train = prepared["X_train"]
    y_train = prepared["y_train"]

    X_val = prepared["X_val"]
    y_val = prepared["y_val"]

    X_test = prepared["X_test"]
    y_test = prepared["y_test"]

    source_metadata = prepared.get(
        "metadata",
        {},
    )

    metadata = {
        "dataset": "olist_brazilian_ecommerce",
        "aggregation": "product_category_month",
        "target": "sales_next_month",
        "feature_version": str(
            source_metadata.get(
                "feature_version",
                "v1",
            )
        ),
        "split_method": "temporal",
        "train_period": get_period(
            source_metadata,
            "train",
            "2017-01..2018-02",
        ),
        "validation_period": get_period(
            source_metadata,
            "validation",
            "2018-03..2018-05",
        ),
        "test_period": get_period(
            source_metadata,
            "test",
            "2018-06..2018-08",
        ),
        "prediction_postprocessing": PREDICTION_POLICY_NAME,
    }

    print(
        f"Train samples: {len(y_train)}"
    )

    print(
        f"Validation samples: {len(y_val)}"
    )

    print(
        f"Test samples: {len(y_test)}"
    )

    experiment_configs = [
        {
            "run_id": "BASE001",
            "model_type": "baseline",
            "model_name": "MeanBaseline",
            "params": {},
        },
        {
            "run_id": "LR001",
            "model_type": "linear_regression",
            "model_name": "LinearRegressionScratch",
            "params": {
                "learning_rate": 0.0005,
                "epochs": 3000,
                "tol": 1e-8,
            },
        },
        {
            "run_id": "LR002",
            "model_type": "linear_regression",
            "model_name": "LinearRegressionScratch",
            "params": {
                "learning_rate": 0.001,
                "epochs": 3000,
                "tol": 1e-8,
            },
        },
        {
            "run_id": "LR003",
            "model_type": "linear_regression",
            "model_name": "LinearRegressionScratch",
            "params": {
                "learning_rate": 0.005,
                "epochs": 3000,
                "tol": 1e-8,
            },
        },
        {
            "run_id": "LR004",
            "model_type": "linear_regression",
            "model_name": "LinearRegressionScratch",
            "params": {
                "learning_rate": 0.01,
                "epochs": 3000,
                "tol": 1e-8,
            },
        },
        {
            "run_id": "TREE001",
            "model_type": "decision_tree",
            "model_name": "DecisionTreeRegressorScratch",
            "params": {
                "max_depth": 2,
                "min_samples_split": 5,
            },
        },
        {
            "run_id": "TREE002",
            "model_type": "decision_tree",
            "model_name": "DecisionTreeRegressorScratch",
            "params": {
                "max_depth": 3,
                "min_samples_split": 10,
            },
        },
        {
            "run_id": "TREE003",
            "model_type": "decision_tree",
            "model_name": "DecisionTreeRegressorScratch",
            "params": {
                "max_depth": 4,
                "min_samples_split": 10,
            },
        },
    ]

    print(
        f"\n[2] Running {len(experiment_configs)} experiments..."
    )

    initialise_experiment_log(EXPERIMENT_LOG, overwrite=True)
    print(f"Started a fresh experiment batch: {EXPERIMENT_LOG}")

    successful_results = []

    for config in experiment_configs:
        print(
            f"\nRunning {config['run_id']} "
            f"- {config['model_name']}"
        )

        model = build_model(
            config["model_type"],
            config["params"],
        )

        try:
            result = run_experiment(
                run_id=config["run_id"],
                model=model,
                model_name=config["model_name"],
                params=config["params"],
                X_train=X_train,
                y_train=y_train,
                X_val=X_val,
                y_val=y_val,
                metadata=metadata,
                log_path=EXPERIMENT_LOG,
            )

            successful_results.append(
                result
            )

            metrics = result[
                "validation_metrics"
            ]

            print(
                f"Validation MAE: "
                f"{metrics['mae']:.4f}"
            )

            print(
                f"Validation RMSE: "
                f"{metrics['rmse']:.4f}"
            )

            print(
                f"Validation R2: "
                f"{metrics['r2']:.4f}"
            )

        except Exception as error:
            print(
                f"Run failed: {error}"
            )

    if not successful_results:
        raise RuntimeError(
            "All experiment runs failed."
        )

    print("\n[3] Selecting best model using validation RMSE...")

    best_run = get_best_run(
        metric="validation_rmse",
        log_path=EXPERIMENT_LOG,
    )

    print(
        f"Best run: {best_run['run_id']}"
    )

    print(
        f"Best model: {best_run['model']}"
    )

    print(
        "Validation RMSE:",
        best_run["validation_rmse"],
    )

    best_config = None

    for config in experiment_configs:
        if config["run_id"] == best_run["run_id"]:
            best_config = config
            break

    if best_config is None:
        raise RuntimeError(
            "The best run configuration could not be found."
        )

    print("\n[4] Training final model using train + validation...")

    X_train_final = np.vstack(
        [
            np.asarray(X_train),
            np.asarray(X_val),
        ]
    )

    y_train_final = np.concatenate(
        [
            np.asarray(y_train).ravel(),
            np.asarray(y_val).ravel(),
        ]
    )

    final_model = build_model(
        best_config["model_type"],
        best_config["params"],
    )

    final_model.fit(
        X_train_final,
        y_train_final,
    )

    print("\n[5] Running final test evaluation ONCE...")

    test_predictions = postprocess_sales_predictions(final_model.predict(X_test))

    test_metrics = regression_metrics(
        y_test,
        test_predictions,
    )

    final_result = {
        "dataset": metadata["dataset"],
        "aggregation": metadata["aggregation"],
        "target": metadata["target"],
        "test_period": metadata["test_period"],
        "selected_run": best_config["run_id"],
        "model": best_config["model_name"],
        "params": best_config["params"],
        "prediction_postprocessing": PREDICTION_POLICY_NAME,
        "test_mae": test_metrics["mae"],
        "test_mse": test_metrics["mse"],
        "test_rmse": test_metrics["rmse"],
        "test_r2": test_metrics["r2"],
    }

    FINAL_TEST_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with FINAL_TEST_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            final_result,
            file,
            indent=4,
        )

    model_bundle = {
        "bundle_version": 1,
        "model": final_model,
        "preprocessor": prepared["preprocessor"],
        "feature_names": list(source_metadata["feature_names"]),
        "source_numerical_features": list(source_metadata["source_numerical_features"]),
        "source_categorical_features": list(source_metadata["source_categorical_features"]),
        "target_name": metadata["target"],
        "prediction_postprocessing": PREDICTION_POLICY_NAME,
        "selected_run": best_config["run_id"],
        "model_name": best_config["model_name"],
        "params": best_config["params"],
    }

    with BEST_MODEL_PATH.open("wb") as file:
        pickle.dump(
            model_bundle,
            file,
        )

    print("\n" + "=" * 70)
    print("FINAL TEST RESULT")
    print("=" * 70)

    print(
        f"Selected Run: "
        f"{best_config['run_id']}"
    )

    print(
        f"Model: "
        f"{best_config['model_name']}"
    )

    print(
        f"Test MAE: "
        f"{test_metrics['mae']:.4f}"
    )

    print(
        f"Test MSE: "
        f"{test_metrics['mse']:.4f}"
    )

    print(
        f"Test RMSE: "
        f"{test_metrics['rmse']:.4f}"
    )

    print(
        f"Test R2: "
        f"{test_metrics['r2']:.4f}"
    )

    print(
        f"\nExperiment log: "
        f"{EXPERIMENT_LOG}"
    )

    print(
        f"Final test result: "
        f"{FINAL_TEST_PATH}"
    )

    print(
        f"Best model file: "
        f"{BEST_MODEL_PATH}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()
