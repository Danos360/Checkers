# Checkers Game Project

This is a final project in Software Engineering for 12th grade. 
The project is a Checkers game built with Python, focusing on the combination 
of a clean graphical interface and an intelligent game agent.

The project transforms the traditional board game into a modern digital experience. 
It features a fully responsive interface, custom-made assets, and an internal logic system designed for competitive play. 
The focus was on creating a "Flow" state for the player through smooth animations and immediate feedback.

## 🎯 Project Goal
The main goal of this project was to implement a full game using the **MVC (Model-View-Controller)** architecture. 
It demonstrates how to separate the game rules (logic) from the visual design (UI) and 
how to integrate a **Neural Network** to power the game's opponent.

## ✨ Main Features
* **Neural Network Opponent:** Play against a trained model that analyzes the board state to make strategic moves.
* **Immersive Design:** Includes custom-designed graphics and sound effects to enhance the gameplay experience.
* **Board Set-Skins:** Players can choose between different board backgrounds and piece skins.
* **Theme Customization:** Support for both **Dark Mode** and **Light Mode**, allowing the user to switch the entire UI theme instantly.
* **1v1 Mode:** Support for local multiplayer to play against a friend on the same machine.
* **Sound Management:** Option to toggle sound effects at any time. The setting is saved and synchronized across all project windows.
* **In-Game Rules:** A dedicated rules section accessible directly from the main menu, ensuring players always have the instructions at hand.
  
## 🛠 Technical Details
- **Language:** Python.
- **Libraries:** **PySide** (UI), **PyTorch** (ML model), and **NumPy**.

## 🚀 How to Run
**1. Clone the repository:**
```bash
git clone https://github.com/Danos360/Checkers.git
```
**2. Install the requirements:**
```bash
pip install PySide6 torch numpy
```
**3. Navigate to the directory:**
```bash
cd Checkers
```
**4. Launch the game:**
```bash
python CheckersMain.py
```

## 📂 **Project Structure**
* **Model**: Handles game rules, legal moves, and the agent logic.
* **View:** Manages the PySide windows, animations, and sound effects.
* **Controller**: Connects the user inputs to the game logic using a Signal-based system.
* **Data/Model**: Contains the ``.pth`` files (trained Neural Network weights) and images and sound paths.

**Author: Dan Levkov [@Danos360](https://github.com/Danos360)** 

**Checkers Game - School Project**
