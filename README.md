# AlgoFlow

An interactive desktop visualizer for algorithms and data structures, built with Python and Pygame. Every algorithm runs step by step: play, pause, or step forward and back, while an info panel shows the highlighted pseudocode, the live variables and the complexity.

## What it shows

| Tab | Algorithms |
|---|---|
| Sorting | Bubble, Selection, Insertion, Merge and Quick sort, as bars or as boxes with pointer labels (`i`, `j`, `pivot`, ...); custom arrays and presets |
| Pathfinding | BFS and DFS on a grid where you draw walls and place the start and end; grid presets (random, maze, spiral, bottle); the frontier and the final path are animated |
| Trees | Binary search tree insert, delete and search; inorder, preorder, postorder and level-order traversals; min-heap insert and extract-min |

## Run it

```bash
pip install -r requirements.txt
python main.py
```

Requires Python 3.10+ and Pygame 2.

Keyboard: `SPACE` play or pause, `←` / `→` step back or forward, `R` reset, `H` help, `ESC` quit.

## Tests

```bash
python -m pytest tests
```

63 tests cover the pathfinding and tree algorithms.

## How it is built

- `algorithms/`: pure algorithm logic with no UI. Each algorithm is a generator that yields one step at a time, so the visualizer can move forward and back through the steps.
- `visualizers/`: one visualizer per tab, all inheriting from an abstract `BaseVisualizer`.
- `ui/`: reusable widgets (buttons, tab bar, slider, text input, info panel, help and custom-array windows).
- `main.py`: the app loop; `config.py`: colors, sizes and constants.
- `docs/`: the design notes and the development log.
