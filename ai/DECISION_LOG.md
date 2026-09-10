# DECISION LOG — Customer Shopping Trends

- Dataset hiện hành: Customer Shopping Trends Dataset từ Kaggle.
- Mỗi dòng là một giao dịch mua hàng; không có timestamp và không dự báo next-month.
- Target product_sales_amount_usd ánh xạ từ Purchase Amount (USD), supervised regression.
- Customer ID không được dùng làm đặc trưng.
- Popularity mappings, median, one-hot vocabulary và scaling chỉ fit trên train.
- Split cố định random 70/15/15 với seed 42.
- Giữ ba thuật toán scratch: MeanBaseline, LinearRegressionScratch, DecisionTreeRegressorScratch.
- Olist không còn là dữ liệu/code hoạt động trong project.

