# visualizers/sorting_viz.py - Sorting algorithm visualizer for AlgoFlow
import pygame
import random
from visualizers.base import BaseVisualizer
from config import Colors
from algorithms.sorting import ALGORITHM_INFO


class SortingVisualizer(BaseVisualizer):
    """
    Visualizes sorting algorithms with animated bars.

    Each bar's height represents a value. Colors indicate:
    - Blue: default state
    - Red: currently being compared
    - Yellow: being swapped
    - Green: in final sorted position

    Uses the generator pattern to step through algorithms one operation
    at a time without threads.
    """

    def __init__(self, canvas_rect):
        super().__init__(canvas_rect)
        self.array_size = 50
        self.array = []
        self.bar_colors = []
        self.algorithm_key = "Bubble"
        self.comparisons = 0
        self.swaps = 0
        self.generator = None

        # Fonts created once, reused every frame
        self.font_info = pygame.font.SysFont("Arial", 14)
        self.font_status = pygame.font.SysFont("Arial", 20)

        self.reset()

    def get_algorithm_info(self):
        """Return metadata dict for the current algorithm."""
        return ALGORITHM_INFO[self.algorithm_key]

    def set_algorithm(self, key):
        """Set the active sorting algorithm by key (e.g. 'Bubble')."""
        if key in ALGORITHM_INFO:
            self.algorithm_key = key
            self.reset()

    def set_array_size(self, size):
        """Change the number of bars."""
        self.array_size = size
        self.reset()

    def reset(self):
        """Generate a new random array and reset all state."""
        self.array = [random.randint(10, 100) for _ in range(self.array_size)]
        self.bar_colors = [Colors.BAR_DEFAULT] * self.array_size
        self.is_running = False
        self.is_complete = False
        self.comparisons = 0
        self.swaps = 0
        self.step_count = 0
        self.generator = None

    def start(self):
        """Start the animation by creating a new generator."""
        if self.generator is None:
            gen_func = ALGORITHM_INFO[self.algorithm_key]["generator"]
            self.generator = gen_func(self.array)
        self.is_running = True
        self.is_complete = False

    def toggle(self):
        """Toggle between running and paused."""
        if self.is_complete:
            self.reset()
        if not self.is_running:
            self.start()
        else:
            self.is_running = False

    def step(self):
        """Consume the next operation from the generator."""
        if self.generator is None:
            return

        # Reset non-sorted bars to default before applying new colors
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
        elif op[0] == "sorted":
            _, i = op
            self.bar_colors[i] = Colors.BAR_SORTED
        elif op[0] == "done":
            self.is_complete = True
            self.is_running = False
            self.bar_colors = [Colors.BAR_SORTED] * len(self.bar_colors)

    def handle_event(self, event):
        """Handle sorting-specific events."""
        pass

    def get_status(self):
        """Return current status string."""
        if self.is_complete:
            return "Complete"
        if self.is_running:
            return "Running"
        if self.comparisons > 0:
            return "Paused"
        return "Ready"

    def draw(self, surface):
        """Draw the array as colored bars."""
        if not self.array:
            return

        padding = 20
        available_width = self.canvas_rect.width - 2 * padding
        available_height = self.canvas_rect.height - 80

        bar_width = max(2, available_width // self.array_size - 1)
        max_val = max(self.array) if self.array else 1

        # Draw bars
        total_bars_width = self.array_size * (bar_width + 1)
        start_x = self.canvas_rect.x + (self.canvas_rect.width - total_bars_width) // 2

        for i, (val, color) in enumerate(zip(self.array, self.bar_colors)):
            bar_height = int((val / max_val) * available_height)
            x = start_x + i * (bar_width + 1)
            y = self.canvas_rect.y + self.canvas_rect.height - 40 - bar_height

            rect = pygame.Rect(x, y, bar_width, bar_height)
            pygame.draw.rect(surface, color, rect, border_radius=1)

        # Draw status text when not running
        if not self.is_running and not self.is_complete:
            status = "Press SPACE to start  |  R to reset"
            status_surf = self.font_status.render(status, True, Colors.TEXT_ACCENT)
            status_rect = status_surf.get_rect(
                centerx=self.canvas_rect.centerx,
                top=self.canvas_rect.y + 15
            )
            surface.blit(status_surf, status_rect)
