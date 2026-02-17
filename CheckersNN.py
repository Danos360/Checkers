import json
import torch
import torch.nn as nn
import os
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader, random_split
import matplotlib.pyplot as plt
import time

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

CHECKPOINT_FILE = "CheckersData/checkers_checkpoint6x6-new.pth"
SNAPSHOT_DIR = "CheckersData/snapshots"
BEST_MODEL_FILE = "CheckersData/best_model6x6.pth"

os.makedirs(SNAPSHOT_DIR, exist_ok=True)

class CheckersNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(180, 256)
        self.layer2 = nn.Linear(256, 512)
        self.layer3 = nn.Linear(512, 256)
        self.layer4 = nn.Linear(256, 64)
        self.output = nn.Linear(64, 1)

    def forward(self, x):
        x = torch.relu(self.layer1(x))
        x = torch.relu(self.layer2(x))
        x = torch.relu(self.layer3(x))
        x = torch.relu(self.layer4(x))
        return torch.tanh(self.output(x))

def load_and_encode_data(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)

    X, Y = [], []
    unicodes = {"w": 1, "b": 2, "W": 3, "B": 4, ".": -1}

    for key, value in data.items():
        board = []
        for char in key:
            char = unicodes.get(char)
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
        Y.append([value[0]])

    return torch.tensor(X, dtype=torch.float32), torch.tensor(Y, dtype=torch.float32)

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

def train(model, train_loader, test_loader, epochs=300, lr=0.01, patience=5):
    start_time = time.time()

    optimizer = optim.SGD(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    train_losses = []
    test_losses = []

    best_test_loss = float("inf")
    best_epoch = -1
    patience_counter = 0

    for epoch in range(epochs):
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

        print(f"Epoch {epoch:03d} | Train {train_loss:.5f} | Test {test_loss:.5f}")

        torch.save({
            "epoch": epoch,
            "model": model.state_dict(),
            "train_loss": train_loss,
            "test_loss": test_loss
        }, f"{SNAPSHOT_DIR}/epoch_{epoch}.pth")

        if test_loss < best_test_loss:
            best_test_loss = test_loss
            best_epoch = epoch
            patience_counter = 0
            torch.save(model.state_dict(), BEST_MODEL_FILE)
        else:
            patience_counter += 1

        if patience_counter >= patience:
            print("Overfitting detected")
            print(f"Best epoch: {best_epoch}")
            break

        torch.save({
            "epoch": epoch,
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "train_losses": train_losses,
            "test_losses": test_losses
        }, CHECKPOINT_FILE)

    end_time = time.time()
    duration = end_time - start_time
    print(f"Done in {duration:.2f} seconds")

    return train_losses, test_losses, best_epoch

if __name__ == "__main__":
    X, Y = load_and_encode_data("CheckersData/checkers_score_huristic6x6.json")

    dataset = TensorDataset(X, Y)
    train_size = int(0.7 * len(dataset))
    test_size = len(dataset) - train_size
    train_ds, test_ds = random_split(dataset, [train_size, test_size])

    train_loader = DataLoader(train_ds, batch_size=128, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=128)

    model = CheckersNet().to(device)
    train_loss, test_loss, best_epoch = train(model, train_loader, test_loader)

    plt.figure(figsize=(8,5))
    plt.plot(train_loss, label="Train Loss")
    plt.plot(test_loss, label="Test Loss")
    plt.axvline(best_epoch, color="red", linestyle="--", label="Best Epoch")
    plt.xlabel("Epoch")
    plt.ylabel("MSE Loss")
    plt.title("Loss over Epochs")
    plt.legend()
    plt.tight_layout()
    plt.show()
