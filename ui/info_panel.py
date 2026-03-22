# ui/info_panel.py - Side panel with card-based sections for AlgoFlow
import pygame
from config import Colors, FONT_FAMILY


class InfoPanel:
    """Polished info panel with card-style sections for algorithm info, stats, and legend."""

    def __init__(self, rect):
        self.rect = rect
        self.padding = 18

        # Fonts - created once
        self.font_section = pygame.font.SysFont(FONT_FAMILY, 20)
        self.font_title = pygame.font.SysFont(FONT_FAMILY, 33, bold=True)
        self.font_stats = pygame.font.SysFont(FONT_FAMILY, 24)
        self.font_label = pygame.font.SysFont(FONT_FAMILY, 21)

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
        pygame.draw.rect(surface, Colors.CARD_BG, card_rect, border_radius=12)
        pygame.draw.rect(surface, Colors.CARD_BORDER, card_rect, width=1, border_radius=12)
        return card_rect

    def draw(self, surface):
        """Draw the panel and all card sections with dynamic sizing."""
        # Panel background
        pygame.draw.rect(surface, Colors.PANEL_BG, self.rect)

        # Left border
        pygame.draw.line(
            surface, Colors.CARD_BORDER,
            (self.rect.x, self.rect.y),
            (self.rect.x, self.rect.bottom), 1
        )

        px = self.rect.x + self.padding
        card_width = self.rect.width - self.padding * 2
        card_pad = 18  # internal card padding
        available_h = self.rect.height - self.padding * 2

        # --- Compute dynamic card heights based on content ---
        algo_rows = 5  # Best, Avg, Worst, Space, Stable
        stats_rows = 3  # Comparisons, Swaps, Status
        legend_count = max(len(self.legend_items), 1)
        controls = [
            ("[Space]", "Play / Pause"),
            ("[R]", "Reset"),
            ("\u2190/\u2192", "Step Back / Forward"),
        ]

        # Standard spacing values (preferred)
        header_h = 33       # space after section header
        title_h = 45        # space after algorithm title
        row_sp = 29         # row spacing for algo complexity
        stat_sp = 33         # row spacing for stats
        legend_sp = 33       # row spacing for legend items
        ctrl_sp = 29         # row spacing for controls
        bottom_pad = 18      # bottom padding inside card
        card_gap = 12        # gap between cards

        # Calculate card heights dynamically from content
        card1_h = card_pad + header_h + title_h + algo_rows * row_sp + bottom_pad
        card2_h = card_pad + header_h + stats_rows * stat_sp + bottom_pad
        card3_h = card_pad + header_h + legend_count * legend_sp + bottom_pad
        card4_h = card_pad + header_h + len(controls) * ctrl_sp + bottom_pad
        num_gaps = 3  # gaps between 4 cards

        total_needed = card1_h + card2_h + card3_h + card4_h + num_gaps * card_gap

        # Adaptive spacing: shrink if content overflows available height
        if total_needed > available_h:
            overflow = total_needed - available_h
            # Strategy: reduce gaps first, then row spacing proportionally
            gap_savings = min(overflow, num_gaps * (card_gap - 4))
            card_gap = max(4, card_gap - gap_savings // num_gaps)
            overflow -= gap_savings

            if overflow > 0:
                # Reduce all row spacings proportionally
                total_rows = algo_rows + stats_rows + legend_count + len(controls)
                reduction = min(overflow / max(total_rows, 1), 8)
                row_sp = max(20, row_sp - reduction)
                stat_sp = max(24, stat_sp - reduction)
                legend_sp = max(24, legend_sp - reduction)
                ctrl_sp = max(20, ctrl_sp - reduction)
                # Recompute card heights with reduced spacing
                card1_h = card_pad + header_h + title_h + algo_rows * row_sp + bottom_pad
                card2_h = card_pad + header_h + stats_rows * stat_sp + bottom_pad
                card3_h = card_pad + header_h + legend_count * legend_sp + bottom_pad
                card4_h = card_pad + header_h + len(controls) * ctrl_sp + bottom_pad

        py = self.rect.y + self.padding

        # --- Card 1: Algorithm Info ---
        self._draw_card(surface, px, py, card_width, card1_h)
        cx = px + card_pad
        cy = py + card_pad

        header_surf = self.font_section.render("ALGORITHM", True, Colors.TEXT_ACCENT)
        surface.blit(header_surf, (cx, cy))
        cy += header_h

        name_surf = self.font_title.render(self.algo_name, True, Colors.TEXT_PRIMARY)
        surface.blit(name_surf, (cx, cy))
        cy += title_h

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
            surface.blit(value_surf, (cx + 90, cy))
            cy += row_sp

        py += card1_h + card_gap

        # --- Card 2: Live Stats ---
        self._draw_card(surface, px, py, card_width, card2_h)
        cx = px + card_pad
        cy = py + card_pad

        header_surf = self.font_section.render("LIVE STATS", True, Colors.TEXT_ACCENT)
        surface.blit(header_surf, (cx, cy))
        cy += header_h

        comp_surf = self.font_stats.render(f"Comparisons:  {self.comparisons}", True, Colors.TEXT_PRIMARY)
        surface.blit(comp_surf, (cx, cy))
        cy += stat_sp

        swap_surf = self.font_stats.render(f"Swaps:  {self.swaps}", True, Colors.TEXT_PRIMARY)
        surface.blit(swap_surf, (cx, cy))
        cy += stat_sp

        status_label = self.font_stats.render("Status:  ", True, Colors.TEXT_SECONDARY)
        surface.blit(status_label, (cx, cy))
        status_val = self.font_stats.render(self.status, True, self._get_status_color())
        surface.blit(status_val, (cx + status_label.get_width(), cy))

        py += card2_h + card_gap

        # --- Card 3: Color Legend ---
        self._draw_card(surface, px, py, card_width, card3_h)
        cx = px + card_pad
        cy = py + card_pad

        header_surf = self.font_section.render("LEGEND", True, Colors.TEXT_ACCENT)
        surface.blit(header_surf, (cx, cy))
        cy += header_h

        square_size = 24
        for color, label in self.legend_items:
            pygame.draw.rect(
                surface, color,
                (cx, cy + 1, square_size, square_size),
                border_radius=3
            )
            label_surf = self.font_label.render(label, True, Colors.TEXT_PRIMARY)
            surface.blit(label_surf, (cx + square_size + 15, cy))
            cy += legend_sp

        py += card3_h + card_gap

        # --- Card 4: Keyboard Controls ---
        self._draw_card(surface, px, py, card_width, card4_h)
        cx = px + card_pad
        cy = py + card_pad

        header_surf = self.font_section.render("CONTROLS", True, Colors.TEXT_ACCENT)
        surface.blit(header_surf, (cx, cy))
        cy += header_h

        for key, desc in controls:
            key_surf = self.font_label.render(key, True, Colors.TEXT_ACCENT)
            desc_surf = self.font_label.render(desc, True, Colors.TEXT_SECONDARY)
            surface.blit(key_surf, (cx, cy))
            surface.blit(desc_surf, (cx + key_surf.get_width() + 12, cy))
            cy += ctrl_sp
