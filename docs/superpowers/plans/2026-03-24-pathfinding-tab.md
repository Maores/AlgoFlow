# Pathfinding Tab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fully interactive pathfinding visualization tab with BFS, DFS, Dijkstra, and A* on a 2D grid, with presets, weighted terrain, time-travel stepping, and animated frontier expansion.

**Architecture:** Extends the existing tab-based visualizer system. A new `PathfindingVisualizer` replaces the placeholder, consuming algorithm generators (same 4-tuple yield pattern as sorting). The info panel API is generalized to dict-based `set_algorithm_info()` and `set_stats()`. Each tab owns its own control bar widgets, swapped on tab switch in `main.py`.

**Tech Stack:** Python 3.10+, Pygame 2.x, existing UI components (Button, ButtonGroup, Slider, InfoPanel)

**Spec:** `docs/superpowers/specs/2026-03-24-pathfinding-tab-design.md`

---

## File Structure

### New Files
| File | Responsibility |
|------|---------------|
| `algorithms/pathfinding.py` | BFS, DFS, Dijkstra, A* generator functions (pure logic, no pygame) |
| `tests/test_pathfinding_algorithms.py` | Tests for all 4 algorithm generators |

### Modified Files
| File | Changes |
|------|---------|
| `config.py` | Add pathfinding colors, grid sizes, cell states, weight cost, grid size options |
| `visualizers/base.py` | Add `step_forward()` and `step_backward()` with default no-op implementations |
| `ui/info_panel.py` | Refactor `set_algorithm_info()` and `set_stats()` to dict-based API |
| `algorithms/pseudocode.py` | Add BFS, DFS, Dijkstra, A* pseudocode definitions |
| `visualizers/pathfinding_viz.py` | Replace placeholder with full grid visualizer |
| `main.py` | Per-tab control bar widgets, tab-switching logic, pathfinding event handling |

---

## Phase 1: Foundation (Config + Base Class + Info Panel API)

### Task 1: Add pathfinding constants to config.py

**Files:**
- Modify: `config.py` (Colors class lines 57-65; after line 108 for new constants)

**Note:** Some grid colors already exist in `config.py` at lines 57-65. We need to UPDATE existing values and ADD missing ones.

- [ ] **Step 1: Update existing grid colors and add missing ones**

In `config.py`, the Colors class already has grid colors at lines 57-65. Make these changes:

1. **Update** `GRID_VISITED` at line 62 from `(70, 100, 160)` to `(120, 80, 160)` (muted purple per spec)
2. **Add** `GRID_WEIGHTED = (180, 140, 50)` after line 64 (after `GRID_PATH`, before `GRID_LINE`)

Then add these new module-level constants after the Colors class (after line ~108):

```python
# --- Pathfinding ---
GRID_SIZES = {
    "Small": (15, 11),
    "Medium": (25, 18),
    "Large": (40, 25),
}
DEFAULT_GRID_SIZE = "Medium"
GRID_SIZE_OPTIONS = ["Small", "Medium", "Large"]
CELL_GAP = 1
WEIGHT_COST = 5
```

- [ ] **Step 2: Verify no syntax errors**

Run: `python -c "import config; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add config.py
git commit -m "feat: add pathfinding grid constants and colors to config"
```

---

### Task 2: Add step_forward/step_backward to base visualizer

**Files:**
- Modify: `visualizers/base.py` (after line 65, after `toggle()`)

- [ ] **Step 1: Add default implementations**

Add after the `toggle()` method (line 65) in `visualizers/base.py`:

```python
    def step_forward(self):
        """Advance one step. Override in subclasses for time-travel support."""
        self.step()

    def step_backward(self):
        """Go back one step. Override in subclasses for time-travel support."""
        pass
```

- [ ] **Step 2: Verify no import breakage**

Run: `python -c "from visualizers.sorting_viz import SortingVisualizer; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add visualizers/base.py
git commit -m "feat: add step_forward/step_backward defaults to BaseVisualizer"
```

---

### Task 3: Refactor info panel to dict-based API

This is the most delicate change — it must not break the existing sorting tab.

**Files:**
- Modify: `ui/info_panel.py` (lines 53-64: `set_algorithm_info()` and `set_stats()`)
- Modify: `main.py` (lines 233-236: calls to `set_algorithm_info()`, and lines 408-418: calls to `set_stats()`)

- [ ] **Step 1: Change `set_algorithm_info()` to accept a dict**

In `ui/info_panel.py`, replace `set_algorithm_info()` (lines 53-59) with:

```python
    def set_algorithm_info(self, info_dict):
        """Accept a dict of algorithm info. Keys vary by tab.
        Sorting: name, time_best, time_avg, time_worst, space, stable
        Pathfinding: name, time, space, optimal
        """
        self.algo_name = info_dict.get("name", "")
        self.time_best = info_dict.get("time_best", "")
        self.time_avg = info_dict.get("time_avg", "")
        self.time_worst = info_dict.get("time_worst", "")
        self.space = info_dict.get("space", "")
        self.stable = info_dict.get("stable", None)
        # Pathfinding-specific
        self.time_general = info_dict.get("time", "")
        self.optimal = info_dict.get("optimal", None)
```

- [ ] **Step 2: Change `set_stats()` to accept a dict with `tab` key**

In `ui/info_panel.py`, replace `set_stats()` (lines 61-64) with:

```python
    def set_stats(self, stats_dict):
        """Accept a dict of live stats. Must include 'tab' key for rendering.
        Sorting: tab="sorting", comparisons, swaps, status
        Pathfinding: tab="pathfinding", cells_explored, frontier_size, path_length, total_cost, status
        """
        self.stats_tab = stats_dict.get("tab", "sorting")
        self.comparisons = stats_dict.get("comparisons", 0)
        self.swaps = stats_dict.get("swaps", 0)
        self.status = stats_dict.get("status", "")
        # Pathfinding-specific
        self.cells_explored = stats_dict.get("cells_explored", 0)
        self.frontier_size = stats_dict.get("frontier_size", 0)
        self.path_length = stats_dict.get("path_length", 0)
        self.total_cost = stats_dict.get("total_cost", 0)
```

Also initialize `self.stats_tab = "sorting"` in `__init__` (around line 36).

- [ ] **Step 3: Update the draw method for algorithm info card (dynamic height)**

In the draw method of `info_panel.py`, find the algorithm info card section (around line 200-227). Replace the hardcoded 5-row layout with a dynamic rows list. The card height should be computed from `len(rows)` not a hardcoded `algo_rows = 5`.

```python
        # Build rows list based on which fields are populated:
        if self.time_general:
            # Pathfinding layout: Time, Space, Optimal (3 rows)
            algo_rows_data = [
                ("Time", self.time_general),
                ("Space", self.space),
                ("Optimal", "Yes" if self.optimal else "No"),
            ]
        else:
            # Sorting layout: Best, Avg, Worst, Space, Stable (5 rows)
            algo_rows_data = [
                ("Best", self.time_best),
                ("Average", self.time_avg),
                ("Worst", self.time_worst),
                ("Space", self.space),
                ("Stable", "Yes" if self.stable else "No"),
            ]

        # Compute card height dynamically:
        algo_rows = len(algo_rows_data)
        card1_h = card_pad + header_h + title_h + algo_rows * row_sp + bottom_pad
```

