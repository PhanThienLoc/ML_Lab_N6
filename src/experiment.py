from src.logger import log_experiment
from src.metrics import regression_metrics
from src.prediction_policy import PREDICTION_POLICY_NAME, postprocess_sales_predictions


def run_experiment(
    *,
    run_id,
    model,
    model_name,
    params,
    X_train,
    y_train,
    X_val,
    y_val,
    metadata,
    log_path="logs/experiments.csv",
):
    """
    Train one model configuration and evaluate it on
    the training and validation sets.

    The test set is intentionally not used here.
    """

    base_record = {
        "run_id": run_id,
        "dataset": metadata.get(
            "dataset",
            "olist_brazilian_ecommerce",
        ),
        "aggregation": metadata.get(
            "aggregation",
            "product_category_month",
        ),
        "target": metadata.get(
            "target",
            "sales_next_month",
        ),
        "feature_version": metadata.get(
            "feature_version",
            "v1",
        ),
        "split_method": metadata.get(
            "split_method",
            "temporal",
        ),
        "train_period": metadata.get(
            "train_period",
            "",
        ),
        "validation_period": metadata.get(
            "validation_period",
            "",
        ),
        "test_period": metadata.get(
            "test_period",
            "",
        ),
        "model": model_name,
        "params": params,
        "prediction_postprocessing": metadata.get("prediction_postprocessing", PREDICTION_POLICY_NAME),
    }

    try:
        model.fit(X_train, y_train)

        train_predictions = postprocess_sales_predictions(model.predict(X_train))
        validation_predictions = postprocess_sales_predictions(model.predict(X_val))

        train_metrics = regression_metrics(
            y_train,
            train_predictions,
        )

        validation_metrics = regression_metrics(
            y_val,
            validation_predictions,
        )

        record = {
            **base_record,
            "train_mae": train_metrics["mae"],
            "train_mse": train_metrics["mse"],
            "train_rmse": train_metrics["rmse"],
            "train_r2": train_metrics["r2"],
            "validation_mae": validation_metrics["mae"],
            "validation_mse": validation_metrics["mse"],
            "validation_rmse": validation_metrics["rmse"],
            "validation_r2": validation_metrics["r2"],
            "status": "success",
            "notes": f"prediction_postprocessing={PREDICTION_POLICY_NAME}",
        }

        log_experiment(
            record,
            log_path=log_path,
        )

        return {
            "run_id": run_id,
            "model_name": model_name,
            "params": params,
            "model": model,
            "train_metrics": train_metrics,
            "validation_metrics": validation_metrics,
        }

    except Exception as error:
        record = {
            **base_record,
            "status": "failed",
            "notes": str(error),
        }

        log_experiment(
            record,
            log_path=log_path,
        )

        raise
