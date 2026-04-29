import json
import torch
import torch.nn as nn
import os
import torch.optim as optim
from torch.utils.data import TensorDataset, Subset, DataLoader
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import time
import numpy as np

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
"""
Device used for training (GPU if available, otherwise CPU)
"""
print(f"Using device: {device}")

MEMORY_FILE_PATH = "CheckersData/checkers_score_huristic6x6.json"
TEST_INDICES_FILE_PATH = "CheckersData/ModelDataLearning/test_indices.json"
CHECKPOINT_FILE = "CheckersData/OldData/checkers_checkpoint6x6-new.pth"
SNAPSHOT_DIR = "CheckersData/snapshots"
BEST_MODEL_FILE = "CheckersData/snapshot/best_model6x6.pth"

os.makedirs(SNAPSHOT_DIR, exist_ok=True)

"""
Neural network for evaluating Checkers board state.

Architecture:
- Input: 180 features (encoded board).
- Hidden layers: 256 - 256 - 64 - 1.
- Activation: LeakyReLU.
- Output: single value in range [-1, 1] using tanh.

Used to predict the heuristic score of a board.
"""
class CheckersNet(nn.Module):
    """
    Initialize the neural network layers and activation function.
    """
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(180, 256)
        self.layer2 = nn.Linear(256, 256)
        self.layer3 = nn.Linear(256, 64)
        self.output = nn.Linear(64, 1)

        self.act = nn.LeakyReLU(negative_slope=0.01)

    """
    Preform a forward pass through the network.
    
    :param x - Input tensor representing encoded baord states.
    :type x: torch.Tensor
    
    :returns - Predicted score for each board in range [-1, 1].
    :rtype: torch.Tensor
    """
    def forward(self, x):
        x = self.act(self.layer1(x))
        x = self.act(self.layer2(x))
        x = self.act(self.layer3(x))
        return torch.tanh(self.output(x))

"""
Load checkers board data from JSON and encode it into tensors.

Each board is encoded using one-hot representing per cell:
- Empty - [1.0, 0.0, 0.0, 0.0, 0.0]
- White - [0.0, 1.0, 0.0, 0.0, 0.0]
- Black - [0.0, 0.0, 1.0, 0.0, 0.0]
- White King - [0.0, 0.0, 0.0, 1.0, 0.0]
- Black King - [0.0, 0.0, 0.0, 0.0, 1.0]

Filters boards that appear too few times (<=3). 

:param file_path - Path to JSON file.
:type file_path: str

:return:
    X - Encode boards.
    Y - Scores.
    boards - Original board strings.
:rtype - (torch.Tensor, torch.Tensor, list[str])
        
"""
def load_and_encode_data(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)

    X, Y, boards = [], [], []
    unicodes = {"w": 1, "b": 2, "W": 3, "B": 4, ".": -1}
    kept = 0; skipped = 0

    for key, value in data.items():
        score, count = value

        if count <= 3:
            skipped += 1
            continue

        board = []
        boards.append(key)

        for char in key:
            char = unicodes[char]
            if char == 1:
                board.extend([0.0, 1.0, 0.0, 0.0, 0.0])
            elif char == 2:
                board.extend([0.0, 0.0, 1.0, 0.0, 0.0])
            elif char == 3:
                board.extend([0.0, 0.0, 0.0, 1.0, 0.0])
            elif char == 4:
                board.extend([0.0, 0.0, 0.0, 0.0, 1.0])
            else:
                board.extend([1.0, 0.0, 0.0, 0.0, 0.0])

        X.append(board)
        Y.append([score])

        kept += 1
    print(f"kept: {kept}, skipped: {skipped}")

    return torch.tensor(X, dtype=torch.float32), torch.tensor(Y, dtype=torch.float32), boards

"""
Evaluate the model on a dataset.

Computes Mean Squared Error (MSE) over all batches.

:param model - Trained neural network.
:type model: nn.Module

:param loader - DataLoader for evaluation.
:type loader: DataLoader
"""
def evaluate(model, loader):
    model.eval()
    loss_fn = nn.MSELoss()
    total_loss = 0

    with torch.no_grad():
        for X, Y in loader:
            X, Y = X.to(device), Y.to(device)
            pred = model(X)
            total_loss += loss_fn(pred, Y).item()

    model.train()
    return total_loss / len(loader)