Then iterate `algo_rows_data` to render each row instead of the hardcoded Best/Avg/Worst/Space/Stable.

- [ ] **Step 4: Update the draw method for stats card (use `stats_tab` flag)**

In the stats card section (around line 229-261), use the `self.stats_tab` flag instead of checking zero values:

```python
        # Inside the stats card drawing section:
        if self.stats_tab == "pathfinding":
            # Pathfinding stats
            stat_rows = [
                ("Explored", str(self.cells_explored)),
                ("Frontier", str(self.frontier_size)),
                ("Path Length", str(self.path_length)),
                ("Total Cost", str(self.total_cost)),
            ]
        else:
            # Sorting stats (default)
            stat_rows = [
                ("Comparisons", str(self.comparisons)),
                ("Swaps", str(self.swaps)),
            ]
```

Compute stats card height dynamically from `len(stat_rows)` as well.

- [ ] **Step 5: Update ALL main.py callers to use dict API**

**IMPORTANT:** There are TWO places in main.py that call info panel methods. Both must be updated.

**A) `_update_info_panel()` (lines 229-239) — algorithm info:**

```python
    # Replace lines 233-236 with:
    info = viz.get_algorithm_info()
    self.info_panel.set_algorithm_info(info)
```

**B) `update()` method (lines 410-414) — live stats:**

This is the main game loop's `set_stats()` call. It currently uses positional args. Replace with dict:

```python
    # Replace the set_stats call in update() with:
    self.info_panel.set_stats({
        "tab": "sorting",
        "comparisons": viz.comparisons,
        "swaps": viz.swaps,
        "status": viz.get_status() if hasattr(viz, 'get_status') else ""
    })
```

Also update `SortingVisualizer.get_algorithm_info()` to return a dict if it doesn't already — check `visualizers/sorting_viz.py` for its return format and ensure it returns a dict with keys `name`, `time_best`, `time_avg`, `time_worst`, `space`, `stable`.

Also update the `set_variables()` call in `update()` (line 418) to be guarded with `if hasattr(viz, 'current_pointers'):` so it doesn't fail on the pathfinding tab.

- [ ] **Step 6: Test that sorting tab still works**

Run: `python main.py`
- Verify sorting tab renders correctly
- Verify info panel shows algorithm name, complexity, stats
- Verify pseudocode highlighting works
- Click through all 3 sorting algorithms to confirm

- [ ] **Step 7: Commit**

```bash
git add ui/info_panel.py main.py visualizers/sorting_viz.py
git commit -m "refactor: generalize info panel API to dict-based for multi-tab support"
```

---

## Phase 2: Algorithm Generators (TDD)

### Task 4: Write BFS algorithm generator with tests

**Files:**
- Create: `algorithms/pathfinding.py`
- Create: `tests/test_pathfinding_algorithms.py`

- [ ] **Step 1: Write BFS test**

Create `tests/test_pathfinding_algorithms.py`:

```python
"""Tests for pathfinding algorithm generators."""


def make_grid(rows, cols, walls=None, weights=None):
    """Create a simple grid for testing.
    Returns 2D list: 0=empty, -1=wall, >1=weighted cost.
    Default empty cell cost is 1.
    """
    grid = [[1] * cols for _ in range(rows)]
    if walls:
        for r, c in walls:
            grid[r][c] = -1
    if weights:
        for (r, c), cost in weights.items():
            grid[r][c] = cost
    return grid


def collect_ops(generator):
    """Collect all operations from a generator into a list."""
    return list(generator)


def test_bfs_simple_path():
    """BFS finds shortest path on a simple 5x5 grid."""
    from algorithms.pathfinding import bfs
    grid = make_grid(5, 5)
    start = (0, 0)
    end = (4, 4)
    ops = collect_ops(bfs(grid, start, end))

    # Must end with "done" or "path" as last op type
    op_types = [op[0] for op in ops]
    assert "done" in op_types
    assert "path" in op_types

    # Path ops should trace from start to end
    path_cells = [op[1] for op in ops if op[0] == "path"]
    assert start in path_cells
    assert end in path_cells

    # BFS optimal path length on open 5x5 grid: Manhattan distance = 8
    done_op = [op for op in ops if op[0] == "done"][0]
    assert done_op[3]["path_length"] == 9  # 9 cells including start and end


def test_bfs_no_path():
    """BFS reports no_path when end is unreachable."""
    from algorithms.pathfinding import bfs
    # Wall across row 2, blocking all passage
    walls = [(2, c) for c in range(5)]
    grid = make_grid(5, 5, walls=walls)
    start = (0, 0)
    end = (4, 4)
    ops = collect_ops(bfs(grid, start, end))

    op_types = [op[0] for op in ops]
    assert "no_path" in op_types
    assert "path" not in op_types


def test_bfs_yields_frontier_and_visit():
    """BFS yields frontier and visit operations."""
    from algorithms.pathfinding import bfs
    grid = make_grid(3, 3)
    ops = collect_ops(bfs(grid, (0, 0), (2, 2)))

    op_types = [op[0] for op in ops]
    assert "frontier" in op_types
    assert "visit" in op_types


def test_bfs_4_tuple_format():
    """Each yielded operation is a 4-tuple with correct types."""
    from algorithms.pathfinding import bfs
    grid = make_grid(3, 3)
    ops = collect_ops(bfs(grid, (0, 0), (2, 2)))

    for op in ops:
        assert len(op) == 4, f"Expected 4-tuple, got {len(op)}-tuple: {op}"
        op_type, cell, msg, data = op
        assert isinstance(op_type, str)
        assert isinstance(msg, str)
        assert isinstance(data, dict)


def test_bfs_ignores_weights():
    """BFS treats weighted cells as passable with cost 1."""
    from algorithms.pathfinding import bfs
    # Grid where direct path goes through weight-5 cells
    weights = {(1, 1): 5}
    grid = make_grid(3, 3, weights=weights)
    ops = collect_ops(bfs(grid, (0, 0), (2, 2)))

    op_types = [op[0] for op in ops]
    assert "done" in op_types
    # BFS should find shortest path (by hops), not cheapest — weighted cell is traversable
    path_cells = [op[1] for op in ops if op[0] == "path"]
    assert len(path_cells) > 0


def test_bfs_start_equals_end():
    """BFS handles start == end gracefully."""
    from algorithms.pathfinding import bfs
    grid = make_grid(3, 3)
    ops = collect_ops(bfs(grid, (1, 1), (1, 1)))

    op_types = [op[0] for op in ops]
    assert "done" in op_types
    done_op = [op for op in ops if op[0] == "done"][0]
    assert done_op[3]["path_length"] == 1
```

- [ ] **Step 2: Run tests — verify they fail**

Run: `python -m pytest tests/test_pathfinding_algorithms.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'algorithms.pathfinding'`

- [ ] **Step 3: Implement BFS generator**

Create `algorithms/pathfinding.py`:

```python
"""Pathfinding algorithm generators.

Each function is a generator that yields 4-tuples:
    (op_type, cell, status_msg, data_dict)

op_type: "frontier", "visit", "update", "path", "no_path", "done"
cell: (row, col) tuple
status_msg: human-readable description
data_dict: algorithm-specific data (distance, cost, f/g/h, parent, etc.)

Grid format: 2D list where -1=wall, 1=empty (cost 1), >1=weighted (cost N).
Movement: 4-directional (up, down, left, right).
"""

from collections import deque


def _neighbors(row, col, rows, cols):
    """Yield valid 4-directional neighbors."""
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            yield nr, nc


def bfs(grid, start, end):
    """Breadth-first search. Ignores weights (all edges cost 1)."""
    rows, cols = len(grid), len(grid[0])
    sr, sc = start
    er, ec = end

    visited = set()
    parent = {}
    queue = deque()

    visited.add((sr, sc))
    queue.append((sr, sc))
    distance = {(sr, sc): 0}

    yield ("frontier", (sr, sc), f"Start at ({sr},{sc})",
           {"distance": 0, "parent": None})

    while queue:
        r, c = queue.popleft()
        dist = distance[(r, c)]

        yield ("visit", (r, c),
               f"Visiting ({r},{c}), distance={dist}",
               {"distance": dist, "queue_size": len(queue)})

        if (r, c) == (er, ec):
            # Trace path back
            path = []
            node = (er, ec)
            while node is not None:
                path.append(node)
                node = parent.get(node)
            path.reverse()

            for cell in path:
                yield ("path", cell, "Tracing shortest path",
                       {"path_length": len(path)})

            yield ("done", (), "Path found!",
                   {"total_explored": len(visited),
                    "path_length": len(path), "total_cost": len(path) - 1})
            return

        for nr, nc in _neighbors(r, c, rows, cols):
            if (nr, nc) not in visited and grid[nr][nc] != -1:
                visited.add((nr, nc))
                parent[(nr, nc)] = (r, c)
                distance[(nr, nc)] = dist + 1
                queue.append((nr, nc))

                yield ("frontier", (nr, nc),
                       f"Adding ({nr},{nc}) to queue, distance={dist + 1}",
                       {"distance": dist + 1, "parent": (r, c)})

    yield ("no_path", (), "No path exists from start to end",
           {"total_explored": len(visited)})
```

- [ ] **Step 4: Run tests — verify they pass**

Run: `python -m pytest tests/test_pathfinding_algorithms.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add algorithms/pathfinding.py tests/test_pathfinding_algorithms.py
git commit -m "feat: add BFS pathfinding generator with tests"
```

---

### Task 5: Add DFS algorithm generator with tests

**Files:**
- Modify: `algorithms/pathfinding.py`
- Modify: `tests/test_pathfinding_algorithms.py`

- [ ] **Step 1: Write DFS tests**

Add to `tests/test_pathfinding_algorithms.py`:

```python
def test_dfs_finds_path():
    """DFS finds a path (not necessarily shortest) on a simple grid."""
    from algorithms.pathfinding import dfs
    grid = make_grid(5, 5)
    ops = collect_ops(dfs(grid, (0, 0), (4, 4)))

    op_types = [op[0] for op in ops]
    assert "done" in op_types
    assert "path" in op_types

    path_cells = [op[1] for op in ops if op[0] == "path"]
    assert (0, 0) in path_cells
    assert (4, 4) in path_cells


def test_dfs_no_path():
    """DFS reports no_path when end is unreachable."""
    from algorithms.pathfinding import dfs
    walls = [(2, c) for c in range(5)]
    grid = make_grid(5, 5, walls=walls)
    ops = collect_ops(dfs(grid, (0, 0), (4, 4)))

    op_types = [op[0] for op in ops]
    assert "no_path" in op_types


def test_dfs_4_tuple_format():
    """DFS yields valid 4-tuples."""
    from algorithms.pathfinding import dfs
    grid = make_grid(3, 3)
    ops = collect_ops(dfs(grid, (0, 0), (2, 2)))

    for op in ops:
        assert len(op) == 4
        op_type, cell, msg, data = op
        assert isinstance(op_type, str)
        assert isinstance(msg, str)
        assert isinstance(data, dict)
```

- [ ] **Step 2: Run tests — verify DFS tests fail**

Run: `python -m pytest tests/test_pathfinding_algorithms.py::test_dfs_finds_path -v`
Expected: FAIL — `ImportError`

- [ ] **Step 3: Implement DFS generator**

Add to `algorithms/pathfinding.py`:

```python
def dfs(grid, start, end):
    """Depth-first search. Ignores weights. Does NOT guarantee shortest path."""
    rows, cols = len(grid), len(grid[0])
    sr, sc = start
    er, ec = end

    visited = set()
    parent = {}
    stack = [(sr, sc)]
    distance = {(sr, sc): 0}

    yield ("frontier", (sr, sc), f"Start at ({sr},{sc})",
           {"distance": 0, "parent": None})

    while stack:
        r, c = stack.pop()

        if (r, c) in visited:
            continue
        visited.add((r, c))
        dist = distance[(r, c)]

        yield ("visit", (r, c),
               f"Visiting ({r},{c}), depth={dist}",
               {"distance": dist, "queue_size": len(stack)})

        if (r, c) == (er, ec):
            path = []
            node = (er, ec)
            while node is not None:
                path.append(node)
                node = parent.get(node)
            path.reverse()

            for cell in path:
                yield ("path", cell, "Tracing path",
                       {"path_length": len(path)})

            yield ("done", (), "Path found!",
                   {"total_explored": len(visited),
                    "path_length": len(path), "total_cost": len(path) - 1})
            return

        for nr, nc in _neighbors(r, c, rows, cols):
            if (nr, nc) not in visited and grid[nr][nc] != -1:
                if (nr, nc) not in distance:
                    parent[(nr, nc)] = (r, c)
                    distance[(nr, nc)] = dist + 1
                stack.append((nr, nc))

                yield ("frontier", (nr, nc),
                       f"Pushing ({nr},{nc}) to stack",
                       {"distance": dist + 1, "parent": (r, c)})

    yield ("no_path", (), "No path exists from start to end",
           {"total_explored": len(visited)})
```

- [ ] **Step 4: Run all tests**

Run: `python -m pytest tests/test_pathfinding_algorithms.py -v`
Expected: All 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add algorithms/pathfinding.py tests/test_pathfinding_algorithms.py
git commit -m "feat: add DFS pathfinding generator with tests"
```

---

### Task 6: Add Dijkstra algorithm generator with tests

**Files:**
- Modify: `algorithms/pathfinding.py`
- Modify: `tests/test_pathfinding_algorithms.py`

- [ ] **Step 1: Write Dijkstra tests**

Add to `tests/test_pathfinding_algorithms.py`:

```python
def test_dijkstra_finds_cheapest_path():
    """Dijkstra finds the minimum-cost path through weighted terrain."""
    from algorithms.pathfinding import dijkstra
    # 5x5 grid with a row of weight-5 cells across row 2
    weights = {(2, c): 5 for c in range(5)}
    grid = make_grid(5, 5, weights=weights)
    ops = collect_ops(dijkstra(grid, (0, 0), (4, 4)))

    op_types = [op[0] for op in ops]
    assert "done" in op_types

    done_op = [op for op in ops if op[0] == "done"][0]
    # Dijkstra should find a path — cost depends on route
    assert done_op[3]["path_length"] > 0
    assert done_op[3]["total_cost"] > 0


