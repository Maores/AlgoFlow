# Algorithm & Data Structure Visualizer

An interactive visual tool that brings algorithms and data structures to life.
Watch sorting algorithms race, pathfinding algorithms explore mazes, and tree operations animate step-by-step.

## Features (Planned)
- **Sorting**: Bubble, Selection, Insertion, Merge, Quick Sort — animated with race mode
- **Pathfinding**: BFS, DFS, Dijkstra, A* — interactive grid with wall drawing
- **Trees**: Binary Search Tree — insert, search, delete with animations

## Setup
```bash
pip install pygame
python main.py
```

## Controls
- `SPACE` — Start / Pause
- `R` — Reset
- `ESC` — Quit

## Tech Stack
- Python 3.10+
- Pygame 2.x
- OOP architecture with abstract base classes

## Architecture
```
algo-visualizer/
├── main.py              # Entry point + game loop
├── config.py            # Colors, sizes, constants
├── ui/                  # Reusable UI components
│   ├── button.py
│   └── tab_bar.py
├── visualizers/         # One per tab (inherits BaseVisualizer)
│   ├── base.py          # Abstract base class
│   ├── sorting_viz.py
│   ├── pathfinding_viz.py
│   └── tree_viz.py
└── algorithms/          # Pure algorithm logic (no UI)
    ├── sorting.py
    ├── pathfinding.py
    └── tree.py
```
