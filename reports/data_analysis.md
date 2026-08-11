# TV1 Data Analysis - Olist Product Sales

This report is generated from the raw CSV files by `python -m src.run_data_pipeline`; all counts below are observed values, not examples.

## Raw inputs

| table | rows | columns | duplicate rows |
| --- | --- | --- | --- |
| orders | 99441 | 8 | 0 |
| order_items | 112650 | 7 | 0 |
| products | 32951 | 9 | 0 |
| category_translation | 71 | 2 | 0 |

Purchase timestamps range from **2016-09-04T21:15:19** to **2018-10-17T17:30:18**. Invalid or missing purchase timestamps: **0**.

Order-status distribution: `{"approved": 2, "canceled": 625, "created": 5, "delivered": 96478, "invoiced": 314, "processing": 301, "shipped": 1107, "unavailable": 609}`.

Full observed dtypes and per-column missing-value counts are preserved in `data/processed/preprocessing_metadata.json` under `raw_audit`; the pipeline never invents or imputes raw-source values.

## Cleaning and completed-sales policy

- Included statuses: `delivered`. The pipeline uses delivered orders as the defensible completed-sales proxy.
- Excluded statuses observed in the source: `approved, canceled, created, invoiced, processing, shipped, unavailable`.
- Records with an invalid purchase timestamp are excluded before the monthly aggregation.
- An English category is used where translated. Otherwise the source category is retained; if both are absent, the explicit label `unknown_category` is used.
- Price, freight, and product-average attributes are not backfilled from future months: zero-sales month gaps use only an in-category forward fill, then a training-only median during preprocessing.
- No outlier is deleted or capped. The generated descriptive inspection is recorded in metadata under `outlier_summary`.

## Join audit

| left | right | key | expected cardinality | left rows | rows after | unmatched-left rate |
| --- | --- | --- | --- | --- | --- | --- |
| orders (filtered) | order_items | order_id | one_to_many | 96478 | 110197 | 0.00% |
| orders + order_items | products | product_id | many_to_one | 110197 | 110197 | 0.00% |
| orders + items + products | category_translation | product_category_name | many_to_one | 110197 | 110197 | 1.41% |

`pandas.merge(validate=...)` enforces every listed cardinality, so an unexpected many-to-many multiplication fails the pipeline rather than silently inflating sales.

## Category-month representation and target

One row represents one `product_category × feature_month`. The pipeline creates a complete global calendar grid across observed categories and months; a missing transaction month therefore has `sales_current = 0` rather than a skipped lag.

The target is **`sales_next_month`**, the category's item quantity in the immediately following calendar month. It is constructed only after grid completion using a one-row forward group shift. Rows lacking three historical sales lags or a future target are excluded from the model-ready table.

## Final feature specification

| feature | formula | available at | leakage assessment |
| --- | --- | --- | --- |
| sales_current | Count of order-item rows for category in feature month t. | End of month t. | Uses month t only, never t+1. |
| sales_lag_1 | Category sales in t-1 after completing the monthly grid. | End of month t. | Explicit backward shift only. |
| sales_lag_2 | Category sales in t-2 after completing the monthly grid. | End of month t. | Explicit backward shift only. |
| sales_lag_3 | Category sales in t-3 after completing the monthly grid. | End of month t. | Explicit backward shift only. |
| rolling_sales_mean_3 | mean(sales_current(t), sales(t-1), sales(t-2)) | End of month t. | Does not include sales(t+1) or any later value. |
| month | Calendar month number of feature month t. | End of month t. | Derived from the feature-month calendar only. |
| quarter | Calendar quarter of feature month t. | End of month t. | Derived from the feature-month calendar only. |
| year | Calendar year of feature month t. | End of month t. | Derived from the feature-month calendar only. |
| orders_current | Number of distinct delivered order_id values for the category in month t. | End of month t. | Uses delivered orders in month t only. |
| unique_products_current | Number of distinct product_id values for the category in month t. | End of month t. | Uses month t only. |
| avg_price_current | Mean item price for category sales in month t. | End of month t; zero-sales gaps use past-only forward fill then train median. | Neither aggregation nor fill looks into future months. |
| avg_freight_current | Mean freight value for category sales in month t. | End of month t; zero-sales gaps use past-only forward fill then train median. | Neither aggregation nor fill looks into future months. |
| avg_product_weight | Mean product_weight_g of products sold in the category in month t. | End of month t; zero-sales gaps use past-only forward fill then train median. | Neither aggregation nor fill looks into future months. |
| avg_product_length | Mean product_length_cm of products sold in the category in month t. | End of month t; zero-sales gaps use past-only forward fill then train median. | Neither aggregation nor fill looks into future months. |
| avg_product_height | Mean product_height_cm of products sold in the category in month t. | End of month t; zero-sales gaps use past-only forward fill then train median. | Neither aggregation nor fill looks into future months. |
| avg_product_width | Mean product_width_cm of products sold in the category in month t. | End of month t; zero-sales gaps use past-only forward fill then train median. | Neither aggregation nor fill looks into future months. |
| avg_product_description_length | Mean product_description_lenght of products sold in the category in month t. | End of month t; zero-sales gaps use past-only forward fill then train median. | Neither aggregation nor fill looks into future months. |
| avg_product_photos_qty | Mean product_photos_qty of products sold in the category in month t. | End of month t; zero-sales gaps use past-only forward fill then train median. | Neither aggregation nor fill looks into future months. |
| product_category | Category label, one-hot encoded from train categories only. | Known before the forecast cutoff. | No target or future sales used; unknown validation/test categories are all-zero encoded. |

