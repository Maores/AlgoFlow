# visualizers/pathfinding_viz.py - Pathfinding algorithm visualizer
import pygame
from visualizers.base import BaseVisualizer
from config import (
    Colors, GRID_SIZES, DEFAULT_GRID_SIZE, CELL_GAP,
    WEIGHT_COST, FONT_FAMILY, FONT_SIZES
)

STATE_COLORS = {
    "empty":    Colors.GRID_EMPTY,
    "wall":     Colors.GRID_WALL,
    "weighted": Colors.GRID_WEIGHTED,
    "start":    Colors.GRID_START,
    "end":      Colors.GRID_END,
    "frontier": Colors.GRID_FRONTIER,
    "visited":  Colors.GRID_VISITED,
    "path":     Colors.GRID_PATH,
}


class PathfindingVisualizer(BaseVisualizer):
    """
    Visualizer for pathfinding algorithms (BFS, DFS, Dijkstra, A*).

    Grid data model
    ---------------
    self.grid        : 2-D list of cell costs  — 1 (empty), -1 (wall), 5 (weighted)
    self.cell_states : 2-D list of visual state strings (see STATE_COLORS)
    self.start       : (row, col) tuple
    self.end         : (row, col) tuple
    """

    def __init__(self, canvas_rect):
        super().__init__(canvas_rect)

        # Fonts
        self.font_label  = pygame.font.SysFont(FONT_FAMILY, FONT_SIZES["small"], bold=True)
        self.font_cost   = pygame.font.SysFont(FONT_FAMILY, FONT_SIZES["tiny"])

        # Algorithm selection
        self.algorithm_key = "BFS"

        # Algorithm counters / status
        self.cells_explored  = 0
        self.path_length     = 0
        self.total_cost      = 0
        self.frontier_size   = 0
        self.current_op_type = ""
        self.current_status  = ""

        # Step-history state
        self.generator     = None
        self.history       = []
        self.history_index = -1

        # Editing state
        self.edit_mode      = "wall"
        self.editing_locked = False
        self.is_dragging    = False
        self._drag_action   = None

        # Data / animation overlays (populated in later tasks)
        self.cell_data    = None
        self.flash_timers = None

        # Geometry (computed in draw; stored for interaction code)
        self.cell_size = 0
        self.offset_x  = 0
        self.offset_y  = 0

        # Build the initial grid
        self._init_grid(DEFAULT_GRID_SIZE)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _init_grid(self, size_key: str):
        """Initialise (or reinitialise) the grid for the given size key."""
        rows, cols = GRID_SIZES[size_key]
        self.grid_rows = rows
        self.grid_cols = cols

        # All cells start as empty (cost = 1)
        self.grid = [[1] * cols for _ in range(rows)]

        # Place default start / end
        self.start = (0, 0)
        self.end   = (rows - 1, cols - 1)

        self._update_cell_states()
        self.cell_data    = None
        self.flash_timers = None

    def _update_cell_states(self):
        """Rebuild cell_states from grid, start, and end."""
        rows = self.grid_rows
        cols = self.grid_cols
        self.cell_states = [["empty"] * cols for _ in range(rows)]

        for r in range(rows):
            for c in range(cols):
                cost = self.grid[r][c]
                if cost == -1:
                    self.cell_states[r][c] = "wall"
                elif cost > 1:
                    self.cell_states[r][c] = "weighted"
                elif (r, c) == self.start:
                    self.cell_states[r][c] = "start"
                elif (r, c) == self.end:
                    self.cell_states[r][c] = "end"
                else:
                    self.cell_states[r][c] = "empty"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self):
        """
        Clear algorithm output (visited/frontier/path cells) but preserve
        the user-drawn walls and weighted cells.
        """
        self._update_cell_states()          # rebuilds from grid (no algo states)
        self.generator     = None
        self.history       = []
        self.history_index = -1
        self.cells_explored  = 0
        self.path_length     = 0
        self.total_cost      = 0
        self.frontier_size   = 0
        self.current_op_type = ""
        self.current_status  = ""
        self.is_running      = False
        self.is_complete     = False
        self.editing_locked  = False

    def clear_grid(self):
        """Reset the entire grid to empty, then call reset()."""
        rows = self.grid_rows
        cols = self.grid_cols
        self.grid = [[1] * cols for _ in range(rows)]
        self.start = (0, 0)
        self.end   = (rows - 1, cols - 1)
        self.reset()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface):
        """Render the grid onto *surface*."""
        canvas_x = self.canvas_rect.x
        canvas_y = self.canvas_rect.y
        canvas_w = self.canvas_rect.width
        canvas_h = self.canvas_rect.height

        rows = self.grid_rows
        cols = self.grid_cols
        gap  = CELL_GAP

        # ---- compute cell size so the whole grid fits inside the canvas ----
        cell_w = (canvas_w - (cols + 1) * gap) / cols
        cell_h = (canvas_h - (rows + 1) * gap) / rows
        cell_size = int(min(cell_w, cell_h))
        self.cell_size = cell_size

        # ---- centre the grid ----
        grid_pixel_w = cols * cell_size + (cols + 1) * gap
        grid_pixel_h = rows * cell_size + (rows + 1) * gap
        self.offset_x = canvas_x + (canvas_w - grid_pixel_w) // 2
        self.offset_y = canvas_y + (canvas_h - grid_pixel_h) // 2

        # ---- draw each cell ----
        for r in range(rows):
            for c in range(cols):
                state = self.cell_states[r][c]
                color = STATE_COLORS.get(state, Colors.GRID_EMPTY)

                x = self.offset_x + gap + c * (cell_size + gap)
                y = self.offset_y + gap + r * (cell_size + gap)
                rect = pygame.Rect(x, y, cell_size, cell_size)

                pygame.draw.rect(surface, color, rect)

                # ---- labels ----
                if state == "start":
                    self._draw_cell_label(surface, "S", rect, Colors.BG)
                elif state == "end":
                    self._draw_cell_label(surface, "E", rect, Colors.BG)
                elif state == "weighted":
                    cost = self.grid[r][c]
                    self._draw_cell_cost(surface, str(cost), rect)

    def _draw_cell_label(self, surface, text, rect, color):
        """Render a centred bold letter inside a cell rect."""
        surf = self.font_label.render(text, True, color)
        surface.blit(surf, surf.get_rect(center=rect.center))

    def _draw_cell_cost(self, surface, text, rect):
        """Render a small cost number centred inside a cell rect."""
        surf = self.font_cost.render(text, True, Colors.BG)
        surface.blit(surf, surf.get_rect(center=rect.center))

    # ------------------------------------------------------------------
    # Grid interaction helpers
    # ------------------------------------------------------------------

    def _pixel_to_cell(self, x, y):
        """Convert pixel (x, y) to grid (row, col) or None if outside."""
        gap = CELL_GAP
        # Relative to grid origin
        rx = x - self.offset_x
        ry = y - self.offset_y
        if rx < 0 or ry < 0:
            return None
        col = int(rx / (self.cell_size + gap))
        row = int(ry / (self.cell_size + gap))
        if row < 0 or row >= self.grid_rows or col < 0 or col >= self.grid_cols:
            return None
        # Check we're actually inside the cell, not in the gap
        cell_x = col * (self.cell_size + gap)
        cell_y = row * (self.cell_size + gap)
        if rx - cell_x > self.cell_size or ry - cell_y > self.cell_size:
            return None
        return (row, col)

    def _apply_edit(self, cell):
        """Apply the current edit_mode action to the given (row, col) cell."""
        r, c = cell
        # Cannot edit start or end cells in wall/weight mode
        if self.edit_mode in ("wall", "weight") and (cell == self.start or cell == self.end):
            return

        if self.edit_mode == "wall":
            if self._drag_action is None:
                # First cell in drag — determine toggle direction
                self._drag_action = "remove" if self.grid[r][c] == -1 else "place"
            if self._drag_action == "place":
                self.grid[r][c] = -1
            else:
                self.grid[r][c] = 1

        elif self.edit_mode == "weight":
            if self._drag_action is None:
                self._drag_action = "remove" if self.grid[r][c] > 1 else "place"
            if self._drag_action == "place":
                self.grid[r][c] = WEIGHT_COST
            else:
                self.grid[r][c] = 1

        elif self.edit_mode == "start":
            if cell != self.end:
                self.start = cell
                # Clear wall/weight at new start
                self.grid[cell[0]][cell[1]] = 1

        elif self.edit_mode == "end":
            if cell != self.start:
                self.end = cell
                self.grid[cell[0]][cell[1]] = 1

        self._update_cell_states()

    # ------------------------------------------------------------------
    # Stubs — implemented in later tasks
    # ------------------------------------------------------------------

    def handle_event(self, event):
        """Handle mouse / keyboard input."""
        if self.editing_locked:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cell = self._pixel_to_cell(event.pos[0], event.pos[1])
            if cell is not None:
                self.is_dragging = True
                self._drag_action = None  # Will be set on first drag
                self._apply_edit(cell)

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            cell = self._pixel_to_cell(event.pos[0], event.pos[1])
            if cell is not None:
                self._apply_edit(cell)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False
            self._drag_action = None

    # ------------------------------------------------------------------
    # Algorithm execution helpers
    # ------------------------------------------------------------------

    def _create_generator(self):
        """Create a fresh algorithm generator from the current grid state."""
        from algorithms.pathfinding import bfs, dfs, dijkstra, astar
        algo_map = {
            "BFS": bfs,
            "DFS": dfs,
            "Dijkstra": dijkstra,
            "A*": astar,
        }
        algo_func = algo_map.get(self.algorithm_key, bfs)
        return algo_func(self.grid, self.start, self.end)

    def _take_snapshot(self):
        """Snapshot current state for history."""
        import copy
        return {
            "cell_states": copy.deepcopy(self.cell_states),
            "cells_explored": self.cells_explored,
            "frontier_size": self.frontier_size,
            "path_length": self.path_length,
            "total_cost": self.total_cost,
            "current_status": self.current_status,
            "current_op_type": self.current_op_type,
        }

    def _restore_snapshot(self, snapshot):
        """Restore state from a history entry."""
        self.cell_states = snapshot["cell_states"]
        self.cells_explored = snapshot["cells_explored"]
        self.frontier_size = snapshot["frontier_size"]
        self.path_length = snapshot["path_length"]
        self.total_cost = snapshot["total_cost"]
        self.current_status = snapshot["current_status"]
        self.current_op_type = snapshot["current_op_type"]

    def _apply_operation(self, op):
        """Apply a yielded operation to the visual state."""
        op_type, cell, msg, data = op
        self.current_op_type = op_type
        self.current_status = msg

        if op_type == "frontier":
            r, c = cell
            if (r, c) != self.start and (r, c) != self.end:
                self.cell_states[r][c] = "frontier"
            self.frontier_size += 1

        elif op_type == "visit":
            r, c = cell
            if (r, c) != self.start and (r, c) != self.end:
                self.cell_states[r][c] = "visited"
            self.cells_explored += 1
            self.frontier_size = max(0, self.frontier_size - 1)

        elif op_type == "update":
            pass  # Cell stays "frontier", just data changed

        elif op_type == "path":
            r, c = cell
            self.cell_states[r][c] = "path"
            self.path_length = data.get("path_length", 0)

        elif op_type == "done":
            self.path_length = data.get("path_length", 0)
            self.total_cost = data.get("total_cost", 0)
            self.is_complete = True

        elif op_type == "no_path":
            self.is_complete = True

    # ------------------------------------------------------------------
    # Step / playback controls
    # ------------------------------------------------------------------

    def step_forward(self):
        """Advance one step, with time-travel support."""
        if self.is_complete:
            return

        # If we can replay from history
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self._restore_snapshot(self.history[self.history_index])
            return

        # Otherwise consume next from generator
        if self.generator is None:
            return

        try:
            op = next(self.generator)
            self._apply_operation(op)
            self.step_count += 1
            self.editing_locked = True
            # Take snapshot and append
            snapshot = self._take_snapshot()
            self.history.append(snapshot)
            self.history_index = len(self.history) - 1
        except StopIteration:
            self.is_complete = True
            self.is_running = False

    def step_backward(self):
        """Go back one step using history."""
        if self.history_index > 0:
            self.history_index -= 1
            import copy
            self._restore_snapshot(copy.deepcopy(self.history[self.history_index]))
            self.is_complete = False
        elif self.history_index == 0:
            # Go back to initial state (before any steps)
            self.history_index = -1
            self._update_cell_states()
            self.cells_explored = 0
            self.frontier_size = 0
            self.path_length = 0
            self.total_cost = 0
            self.current_status = ""
            self.current_op_type = ""
            self.is_complete = False

    def step(self):
        """Auto-advance — called by game loop when is_running is True."""
        self.step_forward()
        if self.is_complete:
            self.is_running = False

    def start(self):
        """Start algorithm execution."""
        if self.generator is None:
            self.generator = self._create_generator()
            self.editing_locked = True
        super().start()

    def toggle(self):
        """Toggle play/pause. If complete, reset first."""
        if self.is_complete:
            self.reset()
        if self.generator is None:
            self.generator = self._create_generator()
            self.editing_locked = True
        super().toggle()

    def set_algorithm(self, key):
        """Set the active algorithm and reset."""
        self.algorithm_key = key
        self.reset()

    def set_grid_size(self, size_key):
        """Resize the grid and reset."""
        self._init_grid(size_key)
        self.reset()
