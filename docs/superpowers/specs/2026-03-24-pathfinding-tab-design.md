# Pathfinding Tab — Design Spec

## Overview

Add a fully interactive pathfinding visualization tab to AlgoFlow, supporting BFS, DFS, Dijkstra, and A* on a 2D grid. Users draw walls, place weighted terrain, pick presets, and step through algorithms with time-travel navigation — matching the sorting tab's educational depth and visual polish.

**Goal:** Interview-ready demo that demonstrates deep understanding of graph algorithms, with consistent UX across tabs.

## Algorithms

| Algorithm | Weighted? | Optimal? | Time | Space |
|-----------|-----------|----------|------|-------|
| BFS | No | Yes (unweighted) | O(V + E) | O(V) |
| DFS | No | No | O(V + E) | O(V) |
| Dijkstra | Yes | Yes | O((V + E) log V) | O(V) |
| A* | Yes | Yes (admissible h) | O((V + E) log V) | O(V) |

All four live in `algorithms/pathfinding.py` as pure generator functions — no pygame imports.

**Movement:** 4-directional only (up, down, left, right). A* uses Manhattan distance heuristic.

**Weighted cell behavior:** Weighted cells have a fixed cost of 5 (empty cells cost 1). BFS and DFS treat weighted cells as passable with cost 1 — weights are ignored. Weighted cells keep their amber color but the algorithm does not consider cost. This is by design: it demonstrates *why* Dijkstra/A* exist.

## Grid System

### Cell Model

Each cell has: row, column, state, weight (default 1, weighted = 5), and optional algorithm data.

**Cell states:** `EMPTY`, `WALL`, `START`, `END`, `WEIGHTED`, `VISITED`, `FRONTIER`, `PATH`

### Grid Sizes

Canvas area is 1425x807 pixels. Cell sizes are square, computed as `min((canvas_w - (cols+1)*gap) / cols, (canvas_h - (rows+1)*gap) / rows)` with 1px gap. Grid is centered within the canvas (leftover space distributed as padding).

| Label | Columns x Rows | Cell size (approx) |
|-------|---------------|-------------------|
| Small | 15 x 11 | ~70px |
| Medium | 25 x 18 | ~44px |
| Large | 40 x 25 | ~32px |

### Interaction

- **Click + drag** to paint cells based on active editing mode
- **Editing modes:** Wall, Weight, Start, End (toggle via button group)
- Default mode: Wall
- Cannot overwrite start/end with walls
- Start and end points are single cells (placing a new one removes the old)
- **Grid editing is locked while algorithm is running or has history.** User must click Reset (clears exploration, keeps grid) before editing the grid. This prevents history invalidation.

## Presets

Parallel to sorting presets (sorted, reversed, nearly-sorted, etc.):

| Preset | Description | Best demonstrates |
|--------|-------------|-------------------|
| Random walls | ~25-30% random walls, guaranteed solvable | General exploration |
| Recursive maze | Recursive backtracking maze generation — corridors and dead ends | DFS behavior |
| Spiral | Walls form spiral, forces winding path | BFS vs DFS difference |
| Open field + weights | Few walls, scattered weighted terrain | Dijkstra vs BFS |
| Bottleneck | Open areas connected by narrow passages | Frontier expansion |

All presets guarantee a valid path from start to end (validated via quick BFS check after generation). Start placed top-left area, end placed bottom-right area. User can edit the grid after a preset is applied (before running the algorithm).

**User-drawn grids** can create unsolvable configurations — this is handled by the "no path found" behavior below.

## Algorithm Generator Pattern

Same 4-tuple yield pattern as sorting:

```
(op_type, cell_or_cells, status_msg, data_dict)
```

### Operation Types

| Type | Meaning | Data |
|------|---------|------|
| `"frontier"` | Cell added to queue/open set | distance, cost, f/g/h |
| `"visit"` | Cell explored (dequeued) | distance, cost, f/g/h, queue_size |
| `"update"` | Cell cost updated (relaxation) | old_cost, new_cost |
| `"path"` | Cell on final path (traceback) | path_length |
| `"no_path"` | Algorithm exhausted frontier, no path exists | total_explored |
| `"done"` | Algorithm complete | total_explored, path_length, total_cost |

### Data Dict by Algorithm

- **BFS/DFS:** `{"distance": int, "parent": (r, c)}`
- **Dijkstra:** `{"cost": float, "parent": (r, c)}`
- **A\*:** `{"g": float, "h": float, "f": float, "parent": (r, c)}`

### No Path Found

