import csv
import json
from datetime import datetime
from pathlib import Path


DEFAULT_LOG_PATH = Path("logs/experiments.csv")

FIELDNAMES = [
    "run_id",
    "timestamp",
    "dataset",
    "aggregation",
    "target",
    "feature_version",
    "split_method",
    "train_period",
    "validation_period",
    "test_period",
    "model",
    "params",
    "train_mae",
    "train_mse",
    "train_rmse",
    "train_r2",
    "validation_mae",
    "validation_mse",
    "validation_rmse",
    "validation_r2",
    "prediction_postprocessing",
    "status",
    "notes",
]


def initialise_experiment_log(log_path=DEFAULT_LOG_PATH, *, overwrite=False):
    """Create an experiment CSV, optionally replacing a previous batch.

    The project uses fixed run IDs such as ``LR003``. A fresh official run must
    therefore start with a fresh CSV; appending would create duplicate IDs and
    make the evidence ambiguous.
    """

    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if overwrite or not log_path.exists():
        with log_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()

    return log_path


def _ensure_log_file(log_path=DEFAULT_LOG_PATH):
    return initialise_experiment_log(log_path, overwrite=False)


def _serialize(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False)

    return value


def log_experiment(record, log_path=DEFAULT_LOG_PATH):
    log_path = _ensure_log_file(log_path)

    row = {}

    for field in FIELDNAMES:
        row[field] = _serialize(record.get(field, ""))

    if not row["timestamp"]:
        row["timestamp"] = datetime.now().isoformat(timespec="seconds")

    with log_path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow(row)

    return log_path


def read_experiments(log_path=DEFAULT_LOG_PATH):
    log_path = Path(log_path)

    if not log_path.exists():
        return []

    with log_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def get_log_path():
    return DEFAULT_LOG_PATH