## Temporal split

| split | target start | target end | target months | rows |
| --- | --- | --- | --- | --- |
| train | 2017-01 | 2018-02 | 14 | 1036 |
| validation | 2018-03 | 2018-05 | 3 | 222 |
| test | 2018-06 | 2018-08 | 3 | 222 |

All rows for a target month are placed in one split. The assertions require train < validation < test with no target-month overlap.

## Outlier inspection

| field | non-missing | min | median | p99 | max |
| --- | --- | --- | --- | --- | --- |
| avg_price_current | 1342 | 3.9 | 109.92 | 1162.5652380952372 | 3549.0 |
| avg_freight_current | 1342 | 0.11 | 18.56291928721174 | 62.399516666666635 | 88.56 |
| sales_current | 1480 | 0.0 | 11.0 | 685.0 | 971.0 |

Large values are retained unless an impossible value is found. This is an inspection report, not a clipping rule.

## Manual lag/target sanity samples

The following two chronological samples are generated from the model-ready data. In each row, `sales_next_month` is the next line's `sales_current` for the same category.

### `agro_industry_and_commerce`

| feature month | sales_lag_2 | sales_lag_1 | sales_current | sales_next_month |
| --- | --- | --- | --- | --- |
| 2016-12 | 0.0 | 0.0 | 0 | 3.0 |
| 2017-01 | 0.0 | 0.0 | 3 | 7.0 |
| 2017-02 | 0.0 | 3.0 | 7 | 2.0 |
| 2017-03 | 3.0 | 7.0 | 2 | 0.0 |
| 2017-04 | 7.0 | 2.0 | 0 | 4.0 |
### `air_conditioning`

| feature month | sales_lag_2 | sales_lag_1 | sales_current | sales_next_month |
| --- | --- | --- | --- | --- |
| 2016-12 | 8.0 | 0.0 | 0 | 4.0 |
| 2017-01 | 0.0 | 0.0 | 4 | 11.0 |
| 2017-02 | 0.0 | 4.0 | 11 | 17.0 |
| 2017-03 | 4.0 | 11.0 | 17 | 15.0 |
| 2017-04 | 11.0 | 17.0 | 15 | 7.0 |

## Leakage checks

- `sales_next_month`, `target_month`, and date keys are excluded from every model matrix.
- The lag/target assertion recalculates shifts from the completed panel at every pipeline run.
- Preprocessor parameters are fitted from the train split only and persisted in metadata.
- Train, validation, and test have identical feature order and finite numeric values.

## Limitations and next work

- The target is sales quantity (order-item count), not revenue or customer lifetime value.
- The grid uses all observed months for all observed categories; it does not infer a product-category launch date.
- Olist lacks direct age, gender, campaign, and ad-spend fields, so none are fabricated.
- TV2 owns model algorithms; TV3 owns experiment tracking, model selection, and final metrics.
