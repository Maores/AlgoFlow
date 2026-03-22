# ui/button.py - Reusable button component
import pygame
from config import Colors, FONT_SIZES


class Button:
    """A clickable button with hover and active states."""
    
    def __init__(self, x, y, width, height, text, font=None, 
                 bg_color=None, hover_color=None, text_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color or Colors.BUTTON_BG
        self.hover_color = hover_color or Colors.BUTTON_HOVER
        self.text_color = text_color or Colors.BUTTON_TEXT
        self.is_hovered = False
        self.is_active = False
    
    def set_font(self, font):
        """Set font after pygame initialization."""
        self.font = font
    
    def handle_event(self, event):
        """Check if button was clicked. Returns True on click."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
    
    def draw(self, surface):
        """Draw the button with current state."""
        if self.is_active:
            color = Colors.BUTTON_ACTIVE
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.bg_color
        
        pygame.draw.rect(surface, color, self.rect, border_radius=9)
        
        if self.font:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
