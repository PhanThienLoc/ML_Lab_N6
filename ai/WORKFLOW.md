# WORKFLOW — Customer Shopping Trends

1. Đặt shopping_trends.csv vào data/raw/.
2. Chạy python -m src.run_data_pipeline --raw-dir data/raw.
3. Pipeline audit, EDA 10 hình, tạo đặc trưng, random split 70/15/15 seed 42 và train-only preprocessing.
4. Chạy python -m pytest -q.
5. Chạy python main.py để huấn luyện 8 cấu hình scratch, chọn theo validation RMSE và đánh giá test một lần.
6. Chạy python -m src.predict --scenario-file examples/prediction_scenario.csv.

Target product_sales_amount_usd = Purchase Amount (USD), dạng số liên tục. Scratch models được giữ từ dự án trước: MeanBaseline, LinearRegressionScratch, DecisionTreeRegressorScratch. Không dùng sklearn.