When the frontier is exhausted without reaching the end, the generator yields `("no_path", (), "No path exists from start to end", {"total_explored": n})`. The UI displays "No path found" in the status area. Explored cells remain visible so the user can see what was searched.

### History & Time-Travel

Cell-state array snapshots at each step (not full cell objects — just a 2D array of states, plus algorithm data arrays for distance/cost/f values). This keeps memory manageable even on Large grids. Backward/forward stepping with arrow keys. Space to play/pause.

For Large grids (~1000 cells, potentially hundreds of steps): each snapshot stores flat arrays of ints/floats, roughly ~10KB per step. At 700 steps that's ~7MB — acceptable.

## Visualization & Animation

### Cell Colors (Dark Theme)

These are the canonical values — any conflicting values in `config.py` should be updated to match.

| State | Color | RGB |
|-------|-------|-----|
| Empty | Dark gray | (40, 40, 55) |
| Wall | Solid dark | (60, 60, 80) |
| Weighted | Amber | (180, 140, 50) |
| Start | Green | (50, 200, 100) |
| End | Red | (230, 70, 70) |
| Frontier | Light blue | (100, 180, 230) |
| Visited | Muted purple | (120, 80, 160) |
| Path | Golden yellow | (255, 200, 50) |

### Animated Frontier Expansion

- Cell flashes at ~1.5x brightness on state change
- Fades back to target color over ~200ms (linear interpolation)
- Creates natural ripple effect as algorithm explores
- Implementation: `flash_timer` per cell, decrement each frame, blend colors

### Data Overlays

- Small grid: show values on all non-empty cells
- Medium/Large grid: show values on frontier and recently visited only
- Font size auto-scales to cell size

### Path Traceback Animation

- After algorithm completes, final path highlights cell-by-cell from start to end
- Slightly slower pace than exploration — satisfying reveal moment

## Control Bar & Tab Switching

### Tab-Switching Strategy

Each tab owns its own set of control bar widgets, stored in `main.py` as a dict keyed by tab name (e.g., `self.tab_controls = {"Sorting": {...}, "Pathfinding": {...}}`). When the user switches tabs, `main.py` draws only the active tab's controls. The pathfinding controls are created in `__init__` alongside sorting's, but only drawn/updated when the Pathfinding tab is active.

Shared controls (Start/Pause, Reset, Speed slider, Help) use the same component classes but are separate instances per tab. This avoids any state leakage between tabs.

### main.py Update Loop Integration

The `_update_info_panel()` method branches on the active tab name:
- **Sorting tab:** Current behavior — reads `viz.comparisons`, `viz.swaps`, `viz.current_pointers`, `viz.array`
- **Pathfinding tab:** Reads `viz.cells_explored`, `viz.path_length`, `viz.total_cost`, `viz.frontier_size`

Each branch calls the info panel with tab-appropriate data. This is a simple `if/elif` on the active tab — no complex abstraction needed.

### Pathfinding Control Bar

| Component | Type | Options |
|-----------|------|---------|
| Start/Pause | Button | Toggle |
| Reset | Button | Clears exploration, keeps grid |
| Speed slider | Slider | 0.1x - 4.0x |
| Algorithm selector | ButtonGroup | BFS, DFS, Dijkstra, A* |
| Size selector | ButtonGroup | Small, Medium, Large |
| Preset selector | ButtonGroup | Random, Maze, Spiral, Weighted, Bottleneck |
| Clear Grid | Button | Resets to empty grid |
| Help | Button | Far right |

### Grid Editing Mode Toggle

Placed as a small button group **above the grid** (below the header, left-aligned within the canvas area). Four buttons: Wall / Weight / Start / End. Active mode highlighted with accent color. This keeps the control bar uncluttered.

### Algorithm Switching

Switching algorithms resets the exploration state (clears visited/frontier/path) but preserves the grid layout (walls, weights, start, end). Same pattern as sorting's `set_algorithm()` → `reset()`.

## Info Panel

Right-side panel mirroring sorting's layout:

1. **Algorithm card** — Name, time complexity, space complexity, optimal (Yes/No)
2. **Live stats card** — Cells explored, frontier size, path length, total path cost
3. **Pseudocode card** — Algorithm pseudocode with highlighted current line
4. **Legend card** — Color key for all cell states (empty, wall, weighted, start, end, frontier, visited, path)

### Info Panel API Changes

**`set_algorithm_info()`** — Change from positional args to a dict-based approach:
```python
# Current (sorting): set_algorithm_info(name, time_best, time_avg, time_worst, space, stable)
# New (generic):     set_algorithm_info(info_dict)
# Sorting passes:    {"name": "Bubble Sort", "time_best": "O(n)", ..., "stable": True}
# Pathfinding passes: {"name": "A*", "time": "O((V+E) log V)", "space": "O(V)", "optimal": True}
```
The info panel renders whatever fields the dict contains. The `draw()` method checks for `"stable"` or `"optimal"` keys and labels accordingly.

