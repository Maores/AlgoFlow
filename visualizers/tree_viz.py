# visualizers/tree_viz.py - Tree visualizer placeholder
import pygame
from visualizers.base import BaseVisualizer
from config import Colors


class TreeVisualizer(BaseVisualizer):
    """Placeholder visualizer for tree algorithms."""

    def __init__(self, canvas_rect):
        super().__init__(canvas_rect)
        self.font = pygame.font.SysFont("Arial", 28)

    def reset(self):
        self.is_running = False
        self.is_complete = False

    def step(self):
        pass

    def handle_event(self, event):
        pass

    def draw(self, surface):
        text_surf = self.font.render(
            "Trees \u2014 Coming Soon", True, Colors.TEXT_SECONDARY
        )
        text_rect = text_surf.get_rect(center=self.canvas_rect.center)
        surface.blit(text_surf, text_rect)
