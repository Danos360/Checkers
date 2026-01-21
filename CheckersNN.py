import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import matplotlib.pyplot as pltH

import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import matplotlib.pyplot as plt

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


def load_and_encode_data(file_path):
    """
    Loads data from JSON and converts it to One-Hot Encoded Tensors
    """
    print(f"Reading data from {file_path}...")

    with open("/checkers_score_huristic.json", "r") as f:
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


# Model definition
class CheckersNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(180, 256)
        self.layer2 = nn.Linear(256, 512)
        self.layer3 = nn.Linear(512, 256)
        self.layer4 = nn.Linear(256, 64)
        self.output = nn.Linear(64, 1)

    def forward(self, x):
        # Layer 1
        x = self.layer1(x)
        x = torch.relu(x)

        # Layer 2
        x = self.layer2(x)
        x = torch.relu(x)

        # Layer 3
        x = self.layer3(x)
        x = torch.relu(x)

        # Layer 4
        x = self.layer4(x)
        x = torch.relu(x)

        # Output layer
        x = self.output(x)
        x = torch.sigmoid(x)

        return x

# Training
def train(model, loader, epochs=1000, learning_rate=0.01):
    loss_fn = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=learning_rate)

    loss_history = []
    print("\nStarting Training Loop...")
    for epoch in range(epochs):
        total_loss = 0

        for batch_X, batch_Y in loader:
            batch_X = batch_X.to(device)
            batch_Y = batch_Y.to(device)

            optimizer.zero_grad()
            # Forward pass
            y_pred = model(batch_X)
            # Calculate loss
            loss = loss_fn(y_pred, batch_Y)
            # Backward pass
            loss.backward()
            # Weight update
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(loader)
        print("Epoch loss:" , avg_loss)
        loss_history.append(avg_loss)

        if epoch % 50 == 0:
            print(f"Epoch {epoch} | Average Loss: {avg_loss:.5f}")

    return loss_history


# Main
if __name__ == "__main__":
    # 1. Prepare Data
    X, Y = load_and_encode_data('/checkers_score_huristic.json.json')

    # 2. Configure dataloader
    dataset = TensorDataset(X, Y)
    loader = DataLoader(dataset, batch_size=128, shuffle=True)

    # 3. Instantiate Model
    net = CheckersNet().to(device)

    # 4. Execute Training
    loss_history = train(net, loader)

    # 5. Save the result
    torch.save(net.state_dict(), "checkersModel.pth")
    print("\nModel saved to checkersModel.pth")

    # 6. Plot loss over epochs
    plt.plot(loss_history)
    plt.title('Loss over epochs')
    plt.show()
