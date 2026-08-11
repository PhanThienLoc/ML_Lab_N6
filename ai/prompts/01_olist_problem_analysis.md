# Olist Problem Analysis

## Context

The project uses the Brazilian E-Commerce Public Dataset by Olist.

The main data files are:

- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_products_dataset.csv`
- `product_category_name_translation.csv`

## Goal

Build a dataset at the `product_category × month` level to predict sales for the following month.

The target variable is:

`sales_next_month`

## Task

Analyze the following aspects:

1. Join plan between the datasets.
2. Join keys and cardinality.
3. Data cleaning rules.
4. Monthly aggregation strategy.
5. Target definition.
6. Feature engineering strategy.
7. Potential data leakage risks.

## Constraints

- Do not create features that cannot be derived from the source data.
- Do not use future information.
- Clearly identify join keys and cardinality.
- Do not use pre-built Machine Learning estimators for the required from-scratch models.
- Complete the analysis before writing implementation code.

## Expected Output

The analysis should provide:

1. Join plan.
2. Cleaning rules.
3. Aggregation strategy.
4. Target definition.
5. Feature list.
6. Potential data leakage risks.
