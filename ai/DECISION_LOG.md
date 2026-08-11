# Decision Log

File này ghi lại các quyết định quan trọng trong quá trình xây dựng project
Predicting Product Sales.

## Decision 001 - Problem Type

### Decision
Xác định bài toán của nhóm là Supervised Learning dạng Regression.

### Reason
Target `sales_next_month` là một biến số liên tục và mục tiêu của nhóm là dự đoán doanh số tháng kế tiếp.

### Impact
Nhóm sử dụng các thuật toán Regression và các metrics phù hợp như MAE, MSE, RMSE và R².

---

## Decision 002 - Dataset Aggregation

### Decision
Dữ liệu được aggregate theo `product_category × month`.

### Reason
Cách aggregate này phù hợp với mục tiêu dự đoán doanh số của từng product category trong tháng kế tiếp.

### Impact
Dataset sau feature engineering sẽ được sử dụng để xây dựng target `sales_next_month`.

---

## Decision 003 - Temporal Split

### Decision
Dữ liệu được chia Train / Validation / Test theo thứ tự thời gian.

### Reason
Bài toán dự đoán doanh số tháng kế tiếp có tính chất dự báo theo thời gian. Không được sử dụng dữ liệu tương lai để huấn luyện hoặc lựa chọn model.

### Impact
Validation được dùng để lựa chọn model và hyperparameters. Test set chỉ được sử dụng cho đánh giá cuối cùng.

---

## Decision 004 - Model Selection

### Decision
Nhóm sử dụng Mean Baseline, Linear Regression và Decision Tree Regression.

### Reason
Các model này được yêu cầu trong phạm vi bài lab và cho phép nhóm so sánh baseline với các mô hình Regression.

### Impact
Các model sẽ được đánh giá bằng cùng một bộ metrics để so sánh.

---

## Decision 005 - Evaluation Metrics

### Decision
Sử dụng MAE, MSE, RMSE và R² để đánh giá model.

### Reason
Các metrics này phù hợp với bài toán Regression và cho phép đánh giá sai số cũng như mức độ giải thích của model.

### Impact
Các validation metrics được ghi vào experiment log để lựa chọn best run.