def test_dijkstra_prefers_cheap_route():
    """Dijkstra avoids expensive cells when a cheaper route exists."""
    from algorithms.pathfinding import dijkstra
    # 3x3 grid: center cell is very expensive
    grid = make_grid(3, 3, weights={(1, 1): 5})
    ops = collect_ops(dijkstra(grid, (0, 0), (2, 2)))

    path_cells = [op[1] for op in ops if op[0] == "path"]
    # The path should go around the center, not through it
    # Path via (0,0)->(0,1)->(0,2)->(1,2)->(2,2) costs 4
    # Path via (0,0)->(1,0)->(2,0)->(2,1)->(2,2) costs 4
    # Path via (0,0)->(1,1)->(2,2) costs 6
    # So center should NOT be in path
    assert (1, 1) not in path_cells


def test_dijkstra_no_path():
    """Dijkstra reports no_path when end is unreachable."""
    from algorithms.pathfinding import dijkstra
    walls = [(2, c) for c in range(5)]
    grid = make_grid(5, 5, walls=walls)
    ops = collect_ops(dijkstra(grid, (0, 0), (4, 4)))

    op_types = [op[0] for op in ops]
    assert "no_path" in op_types


def test_dijkstra_yields_update_ops():
    """Dijkstra yields update operations when relaxing edges."""
    from algorithms.pathfinding import dijkstra
    grid = make_grid(3, 3)
    ops = collect_ops(dijkstra(grid, (0, 0), (2, 2)))

    op_types = [op[0] for op in ops]
    assert "visit" in op_types
    assert "frontier" in op_types
```

- [ ] **Step 2: Run tests — verify Dijkstra tests fail**

Run: `python -m pytest tests/test_pathfinding_algorithms.py::test_dijkstra_finds_cheapest_path -v`
Expected: FAIL

- [ ] **Step 3: Implement Dijkstra generator**

Add to `algorithms/pathfinding.py`:

```python
import heapq


def dijkstra(grid, start, end):
    """Dijkstra's algorithm. Respects cell weights."""
    rows, cols = len(grid), len(grid[0])
    sr, sc = start
    er, ec = end

    dist = {}
    parent = {}
    visited = set()
    counter = 0  # Tiebreaker for heap

    dist[(sr, sc)] = 0
    heap = [(0, counter, sr, sc)]
    counter += 1

    yield ("frontier", (sr, sc), f"Start at ({sr},{sc})",
           {"cost": 0, "parent": None})

    while heap:
        cost, _, r, c = heapq.heappop(heap)

        if (r, c) in visited:
            continue
        visited.add((r, c))

        yield ("visit", (r, c),
               f"Visiting ({r},{c}), cost={cost}",
               {"cost": cost, "queue_size": len(heap)})

        if (r, c) == (er, ec):
            path = []
            node = (er, ec)
            while node is not None:
                path.append(node)
                node = parent.get(node)
            path.reverse()

            for cell in path:
                yield ("path", cell, "Tracing cheapest path",
                       {"path_length": len(path)})

            yield ("done", (), f"Path found! Cost={cost}",
                   {"total_explored": len(visited),
                    "path_length": len(path), "total_cost": cost})
            return

        for nr, nc in _neighbors(r, c, rows, cols):
            if (nr, nc) not in visited and grid[nr][nc] != -1:
                cell_cost = grid[nr][nc]
                new_cost = cost + cell_cost
                if (nr, nc) not in dist or new_cost < dist[(nr, nc)]:
                    old_cost = dist.get((nr, nc))
                    dist[(nr, nc)] = new_cost
                    parent[(nr, nc)] = (r, c)
                    heapq.heappush(heap, (new_cost, counter, nr, nc))
                    counter += 1

                    if old_cost is not None:
                        yield ("update", (nr, nc),
                               f"Relaxing ({nr},{nc}): {old_cost} -> {new_cost}",
                               {"old_cost": old_cost, "cost": new_cost,
                                "parent": (r, c)})
                    else:
                        yield ("frontier", (nr, nc),
                               f"Adding ({nr},{nc}), cost={new_cost}",
                               {"cost": new_cost, "parent": (r, c)})

    yield ("no_path", (), "No path exists from start to end",
           {"total_explored": len(visited)})
```

- [ ] **Step 4: Run all tests**

Run: `python -m pytest tests/test_pathfinding_algorithms.py -v`
Expected: All 11 tests PASS

- [ ] **Step 5: Commit**

```bash
git add algorithms/pathfinding.py tests/test_pathfinding_algorithms.py
git commit -m "feat: add Dijkstra pathfinding generator with tests"
```

---

### Task 7: Add A* algorithm generator with tests

**Files:**
- Modify: `algorithms/pathfinding.py`
- Modify: `tests/test_pathfinding_algorithms.py`

- [ ] **Step 1: Write A* tests**

Add to `tests/test_pathfinding_algorithms.py`:

```python
def test_astar_finds_optimal_path():
    """A* finds the optimal path using Manhattan heuristic."""
    from algorithms.pathfinding import astar
    grid = make_grid(5, 5)
    ops = collect_ops(astar(grid, (0, 0), (4, 4)))

    op_types = [op[0] for op in ops]
    assert "done" in op_types

    done_op = [op for op in ops if op[0] == "done"][0]
    # Optimal path on open grid: Manhattan distance + 1 = 9 cells
    assert done_op[3]["path_length"] == 9


def test_astar_explores_less_than_bfs():
    """A* should explore fewer cells than BFS on an open grid (heuristic guides it)."""
    from algorithms.pathfinding import astar, bfs
    grid = make_grid(10, 10)
    start, end = (0, 0), (9, 9)

    bfs_ops = collect_ops(bfs(grid, start, end))
    astar_ops = collect_ops(astar(grid, start, end))

    bfs_visited = len([op for op in bfs_ops if op[0] == "visit"])
    astar_visited = len([op for op in astar_ops if op[0] == "visit"])

    assert astar_visited <= bfs_visited


def test_astar_with_weights():
    """A* respects weighted terrain."""
    from algorithms.pathfinding import astar
    grid = make_grid(3, 3, weights={(1, 1): 5})
    ops = collect_ops(astar(grid, (0, 0), (2, 2)))

    path_cells = [op[1] for op in ops if op[0] == "path"]
    assert (1, 1) not in path_cells


def test_astar_no_path():
    """A* reports no_path when end is unreachable."""
    from algorithms.pathfinding import astar
    walls = [(2, c) for c in range(5)]
    grid = make_grid(5, 5, walls=walls)
    ops = collect_ops(astar(grid, (0, 0), (4, 4)))

    op_types = [op[0] for op in ops]
    assert "no_path" in op_types


def test_astar_yields_f_g_h():
    """A* data dict includes f, g, h values."""
    from algorithms.pathfinding import astar
    grid = make_grid(3, 3)
    ops = collect_ops(astar(grid, (0, 0), (2, 2)))

    frontier_ops = [op for op in ops if op[0] == "frontier"]
    for op in frontier_ops:
        data = op[3]
        assert "g" in data
        assert "h" in data
        assert "f" in data
        assert data["f"] == data["g"] + data["h"]
