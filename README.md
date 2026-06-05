# Ant Colony — CS1 Project

**Team:** Juan Camilo Méndez, Salomé Roldán  
**Course:** Computer Sciences I — Universidad Distrital Francisco José de Caldas  

## Description
Grid-based simulation where an ant navigates a pheromone terrain back to its nest using a Greedy + Backtracking algorithm. The C++ engine manages the data structures (linked list stack + BST) and the Python/Pygame layer handles the algorithm logic and visual interface.

## Project Structure
'''
project/
  engine/         → C++ engine (linked list, BST, JSON I/O)
  game/
    algorithms/   → greedy.py, backtracking.py
    ui/           → main.py (Pygame), bridge.py (JSON bridge)
  data/           → input.json, state.json
'''

## Setup & Execution

### 1. Compile C++ engine (only once)
'''bash
cd engine
g++ -std=c++11 main.cpp -o ant.exe
cd ..
'''

### 2. Install Python dependency
'''bash
pip install pygame
'''

### 3. Create data folder (only once)
'''bash
mkdir data
'''

### 4. Run the game
'''bash
py -3.11 game/ui/main.py
'''

## How to Play
- **DRAW WALLS** — click/drag cells to place walls
- **REMOVE WALLS** — click to remove walls
- **ADD PHEROMONE** — click a cell to increase its pheromone value (0 → 0.5 → ... → 2.0)
- **REMOVE PHERO** — click to clear pheromone from a cell
- **SET START** — click a cell to place the ant
- **SET HOME** — click a cell to place the nest
- **RUN** — execute the Greedy + Backtracking solver and animate the path
- **RESET** — clear everything

## Color Legend
| Color | Meaning |
|-------|---------|
| 🟡 Yellow | Ant |
| 🔴 Red | Nest (home) |
| 🔵 Blue | Active path |
| ⬜ Gray | Backtracked cells |
| 🟢 Green | Pheromone trail |
| ◼ Dark | Wall |
