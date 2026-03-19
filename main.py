# main.py - AlgoFlow
# Entry point with game loop, tab switching, control bar, and event handling
import pygame
import sys
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE,
    HEADER_HEIGHT, CONTROL_PANEL_HEIGHT, INFO_PANEL_WIDTH,
    SIZE_OPTIONS, DEFAULT_ARRAY_SIZE, Colors
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
    """Main application class - manages the game loop, tabs, and visualizers."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Fonts - created once
        self.font_small = pygame.font.SysFont("Arial", 13)
        self.font_hint = pygame.font.SysFont("Arial", 11)

        # Header with branding + tabs
        self.tab_bar = TabBar(WINDOW_WIDTH)

        # Canvas area (between header and control bar, left of info panel)
        canvas_y = HEADER_HEIGHT
        canvas_h = WINDOW_HEIGHT - HEADER_HEIGHT - CONTROL_PANEL_HEIGHT
        canvas_w = WINDOW_WIDTH - INFO_PANEL_WIDTH
        self.canvas_rect = pygame.Rect(0, canvas_y, canvas_w, canvas_h)

        # Info panel (right side)
        info_rect = pygame.Rect(
            WINDOW_WIDTH - INFO_PANEL_WIDTH, canvas_y,
            INFO_PANEL_WIDTH, canvas_h
        )
        self.info_panel = InfoPanel(info_rect)

        # Initialize all visualizers
        self.visualizers = {
            "Sorting": SortingVisualizer(self.canvas_rect),
            "Pathfinding": PathfindingVisualizer(self.canvas_rect),
            "Trees": TreeVisualizer(self.canvas_rect),
        }

        # --- Control bar components (relative positioning) ---
        control_y = WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT
        btn_y = control_y + (CONTROL_PANEL_HEIGHT - 34) // 2
        gap = 12
        x = gap

        # Start/Pause button
        self.start_button = Button(x, btn_y, 90, 34, "\u25b6 Start", self.font_small)
        x += 90 + 6

        # Reset button
        self.reset_button = Button(x, btn_y, 72, 34, "\u21bb Reset", self.font_small)
        x += 72 + gap

        # Divider 1 position
        self.div1_x = x
        x += gap

        # Speed slider
        slider_label_w = self.font_small.size("Speed")[0] + 8
        self.speed_slider = Slider(
            x + slider_label_w,
            control_y + CONTROL_PANEL_HEIGHT // 2,
            120, 1, 100, 50, label="Speed"
        )
        x += slider_label_w + 120 + gap

        # Divider 2 position
        self.div2_x = x
        x += gap

        # Algorithm selector
        algo_labels = list(ALGORITHM_INFO.keys())
        self.algo_group = ButtonGroup(
            x, btn_y + 2, algo_labels, self.font_small, active_index=0
        )
        # Calculate algo group width
        algo_width = sum(b.rect.width for b in self.algo_group.buttons) + 4 * (len(algo_labels) - 1)
        x += algo_width + gap

        # Divider 3 position
        self.div3_x = x
        x += gap

        # Size selector
        default_idx = SIZE_OPTIONS.index(str(DEFAULT_ARRAY_SIZE))
        self.size_group = ButtonGroup(
            x, btn_y + 2, SIZE_OPTIONS, self.font_small, active_index=default_idx
        )

        self.control_y = control_y

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
        viz = self.visualizers.get("Sorting")
        if viz and hasattr(viz, "get_algorithm_info"):
            info = viz.get_algorithm_info()
            self.info_panel.set_algorithm_info(
                info["name"], info["time_best"], info["time_avg"],
                info["time_worst"], info["space"], info["stable"]
            )

    def get_active_visualizer(self):
        tab_name = self.tab_bar.get_active_tab()
        return self.visualizers[tab_name]

    def handle_events(self):
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

            self.tab_bar.handle_event(event)

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

            viz.handle_event(event)

    def update(self):
        viz = self.get_active_visualizer()
        if viz.is_running and not viz.is_complete:
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

    def _draw_divider(self, x):
        """Draw a subtle vertical divider in the control bar."""
        pygame.draw.line(
            self.screen, (50, 50, 65),
            (x, self.control_y + 14),
            (x, self.control_y + CONTROL_PANEL_HEIGHT - 14), 1
        )

    def draw(self):
        self.screen.fill(Colors.BG)

        # Header (brand + tabs)
        self.tab_bar.draw(self.screen)

        # Active visualizer
        self.get_active_visualizer().draw(self.screen)

        # Info panel
        self.info_panel.draw(self.screen)

        # Control bar background
        control_rect = pygame.Rect(0, self.control_y, WINDOW_WIDTH, CONTROL_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, Colors.PANEL_BG, control_rect)
        # Top border
        pygame.draw.line(
            self.screen, (40, 40, 55),
            (0, self.control_y), (WINDOW_WIDTH, self.control_y), 1
        )

        # Control bar components
        self.start_button.draw(self.screen)
        self.reset_button.draw(self.screen)
        self._draw_divider(self.div1_x)
        self.speed_slider.draw(self.screen, self.font_small)
        self._draw_divider(self.div2_x)
        self.algo_group.draw(self.screen)
        self._draw_divider(self.div3_x)
        self.size_group.draw(self.screen)

        # Keyboard hints (right-aligned in control bar)
        hint = "SPACE: play/pause \u00b7 R: reset"
        hint_surf = self.font_hint.render(hint, True, Colors.HINT_TEXT)
        hint_rect = hint_surf.get_rect(
            right=WINDOW_WIDTH - 12,
            centery=self.control_y + CONTROL_PANEL_HEIGHT // 2
        )
        self.screen.blit(hint_surf, hint_rect)

        pygame.display.flip()

    def run(self):
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
