from __future__ import annotations

from src.analyze_logs import get_best_run
from src.logger import initialise_experiment_log, log_experiment, read_experiments
from src.run_experiments import get_period


def test_fresh_experiment_batch_removes_duplicate_run_history(tmp_path) -> None:
    log_path = tmp_path / "experiments.csv"
    record = {"run_id": "LR003", "status": "success", "model": "LinearRegressionScratch"}
    log_experiment(record, log_path=log_path)
    log_experiment(record, log_path=log_path)
    assert len(read_experiments(log_path)) == 2

    initialise_experiment_log(log_path, overwrite=True)

    assert read_experiments(log_path) == []


def test_best_run_is_ranked_by_validation_metric_not_test_metric(tmp_path) -> None:
    log_path = tmp_path / "experiments.csv"
    log_experiment(
        {
            "run_id": "LR001",
            "status": "success",
            "model": "LinearRegressionScratch",
            "validation_rmse": 20.0,
            "notes": "test metric is intentionally absent",
        },
        log_path=log_path,
    )
    log_experiment(
        {
            "run_id": "LR002",
            "status": "success",
            "model": "LinearRegressionScratch",
            "validation_rmse": 10.0,
            "notes": "test metric is intentionally absent",
        },
        log_path=log_path,
    )

    assert get_best_run(log_path=log_path)["run_id"] == "LR002"


def test_experiment_periods_read_the_temporal_split_metadata() -> None:
    metadata = {
        "temporal_split": {
            "test": {"target_month_start": "2018-06", "target_month_end": "2018-08"}
        }
    }

    assert get_period(metadata, "test", "stale fallback") == "2018-06..2018-08"
