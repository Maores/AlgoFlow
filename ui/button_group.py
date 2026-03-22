# ui/button_group.py - Row of mutually exclusive buttons for AlgoFlow
import pygame
from ui.button import Button
from config import Colors


class ButtonGroup:
    """A row of buttons where exactly one is active at a time."""

    def __init__(self, x, y, labels, font, active_index=0):
        self.labels = labels
        self.font = font
        self.active_index = active_index
        self.buttons = []

        # Build buttons with auto-width based on text
        current_x = x
        for i, label in enumerate(labels):
            text_width = font.size(label)[0]
            btn_width = text_width + 36
            btn = Button(current_x, y, btn_width, 48, label, font)
            if i == active_index:
                btn.is_active = True
            self.buttons.append(btn)
            current_x += btn_width + 5

    def handle_event(self, event):
        """Returns label string if selection changed, else None."""
        for i, btn in enumerate(self.buttons):
            if btn.handle_event(event):
                if i != self.active_index:
                    self.buttons[self.active_index].is_active = False
                    self.active_index = i
                    btn.is_active = True
                    return self.labels[i]
        return None

    def set_position(self, x, y):
        """Reposition all buttons starting from (x, y)."""
        current_x = x
        for btn in self.buttons:
            btn.rect.x = current_x
            btn.rect.y = y
            current_x += btn.rect.width + 5

    def get_active(self):
        """Return the currently active label."""
        return self.labels[self.active_index]

    def draw(self, surface):
        """Draw all buttons."""
        for btn in self.buttons:
            btn.draw(surface)
