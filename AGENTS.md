## TV1 - Pipeline dữ liệu Olist

- TV1 phụ trách nạp dữ liệu, audit, làm sạch, tổng hợp, feature engineering, temporal split và preprocessing.
- Dataset là Olist. Một dòng model là `product_category x month`; target là doanh số tháng kế tiếp.
- Không dùng sklearn hoặc thư viện ML estimator. Phải chống leakage và chỉ fit preprocessing trên train.
- Raw CSV là bất biến. Dữ liệu processed phải tái tạo được từ raw CSV.
- TV1 không triển khai model, experiment tracking hoặc chọn model cuối.
- Mọi biến đổi quan trọng phải có test.
