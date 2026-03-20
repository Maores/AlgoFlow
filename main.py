# main.py - AlgoFlow
# Entry point with game loop, tab switching, control bar, and event handling
import math
import pygame
import sys
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE,
    HEADER_HEIGHT, CONTROL_PANEL_HEIGHT, INFO_PANEL_WIDTH,
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT,
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
        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE
        )
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT

        # Speed accumulator for time-based stepping
        self.step_accumulator = 0.0

        # Fonts - created once
        self.font_small = pygame.font.SysFont("Arial", 15)
        self.font_hint = pygame.font.SysFont("Arial", 13)

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

        # --- Control bar components (created once, repositioned by _rebuild_layout) ---
        control_y = WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT
        btn_h = 34
        btn_y = control_y + (CONTROL_PANEL_HEIGHT - btn_h) // 2

        # Start/Pause button (no unicode icons — avoids glyph rendering artifacts)
        self.start_button = Button(14, btn_y, 96, btn_h, "Start", self.font_small)

        # Reset button
        self.reset_button = Button(116, btn_y, 76, btn_h, "Reset", self.font_small)

        # Speed slider
        slider_label_w = self.font_small.size("Speed")[0] + 8
        self.speed_slider = Slider(
            206 + slider_label_w,
            control_y + CONTROL_PANEL_HEIGHT // 2,
            140, 1, 100, 50, label="Speed"
        )

        # Algorithm selector
        algo_labels = list(ALGORITHM_INFO.keys())
        self.algo_group = ButtonGroup(
            0, btn_y + 1, algo_labels, self.font_small, active_index=0
        )

        # Size selector
        default_idx = SIZE_OPTIONS.index(str(DEFAULT_ARRAY_SIZE))
        self.size_group = ButtonGroup(
            0, btn_y + 1, SIZE_OPTIONS, self.font_small, active_index=default_idx
        )

        # Divider positions (set by _rebuild_layout)
        self.div1_x = 0
        self.div2_x = 0
        self.div3_x = 0
        self.control_y = control_y

        # Apply correct layout positions
        self._rebuild_layout(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Set initial info panel state
        self._update_info_panel()
        self.info_panel.set_legend([
            (Colors.BAR_DEFAULT, "Default"),
            (Colors.BAR_COMPARING, "Comparing"),
            (Colors.BAR_SWAPPING, "Swapping"),
            (Colors.BAR_SORTED, "Sorted"),
        ])

        self.running = True

    def _rebuild_layout(self, w, h):
        """Recalculate all layout positions for the given window dimensions."""
        self.width = w
        self.height = h

        # Canvas area
        canvas_y = HEADER_HEIGHT
        canvas_h = h - HEADER_HEIGHT - CONTROL_PANEL_HEIGHT
        canvas_w = w - INFO_PANEL_WIDTH
        self.canvas_rect = pygame.Rect(0, canvas_y, canvas_w, canvas_h)

        # Update all visualizers
        for viz in self.visualizers.values():
            viz.set_canvas_rect(self.canvas_rect)

        # Info panel
        self.info_panel.rect = pygame.Rect(
            w - INFO_PANEL_WIDTH, canvas_y,
            INFO_PANEL_WIDTH, canvas_h
        )

        # Tab bar
        self.tab_bar.resize(w)

        # Control bar
        control_y = h - CONTROL_PANEL_HEIGHT
        self.control_y = control_y
        btn_h = 34
        btn_y = control_y + (CONTROL_PANEL_HEIGHT - btn_h) // 2
        gap = 14
        x = 14

        # Reposition control bar components
        self.start_button.rect.topleft = (x, btn_y)
        x += self.start_button.rect.width + 6

        self.reset_button.rect.topleft = (x, btn_y)
        x += self.reset_button.rect.width + gap

        self.div1_x = x
        x += gap

        slider_label_w = self.font_small.size("Speed")[0] + 8
        self.speed_slider.set_position(
            x + slider_label_w,
            control_y + CONTROL_PANEL_HEIGHT // 2
        )
        x += slider_label_w + 140 + gap

        self.div2_x = x
        x += gap

        self.algo_group.set_position(x, btn_y + 1)
        algo_width = sum(b.rect.width for b in self.algo_group.buttons) + 4 * (len(self.algo_group.labels) - 1)
        x += algo_width + gap

        self.div3_x = x
        x += gap

        self.size_group.set_position(x, btn_y + 1)

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

            if event.type == pygame.VIDEORESIZE:
                new_w = max(event.w, MIN_WINDOW_WIDTH)
                new_h = max(event.h, MIN_WINDOW_HEIGHT)
                self.screen = pygame.display.set_mode(
                    (new_w, new_h), pygame.RESIZABLE
                )
                self._rebuild_layout(new_w, new_h)
                continue

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
            # Exponential speed curve: 1000^(speed/100) ops per second
            # speed  1 → ~1 op/s,  speed 50 → ~32 ops/s,  speed 100 → 1000 ops/s
            speed_val = self.speed_slider.get_value()
            dt = self.clock.get_time() / 1000.0
            ops_per_second = 1000.0 ** (speed_val / 100.0)
            self.step_accumulator += ops_per_second * dt
            while self.step_accumulator >= 1.0 and viz.is_running and not viz.is_complete:
                self.step_accumulator -= 1.0
                viz.step()
            # Cap accumulator to avoid burst after pause/lag
            self.step_accumulator = min(self.step_accumulator, 5.0)

        # Update info panel stats
        if hasattr(viz, "get_status"):
            self.info_panel.set_stats(
                getattr(viz, "comparisons", 0),
                getattr(viz, "swaps", 0),
                viz.get_status()
            )

        # Update start button text (plain text, no unicode icons)
        if viz.is_running:
            self.start_button.text = "Pause"
        else:
            self.start_button.text = "Start"

    def _draw_divider(self, x):
        """Draw a subtle vertical divider in the control bar."""
        pygame.draw.line(
            self.screen, (50, 50, 65),
            (x, self.control_y + 16),
            (x, self.control_y + CONTROL_PANEL_HEIGHT - 16), 1
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
        control_rect = pygame.Rect(0, self.control_y, self.width, CONTROL_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, Colors.PANEL_BG, control_rect)
        # Top border
        pygame.draw.line(
            self.screen, (40, 40, 55),
            (0, self.control_y), (self.width, self.control_y), 1
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
            right=self.width - 12,
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
