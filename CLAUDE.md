# AlgoFlow - Project Context

## What is this?
AlgoFlow is an interactive algorithm visualization tool built with Python/Pygame. It animates sorting algorithms step-by-step with color-coded bars, pseudocode highlighting, and an info panel.

## Repository
- **Owner:** Maores/AlgoFlow
- **Development branch:** `claude/setup-algoflow-scaffold-V3Aic`
- **Base branch:** `master`

## Tech Stack
- Python 3.10+, Pygame 2.x
- OOP architecture with abstract base classes
- Generator pattern for step-by-step algorithm execution

## Project Structure
```
main.py              # Entry point + game loop, tab switching, controls, events
config.py            # Colors, sizes, layout constants
algorithms/
  sorting.py         # Pure algorithm logic (bubble, selection, insertion sort)
  pseudocode.py      # Pseudocode definitions for algorithms
ui/
  tab_bar.py         # Tab navigation (Sorting / Pathfinding / Trees)
  button.py          # Reusable button component
  button_group.py    # Grouped button selector (algorithm, size)
  slider.py          # Speed slider
  info_panel.py      # Right-side info panel (stats, complexity, pseudocode)
  array_modal.py     # Custom array input modal with presets
  help_modal.py      # Help/keyboard shortcuts modal
visualizers/
  base.py            # Abstract base visualizer class
  sorting_viz.py     # Sorting algorithm visualizer (main feature)
  pathfinding_viz.py # Placeholder - not yet implemented
  tree_viz.py        # Placeholder - not yet implemented
```

## Current State
- Sorting tab is fully functional with Bubble, Selection, and Insertion Sort
- Step-by-step navigation works (arrow keys, space to play/pause)
- Info panel shows algorithm stats, complexity, and highlighted pseudocode
- Custom array modal with presets (sorted, reversed, nearly sorted, etc.)
- Help modal with keyboard shortcuts
- Pathfinding and Trees tabs are placeholders (not yet implemented)

## How to Run
```bash
pip install -r requirements.txt
python main.py
```

## Key Controls
- SPACE: Start/Pause
- Arrow keys: Step forward/backward
- R: Reset
- ESC: Quit
- Speed slider and size selector in control bar

## Development Notes
- All git pushes must go to branch `claude/setup-algoflow-scaffold-V3Aic`
- Use `git push -u origin claude/setup-algoflow-scaffold-V3Aic`
- The branch name must start with `claude/` and match the session ID suffix
