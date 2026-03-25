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
    # Stubs — implemented in later tasks
    # ------------------------------------------------------------------

    def handle_event(self, event):
        """Handle mouse / keyboard input. Implemented in Task 10."""
        pass

    def step(self):
        """Advance the algorithm by one step. Implemented in Task 11."""
        pass

    def step_forward(self):
        """Advance one step with history support. Implemented in Task 11."""
        pass

    def step_backward(self):
        """Rewind one step. Implemented in Task 11."""
        pass
