from pathlib import Path
import csv
from datetime import datetime


LOG_DIR = Path("logs")
EXPERIMENT_LOG = LOG_DIR / "experiments.csv"


FIELDNAMES = [
    "run_id",
    "timestamp",
    "dataset",
    "aggregation",
    "target",
    "train_period",
    "validation_period",
    "test_period",
    "model",
    "params",
    "feature_version",
    "train_mae",
    "train_mse",
    "train_rmse",
    "train_r2",
    "validation_mae",
    "validation_mse",
    "validation_rmse",
    "validation_r2",
    "status",
]


def _ensure_log_directory():
    """Create the log directory if it does not already exist."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_experiment_file():
    """Create experiments.csv with the required header if needed."""
    _ensure_log_directory()

    if not EXPERIMENT_LOG.exists():
        with EXPERIMENT_LOG.open(
            mode="w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()


def log_experiment(
    run_id,
    dataset,
    aggregation,
    target,
    train_period,
    validation_period,
    test_period,
    model,
    params,
    feature_version,
    train_metrics,
    validation_metrics,
    status="completed",
):
    """
    Append one experiment result to experiments.csv.

    Test metrics are intentionally not stored for regular experiments.
    The test set is reserved for final evaluation.
    """
    _ensure_experiment_file()

    row = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "dataset": dataset,
        "aggregation": aggregation,
        "target": target,
        "train_period": train_period,
        "validation_period": validation_period,
        "test_period": test_period,
        "model": model,
        "params": str(params),
        "feature_version": feature_version,
        "train_mae": train_metrics.get("mae"),
        "train_mse": train_metrics.get("mse"),
        "train_rmse": train_metrics.get("rmse"),
        "train_r2": train_metrics.get("r2"),
        "validation_mae": validation_metrics.get("mae"),
        "validation_mse": validation_metrics.get("mse"),
        "validation_rmse": validation_metrics.get("rmse"),
        "validation_r2": validation_metrics.get("r2"),
        "status": status,
    }

    with EXPERIMENT_LOG.open(
        mode="a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow(row)


def read_experiments():
    """
    Read all experiment records from experiments.csv.

    Returns
    -------
    list[dict]
        A list of experiment records.
    """
    _ensure_experiment_file()

    with EXPERIMENT_LOG.open(
        mode="r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)
        return list(reader)


def get_log_path():
    """Return the path to the experiment log file."""
    _ensure_experiment_file()
    return EXPERIMENT_LOG
