# Bàn giao TV1 - Leakage-safe Olist arrays

## Biểu diễn bài toán

Mỗi model row là một `product_category × feature_month`. Ở cuối feature month *t*, nó dự đoán purchase-time item demand cho *t+1*.

## Target

`sales_next_month` = purchase-time order-item demand của category trong tháng lịch kế tiếp. Target không nằm trong `X`.

## Raw input, join và làm sạch

Raw MVP files: `olist_orders_dataset.csv, olist_order_items_dataset.csv, olist_products_dataset.csv, product_category_name_translation.csv`.

- `orders (valid purchase timestamp)` -> `order_items` on `order_id` (one_to_many).
- `orders + order_items` -> `products` on `product_id` (many_to_one).
- `orders + items + products` -> `category_translation` on `product_category_name` (many_to_one).

- Chính sách sales event: `Count order-item demand at order_purchase_timestamp; include every order status with a valid purchase timestamp.`
- Chính sách order status: `Audit only; final order status is not used to select demand events.`
- Category dùng English translation nếu có, source category nếu không, sau cùng là `unknown_category`.
- Purchase timestamp không hợp lệ bị loại trước aggregate. Giá trị price/freight âm chỉ được audit, không tự sửa.

## Forecast cutoff và bảo vệ leakage

- Grid mỗi category bắt đầu ở first observed purchase month; không pre-history nào bị bịa.
- Demand usable kết thúc ở `2018-08`; trailing incomplete period sau cutoff bị loại trước khi tạo target.
- Demand được gán tại `order_purchase_timestamp`; final order status sau cutoff không được dùng.
- Sales lag là history shift tường minh sau monthly calendar grid.
- `rolling_sales_mean_3` chỉ dùng *t*, *t-1* và *t-2*.
- Split dựa trên `target_month`, không random row.
- One-hot category, missing-value median, mean và standard deviation chỉ fit trên train.
- Category ở validation/test chưa thấy trong train được chấp nhận và mã hóa all-zero.

## Ordered model feature schema

- `sales_current`
- `sales_lag_1`
- `sales_lag_2`
- `sales_lag_3`
- `rolling_sales_mean_3`
- `month_sin`
- `month_cos`
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
| train | 755 × 90 | float64 | 2017-01..2018-02 |
| validation | 219 × 90 | float64 | 2018-03..2018-05 |
| test | 219 × 90 | float64 | 2018-06..2018-08 |

## Cách gọi

```python
from src.pipeline import prepare_data

prepared = prepare_data('data/raw')
X_train, y_train = prepared['X_train'], prepared['y_train']
X_val, y_val = prepared['X_val'], prepared['y_val']
X_test, y_test = prepared['X_test'], prepared['y_test']
metadata = prepared['metadata']
```

`X_*` là pandas DataFrame có thứ tự cột giống nhau và finite float. `y_*` là pandas Series float. TV2 chỉ đổi `.to_numpy()` khi implementation cần NumPy; TV3 đọc split period/feature name từ `metadata` và không fit preprocessing lại.

## Preprocessing và xác minh

- One-hot category level chỉ học từ train; category xuất hiện sau đó thành all-zero vector.
- Missing numerical value dùng train median. Mean/std chỉ fit từ train, sau đó tái sử dụng bất biến cho validation/test.
- Preprocessing state tái lập được ở `data/processed/preprocessing_metadata.json`.
- Ba EDA PNG được pipeline sinh lại tại `reports/figures/` và được nhúng trong `reports/data_analysis.md`; không có biểu đồ được chỉnh tay.
- Evidence scoped-prompt nằm trong `ai/results/`; chạy `python -m pytest -q` trước mọi handoff revision.

## Giới hạn đã biết

Artifact là forecast category theo tháng, không phải SKU. Price/freight/product mean không có ở zero-demand month; fallback past-only/train-only được mô tả trong `data_analysis.md` và metadata. First observed purchase month không khẳng định đây là ngày launch thật của category.
