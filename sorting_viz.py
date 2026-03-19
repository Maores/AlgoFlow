# visualizers/sorting_viz.py - Sorting algorithm visualizer
# Day 1: Placeholder with preview bars
# Day 2-4: Full implementation with 5 algorithms
import pygame
import random
from visualizers.base import BaseVisualizer
from config import Colors


class SortingVisualizer(BaseVisualizer):
    """
    Visualizes sorting algorithms with animated bars.
    
    Each bar's height represents a value. Colors indicate:
    - Blue: default state
    - Red: currently being compared
    - Yellow: being swapped
    - Green: in final sorted position
    """
    
    def __init__(self, canvas_rect):
        super().__init__(canvas_rect)
        self.array_size = 50
        self.array = []
        self.bar_colors = []
        self.algorithm_name = "Bubble Sort"
        self.comparisons = 0
        self.swaps = 0
        self.reset()
    
    def reset(self):
        """Generate a new random array."""
        self.array = [random.randint(10, 100) for _ in range(self.array_size)]
        self.bar_colors = [Colors.BAR_DEFAULT] * self.array_size
        self.is_running = False
        self.is_complete = False
        self.comparisons = 0
        self.swaps = 0
        self.step_count = 0
    
    def step(self):
        """Placeholder - will be implemented on Day 2."""
        pass
    
    def handle_event(self, event):
        """Handle sorting-specific events."""
        pass
    
    def draw(self, surface):
        """Draw the array as colored bars."""
        if not self.array:
            return
        
        padding = 20
        available_width = self.canvas_rect.width - 2 * padding
        available_height = self.canvas_rect.height - 80  # leave room for labels
        
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
        
        # Draw info text at bottom
        font = pygame.font.SysFont("Arial", 14)
        info_text = f"{self.algorithm_name}  |  Comparisons: {self.comparisons}  |  Swaps: {self.swaps}"
        text_surf = font.render(info_text, True, Colors.TEXT_SECONDARY)
        text_rect = text_surf.get_rect(
            centerx=self.canvas_rect.centerx,
            bottom=self.canvas_rect.bottom - 10
        )
        surface.blit(text_surf, text_rect)
        
        # Draw "Coming on Day 2" or status
        if not self.is_running and not self.is_complete:
            status_font = pygame.font.SysFont("Arial", 20)
            status = "Press SPACE to start  |  R to reset"
            status_surf = status_font.render(status, True, Colors.TEXT_ACCENT)
            status_rect = status_surf.get_rect(
                centerx=self.canvas_rect.centerx,
                top=self.canvas_rect.y + 15
            )
            surface.blit(status_surf, status_rect)
