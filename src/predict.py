"""CLI inference for new product-category monthly scenarios."""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.prediction_policy import PREDICTION_POLICY_NAME, postprocess_sales_predictions


MODEL_PATH = Path("logs/best_model.pkl")


def load_model_bundle(model_path: str | Path = MODEL_PATH) -> dict[str, Any]:
    """Load and validate the final model together with train-only preprocessing."""

    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError("Best model bundle was not found. Run 'python main.py' first.")
    with path.open("rb") as file:
        bundle = pickle.load(file)
    required = {"model", "preprocessor", "feature_names", "prediction_postprocessing"}
    if not isinstance(bundle, dict) or required.difference(bundle):
        raise ValueError("Model artifact is not a valid model bundle. Run 'python main.py' again.")
    if bundle["prediction_postprocessing"] != PREDICTION_POLICY_NAME:
        raise ValueError("Model bundle uses an unsupported prediction policy.")
    return bundle


def load_scenario_file(path: str | Path) -> pd.DataFrame:
    """Load one or more raw, feature-month scenarios from a CSV file."""

    scenario_path = Path(path)
    if not scenario_path.exists():
        raise FileNotFoundError(f"Scenario file was not found: {scenario_path}")
    scenarios = pd.read_csv(scenario_path)
    if scenarios.empty:
        raise ValueError("Scenario file must contain at least one row.")
    return scenarios


def predict_scenarios(bundle: dict[str, Any], scenarios: pd.DataFrame) -> np.ndarray:
    """Transform new scenarios with saved train state and predict non-negative sales."""

    preprocessor = bundle["preprocessor"]
    matrix = preprocessor.transform(scenarios)
    if list(matrix.columns) != list(bundle["feature_names"]):
        raise AssertionError("Scenario transformation did not preserve the saved feature order.")
    raw_predictions = bundle["model"].predict(matrix)
    return postprocess_sales_predictions(raw_predictions)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Predict next-month product sales for one or more new feature-month scenarios."
    )
    parser.add_argument(
        "--scenario-file",
        required=True,
        help="CSV containing raw feature-month fields; see examples/prediction_scenario.csv.",
    )
    parser.add_argument(
        "--model-path",
        default=str(MODEL_PATH),
        help="Saved model bundle produced by 'python main.py'.",
    )
    args = parser.parse_args()

    bundle = load_model_bundle(args.model_path)
    scenarios = load_scenario_file(args.scenario_file)
    predictions = predict_scenarios(bundle, scenarios)

    print("=" * 60)
    print("PRODUCT SALES PREDICTION DEMO")
    print("=" * 60)
    print(f"Model: {bundle.get('model_name', 'unknown')}")
    print(f"Scenarios: {len(scenarios)}")
    print("Policy: sales predictions are clipped to a minimum of 0.")
    for index, prediction in enumerate(predictions, start=1):
        print(f"Scenario {index}: predicted next-month sales = {prediction:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
