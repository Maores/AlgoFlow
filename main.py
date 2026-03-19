# main.py - Algorithm & Data Structure Visualizer
# Entry point with game loop, tab switching, and event handling
import pygame
import sys
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE,
    TAB_BAR_HEIGHT, CONTROL_PANEL_HEIGHT, Colors
)
from ui.tab_bar import TabBar
from visualizers.sorting_viz import SortingVisualizer
from visualizers.pathfinding_viz import PathfindingVisualizer
from visualizers.tree_viz import TreeVisualizer


class App:
    """
    Main application class - manages the game loop, tabs, and visualizers.
    
    Architecture note (interview talking point):
    The App class follows the Mediator pattern - it coordinates between
    the TabBar (navigation) and Visualizers (content) without them
    knowing about each other. Each visualizer is self-contained.
    """
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_medium = pygame.font.SysFont("Arial", 18)
        self.font_small = pygame.font.SysFont("Arial", 14)
        
        # UI components
        self.tab_bar = TabBar()
        
        # Canvas area (where visualizers draw)
        canvas_y = TAB_BAR_HEIGHT + 5
        canvas_height = WINDOW_HEIGHT - TAB_BAR_HEIGHT - CONTROL_PANEL_HEIGHT - 10
        self.canvas_rect = pygame.Rect(0, canvas_y, WINDOW_WIDTH, canvas_height)
        
        # Initialize all visualizers (polymorphism - they share the same interface)
        self.visualizers = {
            "Sorting": SortingVisualizer(self.canvas_rect),
            "Pathfinding": PathfindingVisualizer(self.canvas_rect),
            "Trees": TreeVisualizer(self.canvas_rect),
        }
        
        self.running = True
    
    def get_active_visualizer(self):
        """Return the currently active visualizer based on selected tab."""
        tab_name = self.tab_bar.get_active_tab()
        return self.visualizers[tab_name]
    
    def handle_events(self):
        """Process all input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
                elif event.key == pygame.K_SPACE:
                    self.get_active_visualizer().toggle()
                elif event.key == pygame.K_r:
                    self.get_active_visualizer().reset()
            
            # Tab bar events
            self.tab_bar.handle_event(event)
            
            # Active visualizer events
            self.get_active_visualizer().handle_event(event)
    
    def update(self):
        """Update the active visualizer."""
        viz = self.get_active_visualizer()
        if viz.is_running and not viz.is_complete:
            viz.step()
    
    def draw(self):
        """Draw everything to the screen."""
        # Clear screen
        self.screen.fill(Colors.BG)
        
        # Draw tab bar
        self.tab_bar.draw(self.screen, self.font_medium)
        
        # Draw active visualizer
        self.get_active_visualizer().draw(self.screen)
        
        # Draw bottom control bar background
        control_y = WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT
        control_rect = pygame.Rect(0, control_y, WINDOW_WIDTH, CONTROL_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, Colors.PANEL_BG, control_rect)
        
        # Draw keyboard shortcuts hint
        hints = "SPACE: Start/Pause  |  R: Reset  |  ESC: Quit"
        hint_surf = self.font_small.render(hints, True, Colors.TEXT_SECONDARY)
        hint_rect = hint_surf.get_rect(
            centerx=WINDOW_WIDTH // 2,
            centery=control_y + CONTROL_PANEL_HEIGHT // 2
        )
        self.screen.blit(hint_surf, hint_rect)
        
        # Draw FPS counter (top right, subtle)
        fps_text = f"FPS: {int(self.clock.get_fps())}"
        fps_surf = self.font_small.render(fps_text, True, Colors.TEXT_SECONDARY)
        self.screen.blit(fps_surf, (WINDOW_WIDTH - 80, TAB_BAR_HEIGHT + 10))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = App()
    app.run()
