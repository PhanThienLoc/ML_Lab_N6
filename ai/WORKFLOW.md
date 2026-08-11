# Machine Learning Workflow

## 1. Problem Definition

The project aims to predict product sales for the following month.

This is a Supervised Learning Regression problem because the target variable, `sales_next_month`, is a continuous numerical value.

## 2. Data Source

The project uses the Brazilian E-Commerce Public Dataset by Olist.

The main data files are:

- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_products_dataset.csv`
- `product_category_name_translation.csv`

## 3. Data Preparation

The datasets are joined using appropriate keys, including:

- `order_id`
- `product_id`
- `product_category_name`

The data preparation process includes:

- Checking missing values.
- Checking duplicate records.
- Checking invalid values.
- Handling order status according to the project policy.
- Verifying join keys and join cardinality.

## 4. Data Aggregation

The data is aggregated at the:

`product_category × month`

level.

The target variable is:

`sales_next_month`

The target represents the sales value of the following month for each product category.

## 5. Feature Engineering

Features are created using historical information only.

Example features include:

- `sales_lag_1`
- `sales_lag_2`
- `sales_lag_3`
- `rolling_sales_mean_3`
- `avg_price`
- `avg_freight`
- `month`
- `quarter`

No future information may be used to construct features.

## 6. Train, Validation, and Test Split

The dataset is split according to chronological order:

- Training set
- Validation set
- Test set

The training set is used to train the models.

The validation set is used to compare models and select hyperparameters.

The test set is used only for the final evaluation after the best model and configuration have been selected.

## 7. Machine Learning Models

The project includes:

1. Mean Baseline
2. Linear Regression from Scratch
3. Decision Tree Regression from Scratch

The required Machine Learning algorithms are implemented from scratch according to the project requirements.

## 8. Model Evaluation

The following regression metrics are used:

- MAE
- MSE
- RMSE
- R²

The validation metrics are used to compare different experiments.

## 9. Experiment Tracking

Important experiments are recorded in:

`logs/experiments.csv`

Each experiment should record relevant information such as:

- Run ID
- Timestamp
- Dataset configuration
- Aggregation level
- Target
- Train/validation/test periods
- Model
- Hyperparameters
- Feature version
- Training metrics
- Validation metrics
- Status

## 10. Model Selection

The best model and configuration are selected based on validation performance.

The test set must not be used to rank models or select hyperparameters.

## 11. Final Evaluation

After selecting the best model and configuration, the model is evaluated on the test set.

The final evaluation results are stored for reporting and presentation.

## 12. Prediction Demo

The selected best model is used to demonstrate prediction of product sales for the following month.

## 13. Overall Workflow

The complete workflow is:

Raw Olist Data

↓

Data Joining and Cleaning

↓

Monthly Product Category Aggregation

↓

Feature Engineering

↓

Temporal Train / Validation / Test Split

↓

Preprocessing

↓

Baseline / Linear Regression / Decision Tree

↓

Validation Metrics

↓

Experiment Logging

↓

Best Run Selection

↓

Final Test Evaluation

↓

Prediction Demo
