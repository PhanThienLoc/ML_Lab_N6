import csv
from pathlib import Path


LOG_FILE = Path("logs/experiments.csv")


def load_experiments():
    """
    Load all experiment records.
    """
    if not LOG_FILE.exists():
        return []

    with LOG_FILE.open(
        mode="r",
        newline="",
        encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)
        return list(reader)


def get_best_run(metric="validation_rmse"):
    """
    Find the best experiment.

    Lower values are better for:
    - MAE
    - MSE
    - RMSE

    Higher values are better for:
    - R²
    """
    experiments = load_experiments()

    if len(experiments) == 0:
        return None

    if metric == "validation_r2":
        return max(
            experiments,
            key=lambda x: float(x[metric])
        )

    return min(
        experiments,
        key=lambda x: float(x[metric])
    )


def print_best_run(metric="validation_rmse"):
    best = get_best_run(metric)

    if best is None:
        print("No experiments found.")
        return

    print("=" * 50)
    print("BEST RUN")
    print("=" * 50)

    for key, value in best.items():
        print(f"{key}: {value}")
