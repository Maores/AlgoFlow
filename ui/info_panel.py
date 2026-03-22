# ui/info_panel.py - Side panel with card-based sections for AlgoFlow
import pygame
from config import Colors, FONT_FAMILY


class InfoPanel:
    """Polished info panel with card-style sections for algorithm info, stats, and legend."""

    def __init__(self, rect):
        self.rect = rect
        self.padding = 12

        # Fonts - created once
        self.font_section = pygame.font.SysFont(FONT_FAMILY, 13)
        self.font_title = pygame.font.SysFont(FONT_FAMILY, 22, bold=True)
        self.font_stats = pygame.font.SysFont(FONT_FAMILY, 16)
        self.font_label = pygame.font.SysFont(FONT_FAMILY, 14)

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
        self.algo_name = name
        self.time_best = time_best
        self.time_avg = time_avg
        self.time_worst = time_worst
        self.space = space
        self.stable = "Yes" if stable else "No"

    def set_stats(self, comparisons, swaps, status):
        self.comparisons = comparisons
        self.swaps = swaps
        self.status = status

    def set_legend(self, legend_items):
        self.legend_items = legend_items

    def _get_status_color(self):
        status_colors = {
            "Ready": Colors.TEXT_ACCENT,
            "Running": Colors.BAR_SORTED,
            "Paused": Colors.BAR_SWAPPING,
            "Complete": Colors.BAR_SORTED,
        }
        return status_colors.get(self.status, Colors.TEXT_PRIMARY)

    def _draw_card(self, surface, x, y, width, height):
        """Draw a card background with border radius."""
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, Colors.CARD_BG, card_rect, border_radius=8)
        pygame.draw.rect(surface, Colors.CARD_BORDER, card_rect, width=1, border_radius=8)
        return card_rect

    def draw(self, surface):
        """Draw the panel and all card sections."""
        # Panel background
        pygame.draw.rect(surface, Colors.PANEL_BG, self.rect)

        # Left border
        pygame.draw.line(
            surface, Colors.CARD_BORDER,
            (self.rect.x, self.rect.y),
            (self.rect.x, self.rect.bottom), 1
        )

        px = self.rect.x + self.padding
        py = self.rect.y + self.padding
        card_width = self.rect.width - self.padding * 2
        card_pad = 12  # internal card padding
        card_gap = 8

        # --- Card 1: Algorithm Info ---
        card1_h = 170
        self._draw_card(surface, px, py, card_width, card1_h)

        cx = px + card_pad
        cy = py + card_pad

        # Section header
        header_surf = self.font_section.render("ALGORITHM", True, Colors.TEXT_ACCENT)
        surface.blit(header_surf, (cx, cy))
        cy += 22

        # Algorithm name
        name_surf = self.font_title.render(self.algo_name, True, Colors.TEXT_PRIMARY)
        surface.blit(name_surf, (cx, cy))
        cy += 30

        # Complexity rows (label: value)
        rows = [
            ("Best", self.time_best),
            ("Avg", self.time_avg),
            ("Worst", self.time_worst),
            ("Space", self.space),
            ("Stable", self.stable),
        ]
        for label, value in rows:
            label_surf = self.font_label.render(f"{label}:", True, Colors.TEXT_SECONDARY)
            value_surf = self.font_label.render(value, True, Colors.TEXT_PRIMARY)
            surface.blit(label_surf, (cx, cy))
            surface.blit(value_surf, (cx + 60, cy))
            cy += 19

        py += card1_h + card_gap

        # --- Card 2: Live Stats ---
        card2_h = 116
        self._draw_card(surface, px, py, card_width, card2_h)

        cx = px + card_pad
        cy = py + card_pad

        header_surf = self.font_section.render("LIVE STATS", True, Colors.TEXT_ACCENT)
        surface.blit(header_surf, (cx, cy))
        cy += 22

        comp_surf = self.font_stats.render(f"Comparisons:  {self.comparisons}", True, Colors.TEXT_PRIMARY)
        surface.blit(comp_surf, (cx, cy))
        cy += 22

        swap_surf = self.font_stats.render(f"Swaps:  {self.swaps}", True, Colors.TEXT_PRIMARY)
        surface.blit(swap_surf, (cx, cy))
        cy += 22

        # Status with colored value
        status_label = self.font_stats.render("Status:  ", True, Colors.TEXT_SECONDARY)
        surface.blit(status_label, (cx, cy))
        status_val = self.font_stats.render(self.status, True, self._get_status_color())
        surface.blit(status_val, (cx + status_label.get_width(), cy))

        py += card2_h + card_gap

        # --- Card 3: Color Legend ---
        legend_count = max(len(self.legend_items), 1)
        card3_h = 28 + legend_count * 22 + 14
        self._draw_card(surface, px, py, card_width, card3_h)

        cx = px + card_pad
        cy = py + card_pad

        header_surf = self.font_section.render("LEGEND", True, Colors.TEXT_ACCENT)
        surface.blit(header_surf, (cx, cy))
        cy += 22

        square_size = 16
        for color, label in self.legend_items:
            pygame.draw.rect(
                surface, color,
                (cx, cy + 1, square_size, square_size),
                border_radius=2
            )
            label_surf = self.font_label.render(label, True, Colors.TEXT_PRIMARY)
            surface.blit(label_surf, (cx + square_size + 10, cy))
            cy += 22
