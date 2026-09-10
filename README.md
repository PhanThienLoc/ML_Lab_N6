# Dự đoán Purchase Amount — Customer Shopping Trends

## Bài toán

Mỗi dòng là một bản ghi mua hàng. Mục tiêu product_sales_amount_usd được ánh xạ từ Purchase Amount (USD), vì vậy đây là supervised regression. Không còn aggregation theo tháng hay target next-month.

## Nguồn dữ liệu

Dataset migration hiện hành: Customer Shopping Trends Dataset  
Kaggle: https://www.kaggle.com/datasets/iamsouravbanerjee/customer-shopping-trends-dataset

Đặt file shopping_trends.csv vào data/raw/ (raw không commit).

## Chạy nhanh

powershell
python -m pip install -r requirements.txt
python -m src.run_data_pipeline --raw-dir data/raw
python -m pytest -q
python main.py
python -m src.predict --scenario-file examples/prediction_scenario.csv

Pipeline dùng random split 70/15/15, seed 42, preprocessing và popularity mappings fit trên train. Kết quả nằm tại data/processed/, reports/figures/, logs/.

Lịch sử Olist và các prompt audit cũ được giữ trong ai/ như archive/superseded record.

