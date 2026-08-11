# TV1 Handoff - Leakage-safe Olist arrays

## Problem representation

Each model row is one `product_category × feature_month`. At the end of feature month *t*, it predicts sales quantity for *t+1*.

## Target

`sales_next_month` = category order-item count in the next calendar month. It is not included in `X`.

## Raw inputs, joins, and cleaning

Raw MVP files: `olist_orders_dataset.csv, olist_order_items_dataset.csv, olist_products_dataset.csv, product_category_name_translation.csv`.

- `orders (filtered)` -> `order_items` on `order_id` (one_to_many).
- `orders + order_items` -> `products` on `product_id` (many_to_one).
- `orders + items + products` -> `category_translation` on `product_category_name` (many_to_one).

- Completed-sales policy: include `delivered` orders; exclude `approved, canceled, created, invoiced, processing, shipped, unavailable`.
- Category policy: use English translation when available, source category as fallback, then explicit `unknown_category`.
- Invalid purchase timestamps are excluded before aggregation. Negative price/freight values are audited, not silently corrected.

## Forecast cutoff and leakage guarantees

- Sales lags are explicit history shifts after a complete monthly calendar grid.
- `rolling_sales_mean_3` uses *t*, *t-1*, and *t-2* only.
- Split allocation uses `target_month`, not random rows.
- One-hot categories, missing-value medians, means, and standard deviations are fitted on train only.
- Validation/test categories not seen in train are accepted and encoded as all zeros.

## Ordered model feature schema

- `sales_current`
- `sales_lag_1`
- `sales_lag_2`
- `sales_lag_3`
- `rolling_sales_mean_3`
- `month`
- `quarter`
- `year`
- `orders_current`
- `unique_products_current`
- `avg_price_current`
- `avg_freight_current`
- `avg_product_weight`
- `avg_product_length`
- `avg_product_height`
- `avg_product_width`
- `avg_product_description_length`
- `avg_product_photos_qty`
- `product_category__agro_industry_and_commerce`
- `product_category__air_conditioning`
- `product_category__art`
- `product_category__arts_and_craftmanship`
- `product_category__audio`
- `product_category__auto`
- `product_category__baby`
- `product_category__bed_bath_table`
- `product_category__books_general_interest`
- `product_category__books_imported`
- `product_category__books_technical`
- `product_category__cds_dvds_musicals`
- `product_category__christmas_supplies`
- `product_category__cine_photo`
- `product_category__computers`
- `product_category__computers_accessories`
- `product_category__consoles_games`
- `product_category__construction_tools_construction`
- `product_category__construction_tools_lights`
- `product_category__construction_tools_safety`
- `product_category__cool_stuff`
- `product_category__costruction_tools_garden`
- `product_category__costruction_tools_tools`
- `product_category__diapers_and_hygiene`
- `product_category__drinks`
- `product_category__dvds_blu_ray`
- `product_category__electronics`
- `product_category__fashio_female_clothing`
- `product_category__fashion_bags_accessories`
- `product_category__fashion_childrens_clothes`
- `product_category__fashion_male_clothing`
- `product_category__fashion_shoes`
- `product_category__fashion_sport`
- `product_category__fashion_underwear_beach`
- `product_category__fixed_telephony`
- `product_category__flowers`
- `product_category__food`
- `product_category__food_drink`
- `product_category__furniture_bedroom`
- `product_category__furniture_decor`
- `product_category__furniture_living_room`
- `product_category__furniture_mattress_and_upholstery`
- `product_category__garden_tools`
- `product_category__health_beauty`
- `product_category__home_appliances`
- `product_category__home_appliances_2`
- `product_category__home_comfort_2`
- `product_category__home_confort`
- `product_category__home_construction`
- `product_category__housewares`
- `product_category__industry_commerce_and_business`
- `product_category__kitchen_dining_laundry_garden_furniture`
- `product_category__la_cuisine`
- `product_category__luggage_accessories`
- `product_category__market_place`
- `product_category__music`
- `product_category__musical_instruments`
- `product_category__office_furniture`
- `product_category__party_supplies`
- `product_category__pc_gamer`
- `product_category__perfumery`
- `product_category__pet_shop`
- `product_category__portateis_cozinha_e_preparadores_de_alimentos`
- `product_category__security_and_services`
- `product_category__signaling_and_security`
- `product_category__small_appliances`
- `product_category__small_appliances_home_oven_and_coffee`
- `product_category__sports_leisure`
- `product_category__stationery`
- `product_category__tablets_printing_image`
- `product_category__telephony`
- `product_category__toys`
- `product_category__unknown_category`
- `product_category__watches_gifts`

## Arrays/DataFrames

| split | X shape | y dtype | target-month range |
| --- | --- | --- | --- |
| train | 1036 × 92 | float64 | 2017-01..2018-02 |
| validation | 222 × 92 | float64 | 2018-03..2018-05 |
| test | 222 × 92 | float64 | 2018-06..2018-08 |

## How to call

```python
from src.pipeline import prepare_data

prepared = prepare_data('data/raw')
X_train, y_train = prepared['X_train'], prepared['y_train']
X_val, y_val = prepared['X_val'], prepared['y_val']
X_test, y_test = prepared['X_test'], prepared['y_test']
metadata = prepared['metadata']
```

`X_*` are pandas DataFrames with identical ordered columns and finite floats. `y_*` are float pandas Series. TV2 should convert with `.to_numpy()` only if its implementation requires NumPy arrays. TV3 should read split periods and feature names from `metadata`, and must not refit preprocessing.

## Preprocessing and verification

- One-hot category levels are learned only from train; unknown later categories become an all-zero category vector.
- Missing numerical values use train medians. Numerical means and standard deviations are fitted only from train, then reused unchanged for validation/test.
- The reproducible preprocessing state is in `data/processed/preprocessing_metadata.json`.
- Current scoped-prompt verification evidence is in `ai/results/`; run `python -m pytest -q` before any handoff revision.

## Known limitations

The artifact is a category-level monthly forecast, not an SKU forecast. Price/freight/product means are unavailable in zero-sales months; the explicit past-only/train-only fallback is described in `data_analysis.md` and metadata.
