# visualizers/base.py - Abstract base class for all visualizers
# This is the OOP foundation of the project - key interview talking point!
from abc import ABC, abstractmethod
import pygame


class BaseVisualizer(ABC):
    """
    Abstract base class that all visualizer tabs inherit from.
    
    This demonstrates:
    - Abstraction: Defines interface without implementation
    - Polymorphism: main.py calls step()/draw() on any visualizer
    - Encapsulation: Each visualizer manages its own state
    
    Interview talking point: "I used an abstract base class so that
    the main loop doesn't need to know which algorithm is running.
    It just calls step() and draw() - that's polymorphism in action."
    """
    
    def __init__(self, canvas_rect):
        """
        Args:
            canvas_rect: pygame.Rect defining the drawable area
        """
        self.canvas_rect = canvas_rect
        self.is_running = False
        self.is_complete = False
        self.speed = 50  # 0-100, controls animation speed
        self.step_count = 0
    
    @abstractmethod
    def reset(self):
        """Reset the visualizer to initial state with new data."""
        pass
    
    @abstractmethod
    def step(self):
        """Perform one step of the algorithm. Called each frame when running."""
        pass
    
    @abstractmethod
    def draw(self, surface):
        """Draw the current state to the surface."""
        pass
    
    @abstractmethod
    def handle_event(self, event):
        """Handle input events (mouse clicks, key presses)."""
        pass
    
    def start(self):
        """Start the animation."""
        self.is_running = True
        self.is_complete = False
    
    def pause(self):
        """Pause the animation."""
        self.is_running = False
    
    def toggle(self):
        """Toggle between running and paused."""
        if self.is_complete:
            self.reset()
        self.is_running = not self.is_running

    def step_forward(self):
        """Advance one step. Override in subclasses for time-travel support."""
        self.step()

    def step_backward(self):
        """Go back one step. Override in subclasses for time-travel support."""
        pass

    def set_speed(self, speed):
        """Set animation speed (0-100)."""
        self.speed = max(0, min(100, speed))

    def set_canvas_rect(self, rect):
        """Update the drawable area (called on window resize)."""
        self.canvas_rect = rect
