from src.logger import log_experiment
from src.metrics import regression_metrics


def run_experiment(
    model,
    model_name,
    X_train,
    y_train,
    X_validation,
    y_validation,
    dataset="Olist",
    aggregation="product_category x month",
    target="sales_next_month",
    train_period="",
    validation_period="",
    test_period="",
    params=None,
    feature_version="v1",
    run_id="",
):
    """
    Train a model, evaluate it on the training and validation sets,
    and record the experiment.

    The test set is intentionally not used in this function.
    Test evaluation is reserved for the final evaluation stage.
    """

    if params is None:
        params = {}

    # Train the model.
    model.fit(X_train, y_train)

    # Generate predictions.
    train_predictions = model.predict(X_train)
    validation_predictions = model.predict(X_validation)

    # Calculate metrics.
    train_metrics = regression_metrics(
        y_train,
        train_predictions,
    )

    validation_metrics = regression_metrics(
        y_validation,
        validation_predictions,
    )

    # Record the experiment.
    log_experiment(
        run_id=run_id,
        dataset=dataset,
        aggregation=aggregation,
        target=target,
        train_period=train_period,
        validation_period=validation_period,
        test_period=test_period,
        model=model_name,
        params=params,
        feature_version=feature_version,
        train_metrics=train_metrics,
        validation_metrics=validation_metrics,
    )

    return {
        "run_id": run_id,
        "model": model_name,
        "train_metrics": train_metrics,
        "validation_metrics": validation_metrics,
    }
