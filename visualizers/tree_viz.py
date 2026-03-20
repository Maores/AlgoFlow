# visualizers/tree_viz.py - Tree visualizer placeholder
import pygame
from visualizers.base import BaseVisualizer
from config import Colors


class TreeVisualizer(BaseVisualizer):
    """Placeholder visualizer for tree algorithms."""

    def __init__(self, canvas_rect):
        super().__init__(canvas_rect)
        self.font_title = pygame.font.SysFont("Arial", 22)
        self.font_sub = pygame.font.SysFont("Arial", 13)

    def reset(self):
        self.is_running = False
        self.is_complete = False

    def step(self):
        pass

    def handle_event(self, event):
        pass

    def draw(self, surface):
        cx = self.canvas_rect.centerx
        cy = self.canvas_rect.centery

        # Dashed border hint
        border = self.canvas_rect.inflate(-60, -60)
        pygame.draw.rect(surface, Colors.CARD_BORDER, border, width=1, border_radius=12)

        title_surf = self.font_title.render(
            "Trees", True, Colors.TEXT_PRIMARY
        )
        sub_surf = self.font_sub.render(
            "Coming Soon", True, Colors.TEXT_SECONDARY
        )
        surface.blit(title_surf, title_surf.get_rect(centerx=cx, centery=cy - 12))
        surface.blit(sub_surf, sub_surf.get_rect(centerx=cx, centery=cy + 14))
