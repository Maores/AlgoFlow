# ui/info_panel.py - Side panel with card-based sections for AlgoFlow
import pygame
from config import Colors, FONT_FAMILY
from algorithms.pseudocode import PSEUDOCODE


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

        # Monospace font for pseudocode
        self.font_mono = pygame.font.SysFont("Consolas, Courier New, monospace", 19)

        # Pseudocode state
        self.algorithm_key = ""
        self.current_op_type = ""

        # Algorithm info
        self.algo_name = ""
        self.time_best = ""
        self.time_avg = ""
        self.time_worst = ""
        self.space = ""
        self.stable = None
        # Pathfinding-specific algorithm info
        self.time_general = ""
        self.optimal = None

        # Live stats
        self.stats_tab = "sorting"
        self.comparisons = 0
        self.swaps = 0
        self.status = "Ready"
        # Pathfinding-specific stats
        self.cells_explored = 0
        self.frontier_size = 0
        self.path_length = 0
        self.total_cost = 0

        # Legend items: list of (color, label)
        self.legend_items = []

        # Variables panel data
        self.current_pointers = {}
        self.current_array = []

        # Font caching for status and variables
        self._prev_status = None
        self._cached_status_lines = []
        self._prev_pointers_for_panel = None
        self._cached_var_lines = []

    def set_algorithm_info(self, info_dict):
        """Accept a dict of algorithm info. Keys vary by tab.
        Sorting: name, time_best, time_avg, time_worst, space, stable
        Pathfinding: name, time, space, optimal
        """
        self.algo_name = info_dict.get("name", "")
        self.time_best = info_dict.get("time_best", "")
        self.time_avg = info_dict.get("time_avg", "")
        self.time_worst = info_dict.get("time_worst", "")
        self.space = info_dict.get("space", "")
        self.stable = info_dict.get("stable", None)
        # Pathfinding-specific
        self.time_general = info_dict.get("time", "")
        self.optimal = info_dict.get("optimal", None)

    def set_stats(self, stats_dict):
        """Accept a dict of live stats. Must include 'tab' key for rendering.
        Sorting: tab="sorting", comparisons, swaps, status
        Pathfinding: tab="pathfinding", cells_explored, frontier_size, path_length, status
        """
        self.stats_tab = stats_dict.get("tab", "sorting")
        self.comparisons = stats_dict.get("comparisons", 0)
        self.swaps = stats_dict.get("swaps", 0)
        self.status = stats_dict.get("status", "")
        # Pathfinding-specific
        self.cells_explored = stats_dict.get("cells_explored", 0)
        self.frontier_size = stats_dict.get("frontier_size", 0)
        self.path_length = stats_dict.get("path_length", 0)
        self.total_cost = stats_dict.get("total_cost", 0)

    def set_legend(self, legend_items):
        self.legend_items = legend_items

    def set_variables(self, pointers_dict, array):
        self.current_pointers = pointers_dict
        self.current_array = array

    def set_pseudocode_state(self, algorithm_key, op_type):
        self.algorithm_key = algorithm_key
        self.current_op_type = op_type

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

    def _wrap_text(self, text, font, max_width):
        """Word-wrap text to fit within max_width. Returns list of strings."""
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines or [""]

    def _build_status_lines(self, max_width):
        """Cache wrapped status lines. Only rebuild when status changes."""
        if self.status == self._prev_status:
            return
        self._prev_status = self.status

        simple_states = {"Ready", "Running", "Paused", "Complete"}
        if self.status in simple_states:
            self._cached_status_lines = []
        else:
            self._cached_status_lines = self._wrap_text(
                self.status, self.font_label, max_width
            )[:2]  # max 2 lines

    def _build_var_lines(self):
        """Cache variable display lines. Only rebuild when pointers change."""
        key = str(self.current_pointers)
        if key == self._prev_pointers_for_panel:
            return
        self._prev_pointers_for_panel = key
        self._cached_var_lines = []

        for name, value in self.current_pointers.items():
            if name.startswith("_"):
                display_name = name[1:]
                self._cached_var_lines.append((display_name, str(value), None))
            else:
                idx = value
                arr_val = ""
                if isinstance(idx, int) and 0 <= idx < len(self.current_array):
                    arr_val = f"(arr[{idx}]={self.current_array[idx]})"
                self._cached_var_lines.append((name, str(idx), arr_val))

    def draw(self, surface):
        """Draw the panel with bottom-anchored CONTROLS and fixed-height cards."""
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
        card_pad = 18
        inner_width = card_width - card_pad * 2

        # Spacing values
        header_h = 33
        title_h = 45
        row_sp = 29
        stat_sp = 33
        legend_sp = 28
        var_sp = 27
        code_line_h = 23
        bottom_pad = 18
        card_gap = 12

        # --- Build cached data ---
        self._build_status_lines(inner_width)
        self._build_var_lines()

        # --- Build algo rows dynamically ---
        if self.time_general:
            # Pathfinding layout: Time, Space, Optimal (3 rows)
            algo_rows_data = [
                ("Time", self.time_general),
                ("Space", self.space),
                ("Optimal", "Yes" if self.optimal else "No"),
            ]
        else:
            # Sorting layout: Best, Avg, Worst, Space, Stable (5 rows)
            algo_rows_data = [
                ("Best", self.time_best),
                ("Average", self.time_avg),
                ("Worst", self.time_worst),
                ("Space", self.space),
                ("Stable", "Yes" if self.stable else "No"),
            ]

        # --- Build stats rows dynamically ---
        if self.stats_tab == "pathfinding":
            stat_rows = [
                ("Explored", str(self.cells_explored)),
                ("Frontier", str(self.frontier_size)),
                ("Path Length", str(self.path_length)),
            ]
        else:
            stat_rows = [
                ("Comparisons", str(self.comparisons)),
                ("Swaps", str(self.swaps)),
            ]

        # --- Dynamic card heights ---
        algo_rows = len(algo_rows_data)
        stats_rows = len(stat_rows)

        card1_h = card_pad + header_h + title_h + algo_rows * row_sp + bottom_pad

        # LIVE STATS — dynamic height, always reserves 2 status text lines
        card2_h = card_pad + header_h + stats_rows * stat_sp + 2 * 24 + bottom_pad

        # PSEUDOCODE — sized to current algorithm's actual line count
        pc_data = PSEUDOCODE.get(self.algorithm_key)
        actual_pc_lines = len(pc_data["lines"]) if pc_data else 0
        card_pseudo_h = card_pad + header_h + actual_pc_lines * code_line_h + bottom_pad

        # Variables card (desired height, may be clamped)
        has_vars = bool(self.current_pointers)
        var_count = len(self._cached_var_lines) if has_vars else 0
        card_vars_h = card_pad + header_h + var_count * var_sp + bottom_pad if has_vars else 0

        # Bottom limit for cards
        panel_bottom = self.rect.bottom - self.padding

        # --- Draw top-down cards ---
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

        for label, value in algo_rows_data:
            label_surf = self.font_label.render(f"{label}:", True, Colors.TEXT_SECONDARY)
            value_surf = self.font_label.render(value, True, Colors.TEXT_PRIMARY)
            surface.blit(label_surf, (cx, cy))
            surface.blit(value_surf, (cx + 90, cy))
            cy += row_sp

        py += card1_h + card_gap

        # --- Card 2: Live Stats (fixed height) ---
        self._draw_card(surface, px, py, card_width, card2_h)
        cx = px + card_pad
        cy = py + card_pad

        header_surf = self.font_section.render("LIVE STATS", True, Colors.TEXT_ACCENT)
        surface.blit(header_surf, (cx, cy))
        cy += header_h

        for stat_label, stat_value in stat_rows:
            row_surf = self.font_stats.render(f"{stat_label}:  {stat_value}", True, Colors.TEXT_PRIMARY)
            surface.blit(row_surf, (cx, cy))
            cy += stat_sp

        simple_states = {"Ready", "Running", "Paused", "Complete"}
        if self.status in simple_states:
            status_label = self.font_stats.render("Status:  ", True, Colors.TEXT_SECONDARY)
            surface.blit(status_label, (cx, cy))
            status_val = self.font_stats.render(self.status, True, self._get_status_color())
            surface.blit(status_val, (cx + status_label.get_width(), cy))
        else:
            status_label = self.font_stats.render("Status:", True, Colors.TEXT_SECONDARY)
            surface.blit(status_label, (cx, cy))
            cy += stat_sp
            for line in self._cached_status_lines:
                line_surf = self.font_label.render(line, True, Colors.TEXT_PRIMARY)
                surface.blit(line_surf, (cx, cy))
                cy += 24

        py += card2_h + card_gap

        # --- Card 3: Pseudocode (fixed height) ---
        self._draw_card(surface, px, py, card_width, card_pseudo_h)
        cx = px + card_pad
        cy = py + card_pad

        header_surf = self.font_section.render("PSEUDOCODE", True, Colors.TEXT_ACCENT)
        surface.blit(header_surf, (cx, cy))
        cy += header_h

        if pc_data is not None:
            highlighted = set(pc_data["highlight_map"].get(self.current_op_type, []))
            code_top = cy
            # Hard-clip to card boundary to prevent any text overflow
            clip_rect = pygame.Rect(px, py, card_width, card_pseudo_h)
            surface.set_clip(clip_rect)
            for i, line_text in enumerate(pc_data["lines"]):
                line_y = code_top + i * code_line_h
                # Truncate text to fit within card width
                display_text = line_text
                if self.font_mono.size(display_text)[0] > inner_width:
                    while len(display_text) > 1 and self.font_mono.size(display_text + "..")[0] > inner_width:
                        display_text = display_text[:-1]
                    display_text = display_text + ".."
                if i in highlighted:
                    hl_rect = pygame.Rect(cx - 4, line_y - 2, inner_width + 8, code_line_h)
                    hl_surf = pygame.Surface((hl_rect.width, hl_rect.height), pygame.SRCALPHA)
                    hl_surf.fill((60, 130, 200, 50))
                    surface.blit(hl_surf, hl_rect)
                    text_surf = self.font_mono.render(display_text, True, Colors.TEXT_PRIMARY)
                else:
                    text_surf = self.font_mono.render(display_text, True, Colors.TEXT_SECONDARY)
                surface.blit(text_surf, (cx, line_y))
            surface.set_clip(None)

        py += card_pseudo_h + card_gap

        # --- Remaining space — Legend always visible, Variables below when active ---
        remaining = panel_bottom - py - card_gap

        # --- Card: Legend (always shown if items exist) ---
        legend_count = len(self.legend_items)
        if legend_count > 0 and remaining >= 60:
            legend_header_cost = card_pad + header_h + bottom_pad
            max_legend_items = min(
                legend_count,
                max(0, int((remaining - legend_header_cost) / legend_sp))
            )
            if max_legend_items > 0:
                card_legend_h = legend_header_cost + max_legend_items * legend_sp
                card_legend_h = min(card_legend_h, remaining)
                self._draw_card(surface, px, py, card_width, card_legend_h)
                cx = px + card_pad
                cy = py + card_pad

                header_surf = self.font_section.render("LEGEND", True, Colors.TEXT_ACCENT)
                surface.blit(header_surf, (cx, cy))
                cy += header_h

                square_size = 24
                for color, label in self.legend_items[:max_legend_items]:
                    pygame.draw.rect(
                        surface, color,
                        (cx, cy + 1, square_size, square_size),
                        border_radius=3
                    )
                    label_surf = self.font_label.render(label, True, Colors.TEXT_PRIMARY)
                    surface.blit(label_surf, (cx + square_size + 15, cy))
                    cy += legend_sp

                py += card_legend_h + card_gap
                remaining = panel_bottom - py - card_gap

        # --- Card: Variables (shown below Legend when active) ---
        if has_vars and remaining >= 60:
            draw_h = min(card_vars_h, remaining)
            self._draw_card(surface, px, py, card_width, draw_h)
            cx = px + card_pad
            cy = py + card_pad

            header_surf = self.font_section.render("VARIABLES", True, Colors.TEXT_ACCENT)
            surface.blit(header_surf, (cx, cy))
            cy += header_h

            # Only draw variable rows that fit within the clamped card
            max_var_y = py + draw_h - bottom_pad
            for name, value, arr_info in self._cached_var_lines:
                if cy + var_sp > max_var_y:
                    break
                name_surf = self.font_label.render(f"{name} = ", True, Colors.TEXT_ACCENT)
                surface.blit(name_surf, (cx, cy))
                val_x = cx + name_surf.get_width()
                val_surf = self.font_label.render(value, True, Colors.TEXT_PRIMARY)
                surface.blit(val_surf, (val_x, cy))
                if arr_info:
                    info_x = val_x + val_surf.get_width() + 8
                    info_surf = self.font_label.render(arr_info, True, Colors.TEXT_SECONDARY)
                    surface.blit(info_surf, (info_x, cy))
                cy += var_sp
