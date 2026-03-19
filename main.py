# main.py - AlgoFlow
# Entry point with game loop, tab switching, control bar, and event handling
import pygame
import sys
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE,
    TAB_BAR_HEIGHT, CONTROL_PANEL_HEIGHT, INFO_PANEL_WIDTH, Colors
)
from ui.tab_bar import TabBar
from ui.button import Button
from ui.slider import Slider
from ui.button_group import ButtonGroup
from ui.info_panel import InfoPanel
from visualizers.sorting_viz import SortingVisualizer
from visualizers.pathfinding_viz import PathfindingVisualizer
from visualizers.tree_viz import TreeVisualizer
from algorithms.sorting import ALGORITHM_INFO


class App:
    """
    Main application class - manages the game loop, tabs, and visualizers.

    The App class follows the Mediator pattern - it coordinates between
    the TabBar (navigation) and Visualizers (content) without them
    knowing about each other.
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Fonts - created once, reused every frame
        self.font_medium = pygame.font.SysFont("Arial", 18)
        self.font_small = pygame.font.SysFont("Arial", 14)

        # UI components
        self.tab_bar = TabBar()

        # Canvas area (leaves room for info panel on the right)
        canvas_y = TAB_BAR_HEIGHT + 5
        canvas_height = WINDOW_HEIGHT - TAB_BAR_HEIGHT - CONTROL_PANEL_HEIGHT - 10
        canvas_width = WINDOW_WIDTH - INFO_PANEL_WIDTH
        self.canvas_rect = pygame.Rect(0, canvas_y, canvas_width, canvas_height)

        # Info panel (right side)
        info_rect = pygame.Rect(
            WINDOW_WIDTH - INFO_PANEL_WIDTH, canvas_y,
            INFO_PANEL_WIDTH, canvas_height
        )
        self.info_panel = InfoPanel(info_rect)

        # Initialize all visualizers
        self.visualizers = {
            "Sorting": SortingVisualizer(self.canvas_rect),
            "Pathfinding": PathfindingVisualizer(self.canvas_rect),
            "Trees": TreeVisualizer(self.canvas_rect),
        }

        # Control bar components
        control_y = WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT
        btn_y = control_y + (CONTROL_PANEL_HEIGHT - 36) // 2

        self.start_button = Button(16, btn_y, 100, 36, "\u25b6 Start", self.font_small)
        self.reset_button = Button(124, btn_y, 80, 36, "\u21bb Reset", self.font_small)

        # Speed slider - label "Speed" drawn by slider itself
        slider_x = 260
        self.speed_slider = Slider(
            slider_x, control_y + CONTROL_PANEL_HEIGHT // 2,
            160, 1, 100, 50, label="Speed"
        )

        # Algorithm selector
        algo_labels = list(ALGORITHM_INFO.keys())
        self.algo_group = ButtonGroup(
            480, btn_y + 2, algo_labels, self.font_small, active_index=0
        )

        # Size selector
        self.size_group = ButtonGroup(
            750, btn_y + 2, ["20", "50", "100"], self.font_small, active_index=1
        )

        # Set initial info panel state
        self._update_info_panel()
        self.info_panel.set_legend([
            (Colors.BAR_DEFAULT, "Default"),
            (Colors.BAR_COMPARING, "Comparing"),
            (Colors.BAR_SWAPPING, "Swapping"),
            (Colors.BAR_SORTED, "Sorted"),
        ])

        self.running = True

    def _update_info_panel(self):
        """Update info panel with current algorithm metadata."""
        viz = self.visualizers.get("Sorting")
        if viz and hasattr(viz, "get_algorithm_info"):
            info = viz.get_algorithm_info()
            self.info_panel.set_algorithm_info(
                info["name"], info["time_best"], info["time_avg"],
                info["time_worst"], info["space"], info["stable"]
            )

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

            # Control bar events (only affect sorting for now)
            viz = self.get_active_visualizer()

            if self.start_button.handle_event(event):
                viz.toggle()

            if self.reset_button.handle_event(event):
                viz.reset()

            self.speed_slider.handle_event(event)

            algo_change = self.algo_group.handle_event(event)
            if algo_change and hasattr(viz, "set_algorithm"):
                viz.set_algorithm(algo_change)
                self._update_info_panel()

            size_change = self.size_group.handle_event(event)
            if size_change and hasattr(viz, "set_array_size"):
                viz.set_array_size(int(size_change))

            # Active visualizer events
            viz.handle_event(event)

    def update(self):
        """Update the active visualizer."""
        viz = self.get_active_visualizer()
        if viz.is_running and not viz.is_complete:
            # Speed control: map slider value to steps per frame
            speed_val = self.speed_slider.get_value()
            steps = max(1, int(speed_val / 5))
            for _ in range(steps):
                if viz.is_running and not viz.is_complete:
                    viz.step()

        # Update info panel stats
        if hasattr(viz, "get_status"):
            self.info_panel.set_stats(
                getattr(viz, "comparisons", 0),
                getattr(viz, "swaps", 0),
                viz.get_status()
            )

        # Update start button text
        if viz.is_running:
            self.start_button.text = "\u23f8 Pause"
        else:
            self.start_button.text = "\u25b6 Start"

    def draw(self):
        """Draw everything to the screen."""
        self.screen.fill(Colors.BG)

        # Tab bar
        self.tab_bar.draw(self.screen, self.font_medium)

        # Active visualizer
        self.get_active_visualizer().draw(self.screen)

        # Info panel
        self.info_panel.draw(self.screen)

        # Control bar background
        control_y = WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT
        control_rect = pygame.Rect(0, control_y, WINDOW_WIDTH, CONTROL_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, Colors.PANEL_BG, control_rect)

        # Control bar components
        self.start_button.draw(self.screen)
        self.reset_button.draw(self.screen)

        # Divider after buttons
        div_x = 216
        pygame.draw.line(
            self.screen, Colors.TEXT_SECONDARY,
            (div_x, control_y + 12), (div_x, control_y + CONTROL_PANEL_HEIGHT - 12), 1
        )

        self.speed_slider.draw(self.screen, self.font_small)

        # Divider after slider
        div_x = 440
        pygame.draw.line(
            self.screen, Colors.TEXT_SECONDARY,
            (div_x, control_y + 12), (div_x, control_y + CONTROL_PANEL_HEIGHT - 12), 1
        )

        self.algo_group.draw(self.screen)

        # Divider after algo group
        div_x = 720
        pygame.draw.line(
            self.screen, Colors.TEXT_SECONDARY,
            (div_x, control_y + 12), (div_x, control_y + CONTROL_PANEL_HEIGHT - 12), 1
        )

        self.size_group.draw(self.screen)

        # FPS counter (top right, subtle)
        fps_text = f"FPS: {int(self.clock.get_fps())}"
        fps_surf = self.font_small.render(fps_text, True, Colors.TEXT_SECONDARY)
        self.screen.blit(fps_surf, (WINDOW_WIDTH - INFO_PANEL_WIDTH - 80, TAB_BAR_HEIGHT + 10))

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