"""
Train the neural network on checkers data.

Features: 
- AdamW optimizer with weight decay.
- ReduceLROnPlatelu scheduler.
- Snapshot saving every few epochs.
- Best model saving based on test loss.

:param model - Neural network to train.
:type model: nn.Module

:param train_loader - Training data loader.
:type train_loader: DataLoader

:param test_loader - Validation/test data loader.
:type test_loader: DataLoader

:param epochs - Number of training epochs.
:type epochs: int

:param learning_rate - Initial learning rate.
:type learning_rate: float

:param snapshot_jump - Save snapshot every X epochs.
:type snapshot_jump: int

:return:
    - trian_losses - list of training losses.
    - val_losses - list of test losses.
:rtype: (list[float], list[float])
"""
def train(model, train_loader, test_loader, epochs=101, learning_rate=1e-3, snapshot_jump=10):
    start_time = time.time()

    loss_fn = nn.MSELoss()
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)

    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5,factor=0.5,threshold=1e-4,min_lr=1e-6)

    train_losses = []
    test_losses = []
    best_test = float("inf")

    for epoch in range(epochs):
        model.train()
        total_loss = 0

        for X, Y in train_loader:
            X, Y = X.to(device), Y.to(device)

            optimizer.zero_grad()
            pred = model(X)
            loss = loss_fn(pred, Y)

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        train_loss = total_loss / len(train_loader)
        test_loss = evaluate(model, test_loader)

        train_losses.append(train_loss)
        test_losses.append(test_loss)

        scheduler.step(test_loss)

        current_lr = optimizer.param_groups[0]['lr']

        print(f"Epoch {epoch:03d} | Train {train_loss:.6f} | Test {test_loss:.6f} | LR {current_lr:.6f}")


        if test_loss < best_test:
            best_test = test_loss
            print(f"Saved Epoch {epoch:03d} | Best Epoch")
            torch.save(model.state_dict(), BEST_MODEL_FILE)


        if epoch % snapshot_jump == 0 or epoch == epochs - 1:
            snapshot_path = f"{SNAPSHOT_DIR}/epoch_{epoch}.pth"
            torch.save({
                "epoch": epoch,
                "model": model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "train_loss": train_loss,
                "test_loss": test_loss
            }, snapshot_path)
            print(f"Saved snapshot: {snapshot_path}")

    duration = time.time() - start_time
    print(f"Training finished in {duration:.2f} seconds")

    return train_losses, test_losses

if __name__ == "__main__":
    """
    Main training preperation.
    
    Steps:
    - Load and encode dataset.
    - Splite into train/test using stratification.
    - Save test boards for later evaluation.
    - Create DataLoaders.
    - Train model.
    - Plot training vs test loss.
    """
    X, Y, boards = load_and_encode_data(MEMORY_FILE_PATH)

    dataset = TensorDataset(X, Y)

    targets = dataset.tensors[1].numpy()
    num_bins = 10
    bins = np.linspace(np.min(targets), np.max(targets), num_bins)
    binned_targets = np.digitize(targets, bins)

    train_indices, test_indices = train_test_split(
        range(len(dataset)),
        test_size=0.2,
        stratify=binned_targets,
        random_state=42
    )

    test_boards = [boards[i] for i in test_indices]
    with open(TEST_INDICES_FILE_PATH, "w") as f:
        json.dump(test_boards, f, indent=4)

    train_dataset = Subset(dataset, train_indices)
    test_dataset = Subset(dataset, test_indices)

    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)

    model = CheckersNet().to(device)
    train_losses, test_losses = train(model, train_loader, test_loader)

    plt.figure(figsize=(9,5))
    plt.plot(train_losses, label="Train Loss")
    plt.plot(test_losses, label="Test Loss")
    plt.xlabel("Epoch")
    plt.ylabel("MSE Loss")
    plt.title("Train vs Test Loss")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()