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
        self.font_mono = pygame.font.SysFont("Consolas, Courier New, monospace", 15)

        # Pseudocode state
        self.algorithm_key = ""
        self.current_op_type = ""

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

        # Variables panel data
        self.current_pointers = {}
        self.current_array = []

        # Font caching for status and variables
        self._prev_status = None
        self._cached_status_lines = []
        self._prev_pointers_for_panel = None
        self._cached_var_lines = []

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
        """Draw the panel with bottom-anchored CONTROLS and dynamic cards."""
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
        available_h = self.rect.height - self.padding * 2

        # Spacing values
        header_h = 33
        title_h = 45
        row_sp = 29
        stat_sp = 33
        legend_sp = 33
        ctrl_sp = 29
        var_sp = 27
        code_line_h = 20
        bottom_pad = 18
        card_gap = 12

        # --- Build cached data ---
        inner_width = card_width - card_pad * 2
        self._build_status_lines(inner_width)
        self._build_var_lines()

        # --- Compute card heights ---
        algo_rows = 5
        stats_rows = 3
        controls = [
            ("[Space]", "Play / Pause"),
            ("[R]", "Reset"),
            ("\u2190/\u2192", "Step Back / Forward"),
        ]

        card1_h = card_pad + header_h + title_h + algo_rows * row_sp + bottom_pad

        # Stats card: extra lines for wrapped status
        extra_status_lines = len(self._cached_status_lines)
        card2_h = card_pad + header_h + stats_rows * stat_sp + bottom_pad
        if extra_status_lines > 0:
            card2_h += extra_status_lines * 24

        # Pseudocode card
        pc_data = PSEUDOCODE.get(self.algorithm_key)
        has_pseudo = pc_data is not None
        pc_line_count = len(pc_data["lines"]) if has_pseudo else 0
        card_pseudo_h = card_pad + header_h + pc_line_count * code_line_h + bottom_pad if has_pseudo else 0

        # Variables card (only if pointers exist)
        has_vars = bool(self.current_pointers)
        var_count = len(self._cached_var_lines) if has_vars else 0
        card_vars_h = card_pad + header_h + var_count * var_sp + bottom_pad if has_vars else 0

        # Controls card (fixed)
        card_ctrl_h = card_pad + header_h + len(controls) * ctrl_sp + bottom_pad

        # Legend card — gets remaining space
        legend_count = len(self.legend_items)

        # Calculate remaining space for legend
        num_cards = 3 + (1 if has_pseudo else 0) + (1 if has_vars else 0)
        num_gaps = num_cards  # gaps between all cards including legend
        used = card1_h + card2_h + card_ctrl_h + card_pseudo_h + (card_vars_h if has_vars else 0) + num_gaps * card_gap
        remaining = available_h - used

        # Legend card height — fit as many items as space allows
        legend_header_cost = card_pad + header_h + bottom_pad
        if remaining >= legend_header_cost + legend_sp:
            max_legend_items = min(legend_count, int((remaining - legend_header_cost) / legend_sp))
            max_legend_items = max(max_legend_items, 1)
            card_legend_h = legend_header_cost + max_legend_items * legend_sp
        elif remaining >= 40:
            max_legend_items = 0
            card_legend_h = remaining
        else:
            max_legend_items = 0
            card_legend_h = 0

        # Adaptive spacing if still overflowing
        total_needed = card1_h + card2_h + card_ctrl_h + card_pseudo_h + card_legend_h
        if has_vars:
            total_needed += card_vars_h
        total_needed += num_gaps * card_gap

        if total_needed > available_h:
            overflow = total_needed - available_h
            gap_savings = min(overflow, num_gaps * (card_gap - 4))
            card_gap = max(4, card_gap - gap_savings // max(num_gaps, 1))
            overflow -= gap_savings
            if overflow > 0:
                total_rows = algo_rows + stats_rows + pc_line_count + var_count + len(controls) + max_legend_items
                if total_rows > 0:
                    reduction = min(overflow / total_rows, 8)
                    row_sp = max(20, row_sp - reduction)
                    stat_sp = max(24, stat_sp - reduction)
                    legend_sp = max(24, legend_sp - reduction)
                    ctrl_sp = max(20, ctrl_sp - reduction)
                    var_sp = max(20, var_sp - reduction)
                    code_line_h = max(16, code_line_h - reduction)
                    card1_h = card_pad + header_h + title_h + algo_rows * row_sp + bottom_pad
                    card2_h = card_pad + header_h + stats_rows * stat_sp + bottom_pad
                    if extra_status_lines > 0:
                        card2_h += extra_status_lines * 24
                    if has_pseudo:
                        card_pseudo_h = card_pad + header_h + pc_line_count * code_line_h + bottom_pad
                    if has_vars:
                        card_vars_h = card_pad + header_h + var_count * var_sp + bottom_pad
                    card_ctrl_h = card_pad + header_h + len(controls) * ctrl_sp + bottom_pad
                    if max_legend_items > 0:
                        card_legend_h = legend_header_cost + max_legend_items * legend_sp

        # --- Draw CONTROLS card anchored to bottom ---
        ctrl_y = self.rect.bottom - self.padding - card_ctrl_h
        self._draw_card(surface, px, ctrl_y, card_width, card_ctrl_h)
        cx = px + card_pad
        cy = ctrl_y + card_pad

        header_surf = self.font_section.render("CONTROLS", True, Colors.TEXT_ACCENT)
        surface.blit(header_surf, (cx, cy))
        cy += header_h

        for key, desc in controls:
            key_surf = self.font_label.render(key, True, Colors.TEXT_ACCENT)
            desc_surf = self.font_label.render(desc, True, Colors.TEXT_SECONDARY)
            surface.blit(key_surf, (cx, cy))
            surface.blit(desc_surf, (cx + key_surf.get_width() + 12, cy))
            cy += ctrl_sp

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

        # --- Card: Pseudocode ---
        if has_pseudo and card_pseudo_h > 0:
            self._draw_card(surface, px, py, card_width, card_pseudo_h)
            cx = px + card_pad
            cy = py + card_pad

            header_surf = self.font_section.render("PSEUDOCODE", True, Colors.TEXT_ACCENT)
            surface.blit(header_surf, (cx, cy))
            cy += header_h

            highlighted = set(pc_data["highlight_map"].get(self.current_op_type, []))
            for i, line_text in enumerate(pc_data["lines"]):
                if i in highlighted:
                    hl_rect = pygame.Rect(cx - 4, cy - 2, inner_width + 8, code_line_h)
                    hl_surf = pygame.Surface((hl_rect.width, hl_rect.height), pygame.SRCALPHA)
                    hl_surf.fill((60, 130, 200, 50))
                    surface.blit(hl_surf, hl_rect)
                    text_surf = self.font_mono.render(line_text, True, Colors.TEXT_PRIMARY)
                else:
                    text_surf = self.font_mono.render(line_text, True, Colors.TEXT_SECONDARY)
                surface.blit(text_surf, (cx, cy))
                cy += code_line_h

            py += card_pseudo_h + card_gap

        # --- Card: Variables (only when pointers are active) ---
        if has_vars and card_vars_h > 0:
            self._draw_card(surface, px, py, card_width, card_vars_h)
            cx = px + card_pad
            cy = py + card_pad

            header_surf = self.font_section.render("VARIABLES", True, Colors.TEXT_ACCENT)
            surface.blit(header_surf, (cx, cy))
            cy += header_h

            for name, value, arr_info in self._cached_var_lines:
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

            py += card_vars_h + card_gap

        # --- Card: Legend (remaining space between variables and controls) ---
        if card_legend_h > 0 and max_legend_items > 0:
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