```

- [ ] **Step 2: Run tests — verify A* tests fail**

Run: `python -m pytest tests/test_pathfinding_algorithms.py::test_astar_finds_optimal_path -v`
Expected: FAIL

- [ ] **Step 3: Implement A* generator**

Add to `algorithms/pathfinding.py`:

```python
def _manhattan(r1, c1, r2, c2):
    """Manhattan distance heuristic."""
    return abs(r1 - r2) + abs(c1 - c2)


def astar(grid, start, end):
    """A* search with Manhattan distance heuristic. Respects cell weights."""
    rows, cols = len(grid), len(grid[0])
    sr, sc = start
    er, ec = end

    g_score = {}
    parent = {}
    visited = set()
    counter = 0

    g_score[(sr, sc)] = 0
    h = _manhattan(sr, sc, er, ec)
    heap = [(h, counter, sr, sc)]
    counter += 1

    yield ("frontier", (sr, sc), f"Start at ({sr},{sc})",
           {"g": 0, "h": h, "f": h, "parent": None})

    while heap:
        f, _, r, c = heapq.heappop(heap)

        if (r, c) in visited:
            continue
        visited.add((r, c))
        g = g_score[(r, c)]

        yield ("visit", (r, c),
               f"Visiting ({r},{c}), g={g}, f={f}",
               {"g": g, "h": f - g, "f": f, "queue_size": len(heap)})

        if (r, c) == (er, ec):
            path = []
            node = (er, ec)
            while node is not None:
                path.append(node)
                node = parent.get(node)
            path.reverse()

            for cell in path:
                yield ("path", cell, "Tracing optimal path",
                       {"path_length": len(path)})

            yield ("done", (), f"Path found! Cost={g}",
                   {"total_explored": len(visited),
                    "path_length": len(path), "total_cost": g})
            return

        for nr, nc in _neighbors(r, c, rows, cols):
            if (nr, nc) not in visited and grid[nr][nc] != -1:
                cell_cost = grid[nr][nc]
                new_g = g + cell_cost
                if (nr, nc) not in g_score or new_g < g_score[(nr, nc)]:
                    old_g = g_score.get((nr, nc))
                    g_score[(nr, nc)] = new_g
                    parent[(nr, nc)] = (r, c)
                    h = _manhattan(nr, nc, er, ec)
                    new_f = new_g + h
                    heapq.heappush(heap, (new_f, counter, nr, nc))
                    counter += 1

                    if old_g is not None:
                        yield ("update", (nr, nc),
                               f"Relaxing ({nr},{nc}): g={old_g}->{new_g}, f={new_f}",
                               {"g": new_g, "h": h, "f": new_f,
                                "old_cost": old_g, "cost": new_g,
                                "parent": (r, c)})
                    else:
                        yield ("frontier", (nr, nc),
                               f"Adding ({nr},{nc}), g={new_g}, h={h}, f={new_f}",
                               {"g": new_g, "h": h, "f": new_f,
                                "parent": (r, c)})

    yield ("no_path", (), "No path exists from start to end",
           {"total_explored": len(visited)})
```

- [ ] **Step 4: Run all tests**

Run: `python -m pytest tests/test_pathfinding_algorithms.py -v`
Expected: All 16 tests PASS

- [ ] **Step 5: Commit**

```bash
git add algorithms/pathfinding.py tests/test_pathfinding_algorithms.py
git commit -m "feat: add A* pathfinding generator with tests"
```

---

### Task 8: Add pathfinding pseudocode definitions

**Files:**
- Modify: `algorithms/pseudocode.py` (append after line 95, end of PSEUDOCODE dict)

- [ ] **Step 1: Add pseudocode for all 4 algorithms**

Add to the `PSEUDOCODE` dict in `algorithms/pseudocode.py`:

```python
    "BFS": {
        "lines": [
            "function BFS(grid, start, end):",
            "  queue ← [start]",
            "  visited ← {start}",
            "  while queue is not empty:",
            "    node ← queue.dequeue()",
            "    if node = end: trace path, return",
            "    for each neighbor of node:",
            "      if neighbor not visited and not wall:",
            "        visited.add(neighbor)",
            "        queue.enqueue(neighbor)",
            "  return no path found",
        ],
        "highlight_map": {
            "frontier": [9],
            "visit": [4],
            "path": [5],
            "no_path": [10],
            "done": [],
        }
    },
    "DFS": {
        "lines": [
            "function DFS(grid, start, end):",
            "  stack ← [start]",
            "  visited ← {}",
            "  while stack is not empty:",
            "    node ← stack.pop()",
            "    if node in visited: continue",
            "    visited.add(node)",
            "    if node = end: trace path, return",
            "    for each neighbor of node:",
            "      if neighbor not visited and not wall:",
            "        stack.push(neighbor)",
            "  return no path found",
        ],
        "highlight_map": {
            "frontier": [10],
            "visit": [4, 6],
            "path": [7],
            "no_path": [11],
            "done": [],
        }
    },
    "Dijkstra": {
        "lines": [
            "function Dijkstra(grid, start, end):",
            "  dist[start] ← 0",
            "  priority_queue ← [(0, start)]",
            "  while queue is not empty:",
            "    (cost, node) ← queue.pop_min()",
            "    if node visited: continue",
            "    mark node visited",
            "    if node = end: trace path, return",
            "    for each neighbor of node:",
            "      new_cost ← cost + edge_weight",
            "      if new_cost < dist[neighbor]:",
            "        dist[neighbor] ← new_cost",
            "        queue.push((new_cost, neighbor))",
            "  return no path found",
        ],
        "highlight_map": {
            "frontier": [12],
            "visit": [4, 6],
            "update": [10, 11],
            "path": [7],
            "no_path": [13],
            "done": [],
        }
    },
    "A*": {
        "lines": [
            "function A*(grid, start, end):",
            "  g[start] ← 0",
            "  f[start] ← h(start, end)",
            "  open_set ← [(f[start], start)]",
            "  while open_set is not empty:",
            "    (f, node) ← open_set.pop_min()",
            "    if node visited: continue",
            "    mark node visited",
            "    if node = end: trace path, return",
            "    for each neighbor of node:",
            "      new_g ← g[node] + edge_weight",
            "      if new_g < g[neighbor]:",
            "        g[neighbor] ← new_g",
            "        f[neighbor] ← new_g + h(neighbor, end)",
            "        open_set.push((f[neighbor], neighbor))",
            "  return no path found",
        ],
        "highlight_map": {
            "frontier": [14],
            "visit": [5, 7],
            "update": [11, 12, 13],
            "path": [8],
            "no_path": [15],
            "done": [],
        }
    },
