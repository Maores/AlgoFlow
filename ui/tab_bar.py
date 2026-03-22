# ui/tab_bar.py - Header bar with AlgoFlow branding and tab navigation
import pygame
from config import Colors, TABS, HEADER_HEIGHT, TITLE, FONT_FAMILY


class TabBar:
    """Header bar: AlgoFlow brand on the left, pill-style tabs on the right."""

    def __init__(self, width):
        self.width = width
        self.tabs = TABS
        self.active_tab = 0
        self.hover_tab = -1

        # Fonts - created once
        self.font_brand = pygame.font.SysFont(FONT_FAMILY, 22, bold=True)
        self.font_tab = pygame.font.SysFont(FONT_FAMILY, 16)

        # Brand area
        self.brand_x = 16

        # Build tab rects (pill-style, right-aligned)
        self.tab_rects = []
        self._build_tabs()

    def _build_tabs(self):
        """Calculate pill-style tab positions, starting after brand area."""
        tab_padding_h = 16  # horizontal padding inside each tab
        tab_height = 34
        tab_gap = 6
        tab_y = (HEADER_HEIGHT - tab_height) // 2

        # Start tabs at x=140 (after brand)
        x = 140
        self.tab_rects = []
        for tab_name in self.tabs:
            text_w = self.font_tab.size(tab_name)[0]
            tab_w = text_w + tab_padding_h * 2
            self.tab_rects.append(pygame.Rect(x, tab_y, tab_w, tab_height))
            x += tab_w + tab_gap

    def resize(self, width):
        """Update width and rebuild tab positions for new window width."""
        self.width = width
        self._build_tabs()

    def handle_event(self, event):
        """Handle mouse events. Returns True if tab changed."""
        if event.type == pygame.MOUSEMOTION:
            self.hover_tab = -1
            for i, rect in enumerate(self.tab_rects):
                if rect.collidepoint(event.pos):
                    self.hover_tab = i
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.tab_rects):
                if rect.collidepoint(event.pos) and i != self.active_tab:
                    self.active_tab = i
                    return True
        return False

    def draw(self, surface):
        """Draw the header bar with brand and tabs."""
        # Full header background
        header_rect = pygame.Rect(0, 0, self.width, HEADER_HEIGHT)
        pygame.draw.rect(surface, Colors.HEADER_BG, header_rect)

        # Bottom border line
        pygame.draw.line(
            surface, (40, 40, 55),
            (0, HEADER_HEIGHT - 1), (self.width, HEADER_HEIGHT - 1), 1
        )

        # Brand text
        brand_surf = self.font_brand.render(TITLE, True, Colors.TEXT_ACCENT)
        brand_rect = brand_surf.get_rect(
            left=self.brand_x,
            centery=HEADER_HEIGHT // 2
        )
        surface.blit(brand_surf, brand_rect)

        # Draw tabs as pills
        for i, (tab_name, rect) in enumerate(zip(self.tabs, self.tab_rects)):
            if i == self.active_tab:
                bg = Colors.TAB_ACTIVE
                text_color = Colors.TAB_TEXT_ACTIVE
            elif i == self.hover_tab:
                bg = Colors.TAB_HOVER
                text_color = Colors.TAB_TEXT
            else:
                bg = Colors.TAB_INACTIVE
                text_color = Colors.TAB_TEXT

            pygame.draw.rect(surface, bg, rect, border_radius=6)

            text_surf = self.font_tab.render(tab_name, True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            surface.blit(text_surf, text_rect)

    def get_active_tab(self):
        """Return the name of the currently active tab."""
        return self.tabs[self.active_tab]
