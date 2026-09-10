# Preprocessing

Random split 70/15/15 với seed 42. Median, missing token, one-hot vocabulary, mean/std và popularity mappings đều fit trên train. Validation/test chỉ transform bằng state đã lưu; target, Customer ID và Purchase Amount (USD) không vào X. Unknown category được mã hóa vector 0 và input phải hữu hạn.

