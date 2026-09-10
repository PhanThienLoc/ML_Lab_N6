# RUN GUIDE — Customer Shopping Trends

1. Tạo môi trường Python và cài requirements:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

2. Tải shopping_trends.csv từ Kaggle và đặt vào data/raw/.

3. Chạy pipeline:
python -m src.run_data_pipeline --raw-dir data/raw

4. Kiểm thử:
python -m pytest -q

5. Huấn luyện, chọn model theo validation RMSE, đánh giá test một lần:
python main.py

6. Dự đoán:
python -m src.predict --scenario-file examples/prediction_scenario.csv

Artifacts: data/processed/customer_shopping_trends_features.csv, data/processed/preprocessing_metadata.json, reports/figures/ (10 EDA figures), logs/.

