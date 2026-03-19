# AlgoFlow

An interactive visual tool that brings algorithms and data structures to life.
Watch sorting algorithms race, pathfinding algorithms explore mazes, and tree operations animate step-by-step.

## Features
- **Sorting**: Bubble, Selection, Insertion Sort — animated with color-coded bars
- **Pathfinding**: Coming soon
- **Trees**: Coming soon

## Setup
```bash
pip install -r requirements.txt
python main.py
```

## Controls
- `SPACE` — Start / Pause
- `R` — Reset
- `ESC` — Quit
- Speed slider, algorithm selector, and size selector in the control bar

## Tech Stack
- Python 3.10+
- Pygame 2.x
- OOP architecture with abstract base classes
- Generator pattern for step-by-step algorithm execution

## Architecture
```
algoflow/
├── main.py                  # Entry point + game loop
├── config.py                # Colors, sizes, constants
├── requirements.txt
├── .gitignore
├── README.md
├── ui/                      # Reusable UI components
│   ├── __init__.py
│   ├── button.py
│   ├── tab_bar.py
│   ├── slider.py
│   ├── info_panel.py
│   └── button_group.py
├── visualizers/             # One per tab (inherits BaseVisualizer)
│   ├── __init__.py
│   ├── base.py              # Abstract base class
│   ├── sorting_viz.py
│   ├── pathfinding_viz.py   # Placeholder
│   └── tree_viz.py          # Placeholder
└── algorithms/              # Pure algorithm logic (no UI)
    ├── __init__.py
    └── sorting.py
```
