## TV1 - Pipeline dữ liệu Olist

- TV1 phụ trách nạp dữ liệu, audit, làm sạch, tổng hợp, feature engineering, temporal split và preprocessing.
- Dataset là Olist. Một dòng model là `product_category x month`; target là purchase-time item demand tháng kế tiếp tại `order_purchase_timestamp`.
- Usable Olist demand kết thúc ở 2018-08; trailing incomplete period sau mốc này phải bị loại trước khi tạo calendar, lag và target.
- Không dùng sklearn hoặc thư viện ML estimator. Phải chống leakage và chỉ fit preprocessing trên train.
- Raw CSV là bất biến. Dữ liệu processed phải tái tạo được từ raw CSV.
- EDA phải được sinh bằng code từ dữ liệu thật; không thêm hoặc chỉnh tay biểu đồ/số liệu trong `reports/figures/`.
- TV1 không triển khai model, experiment tracking hoặc chọn model cuối.
- Mọi biến đổi quan trọng phải có test.
