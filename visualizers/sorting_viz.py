# visualizers/sorting_viz.py - Sorting algorithm visualizer for AlgoFlow
import pygame
import random
from visualizers.base import BaseVisualizer
from config import Colors, BOX_MODE_THRESHOLD, DEFAULT_ARRAY_SIZE, FONT_FAMILY
from algorithms.sorting import ALGORITHM_INFO


class SortingVisualizer(BaseVisualizer):
    """
    Visualizes sorting algorithms with hybrid rendering:
    - Box mode (≤30 elements): array cells showing numeric values
    - Bar mode (>30 elements): vertical bars proportional to value

    Uses the generator pattern to step through algorithms one operation
    at a time without threads.
    """

    def __init__(self, canvas_rect):
        super().__init__(canvas_rect)
        self.array_size = DEFAULT_ARRAY_SIZE
        self.array = []
        self.bar_colors = []
        self.algorithm_key = "Bubble"
        self.comparisons = 0
        self.swaps = 0
        self.generator = None

        # Time-travel history: list of (array_copy, colors_copy, comparisons, swaps) snapshots
        self.history = []
        self.history_index = -1

        # Fonts created once, reused every frame
        self.font_box_large = pygame.font.SysFont(FONT_FAMILY, 24, bold=True)
        self.font_box_small = pygame.font.SysFont(FONT_FAMILY, 20, bold=True)
        self.font_index = pygame.font.SysFont(FONT_FAMILY, 18)

        self.reset()

    def _use_box_mode(self):
        return self.array_size <= BOX_MODE_THRESHOLD

    def get_algorithm_info(self):
        return ALGORITHM_INFO[self.algorithm_key]

    def set_algorithm(self, key):
        if key in ALGORITHM_INFO:
            self.algorithm_key = key
            self.reset()

    def set_array_size(self, size):
        self.array_size = size
        self.reset()

    def reset(self):
        if self._use_box_mode():
            self.array = [random.randint(1, 50) for _ in range(self.array_size)]
        else:
            self.array = [random.randint(10, 100) for _ in range(self.array_size)]
        self.bar_colors = [Colors.BAR_DEFAULT] * self.array_size
        self.is_running = False
        self.is_complete = False
        self.comparisons = 0
        self.swaps = 0
        self.step_count = 0
        self.generator = None
        self.history = []
        self.history_index = -1

    def start(self):
        if self.generator is None:
            gen_func = ALGORITHM_INFO[self.algorithm_key]["generator"]
            self.generator = gen_func(self.array)
        self.is_running = True
        self.is_complete = False

    def toggle(self):
        if self.is_complete:
            self.reset()
        if not self.is_running:
            self.start()
        else:
            self.is_running = False

    def step(self):
        """Advance the generator by one operation and record the snapshot."""
        if self.generator is None:
            return

        # Reset non-sorted bars to default
        for i in range(len(self.bar_colors)):
            if self.bar_colors[i] != Colors.BAR_SORTED:
                self.bar_colors[i] = Colors.BAR_DEFAULT

        try:
            op = next(self.generator)
        except StopIteration:
            self.is_complete = True
            self.is_running = False
            return

        if op[0] == "compare":
            _, i, j = op
            self.bar_colors[i] = Colors.BAR_COMPARING
            self.bar_colors[j] = Colors.BAR_COMPARING
            self.comparisons += 1
        elif op[0] == "swap":
            _, i, j = op
            self.bar_colors[i] = Colors.BAR_SWAPPING
            self.bar_colors[j] = Colors.BAR_SWAPPING
            self.swaps += 1
        elif op[0] == "set":
            _, i, val = op
            self.array[i] = val
            self.bar_colors[i] = Colors.BAR_SWAPPING
        elif op[0] == "pivot":
            _, i = op
            self.bar_colors[i] = Colors.BAR_PIVOT
        elif op[0] == "sorted":
            _, i = op
            self.bar_colors[i] = Colors.BAR_SORTED
        elif op[0] == "done":
            self.is_complete = True
            self.is_running = False
            self.bar_colors = [Colors.BAR_SORTED] * len(self.bar_colors)

        # Record snapshot for time-travel
        self.history.append((
            list(self.array),
            list(self.bar_colors),
            self.comparisons,
            self.swaps,
        ))
        self.history_index = len(self.history) - 1

    def step_forward(self):
        """Step forward one frame (arrow key). Uses cache if available, else advances generator."""
        if self.is_complete:
            return
        if self.history_index < len(self.history) - 1:
            # Replay from cache — generator stays untouched
            self.history_index += 1
            self._load_snapshot(self.history_index)
        else:
            # At the end of cache — advance the generator to produce a new step
            if self.generator is None:
                self.start()
                self.is_running = False  # stay paused
            self.step()

    def step_backward(self):
        """Step backward one frame by loading previous snapshot from cache."""
        if self.history_index > 0:
            self.history_index -= 1
            self._load_snapshot(self.history_index)

    def _load_snapshot(self, index):
        """Restore visualizer state from a history snapshot."""
        arr, colors, comps, swps = self.history[index]
        self.array = list(arr)
        self.bar_colors = list(colors)
        self.comparisons = comps
        self.swaps = swps

    def handle_event(self, event):
        pass

    def get_status(self):
        if self.is_complete:
            return "Complete"
        if self.is_running:
            return "Running"
        if self.comparisons > 0:
            return "Paused"
        return "Ready"

    def _draw_boxes(self, surface):
        """Draw array as horizontal row of boxes with values."""
        n = self.array_size
        padding = 42
        available_width = self.canvas_rect.width - 2 * padding

        gap = 6
        min_box = 24  # minimum readable box width
        box_size = min(78, (available_width - (n - 1) * gap) // n)

        if box_size < min_box:
            # UX tradeoff: boxes would be too small to read at this width,
            # so we fall back to bar mode which scales gracefully to any width.
            self._draw_bars(surface)
            return

        # Adaptive font: large for roomy boxes, small for compact, none if too tight
        if box_size >= 60:
            font = self.font_box_large
        elif box_size >= 36:
            font = self.font_box_small
        else:
            font = None  # too small for text — just colored boxes

        total_width = n * box_size + (n - 1) * gap
        start_x = self.canvas_rect.x + (self.canvas_rect.width - total_width) // 2
        center_y = self.canvas_rect.y + self.canvas_rect.height // 2 - 15

        for i, (val, color) in enumerate(zip(self.array, self.bar_colors)):
            x = start_x + i * (box_size + gap)
            y = center_y - box_size // 2

            box_rect = pygame.Rect(x, y, box_size, box_size)

            # Box background
            pygame.draw.rect(surface, Colors.BOX_BG, box_rect, border_radius=6)

            # Colored border (3px)
            pygame.draw.rect(surface, color, box_rect, width=3, border_radius=6)

            # Value text centered in box (only if box is large enough)
            if font is not None:
                val_surf = font.render(str(val), True, Colors.BOX_TEXT)
                val_rect = val_surf.get_rect(center=box_rect.center)
                surface.blit(val_surf, val_rect)

            # Index below box
            idx_surf = self.font_index.render(str(i), True, Colors.TEXT_SECONDARY)
            idx_rect = idx_surf.get_rect(centerx=box_rect.centerx, top=box_rect.bottom + 6)
            surface.blit(idx_surf, idx_rect)

    def _draw_bars(self, surface):
        """Draw array as vertical bars."""
        padding = 24
        available_width = self.canvas_rect.width - 2 * padding
        available_height = self.canvas_rect.height - 60
        if available_width < 1 or available_height < 1:
            return  # canvas too small to draw

        bar_width = max(3, available_width // self.array_size - 1)
        max_val = max(self.array) if self.array else 1

        total_bars_width = self.array_size * (bar_width + 1)
        start_x = self.canvas_rect.x + (self.canvas_rect.width - total_bars_width) // 2

        for i, (val, color) in enumerate(zip(self.array, self.bar_colors)):
            bar_height = max(1, int((val / max_val) * available_height))
            x = start_x + i * (bar_width + 1)
            y = self.canvas_rect.y + self.canvas_rect.height - 30 - bar_height

            rect = pygame.Rect(x, y, bar_width, bar_height)
            pygame.draw.rect(surface, color, rect, border_radius=2)

    def draw(self, surface):
        """Draw the array using box or bar mode."""
        if not self.array:
            return

        if self._use_box_mode():
            self._draw_boxes(surface)
        else:
            self._draw_bars(surface)
