# Teeko Game - Python Implementation

A robust and interactive implementation of the **Teeko** strategy board game in Python. This project features a polished Graphical User Interface (GUI) built with `tkinter` and a sophisticated Artificial Intelligence (AI) opponent capable of adaptive difficulty levels.

## 📋 Table of Contents
- [Teeko Game - Python Implementation](#teeko-game---python-implementation)
  - [📋 Table of Contents](#-table-of-contents)
  - [🎮 About the Game](#-about-the-game)
  - [✨ Features](#-features)
  - [📂 Project Structure](#-project-structure)
  - [⚙️ Installation](#️-installation)
    - [Prerequisites](#prerequisites)
    - [Setup](#setup)
  - [🚀 Usage](#-usage)
    - [In-Game Controls](#in-game-controls)
  - [📜 Game Rules](#-game-rules)
  - [🧠 AI \& Technical Details](#-ai--technical-details)

## 🎮 About the Game
Teeko is a strategy game played on a 5x5 board. It is a mix of Tic-Tac-Toe and Checkers. The goal is to align four of your pieces in a row (horizontally, vertically, or diagonally) or in a 2x2 square. The game proceeds in two phases: the **Drop Phase** (placing pieces) and the **Move Phase** (moving pieces to adjacent empty spots).

## ✨ Features
- **Multiple Game Modes:**
  - 👤 **Human vs AI:** Challenge the computer.
  - 🤖 **AI vs AI:** Watch two AI algorithms battle it out.
  - 👥 **Human vs Human:** Play against a friend on the same screen.
- **Adjustable AI Difficulty:**
  - Levels: **Débutant** (Beginner), **Normal**, **Pro**, **Expert**.
  - **Adaptive Expert Mode:** The AI adjusts its strategy based on the opponent's playstyle and board state.
- **Graphical User Interface:**
  - Clean and intuitive `tkinter` interface.
  - Real-time status updates and visual indicators for valid moves.
  - "Replay" and "Quit" options.
- **Advanced Game Engine:**
  - Full implementation of standard Teeko rules.
  - Efficient win condition checking and state management.

## 📂 Project Structure
```
c:\Users\Walle\Desktop\test\Teeko-IA41\
├── main.py                # Entry point of the application
├── game_engine.py         # Core game logic (rules, board state, validation)
├── interface.py           # GUI implementation using tkinter (Menus, Game Board)
├── ai_template.py         # AI logic (Minimax, Alpha-Beta pruning, Heuristics)
├── history_analyzer.py    # Helper tool for AI to analyze opponent strategies
├── .gitignore             # Git ignore file
└── README.md              # Project documentation
```

## ⚙️ Installation

### Prerequisites
- **Python 3.x**: Ensure Python is installed on your system.
- **Tkinter**: Usually included with standard Python installations.

### Setup
1. Clone the repository or download the source code.
   ```bash
   git clone <repository_url>
   cd Teeko-IA41
   ```
2. No external dependencies (like `pip install`) are required as the project uses standard libraries.

## 🚀 Usage
To start the game, simply run the `main.py` file from your terminal:

```bash
python main.py
```

### In-Game Controls
1. **Start Screen:** Select the game mode, starting player ("Noir" or "Rouge"), and AI difficulty levels.
2. **Drop Phase:** Click on any empty square to place your piece.
3. **Move Phase:**
   - Click on one of your pieces to select it (it will be highlighted).
   - Click on an adjacent empty square to move the selected piece.
   - If you change your mind, click on another of your pieces to change selection.
4. **Game Over:** A message will announce the winner. You can choose to replay or quit.

## 📜 Game Rules
1. **The Board:** 5x5 grid.
2. **Pieces:** Each player (Black and Red) has 8 pieces. Black usually starts.
3. **Phase 1: Drop:** Players take turns placing one piece at a time on any empty spot until all 8 pieces are on the board.
4. **Phase 2: Move:** Players take turns moving one of their pieces to an adjacent empty space (horizontal, vertical, or diagonal).
5. **Winning:** The first player to arrange 4 of their pieces in a straight line (horizontal, vertical, diagonal) or a 2x2 square wins immediately.

## 🧠 AI & Technical Details
The AI (`ai_template.py`) is powered by the **Minimax algorithm** with **Alpha-Beta pruning** for optimization.

- **Heuristic Evaluation:** The AI evaluates board states based on:
  - **Material:** Winning/Losing states.
  - **Position:** Controlling the center and key squares.
  - **Mobility:** Number of available moves (in move phase).
  - **Threats:** Detecting and creating alignments of 3 pieces.
- **Adaptive Strategy:** In "Expert" mode, the AI uses `history_analyzer.py` to:
  - Analyze the opponent's "Aggressiveness" (Offensive vs. Defensive ratio).
  - Adjust its scoring weights dynamically to counter specific playstyles.
  - Avoid repetitive moves (transposition tables and history tracking).

---
*Developed for the IA41 course in UTBM.*
