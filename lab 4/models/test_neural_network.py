import torch

from neural_network import (
    HousePriceMLP,
    train_neural_network,
    evaluate_neural_network
)


# ============================================================
# TEST DATA - KHONG LIEN QUAN DATASET CUA NHOM
# ============================================================

torch.manual_seed(42)

# Gia su co 1000 can nha, moi can nha co 10 features
X = torch.randn(1000, 10)

# Tao gia nha gia lap
y = (
    X[:, 0] * 50000
    + X[:, 1] * 30000
    + X[:, 2] * 20000
    + 300000
)

# Chia train/test tam thoi
X_train = X[:800]
X_test = X[800:]

y_train = y[:800]
y_test = y[800:]


# ============================================================
# TRAIN
# ============================================================

model, loss_history = train_neural_network(
    X_train,
    y_train,
    input_dim=X_train.shape[1],
    epochs=100,
    batch_size=32,
    learning_rate=0.001
)


# ============================================================
# EVALUATE
# ============================================================

metrics, y_pred = evaluate_neural_network(
    model,
    X_test,
    y_test
)

print("\nTest neural network completed successfully.")