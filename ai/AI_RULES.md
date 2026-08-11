# Quy tắc sử dụng AI

## Mục đích

AI là công cụ hỗ trợ học tập, thiết kế, cài đặt, debug, tài liệu và review code trong project ML.

## AI được phép hỗ trợ

- Giải thích khái niệm/công thức ML; phân tích dataset và vấn đề dữ liệu.
- Đề xuất preprocessing, feature engineering, module/interface và pseudocode.
- Hỗ trợ debug, phân tích lỗi, unit test/edge case, review code và tài liệu.

## Các giới hạn khi dùng AI

AI không được thay thế sự hiểu biết của nhóm; bịa dữ liệu/kết quả; dùng thông tin tương lai; dùng test set để chọn model; thay phần tự cài đặt bằng estimator có sẵn; hoặc tự đưa ra quyết định cuối khi chưa review.

## Quy tắc tự cài đặt

Các thuật toán ML bắt buộc phải được tự cài đặt. Không dùng `sklearn.LinearRegression` hoặc `sklearn.DecisionTreeRegressor` trong phần cài đặt chính. Được dùng NumPy cho phép tính số và thao tác mảng.

## Chống data leakage

- Feature chỉ dùng thông tin có ở thời điểm dự đoán.
- Không dùng quan sát tương lai để tạo feature lịch sử.
- Validation dùng để so sánh/chọn model; test chỉ dùng đánh giá cuối.

## Xác minh và tài liệu

Gợi ý do AI tạo phải được nhóm review và test trước khi đưa vào project. Nhóm chịu trách nhiệm hiểu và giải thích code, công thức, quyết định và kết quả. Prompt/quyết định quan trọng được ghi trong `WORKFLOW.md`, `DECISION_LOG.md`, `prompts/` và `results/`; không cần lưu mọi hội thoại AI.
