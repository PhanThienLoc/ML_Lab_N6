# Decision Log

This document records important decisions made during the development of the Product Sales Prediction project.

---

## Decision 001 - Problem Type

### Decision

The project is defined as a Supervised Learning Regression problem.

### Reason

The target variable `sales_next_month` is a continuous numerical value, and the objective is to predict the sales value for the following month.

### Impact

Regression models and regression evaluation metrics will be used throughout the project.

---

## Decision 002 - Dataset Aggregation

### Decision

The dataset is aggregated at the `product_category × month` level.

### Reason

This aggregation is appropriate for predicting the sales of each product category in the following month.

### Impact

The aggregated dataset will be used to construct features and the target variable `sales_next_month`.

---

## Decision 003 - Temporal Data Split

### Decision

The dataset is divided into training, validation, and test sets according to chronological order.

### Reason

The project is a time-dependent prediction problem. Future information must not be used to train the model or construct historical features.

### Impact

The validation set is used for model and hyperparameter selection, while the test set is reserved for final evaluation.

---

## Decision 004 - Machine Learning Models

### Decision

The project uses:

1. Mean Baseline
2. Linear Regression from Scratch
3. Decision Tree Regression from Scratch

### Reason

These models provide a baseline and two required regression approaches for comparison.

### Impact

All models will be evaluated using the same validation metrics.

---

## Decision 005 - Evaluation Metrics

### Decision

The project uses:

- MAE
- MSE
- RMSE
- R²

### Reason

These metrics are appropriate for evaluating regression models and provide different views of prediction error and model performance.

### Impact

The validation metrics will be recorded in the experiment log and used to compare different runs.

---

## Decision 006 - Test Set Usage

### Decision

The test set will only be used for final evaluation.

### Reason

Using the test set during model selection would introduce evaluation bias and violate the separation between model selection and final evaluation.

### Impact

The best model must be selected using validation performance before the final test evaluation is performed.
