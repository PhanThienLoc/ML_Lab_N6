import json

from src.logger import read_experiments


def get_best_run(
    metric="validation_rmse",
    log_path="logs/experiments.csv",
):
    experiments = read_experiments(log_path)

    valid_runs = []

    for row in experiments:
        if row.get("status") != "success":
            continue

        value = row.get(metric)

        if value in (None, ""):
            continue

        try:
            row[metric] = float(value)
        except ValueError:
            continue

        valid_runs.append(row)

    if not valid_runs:
        raise ValueError(
            "No successful experiment runs were found."
        )

    if metric == "validation_r2":
        best_run = max(
            valid_runs,
            key=lambda row: row[metric],
        )
    else:
        best_run = min(
            valid_runs,
            key=lambda row: row[metric],
        )

    return best_run


def print_best_run(
    metric="validation_rmse",
    log_path="logs/experiments.csv",
):
    best = get_best_run(
        metric=metric,
        log_path=log_path,
    )

    print("=" * 60)
    print("BEST EXPERIMENT")
    print("=" * 60)

    print(f"Run ID: {best['run_id']}")
    print(f"Model: {best['model']}")

    params = best.get("params", "")

    try:
        params = json.loads(params)
    except (json.JSONDecodeError, TypeError):
        pass

    print(f"Parameters: {params}")

    print(
        "Validation MAE:",
        best.get("validation_mae"),
    )

    print(
        "Validation MSE:",
        best.get("validation_mse"),
    )

    print(
        "Validation RMSE:",
        best.get("validation_rmse"),
    )

    print(
        "Validation R2:",
        best.get("validation_r2"),
    )

    print("=" * 60)

    return best


if __name__ == "__main__":
    print_best_run()