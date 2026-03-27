# ui/help_modal.py - Lightweight modal showing keyboard controls for AlgoFlow
import pygame
from config import Colors, FONT_FAMILY


class HelpModal:
    """Lightweight modal showing keyboard controls, tab-aware."""

    SORTING_CONTROLS = [
        ("[Space]", "Play / Pause"),
        ("[R]", "Reset"),
        ("\u2192", "Step Forward"),
        ("\u2190", "Step Backward"),
        ("[C]", "Custom Array"),
        ("[H]", "Toggle Help"),
        ("[Esc]", "Close / Quit"),
    ]

    PATHFINDING_CONTROLS = [
        ("[Space]", "Play / Pause"),
        ("[R]", "Reset Algorithm"),
        ("\u2192", "Step Forward"),
        ("\u2190", "Step Backward"),
        ("[H]", "Toggle Help"),
        ("[Esc]", "Close / Quit"),
        ("", ""),
        ("Mouse", "Draw / erase walls"),
        ("", "Use toolbar to switch"),
        ("", "between Wall / Start / End"),
    ]

    def __init__(self, screen_width, screen_height):
        self.visible = False
        self.current_tab = "Sorting"
        self.font_title = pygame.font.SysFont(FONT_FAMILY, 28, bold=True)
        self.font_text = pygame.font.SysFont(FONT_FAMILY, 20)
        self.font_hint = pygame.font.SysFont(FONT_FAMILY, 16)

        self.card_w = 420
        # Dynamic height based on longest controls list
        max_rows = max(len(self.SORTING_CONTROLS), len(self.PATHFINDING_CONTROLS))
        self.card_h = 100 + max_rows * 34 + 40  # title + rows + hint padding
        self.close_btn_size = 28
        self._overlay = None
        self.card_rect = pygame.Rect(0, 0, self.card_w, self.card_h)
        self.close_btn_rect = pygame.Rect(0, 0, self.close_btn_size, self.close_btn_size)
        self.resize(screen_width, screen_height)

    def open(self, tab="Sorting"):
        self.visible = True
        self.current_tab = tab

    def close(self):
        self.visible = False

    def is_open(self):
        return self.visible

    def resize(self, screen_width, screen_height):
        self.card_rect = pygame.Rect(
            (screen_width - self.card_w) // 2,
            (screen_height - self.card_h) // 2,
            self.card_w, self.card_h
        )
        self.close_btn_rect = pygame.Rect(
            self.card_rect.right - self.close_btn_size - 12,
            self.card_rect.top + 12,
            self.close_btn_size, self.close_btn_size
        )
        self._overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 240))

    def handle_event(self, event):
        """Returns {'action': 'close'} or None."""
        if not self.visible:
            return None

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return {"action": "close"}

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.close_btn_rect.collidepoint(event.pos):
                self.close()
                return {"action": "close"}
            if not self.card_rect.collidepoint(event.pos):
                self.close()
                return {"action": "close"}

        # Consume all events while open
        return {"action": "none"}

    def draw(self, surface):
        if not self.visible:
            return

        # Overlay
        surface.blit(self._overlay, (0, 0))

        # Card
        pygame.draw.rect(surface, Colors.PANEL_BG, self.card_rect, border_radius=12)
        pygame.draw.rect(surface, Colors.CARD_BORDER, self.card_rect, width=1, border_radius=12)

        # X close button (hover highlight)
        mouse_pos = pygame.mouse.get_pos()
        if self.close_btn_rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, Colors.BUTTON_HOVER, self.close_btn_rect, border_radius=6)
        x_surf = self.font_text.render("X", True, Colors.TEXT_SECONDARY)
        x_rect = x_surf.get_rect(center=self.close_btn_rect.center)
        surface.blit(x_surf, x_rect)

        # Title
        if self.current_tab == "Pathfinding":
            title_text = "Pathfinding Controls"
        else:
            title_text = "Sorting Controls"
        title_surf = self.font_title.render(title_text, True, Colors.TEXT_PRIMARY)
        title_rect = title_surf.get_rect(
            centerx=self.card_rect.centerx, top=self.card_rect.top + 24
        )
        surface.blit(title_surf, title_rect)

        # Select controls based on tab
        if self.current_tab == "Pathfinding":
            controls = self.PATHFINDING_CONTROLS
        else:
            controls = self.SORTING_CONTROLS

        # Control rows
        start_y = title_rect.bottom + 28
        row_h = 34
        key_x = self.card_rect.x + 60
        desc_x = self.card_rect.x + 160

        for i, (key, desc) in enumerate(controls):
            y = start_y + i * row_h
            if key:
                key_surf = self.font_text.render(key, True, Colors.TEXT_ACCENT)
                surface.blit(key_surf, (key_x, y))
            desc_surf = self.font_text.render(desc, True, Colors.TEXT_SECONDARY)
            surface.blit(desc_surf, (desc_x, y))

        # Close hint
        hint_surf = self.font_hint.render(
            "Click outside or press Esc to close", True, Colors.HINT_TEXT
        )
        hint_rect = hint_surf.get_rect(
            centerx=self.card_rect.centerx, bottom=self.card_rect.bottom - 16
        )
        surface.blit(hint_surf, hint_rect)
