# visualizers/sorting_viz.py - Sorting algorithm visualizer for AlgoFlow
import pygame
import random
from collections import defaultdict
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

        # Study mode: play-by-play status and variable pointers
        self.current_status = ""
        self.current_pointers = {}
        self.current_op_type = ""

        # Pointer pill cache (rebuilt per-step, not per-frame)
        self._prev_pointers = None
        self._cached_pills = []  # list of (surface, x, y)

        # Custom array mode: preserve user input across algorithm switches/resets
        self.custom_source_array = None
        self.has_custom_array = False

        # Time-travel history: list of (array, colors, comparisons, swaps, status, pointers)
        self.history = []
        self.history_index = -1

        # Fonts created once, reused every frame
        self.font_box_large = pygame.font.SysFont(FONT_FAMILY, 24, bold=True)
        self.font_box_small = pygame.font.SysFont(FONT_FAMILY, 20, bold=True)
        self.font_index = pygame.font.SysFont(FONT_FAMILY, 18)
        self.font_pointer = pygame.font.SysFont(FONT_FAMILY, 16, bold=True)

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
        """Change array size and exit custom mode."""
        self.has_custom_array = False
        self.custom_source_array = None
        self.array_size = size
        self.reset()

    def set_custom_array(self, array):
        """Load a user-provided array and enter custom mode."""
        self.custom_source_array = list(array)
        self.has_custom_array = True
        self.array = list(array)
        self.array_size = len(array)
        self._reset_visual_state()

    def _reset_visual_state(self):
        """Reset colors, counters, and generator without touching array data."""
        self.bar_colors = [Colors.BAR_DEFAULT] * self.array_size
        self.is_running = False
        self.is_complete = False
        self.comparisons = 0
        self.swaps = 0
        self.step_count = 0
        self.generator = None
        self.current_status = ""
        self.current_pointers = {}
        self.current_op_type = ""
        self._prev_pointers = None
        self._cached_pills = []
        self.history = []
        self.history_index = -1

    def reset(self):
        """Reset visualization. Restores custom array if in custom mode."""
        if self.has_custom_array and self.custom_source_array is not None:
            self.array = list(self.custom_source_array)
        elif self._use_box_mode():
            self.array = [random.randint(1, 50) for _ in range(self.array_size)]
        else:
            self.array = [random.randint(10, 100) for _ in range(self.array_size)]
        self._reset_visual_state()

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

        # Parse 4-tuple (new format) or legacy tuple
        if len(op) == 4:
            op_type, indices, status_msg, pointers = op
            self.current_status = status_msg
            self.current_pointers = pointers
        else:
            op_type = op[0]
            indices = op[1:] if len(op) > 1 else ()
            self.current_status = ""
            self.current_pointers = {}
        self.current_op_type = op_type

        if op_type == "compare":
            i, j = indices
            self.bar_colors[i] = Colors.BAR_COMPARING
            self.bar_colors[j] = Colors.BAR_COMPARING
            self.comparisons += 1
        elif op_type == "swap":
            i, j = indices
            self.bar_colors[i] = Colors.BAR_SWAPPING
            self.bar_colors[j] = Colors.BAR_SWAPPING
            self.swaps += 1
        elif op_type == "set":
            i, val = indices
            self.array[i] = val
            self.bar_colors[i] = Colors.BAR_SWAPPING
        elif op_type == "pivot":
            i = indices[0]
            self.bar_colors[i] = Colors.BAR_PIVOT
        elif op_type == "sorted":
            i = indices[0]
            self.bar_colors[i] = Colors.BAR_SORTED
        elif op_type == "done":
            self.is_complete = True
            self.is_running = False
            self.bar_colors = [Colors.BAR_SORTED] * len(self.bar_colors)

        # Record snapshot for time-travel (7-tuple with status + pointers + op_type)
        self.history.append((
            list(self.array),
            list(self.bar_colors),
            self.comparisons,
            self.swaps,
            self.current_status,
            dict(self.current_pointers),
            self.current_op_type,
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
        snapshot = self.history[index]
        if len(snapshot) >= 7:
            arr, colors, comps, swps, status, pointers, op_type = snapshot
            self.current_status = status
            self.current_pointers = pointers
            self.current_op_type = op_type
        elif len(snapshot) == 6:
            arr, colors, comps, swps, status, pointers = snapshot
            self.current_status = status
            self.current_pointers = pointers
            self.current_op_type = ""
        else:
            arr, colors, comps, swps = snapshot
            self.current_status = ""
            self.current_pointers = {}
            self.current_op_type = ""
        self.array = list(arr)
        self.bar_colors = list(colors)
        self.comparisons = comps
        self.swaps = swps

    def handle_event(self, event):
        pass

    def get_status(self):
        if self.is_complete:
            return "Complete"
        if self.current_status and (self.is_running or self.comparisons > 0):
            return self.current_status
        if self.is_running:
            return "Running"
        if self.comparisons > 0:
            return "Paused"
        return "Ready"

    # --- Pointer pill labels (box mode only) ---

    def _build_pointer_pills(self, index_to_x, index_to_top_y, element_width):
        """Build cached pill badge surfaces for current pointers."""
        # Group positional pointers by target index
        groups = defaultdict(list)
        for name, idx in self.current_pointers.items():
            if name.startswith("_"):
                continue  # skip value-type pointers
            if idx in index_to_x:
                groups[idx].append(name)

        self._cached_pills = []
        pill_h = 20
        pill_pad = 8
        pill_gap = 3

        for idx, names in groups.items():
            cx = index_to_x[idx] + element_width // 2
            top_y = index_to_top_y[idx]

            # Stack pills upward from above the box
            for stack_i, name in enumerate(names):
                color = Colors.POINTER_COLORS.get(name, Colors.POINTER_DEFAULT_COLOR)
                text_surf = self.font_pointer.render(name, True, Colors.POINTER_TEXT_COLOR)
                pill_w = text_surf.get_width() + pill_pad * 2

                pill_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
                pygame.draw.rect(pill_surf, color, (0, 0, pill_w, pill_h), border_radius=6)
                pill_surf.blit(text_surf, (pill_pad, (pill_h - text_surf.get_height()) // 2))

                px = cx - pill_w // 2
                py = top_y - (stack_i + 1) * (pill_h + pill_gap)
                self._cached_pills.append((pill_surf, px, py))

        self._prev_pointers = dict(self.current_pointers)

    def _draw_pointer_labels(self, surface, index_to_x, index_to_top_y, element_width):
        """Draw pointer pill labels above boxes. Rebuilds cache only when pointers change."""
        if not self.current_pointers:
            self._cached_pills = []
            self._prev_pointers = None
            return

        if self.current_pointers != self._prev_pointers:
            self._build_pointer_pills(index_to_x, index_to_top_y, element_width)

        for pill_surf, px, py in self._cached_pills:
            surface.blit(pill_surf, (px, py))

    # --- Sorted boundary line ---

    def _draw_dashed_line(self, surface, x, y1, y2, color, dash_len=6, gap_len=4):
        """Draw a vertical dashed line."""
        y = y1
        while y < y2:
            end = min(y + dash_len, y2)
            pygame.draw.line(surface, color, (x, y), (x, end), 2)
            y += dash_len + gap_len

    def _draw_sorted_boundary(self, surface, index_to_x, element_width, gap, y_top, y_bottom):
        """Draw dashed boundary lines at the edges of sorted regions."""
        n = len(self.bar_colors)
        if n == 0:
            return

        # Left-anchored sorted region (Selection/Insertion sort)
        left_sorted = 0
        while left_sorted < n and self.bar_colors[left_sorted] == Colors.BAR_SORTED:
            left_sorted += 1

        # Right-anchored sorted region (Bubble sort)
        right_sorted = n
        while right_sorted > 0 and self.bar_colors[right_sorted - 1] == Colors.BAR_SORTED:
            right_sorted -= 1

        color = Colors.SORTED_BOUNDARY_COLOR

        # Draw boundary after left sorted region (if partial, not all sorted)
        if 0 < left_sorted < n and left_sorted in index_to_x:
            bx = index_to_x[left_sorted] - gap // 2
            self._draw_dashed_line(surface, bx, y_top, y_bottom, color)

        # Draw boundary before right sorted region (if partial, not all sorted)
        if 0 < right_sorted < n and right_sorted - 1 in index_to_x:
            bx = index_to_x[right_sorted - 1] + element_width + gap // 2
            # Avoid drawing on top of left boundary
            if not (0 < left_sorted < n and left_sorted >= right_sorted):
                self._draw_dashed_line(surface, bx, y_top, y_bottom, color)

    # --- Drawing methods ---

    def _draw_boxes(self, surface):
        """Draw array as horizontal row of boxes with values."""
        n = self.array_size
        padding = 42
        available_width = self.canvas_rect.width - 2 * padding

        gap = 6
        min_box = 24  # minimum readable box width
        box_size = min(78, (available_width - (n - 1) * gap) // n)

        if box_size < min_box:
            self._draw_bars(surface)
            return

        # Adaptive font: large for roomy boxes, small for compact, none if too tight
        if box_size >= 60:
            font = self.font_box_large
        elif box_size >= 36:
            font = self.font_box_small
        else:
            font = None

        total_width = n * box_size + (n - 1) * gap
        start_x = self.canvas_rect.x + (self.canvas_rect.width - total_width) // 2
        center_y = self.canvas_rect.y + self.canvas_rect.height // 2 - 15

        # Build index-to-position maps for pointer labels and boundary
        index_to_x = {}
        index_to_top_y = {}

        for i, (val, color) in enumerate(zip(self.array, self.bar_colors)):
            x = start_x + i * (box_size + gap)
            y = center_y - box_size // 2

            index_to_x[i] = x
            index_to_top_y[i] = y

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

        # Pointer labels above boxes
        self._draw_pointer_labels(surface, index_to_x, index_to_top_y, box_size)

        # Sorted boundary
        y_top = center_y - box_size // 2 - 5
        y_bottom = center_y + box_size // 2 + 30
        self._draw_sorted_boundary(surface, index_to_x, box_size, gap, y_top, y_bottom)

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

        index_to_x = {}
        bar_gap = 1

        for i, (val, color) in enumerate(zip(self.array, self.bar_colors)):
            bar_height = max(1, int((val / max_val) * available_height))
            x = start_x + i * (bar_width + 1)
            y = self.canvas_rect.y + self.canvas_rect.height - 30 - bar_height

            index_to_x[i] = x

            rect = pygame.Rect(x, y, bar_width, bar_height)
            pygame.draw.rect(surface, color, rect, border_radius=2)

        # Sorted boundary (no pointer labels in bar mode)
        y_top = self.canvas_rect.y + 20
        y_bottom = self.canvas_rect.y + self.canvas_rect.height - 25
        self._draw_sorted_boundary(surface, index_to_x, bar_width, bar_gap, y_top, y_bottom)

    def draw(self, surface):
        """Draw the array using box or bar mode."""
        if not self.array:
            return

        if self._use_box_mode():
            self._draw_boxes(surface)
        else:
            self._draw_bars(surface)
