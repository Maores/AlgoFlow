import pygame
from config import Colors, FONT_FAMILY


class TextInput:
    """Inline numeric text input widget (digits only, 1-99)."""

    def __init__(self, rect, placeholder=""):
        self.rect = pygame.Rect(rect)
        self.placeholder = placeholder
        self.text = ""
        self.focused = False
        self.font = pygame.font.SysFont(FONT_FAMILY, 20)
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.focused = self.rect.collidepoint(event.pos)
            if self.focused:
                self.cursor_visible = True
                self.cursor_timer = 0
        elif event.type == pygame.KEYDOWN and self.focused:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit() and len(self.text) < 3:
                self.text += event.unicode

    def update(self, dt):
        """Update cursor blink (call each frame with dt in ms)."""
        if self.focused:
            self.cursor_timer += dt
            if self.cursor_timer >= 500:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

    def draw(self, surface):
        # Border color: accent when focused, default otherwise
        border_color = Colors.TAB_ACTIVE if self.focused else Colors.CARD_BORDER
        pygame.draw.rect(surface, Colors.CARD_BG, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=6)

        if self.text:
            text_surf = self.font.render(self.text, True, Colors.TEXT_PRIMARY)
        else:
            text_surf = self.font.render(self.placeholder, True, Colors.HINT_TEXT)

        text_rect = text_surf.get_rect(midleft=(self.rect.x + 8, self.rect.centery))
        surface.blit(text_surf, text_rect)

        # Cursor
        if self.focused and self.cursor_visible and self.text:
            cursor_x = text_rect.right + 2
            pygame.draw.line(surface, Colors.TEXT_PRIMARY,
                           (cursor_x, self.rect.y + 6),
                           (cursor_x, self.rect.bottom - 6), 2)
        elif self.focused and self.cursor_visible and not self.text:
            cursor_x = self.rect.x + 8
            pygame.draw.line(surface, Colors.TEXT_PRIMARY,
                           (cursor_x, self.rect.y + 6),
                           (cursor_x, self.rect.bottom - 6), 2)

    def get_int_value(self):
        """Return int value or None if empty/invalid."""
        if self.text and self.text.isdigit():
            val = int(self.text)
            if 1 <= val <= 99:
                return val
        return None

    def clear(self):
        self.text = ""
