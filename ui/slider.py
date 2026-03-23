# ui/slider.py - Horizontal slider component for AlgoFlow
import pygame
from config import Colors


class Slider:
    """Horizontal slider for speed control and other numeric values."""

    def __init__(self, x, y, width, min_val, max_val, initial_val, label=""):
        self.x = x
        self.y = y
        self.width = width
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        self.knob_radius = 9
        self.track_height = 7

    def _get_knob_x(self):
        """Calculate knob x position from current value."""
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return self.x + int(ratio * self.width)

    def _value_from_x(self, mouse_x):
        """Calculate value from mouse x position."""
        ratio = max(0, min(1, (mouse_x - self.x) / self.width))
        return self.min_val + ratio * (self.max_val - self.min_val)

    def handle_event(self, event):
        """Handle mouse events. Returns True if value changed."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            knob_x = self._get_knob_x()
            knob_rect = pygame.Rect(
                knob_x - self.knob_radius, self.y - self.knob_radius,
                self.knob_radius * 2, self.knob_radius * 2
            )
            track_rect = pygame.Rect(
                self.x, self.y - self.track_height,
                self.width, self.track_height * 2
            )
            if knob_rect.collidepoint(event.pos) or track_rect.collidepoint(event.pos):
                self.dragging = True
                self.value = self._value_from_x(event.pos[0])
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.value = self._value_from_x(event.pos[0])
            return True

        return False

    def get_value(self):
        """Return current slider value."""
        return self.value

    def set_position(self, x, y, width=None):
        """Reposition the slider (used on window resize)."""
        self.x = x
        self.y = y
        if width is not None:
            self.width = width

    def draw(self, surface, font):
        """Draw track, fill, knob, and label."""
        # Draw label to the left
        if self.label:
            label_surf = font.render(self.label, True, Colors.TEXT_SECONDARY)
            surface.blit(label_surf, (self.x - label_surf.get_width() - 14, self.y - label_surf.get_height() // 2))

        # Track background
        track_rect = pygame.Rect(
            self.x, self.y - self.track_height // 2,
            self.width, self.track_height
        )
        pygame.draw.rect(surface, Colors.SLIDER_TRACK, track_rect, border_radius=3)

        # Fill (left of knob)
        knob_x = self._get_knob_x()
        fill_rect = pygame.Rect(
            self.x, self.y - self.track_height // 2,
            knob_x - self.x, self.track_height
        )
        if fill_rect.width > 0:
            pygame.draw.rect(surface, Colors.SLIDER_FILL, fill_rect, border_radius=3)

        # Knob
        pygame.draw.circle(surface, Colors.SLIDER_KNOB, (knob_x, self.y), self.knob_radius)