**`set_stats()`** — Same dict-based approach:
```python
# Sorting passes:    {"comparisons": 45, "swaps": 12, "status": "Comparing..."}
# Pathfinding passes: {"cells_explored": 89, "frontier_size": 14, "path_length": 23, "total_cost": 47, "status": "Visiting (3,5)"}
```
The stats card renders each key-value pair with the key as the label (title-cased). This generalizes naturally for any future tab (trees, etc.).

Pseudocode definitions added to `algorithms/pseudocode.py` with line-to-operation mapping.

## Required Visualizer Interface

The pathfinding visualizer must implement these methods/attributes for `main.py` integration (matching what sorting provides via `hasattr()` checks):

### Methods
- `reset()` — Clear exploration state
- `step()` — Auto-advance (called by timer during playback)
- `step_forward()` — Single step forward
- `step_backward()` — Single step backward (from history)
- `draw(surface)` — Render grid and overlays
- `handle_event(event)` — Mouse/keyboard input
- `start()` / `pause()` / `toggle()` — Playback control
- `set_speed(speed)` — Animation speed
- `set_algorithm(key)` — Switch algorithm
- `set_grid_size(size_key)` — Switch grid dimensions (keys: `"Small"`, `"Medium"`, `"Large"`)
- `get_algorithm_info()` — Returns dict with name, time, space, optimal
- `get_status()` — Returns current status message
- `load_preset(preset_key)` — Apply a maze preset

### Attributes
- `algorithm_key` — Current algorithm identifier
- `is_running` — Playback state
- `is_complete` — Algorithm finished
- `cells_explored` — Counter (replaces sorting's `comparisons`)
- `path_length` — Counter (replaces sorting's `swaps`)
- `total_cost` — Path cost for weighted algorithms
- `current_op_type` — Last operation type (for pseudocode highlighting)
- `step_count` — Total steps taken

## File Changes

### New Files

| File | Purpose |
|------|---------|
| `algorithms/pathfinding.py` | BFS, DFS, Dijkstra, A* generator functions |

### Modified Files

| File | Changes |
|------|---------|
| `visualizers/pathfinding_viz.py` | Replace placeholder with full grid visualizer |
| `algorithms/pseudocode.py` | Add pathfinding pseudocode definitions |
| `config.py` | Add pathfinding colors, grid sizes, cell states, weight cost |
| `main.py` | Tab-switching control bar strategy: each tab owns its controls, swap on tab switch. Wire up pathfinding-specific buttons, selectors, and info panel fields. |
| `visualizers/base.py` | Add `step_forward()` and `step_backward()` to base interface (with default no-op implementations so sorting isn't broken) |
| `ui/info_panel.py` | Extend `set_algorithm_info()` to accept "optimal" field alongside "stable" |

### Untouched Files

- `algorithms/sorting.py`
- `visualizers/sorting_viz.py`
- All UI components (`button.py`, `button_group.py`, `slider.py`, `array_modal.py`, `help_modal.py`) — reused as-is

## Build Order (Incremental Safe Stops)

Each phase produces a demoable state:

1. **Grid infrastructure** — Grid rendering, cell model, wall/weight drawing, start/end placement, editing modes, editing mode toggle, Clear Grid
2. **BFS + DFS** — Algorithm generators, stepping, time-travel history, info panel integration, pseudocode, tab-switching control bar
3. **Weighted terrain + Dijkstra + A\*** — Weight painting, cost overlays, new algorithm generators, data overlays on cells
4. **Presets + polish** — Maze generation, preset patterns, animation effects (frontier pulse), path traceback animation, final tuning

## Design Decisions

- **Generator pattern reuse:** Same 4-tuple yield as sorting — consistent architecture, easy to understand in interview
- **Independent visualizer:** Pathfinding visualizer is fully self-contained, zero coupling with sorting
- **Incremental delivery:** Each build phase is independently demoable — safe to stop at any point
- **Weighted cells for Dijkstra/A\*:** Essential to demonstrate why these algorithms exist vs. BFS
- **Presets parallel sorting:** Design consistency across tabs (random, structured patterns, edge cases)
- **4-directional movement:** Simpler to implement and explain; Manhattan heuristic is clean for interviews
- **Grid editing locked during runs:** Prevents history invalidation without complex diffing
- **Per-tab control bars:** Clean separation, no state leakage, simpler code than dynamic reconfiguration
