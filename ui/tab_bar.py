# ui/tab_bar.py - Tab navigation bar
import pygame
from config import Colors, TABS, TAB_BAR_HEIGHT, WINDOW_WIDTH


class TabBar:
    """Horizontal tab bar for switching between visualizer modules."""
    
    def __init__(self):
        self.tabs = TABS
        self.active_tab = 0
        self.tab_rects = []
        self.hover_tab = -1
        self._calculate_rects()
    
    def _calculate_rects(self):
        """Calculate the rectangle for each tab."""
        tab_width = WINDOW_WIDTH // len(self.tabs)
        self.tab_rects = [
            pygame.Rect(i * tab_width, 0, tab_width, TAB_BAR_HEIGHT)
            for i in range(len(self.tabs))
        ]
    
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
    
    def draw(self, surface, font):
        """Draw the tab bar."""
        for i, (tab_name, rect) in enumerate(zip(self.tabs, self.tab_rects)):
            # Background
            if i == self.active_tab:
                color = Colors.TAB_ACTIVE
            elif i == self.hover_tab:
                color = Colors.TAB_HOVER
            else:
                color = Colors.TAB_INACTIVE
            
            pygame.draw.rect(surface, color, rect)
            
            # Active indicator line
            if i == self.active_tab:
                indicator = pygame.Rect(rect.x, rect.bottom - 3, rect.width, 3)
                pygame.draw.rect(surface, Colors.TEXT_ACCENT, indicator)
            
            # Tab text
            text_color = Colors.TAB_TEXT_ACTIVE if i == self.active_tab else Colors.TAB_TEXT
            text_surf = font.render(tab_name, True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            surface.blit(text_surf, text_rect)
            
            # Separator line between tabs
            if i < len(self.tabs) - 1:
                sep_x = rect.right
                pygame.draw.line(surface, Colors.BG, (sep_x, 5), (sep_x, TAB_BAR_HEIGHT - 5), 1)
    
    def get_active_tab(self):
        """Return the name of the currently active tab."""
        return self.tabs[self.active_tab]
