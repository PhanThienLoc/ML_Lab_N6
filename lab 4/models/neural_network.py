import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score
)


# ============================================================
# 1. DEFINE MULTILAYER PERCEPTRON
# ============================================================

class HousePriceMLP(nn.Module):

    def __init__(self, input_dim):
        super(HousePriceMLP, self).__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),

            nn.Linear(32, 16),
            nn.ReLU(),

            nn.Linear(16, 1)
        )

    def forward(self, x):
        return self.network(x)


# ============================================================
# 2. TRAIN NEURAL NETWORK
# ============================================================

def train_neural_network(
    X_train,
    y_train,
    input_dim,
    epochs=100,
    batch_size=32,
    learning_rate=0.001
):

    # Create model
    model = HousePriceMLP(input_dim)

    # Loss function
    criterion = nn.MSELoss()

    # Optimizer
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=learning_rate
    )

    # Make sure y has shape (n, 1)
    y_train = y_train.view(-1, 1)

    # Create DataLoader
    dataset = TensorDataset(X_train, y_train)

    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True
    )

    loss_history = []

    print("Training Neural Network...")
    print("-" * 50)

    # Training loop
    for epoch in range(epochs):

        model.train()

        total_loss = 0.0

        for X_batch, y_batch in dataloader:

            # Reset gradients
            optimizer.zero_grad()

            # Forward propagation
            predictions = model(X_batch)

            # Calculate loss
            loss = criterion(predictions, y_batch)

            # Backpropagation
            loss.backward()

            # Update weights
            optimizer.step()

            total_loss += loss.item()

        average_loss = total_loss / len(dataloader)

        loss_history.append(average_loss)

        if (epoch + 1) % 10 == 0:

            print(
                f"Epoch [{epoch + 1}/{epochs}] "
                f"- Loss: {average_loss:.4f}"
            )

    print("-" * 50)
    print("Training completed.")

    return model, loss_history


# ============================================================
# 3. MAKE PREDICTIONS
# ============================================================

def predict_neural_network(model, X_test):

    model.eval()

    with torch.no_grad():

        predictions = model(X_test)

    return predictions.cpu().numpy().flatten()


# ============================================================
# 4. EVALUATE MODEL
# ============================================================

def evaluate_neural_network(model, X_test, y_test):

    # Prediction
    y_pred = predict_neural_network(
        model,
        X_test
    )

    # Convert y_test to numpy
    if isinstance(y_test, torch.Tensor):

        y_true = (
            y_test
            .detach()
            .cpu()
            .numpy()
            .flatten()
        )

    else:

        y_true = np.asarray(
            y_test
        ).flatten()

    # Metrics
    mse = mean_squared_error(
        y_true,
        y_pred
    )

    mae = mean_absolute_error(
        y_true,
        y_pred
    )

    r2 = r2_score(
        y_true,
        y_pred
    )

    print("\nNeural Network Evaluation")
    print("-" * 35)

    print(f"MSE : {mse:.4f}")
    print(f"MAE : {mae:.4f}")
    print(f"R2  : {r2:.4f}")

    return {
        "model": "Neural Network",
        "MSE": mse,
        "MAE": mae,
        "R2": r2
    }, y_pred


# ============================================================
# 5. PLOT TRAINING LOSS
# ============================================================

def plot_training_loss(loss_history):

    plt.figure(figsize=(8, 5))

    plt.plot(
        range(1, len(loss_history) + 1),
        loss_history
    )

    plt.xlabel("Epoch")
    plt.ylabel("MSE Loss")

    plt.title(
        "Neural Network Training Loss"
    )

    plt.grid(True)

    plt.tight_layout()

    plt.show()


# ============================================================
# 6. ACTUAL PRICE VS PREDICTED PRICE
# ============================================================

def plot_predictions(y_test, y_pred):

    if isinstance(y_test, torch.Tensor):

        y_true = (
            y_test
            .detach()
            .cpu()
            .numpy()
            .flatten()
        )

    else:

        y_true = np.asarray(
            y_test
        ).flatten()

    plt.figure(figsize=(8, 6))

    plt.scatter(
        y_true,
        y_pred,
        alpha=0.5
    )

    min_value = min(
        y_true.min(),
        y_pred.min()
    )

    max_value = max(
        y_true.max(),
        y_pred.max()
    )

    plt.plot(
        [min_value, max_value],
        [min_value, max_value],
        linestyle="--"
    )

    plt.xlabel("Actual House Price")
    plt.ylabel("Predicted House Price")

    plt.title(
        "Actual vs Predicted House Prices - MLP"
    )

    plt.tight_layout()

    plt.show()


# ============================================================
# 7. CONVERT NUMPY DATA TO PYTORCH TENSOR
# ============================================================

def to_tensor(X, y=None):

    X_tensor = torch.tensor(
        np.asarray(X),
        dtype=torch.float32
    )

    if y is None:
        return X_tensor

    y_tensor = torch.tensor(
        np.asarray(y),
        dtype=torch.float32
    )

    return X_tensor, y_tensor