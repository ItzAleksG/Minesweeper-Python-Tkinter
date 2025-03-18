# Minesweeper Python Tkinter
- This Minesweeper game is built using Python and tkinter for the graphical user interface. 
- Uses recursion to reveal many empty cells at once, making gameplay faster and more enjoyable. 
- Game interface coloring inspired by the minesweeper version from Google search.

![Preview](preview.gif)

## 💾 How to install
To install this game you need to download the file [Minesweeper.py](Minesweeper.py) and run it.
If you want to download code with comments, download [MinesweeperComs.py](MinesweeperComs.py)
Especially for Russian speakers there is a file with comments in Russian [MinesweeperComsRus.py](MinesweeperComsRus.py)

## 🎓 How to play
- **Left-click** on a cell to reveal it.
- **Right-click** to flag a cell as a potential mine.
  - **Left-click** on the cell *with the flag* does nothing.
  - **Right-click** on the cell *with the flag* removes the flag.
- The goal is to clear the board without detonating any mines.
- Left-click on the face button on the top panel restarts the game.

## ☕ Features
- Classic Minesweeper gameplay.
- The first left-click on a cell is **always** safe.
- Pleasant coloring of the interface elements.
- 3 different difficulty levels.
  - Easy: 10x8, 10 mines.
  - Medium: 18x14, 40 mines.
  - Hard: 30x16, 100 mines.
- Stopwatch counting how many seconds have passed after the first left-click on a cell
- A counter for how many flags are still needed (optional, you can put more/less).
