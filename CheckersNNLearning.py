import matplotlib.pyplot as plt

from CheckersNN import CheckersNet
import torch
import numpy as np
import json

"""
Predict the score of a given checkers board using a trained model.

Automatically handles single board input by adding bacth dimention.

:param model - Traind neural network model.
:type model: torch.nn.Module

:param board_tensor - Encoded board tensor. (shape: [180] or [1,180]).
:type board_tensor: torch.Tensor

:param device - Device used for computation. (CPU/GPU).
:type device: torch.device

:return: Predicted score. (range [-1,1])
:rtype: float
"""
def predict_board_score(model, board_tensor, device):
    model.eval()

    if board_tensor.dim() == 1:
        board_tensor = board_tensor.unsqueeze(0)

    board_tensor = board_tensor.to(device)

    with torch.no_grad():
        prediction = model(board_tensor)

    model.train()
    return float(prediction.item())

"""
Encode a board string into a tensor representing.

Each character in the string is encoded using one-hot vector.
- Empty - [1.0, 0.0, 0.0, 0.0, 0.0]
- White - [0.0, 1.0, 0.0, 0.0, 0.0]
- Black - [0.0, 0.0, 1.0, 0.0, 0.0]
- White King - [0.0, 0.0, 0.0, 1.0, 0.0]
- Black King - [0.0, 0.0, 0.0, 0.0, 1.0]

:param key - String representation of the board.
:type key: str

:return: Encoded board tensor.
:rtype: torch.Tensor
"""
def encode_board_from_key(key):
    unicodes = {"w": 1, "b": 2, "W": 3, "B": 4, ".": -1}
    board = []

    for char in key:
        char = unicodes.get(char)
        if char == 1:
            board.extend([0, 1, 0, 0, 0])
        elif char == 2:
            board.extend([0, 0, 1, 0, 0])
        elif char == 3:
            board.extend([0, 0, 0, 1, 0])
        elif char == 4:
            board.extend([0, 0, 0, 0, 1])
        else:
            board.extend([1, 0, 0, 0, 0])

    return torch.tensor(board, dtype=torch.float32)

if __name__ == "__main__":
    """
    Model evaluation and analysis.
        
    Steps:
    - Load train model from checkpoint.
    - Load test board indices.
    - Load full data with true scores.
    - Predict scores for test boards.
    - Create model evaluation statistics.
    - Save detailed results to JSON.
    - Plot distribution of prediction vs true scores. 
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    net = CheckersNet().to(device)
    model = torch.load("CheckersData/best_model6x6.pth", map_location=device)
    net.load_state_dict(model["model"])
    net.eval()

    with open("CheckersData/ModelDataLearning/test_indices.json", "r") as f:
        test_boards = json.load(f)

    with open("CheckersData/checkers_score_huristic6x6.json", "r") as f:
        data = json.load(f)

    results = []
    errors = []
    predictions = []
    true_preds = []

    for board_key in test_boards:
        board_tensor = encode_board_from_key(board_key)

        pred = predict_board_score(net, board_tensor, device)
        true_score = data[board_key][0]
        board_count = data[board_key][1]

        error = abs(pred - true_score)

        results.append({
            "board": board_key,
            "prediction": pred,
            "true": true_score,
            "error": error,
            "count": board_count
        })

        errors.append(error)
        predictions.append(pred)
        true_preds.append(true_score)

    predictions = np.array(predictions)
    true_scores = np.array(true_preds)
    errors = np.array(errors)

    mae = np.mean(errors)
    mse = np.mean((predictions - true_scores) ** 2)
    rmse = np.sqrt(mse)

    correlation = np.corrcoef(true_scores, predictions)[0, 1]

    within_010 = np.mean(errors <= 0.10) * 100
    within_020 = np.mean(errors <= 0.20) * 100

    print("===== MODEL ACCURACY REPORT =====")
    print(f"Boards tested        : {len(test_boards)}")
    print(f"MAE (Mean Error)     : {mae:.6f}")
    print(f"MSE                 : {mse:.6f}")
    print(f"RMSE                : {rmse:.6f}")
    print(f"Correlation         : {correlation:.6f}")
    print(f"Inside 0.10 error  : {within_010:.2f}%")
    print(f"Inside 0.20 error  : {within_020:.2f}%")

    with open("CheckersData/ModelDataLearning/test_analysis.json", "w") as f:
        json.dump(results, f, indent=4)

    plt.figure(figsize=(8, 5))
    plt.hist(predictions, bins=30, alpha=0.5, label="Predictions")
    plt.hist(true_preds, bins=30, alpha=0.5, label="True Scores")
    plt.xlabel("Score")
    plt.ylabel("Frequency")
    plt.title("Predicted vs True Scores Distribution")
    plt.legend()
    plt.grid(True)

    plt.show()