```

- [ ] **Step 2: Verify no syntax errors**

Run: `python -c "from algorithms.pseudocode import PSEUDOCODE; print(list(PSEUDOCODE.keys()))"`
Expected: Prints list including BFS, DFS, Dijkstra, A*

- [ ] **Step 3: Commit**

```bash
git add algorithms/pseudocode.py
git commit -m "feat: add pathfinding pseudocode definitions for BFS, DFS, Dijkstra, A*"
```

---

## Phase 3: Grid Visualizer

### Task 9: Build the pathfinding visualizer — grid rendering and cell model

**Files:**
- Modify: `visualizers/pathfinding_viz.py` (replace entire placeholder)

- [ ] **Step 1: Implement grid data model and basic rendering**

Replace the entire contents of `visualizers/pathfinding_viz.py` with the grid visualizer. This is the largest single task. The visualizer must:

1. **Grid data model:**
   - `self.grid` — 2D list of cell costs: `1` (empty), `-1` (wall), `5` (weighted)
   - `self.cell_states` — 2D list of visual states: `"empty"`, `"wall"`, `"start"`, `"end"`, `"weighted"`, `"visited"`, `"frontier"`, `"path"`
   - `self.start` and `self.end` — `(row, col)` tuples
   - `self.grid_rows`, `self.grid_cols` — current dimensions from `GRID_SIZES[size_key]`

2. **Cell size computation:**
   - `cell_size = min((canvas_w - (cols+1)*gap) / cols, (canvas_h - (rows+1)*gap) / rows)`
   - Grid centered in canvas: compute `offset_x`, `offset_y` for centering

3. **Drawing:**
   - Loop over all cells, draw colored rectangles based on `self.cell_states[r][c]`
   - Map cell state to color using `Colors.GRID_*` constants from config
   - Draw weighted cell cost number centered in cell
   - Draw start cell with "S" label, end cell with "E" label

4. **Constructor:**
   - Accept `canvas_rect` (same as base class)
   - Initialize Medium grid by default
   - Place start at (0, 0), end at (rows-1, cols-1)
   - Set `self.algorithm_key = "BFS"`
   - Initialize empty state: `self.cells_explored = 0`, `self.path_length = 0`, etc.

5. **`reset()` implementation:**
   - Clear all cell_states back to empty/wall/weighted/start/end (preserve grid layout)
   - Reset algorithm state (generator, history, counters)
   - Set `is_running = False`, `is_complete = False`
   - Unlock editing (`self.editing_locked = False`)

6. **`clear_grid()` implementation:**
   - Reset entire grid to empty (all cells cost 1, state "empty")
   - Re-place start at (0,0) and end at (rows-1, cols-1)
   - Call `reset()` to clear any algorithm state

7. **Minimal `draw()` implementation:**
   - Draw grid cells with correct colors
   - Do NOT implement data overlays or animations yet — just solid colors

Key implementation details:
- Use `pygame.Rect` for each cell: `Rect(offset_x + c*(cell_size+gap), offset_y + r*(cell_size+gap), cell_size, cell_size)`
- Color mapping dict: `STATE_COLORS = {"empty": Colors.GRID_EMPTY, "wall": Colors.GRID_WALL, ...}`
- Fonts: use `pygame.font.SysFont(FONT_FAMILY, size)` scaled to cell_size

- [ ] **Step 2: Test grid renders**

Run: `python main.py`
- Switch to Pathfinding tab
- Verify grid of colored cells appears centered in canvas
- Verify start (green, "S") and end (red, "E") cells visible

- [ ] **Step 3: Commit**

```bash
git add visualizers/pathfinding_viz.py
git commit -m "feat: pathfinding visualizer — grid data model and basic rendering"
```

---

### Task 10: Add grid interaction — wall/weight drawing and editing modes

**Files:**
- Modify: `visualizers/pathfinding_viz.py`

- [ ] **Step 1: Implement mouse interaction**

Add to the pathfinding visualizer:

1. **Editing mode state:** `self.edit_mode = "wall"` (options: "wall", "weight", "start", "end")
2. **`self.editing_locked`** — True when algorithm has run (history exists)

3. **`handle_event()` implementation:**
   - On `MOUSEBUTTONDOWN` (left click): if click is within grid bounds and not locked:
     - Convert mouse (x, y) to grid (row, col) using offset and cell_size
     - If edit_mode is "wall": toggle cell between empty and wall
     - If edit_mode is "weight": toggle cell between empty and weighted (cost 5)
     - If edit_mode is "start": move start point to clicked cell
     - If edit_mode is "end": move end point to clicked cell
   - Cannot place wall/weight on start or end cell
   - Set `self.is_dragging = True`

   - On `MOUSEMOTION` while `is_dragging`: continue painting walls/weights (drag to paint)
   - On `MOUSEBUTTONUP`: set `self.is_dragging = False`

4. **Helper: `_pixel_to_cell(x, y)`** — returns (row, col) or None if outside grid

- [ ] **Step 2: Test grid interaction**

Run: `python main.py`
- Switch to Pathfinding tab
- Click on cells — verify walls appear (dark cells)
- Drag to paint multiple walls
- Verify start/end cells cannot be overwritten

- [ ] **Step 3: Commit**

```bash
git add visualizers/pathfinding_viz.py
git commit -m "feat: pathfinding grid interaction — wall drawing and editing modes"
```

---

### Task 11: Add algorithm execution, stepping, and time-travel history

**Files:**
- Modify: `visualizers/pathfinding_viz.py`

- [ ] **Step 1: Implement generator consumption and history**

Add to the pathfinding visualizer:

1. **Algorithm execution:**
   - `self.generator` — the active algorithm generator (BFS/DFS/Dijkstra/A*)
   - `self.history` — list of snapshots: each is `(cell_states_copy, cells_explored, frontier_size, path_length, total_cost, status_msg, op_type)`
   - `self.history_index` — current position in history

2. **`_create_generator()`** — builds grid cost array from `self.grid`, calls the appropriate algorithm function

3. **`step_forward()` override:**
   - If `history_index < len(history) - 1`: replay next snapshot from history
   - Else: consume next yield from generator, apply operation to cell_states, take snapshot, append to history
   - Update counters: cells_explored, frontier_size, path_length, total_cost

4. **`step_backward()` override:**
   - If `history_index > 0`: decrement index, restore snapshot
   - Update all counters from snapshot

5. **`step()` override (auto-advance):**
   - Calls `step_forward()`, sets `is_complete` if generator exhausted

6. **`start()` override:**
   - If generator is None, create it
   - Call `super().start()`

7. **`set_algorithm(key)`:**
   - Set `self.algorithm_key = key`
   - Call `reset()`

8. **`set_grid_size(size_key)`:**
   - Update grid dimensions from `GRID_SIZES[size_key]`
   - Reinitialize grid
   - Call `reset()`

9. **Operation application:**
   - `"frontier"`: set cell_state to "frontier"
   - `"visit"`: set cell_state to "visited"
   - `"path"`: set cell_state to "path"
   - `"update"`: cell stays "frontier" (just data changed)
   - `"no_path"` / `"done"`: set `is_complete = True`

10. **Lock editing:** Set `self.editing_locked = True` when history is non-empty. `reset()` clears history and unlocks.

- [ ] **Step 2: Test stepping**

Run: `python main.py`
- Switch to Pathfinding tab
- Draw some walls
- Press Space to start BFS — verify cells light up as frontier (blue) then visited (purple)
- Press Space to pause
- Press Right arrow to step forward — verify one cell changes
- Press Left arrow to step backward — verify it reverts
- Verify algorithm completes and path highlights in yellow

- [ ] **Step 3: Commit**

```bash
git add visualizers/pathfinding_viz.py
git commit -m "feat: pathfinding algorithm execution with time-travel history"
```

---

### Task 12: Add data overlays on cells

**Files:**
- Modify: `visualizers/pathfinding_viz.py`

- [ ] **Step 1: Implement value rendering on cells**

Add to the `draw()` method:

1. **Store algorithm data per cell:** `self.cell_data` — 2D array of dicts (distance, cost, f/g/h values from operation data_dict)
2. **Render values:**
   - For each cell in "frontier" or "visited" state, draw the relevant value:
     - BFS/DFS: distance value
     - Dijkstra: cost value
     - A*: f-score value
   - Font size: auto-scale based on `self.cell_size` (e.g., `max(10, cell_size // 3)`)
   - Color: white with slight transparency
   - Centered in cell
3. **Density control:**
   - Small grid (cell_size > 60): show on all non-empty cells
   - Medium/Large grid (cell_size < 60): show on frontier cells only

- [ ] **Step 2: Test overlays**

Run: `python main.py`
- Run BFS on Small grid — verify distance numbers appear on cells
- Switch to A* — verify f-scores appear
- Switch to Medium grid — verify only frontier cells show values

- [ ] **Step 3: Commit**

```bash
git add visualizers/pathfinding_viz.py
git commit -m "feat: add data value overlays on pathfinding grid cells"
```

---

### Task 13: Implement `get_algorithm_info()`, `get_status()`, and `clear_grid()` on pathfinding visualizer

This must come BEFORE main.py integration since main.py calls these methods.

**Files:**
- Modify: `visualizers/pathfinding_viz.py`

- [ ] **Step 1: Implement the info methods and clear_grid**

```python
PATHFINDING_ALGO_INFO = {
    "BFS": {"name": "Breadth-First Search", "time": "O(V + E)", "space": "O(V)", "optimal": True},
    "DFS": {"name": "Depth-First Search", "time": "O(V + E)", "space": "O(V)", "optimal": False},
    "Dijkstra": {"name": "Dijkstra's Algorithm", "time": "O((V+E) log V)", "space": "O(V)", "optimal": True},
    "A*": {"name": "A* Search", "time": "O((V+E) log V)", "space": "O(V)", "optimal": True},
}

def get_algorithm_info(self):
    return PATHFINDING_ALGO_INFO.get(self.algorithm_key, {})

def get_status(self):
    return self.current_status

def clear_grid(self):
    """Reset to fully empty grid with default start/end placement."""
    self.grid = [[1] * self.grid_cols for _ in range(self.grid_rows)]
    self.start = (0, 0)
    self.end = (self.grid_rows - 1, self.grid_cols - 1)
    self._update_cell_states()
    self.reset()
```

- [ ] **Step 2: Verify methods work**

Run: `python -c "from visualizers.pathfinding_viz import PathfindingVisualizer; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add visualizers/pathfinding_viz.py
git commit -m "feat: add algorithm info, status, and clear_grid methods to pathfinding visualizer"
```

---

## Phase 4: main.py Integration

### Task 14: Wire up pathfinding control bar and tab switching

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Create pathfinding control bar widgets**

In `main.py` `__init__()`, after the existing sorting control bar creation (around line 116), add:

1. **Pathfinding-specific widgets:**
   - `self.pf_algo_group` — `ButtonGroup` with labels `["BFS", "DFS", "Dijkstra", "A*"]`
   - `self.pf_size_group` — `ButtonGroup` with labels `["Small", "Medium", "Large"]`, default index 1
   - `self.pf_preset_group` — `ButtonGroup` with labels `["Random", "Maze", "Spiral", "Weighted", "Bottleneck"]`
   - `self.pf_clear_btn` — `Button` with label "Clear"
   - `self.pf_start_btn` — `Button` with label "Start"
   - `self.pf_reset_btn` — `Button` with label "Reset"
   - `self.pf_speed_slider` — `Slider` (same config as sorting)
   - `self.pf_help_btn` — `Button` with label "Help"

2. **Editing mode toggle:**
   - `self.pf_edit_mode_group` — `ButtonGroup` with labels `["Wall", "Weight", "Start", "End"]`, default index 0
   - Position: above the grid (y = HEADER_HEIGHT + 4), x = left edge of canvas + padding

3. **Store all pathfinding widgets** in a list for easy draw/event iteration

- [ ] **Step 2: Add layout positioning for pathfinding widgets**

In `_rebuild_layout()`, add a branch for pathfinding widget positioning:
- Same sequential x-accumulation pattern as sorting
- Edit mode group positioned above the grid
- Help button right-anchored (same as sorting)

- [ ] **Step 3: Update event handling for tab-aware dispatch**

In `handle_events()`:
- Check `self.tab_bar.get_active_tab()` to determine which widgets to dispatch events to
- If Pathfinding tab active:
  - Route events to `pf_start_btn`, `pf_reset_btn`, `pf_speed_slider`, `pf_algo_group`, `pf_size_group`, `pf_preset_group`, `pf_clear_btn`, `pf_edit_mode_group`, `pf_help_btn`
  - On algo change: call `viz.set_algorithm(label)` + `_update_info_panel()`
  - On size change: call `viz.set_grid_size(label)`
  - On preset change: call `viz.load_preset(label)`
  - On clear: call `viz.clear_grid()`
  - On edit mode change: set `viz.edit_mode = label.lower()`

- [ ] **Step 4: Update draw method**

In `draw()`, draw only the active tab's control bar widgets:
- If sorting active: draw sorting widgets (existing code)
- If pathfinding active: draw pathfinding widgets + edit mode toggle

- [ ] **Step 5: Update `_update_info_panel()` for pathfinding**

Add an `elif` branch:

```python
def _update_info_panel(self):
    tab = self.tab_bar.get_active_tab()
    viz = self.get_active_visualizer()
    if tab == "Sorting":
        # existing sorting code (now using dict API)
        if hasattr(viz, 'get_algorithm_info'):
            self.info_panel.set_algorithm_info(viz.get_algorithm_info())
        self.info_panel.set_pseudocode_state(viz.algorithm_key, viz.current_op_type)
    elif tab == "Pathfinding":
        if hasattr(viz, 'get_algorithm_info'):
            self.info_panel.set_algorithm_info(viz.get_algorithm_info())
        self.info_panel.set_stats({
            "tab": "pathfinding",
            "cells_explored": viz.cells_explored,
            "frontier_size": getattr(viz, 'frontier_size', 0),
            "path_length": viz.path_length,
            "total_cost": viz.total_cost,
            "status": viz.get_status() if hasattr(viz, 'get_status') else ""
        })
        self.info_panel.set_pseudocode_state(viz.algorithm_key, viz.current_op_type)
```

Also update the `update()` method's `set_stats()` call (around line 410) to include `"tab": "sorting"` so the info panel knows which stats to render.

- [ ] **Step 6: Set legend on tab switch (both directions)**

In the tab-switch handler (where `tab_bar.handle_event()` detects a change), set the appropriate legend:

```python
# When switching TO Pathfinding tab:
self.info_panel.set_legend([
    (Colors.GRID_START, "Start"),
    (Colors.GRID_END, "End"),
    (Colors.GRID_WALL, "Wall"),
    (Colors.GRID_WEIGHTED, "Weighted"),
    (Colors.GRID_FRONTIER, "Frontier"),
    (Colors.GRID_VISITED, "Visited"),
    (Colors.GRID_PATH, "Path"),
])

# When switching TO Sorting tab:
self.info_panel.set_legend([
    (Colors.BAR_DEFAULT, "Default"),
    (Colors.BAR_COMPARING, "Comparing"),
    (Colors.BAR_SWAPPING, "Swapping"),
    (Colors.BAR_SORTED, "Sorted"),
    (Colors.BAR_PIVOT, "Pivot"),
])
```

This ensures the legend updates in BOTH directions, not just when entering pathfinding.

- [ ] **Step 7: Test full integration**

Run: `python main.py`
- Switch between Sorting and Pathfinding tabs — verify control bars swap correctly
- In Pathfinding: verify all buttons work (algorithm switch, size switch, start/pause, reset)
- Verify info panel shows pathfinding stats and pseudocode
- Verify sorting tab still works correctly after switching back
- Test continuous arrow key stepping in pathfinding

- [ ] **Step 8: Commit**

```bash
git add main.py
git commit -m "feat: wire up pathfinding control bar and tab switching in main.py"
```

---

## Phase 5: Presets and Polish

### Task 15: Implement maze presets

**Files:**
- Modify: `visualizers/pathfinding_viz.py`

- [ ] **Step 1: Implement `load_preset()` method**

Add to pathfinding visualizer:

```python
def load_preset(self, preset_key):
    """Generate a preset grid pattern."""
    self.reset()
    self._clear_grid()

    if preset_key == "Random":
        self._generate_random_walls()
    elif preset_key == "Maze":
        self._generate_recursive_maze()
    elif preset_key == "Spiral":
        self._generate_spiral()
    elif preset_key == "Weighted":
        self._generate_weighted_field()
    elif preset_key == "Bottleneck":
        self._generate_bottleneck()

    # Place start top-left, end bottom-right
    self.start = (0, 0)
    self.end = (self.grid_rows - 1, self.grid_cols - 1)
    self._update_cell_states()

    # Validate path exists (BFS check) — retry with loop, max 10 attempts
    for _ in range(10):
        if self._has_valid_path():
            break
        self._clear_grid()
        if preset_key == "Random":
            self._generate_random_walls()
        elif preset_key == "Maze":
            self._generate_recursive_maze()
        elif preset_key == "Spiral":
            self._generate_spiral()
        elif preset_key == "Weighted":
            self._generate_weighted_field()
        elif preset_key == "Bottleneck":
            self._generate_bottleneck()
```

- [ ] **Step 2: Implement each preset generator**

1. **`_generate_random_walls()`:** Randomly set ~25-30% of cells to wall. Avoid start/end positions.

2. **`_generate_recursive_maze()`:** Recursive backtracking:
   - Fill grid with walls
   - Start from (0,0), carve paths by visiting random unvisited neighbors (2 cells away)
   - Creates corridors with walls between them

3. **`_generate_spiral()`:** Programmatically create walls in a spiral pattern from the outside in, leaving a passage.

4. **`_generate_weighted_field()`:** Few random walls (~5%), scatter weighted cells (cost 5) across ~20-30% of grid.

5. **`_generate_bottleneck()`:** Create 2-3 large open chambers connected by 1-cell-wide passages.

6. **`_has_valid_path()`:** Quick BFS from start to end (not a generator — just returns bool).

- [ ] **Step 3: Test presets**

Run: `python main.py`
- Switch to Pathfinding tab
- Click each preset button — verify grid pattern changes
- Run BFS on each preset — verify path is always found
- Verify you can edit the grid after applying a preset (before running)

- [ ] **Step 4: Commit**

```bash
git add visualizers/pathfinding_viz.py
git commit -m "feat: add maze preset generators for pathfinding grid"
```

---

### Task 16: Add animated frontier expansion

**Files:**
- Modify: `visualizers/pathfinding_viz.py`

- [ ] **Step 1: Implement flash animation**

Add to pathfinding visualizer:

1. **`self.flash_timers`** — 2D array of floats, same dimensions as grid. Each value is the remaining flash time in seconds (0 = no flash).

2. **On cell state change:** Set `self.flash_timers[r][c] = 0.2` (200ms)

3. **In `draw()`:** For each cell:
   - If `flash_timers[r][c] > 0`:
     - Compute blend factor: `flash_timers[r][c] / 0.2` (1.0 = full flash, 0.0 = done)
     - Brighten the base color by factor: `min(255, int(base_r * (1 + 0.5 * blend)))` for each RGB channel
     - Decrement timer: `flash_timers[r][c] -= dt` (where dt = 1/60 at 60fps)

- [ ] **Step 2: Add path traceback animation**

After algorithm yields "done":
- Instead of showing all path cells at once, reveal them one per frame
- Use a `self.path_reveal_index` counter, incrementing each draw frame
- Only draw path cells up to `path_reveal_index`

- [ ] **Step 3: Test animations**

Run: `python main.py`
- Run BFS — verify cells flash brighter when first explored
- Verify the ripple effect looks smooth
- Verify path traces out cell-by-cell at the end

- [ ] **Step 4: Commit**

```bash
git add visualizers/pathfinding_viz.py
git commit -m "feat: add frontier flash animation and path traceback reveal"
```

---

### Task 17: Final integration testing and polish

**Files:**
- All files touched in previous tasks

- [ ] **Step 1: Run all automated tests**

Run: `python -m pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 2: Manual integration test checklist**

Run: `python main.py` and verify:

- [ ] Sorting tab works exactly as before (no regressions)
- [ ] Pathfinding tab: grid renders with correct colors
- [ ] Click+drag to paint walls works
- [ ] Edit mode toggle (Wall/Weight/Start/End) works
- [ ] All 4 algorithms run correctly (BFS, DFS, Dijkstra, A*)
- [ ] Step forward/backward with arrow keys works
- [ ] Space to play/pause works
- [ ] Speed slider affects animation speed
- [ ] Size selector changes grid (Small/Medium/Large)
- [ ] All 5 presets generate valid mazes
- [ ] Grid editing is locked during/after algorithm run
- [ ] Reset clears exploration but keeps grid
- [ ] Clear Grid resets everything
- [ ] Info panel shows correct algorithm info, live stats, pseudocode
- [ ] Legend shows pathfinding color key
- [ ] Pseudocode highlights current operation
- [ ] Frontier flash animation visible
- [ ] Path traceback animates cell-by-cell
- [ ] Weighted cells display cost number
- [ ] Data overlays show on cells (distances/f-scores)
- [ ] Dijkstra/A* avoid expensive weighted cells
- [ ] No path found message when grid is unsolvable
- [ ] Tab switching preserves state in each tab
- [ ] Window resize reflows layout correctly

- [ ] **Step 3: Fix any issues found**

Address any bugs or visual glitches discovered during testing.

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete pathfinding tab — all algorithms, presets, and animations"
```

- [ ] **Step 5: Push to remote**

```bash
git push -u origin claude/setup-algoflow-scaffold-V3Aic
```
