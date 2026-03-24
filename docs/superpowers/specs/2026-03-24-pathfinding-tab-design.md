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
| A* | Yes | Yes (with admissible h) | O((V + E) log V) | O(V) |

All four live in `algorithms/pathfinding.py` as pure generator functions — no pygame imports.

## Grid System

### Cell Model

Each cell has: row, column, state, weight, and optional algorithm data.

**Cell states:** `EMPTY`, `WALL`, `START`, `END`, `WEIGHTED`, `VISITED`, `FRONTIER`, `PATH`

### Grid Sizes

| Label | Columns x Rows | Fits 1425x807 canvas |
|-------|---------------|----------------------|
| Small | 15 x 11 | ~95px cells |
| Medium | 25 x 18 | ~57px cells |
| Large | 40 x 28 | ~35px cells |

Cells are square with 1px gap between them. Sizes tuned to fill the canvas area.

### Interaction

- **Click + drag** to paint cells based on active editing mode
- **Editing modes:** Wall, Weight, Start, End (toggle via button group)
- Default mode: Wall
- Cannot overwrite start/end with walls
- Start and end points are single cells (placing a new one removes the old)

## Presets

Parallel to sorting presets (sorted, reversed, nearly-sorted, etc.):

| Preset | Description | Best demonstrates |
|--------|-------------|-------------------|
| Random walls | ~25-30% random walls, guaranteed solvable | General exploration |
| Recursive maze | Generated corridors and dead ends | DFS behavior |
| Spiral | Walls form spiral, forces winding path | BFS vs DFS difference |
| Open field + weights | Few walls, scattered weighted terrain | Dijkstra vs BFS |
| Bottleneck | Open areas connected by narrow passages | Frontier expansion |

All presets guarantee a valid path from start to end. Start placed top-left area, end placed bottom-right area. User can edit the grid after a preset is applied.

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
| `"done"` | Algorithm complete | total_explored, path_length, total_cost |

### Data Dict by Algorithm

- **BFS/DFS:** `{"distance": int, "parent": (r, c)}`
- **Dijkstra:** `{"cost": float, "parent": (r, c)}`
- **A\*:** `{"g": float, "h": float, "f": float, "parent": (r, c)}`

### History & Time-Travel

Full grid snapshot at each step (same as sorting). Backward/forward stepping with arrow keys. Space to play/pause.

## Visualization & Animation

### Cell Colors (Dark Theme)

| State | Color | RGB |
|-------|-------|-----|
| Empty | Dark gray | (40, 40, 55) |
| Wall | Solid dark | (60, 60, 75) |
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

## Control Bar

Same layout pattern as sorting tab's control bar:

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

**Grid editing mode** toggle (button group near grid or control bar): Wall / Weight / Start / End.

## Info Panel

Right-side panel mirroring sorting's layout:

1. **Algorithm card** — Name, time complexity, space complexity
2. **Live stats card** — Cells explored, frontier size, path length, total path cost
3. **Pseudocode card** — Algorithm pseudocode with highlighted current line
4. **Legend card** — Color key for all cell states

Pseudocode definitions added to `algorithms/pseudocode.py` with line-to-operation mapping.

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
| `config.py` | Add pathfinding colors, grid sizes, cell states |
| `main.py` | Wire up pathfinding control bar elements |

### Untouched Files

- `algorithms/sorting.py`
- `visualizers/sorting_viz.py`
- `visualizers/base.py` (existing abstract interface sufficient)
- All UI components (`button.py`, `button_group.py`, `slider.py`, `info_panel.py`, etc.) — reused as-is

## Build Order (Incremental Safe Stops)

Each phase produces a demoable state:

1. **Grid infrastructure** — Grid rendering, wall drawing, start/end placement, editing modes
2. **BFS + DFS** — Algorithm generators, stepping, time-travel, info panel, pseudocode
3. **Weighted terrain + Dijkstra + A\*** — Weight painting, cost overlays, new algorithms
4. **Presets + polish** — Maze generation, preset patterns, animation effects, final tuning

## Design Decisions

- **Generator pattern reuse:** Same 4-tuple yield as sorting — consistent architecture, easy to understand in interview
- **Independent visualizer:** Pathfinding visualizer is fully self-contained, zero coupling with sorting
- **Incremental delivery:** Each build phase is independently demoable — safe to stop at any point
- **Weighted cells for Dijkstra/A\*:** Essential to demonstrate why these algorithms exist vs. BFS
- **Presets parallel sorting:** Design consistency across tabs (random, structured patterns, edge cases)
