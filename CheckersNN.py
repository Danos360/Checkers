import json
import torch
import torch.nn as nn
import os
import torch.optim as optim
from sympy import evaluate
from torch.utils.data import TensorDataset, DataLoader
import matplotlib.pyplot as plt

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

CHECKPOINT_FILE = "checkers_checkpoint.pth"

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
        return torch.sigmoid(self.output(x))

def load_and_encode_data(file_path):
    print(f"Reading data from {file_path}...")

    with open("CheckersData/checkers_score_huristic.json", "r") as f:
        data = json.load(f)

    X = []
    Y = []

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
    return torch.tensor(X), torch.tensor(Y)

def train(model, train_loader, test_loader, epochs=101, learning_rate=0.01):
    loss_fn = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=learning_rate)

    start_epoch = 0
    trian_loss_history = []
    test_loss_history = []

    if os.path.exists(CHECKPOINT_FILE):
        checkpoint = torch.load(CHECKPOINT_FILE, map_location=device)
        model.load_state_dict(checkpoint["model"])
        optimizer.load_state_dict(checkpoint["optimizer"])
        start_epoch = checkpoint["epoch"] + 1
        loss_history = checkpoint["loss_history"]
        print(f"Resuming from epoch {start_epoch}")

    for epoch in range(start_epoch, epochs):
        total_loss = 0
        model.train()
        for batch_X, batch_Y in loader:
            batch_X = batch_X.to(device)
            batch_Y = batch_Y.to(device)

            optimizer.zero_grad()
            y_pred = model(batch_X)
            loss = loss_fn(y_pred, batch_Y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        train_loss_history.append(avg_loss)

        if epoch % 50 == 0:
            avg_test_loss = evaluate(model, test_loader, device)
            test_loss_history.append(avg_test_loss)
            print(f"Epoch {epoch} | Loss: {avg_loss:.6f}")

        torch.save({
            "epoch": epoch,
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "loss_history": trian_loss_history
        }, CHECKPOINT_FILE)

    return trian_loss_history, test_loss_history


def evaluate(model, loader, device):
    model.eval()
    loss_fn = nn.MSELoss()
    total_loss = 0

    with torch.no_grad():
        for batch_X, batch_Y in loader:
            batch_X = batch_X.to(device)
            batch_Y = batch_Y.to(device)
            prediction = model(batch_X)
            loss = loss_fn(prediction, batch_Y)
            total_loss += loss.item()

    avg_loss = total_loss / len(loader)
    model.train()
    return avg_loss

if __name__ == "__main__":
    X, Y = load_and_encode_data('CheckersData/checkers_score_huristic.json')

    dataset = TensorDataset(X, Y)
    train_size = int(len(dataset) * 0.7)
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=128, shuffle=True)

    net = CheckersNet().to(device)

    trian_loss_history, test_loss_history = train(net, train_loader, test_loader)

    torch.save(net.state_dict(), "checkersModel.pth")
    print("\nModel saved to checkersModel.pth")

    plt.figure()
    epoch_axis = list(range(len(trian_loss_history)))
    plt.plot(epoch_axis, trian_loss_history, label="Train Loss")

    eval_axis = list(range(0, len(trian_loss_history), 50))
    plt.plot(eval_axis, test_loss_history, label="Test Loss")

    plt.title('Loss over epochs: train and test')
    plt.xlabel('Epochs')
    plt.ylabel('Loss (MSE)')
    plt.legend()
    plt.show()
