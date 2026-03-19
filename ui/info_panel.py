# ui/info_panel.py - Side panel showing algorithm info, stats, and legend
import pygame
from config import Colors


class InfoPanel:
    """Vertical info panel on the right side of the canvas."""

    def __init__(self, rect):
        """rect defines the panel area."""
        self.rect = rect
        self.padding = 16
        self.border_color = (50, 50, 70)

        # Fonts - created once, reused every frame
        self.font_title = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_stats = pygame.font.SysFont("Arial", 16)
        self.font_label = pygame.font.SysFont("Arial", 14)

        # Algorithm info
        self.algo_name = ""
        self.time_best = ""
        self.time_avg = ""
        self.time_worst = ""
        self.space = ""
        self.stable = ""

        # Live stats
        self.comparisons = 0
        self.swaps = 0
        self.status = "Ready"

        # Legend items: list of (color, label)
        self.legend_items = []

    def set_algorithm_info(self, name, time_best, time_avg, time_worst, space, stable):
        """Update static algorithm info."""
        self.algo_name = name
        self.time_best = time_best
        self.time_avg = time_avg
        self.time_worst = time_worst
        self.space = space
        self.stable = "Yes" if stable else "No"

    def set_stats(self, comparisons, swaps, status):
        """Update live stats. Called every frame."""
        self.comparisons = comparisons
        self.swaps = swaps
        self.status = status

    def set_legend(self, legend_items):
        """legend_items: list of (color_tuple, label_string)"""
        self.legend_items = legend_items

    def _get_status_color(self):
        """Return color for the current status label."""
        status_colors = {
            "Ready": Colors.TEXT_ACCENT,
            "Running": Colors.BAR_SORTED,
            "Paused": Colors.BAR_SWAPPING,
            "Complete": Colors.BAR_SORTED,
        }
        return status_colors.get(self.status, Colors.TEXT_PRIMARY)

    def draw(self, surface):
        """Draw the panel and all sections."""
        # Panel background
        pygame.draw.rect(surface, Colors.PANEL_BG, self.rect)

        # Left border
        pygame.draw.line(
            surface, self.border_color,
            (self.rect.x, self.rect.y),
            (self.rect.x, self.rect.bottom), 1
        )

        x = self.rect.x + self.padding
        y = self.rect.y + self.padding
        max_width = self.rect.width - self.padding * 2

        # Section 1: Algorithm Info
        title_surf = self.font_title.render(self.algo_name, True, Colors.TEXT_PRIMARY)
        surface.blit(title_surf, (x, y))
        y += 30

        info_lines = [
            f"Best:    {self.time_best}",
            f"Avg:     {self.time_avg}",
            f"Worst:   {self.time_worst}",
            f"Space:   {self.space}",
            f"Stable:  {self.stable}",
        ]
        for line in info_lines:
            surf = self.font_label.render(line, True, Colors.TEXT_SECONDARY)
            surface.blit(surf, (x, y))
            y += 20

        # Separator
        y += 8
        pygame.draw.line(surface, self.border_color, (x, y), (x + max_width, y), 1)
        y += 12

        # Section 2: Live Stats
        header_surf = self.font_stats.render("LIVE STATS", True, Colors.TEXT_SECONDARY)
        surface.blit(header_surf, (x, y))
        y += 24

        comp_surf = self.font_stats.render(f"Comparisons: {self.comparisons}", True, Colors.TEXT_PRIMARY)
        surface.blit(comp_surf, (x, y))
        y += 22

        swap_surf = self.font_stats.render(f"Swaps: {self.swaps}", True, Colors.TEXT_PRIMARY)
        surface.blit(swap_surf, (x, y))
        y += 22

        status_label = self.font_stats.render("Status: ", True, Colors.TEXT_SECONDARY)
        surface.blit(status_label, (x, y))
        status_val = self.font_stats.render(self.status, True, self._get_status_color())
        surface.blit(status_val, (x + status_label.get_width(), y))
        y += 22

        # Separator
        y += 8
        pygame.draw.line(surface, self.border_color, (x, y), (x + max_width, y), 1)
        y += 12

        # Section 3: Color Legend
        legend_header = self.font_stats.render("COLOR LEGEND", True, Colors.TEXT_SECONDARY)
        surface.blit(legend_header, (x, y))
        y += 24

        square_size = 12
        for color, label in self.legend_items:
            pygame.draw.rect(surface, color, (x, y + 1, square_size, square_size))
            label_surf = self.font_label.render(label, True, Colors.TEXT_PRIMARY)
            surface.blit(label_surf, (x + square_size + 8, y))
            y += 20
