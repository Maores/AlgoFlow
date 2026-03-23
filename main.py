# main.py - AlgoFlow
# Entry point with game loop, tab switching, control bar, and event handling

# Enable Windows High DPI awareness so the OS renders at native resolution
try:
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
except (AttributeError, OSError):
    pass  # Not on Windows — no action needed

import pygame
import sys
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE, FONT_FAMILY,
    HEADER_HEIGHT, CONTROL_PANEL_HEIGHT, INFO_PANEL_WIDTH,
    SIZE_OPTIONS, DEFAULT_ARRAY_SIZE,
    BASE_SPEED,
    Colors
)
from ui.tab_bar import TabBar
from ui.button import Button
from ui.button_group import ButtonGroup
from ui.slider import Slider
from ui.info_panel import InfoPanel
from ui.array_modal import ArrayModal
from visualizers.sorting_viz import SortingVisualizer
from visualizers.pathfinding_viz import PathfindingVisualizer
from visualizers.tree_viz import TreeVisualizer
from algorithms.sorting import ALGORITHM_INFO


class App:
    """Main application class - manages the game loop, tabs, and visualizers."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT

        # Speed accumulator for time-based stepping
        self.step_accumulator = 0.0

        # Fonts - created once
        self.font_small = pygame.font.SysFont(FONT_FAMILY, 23)

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
        btn_h = 51
        btn_y = control_y + (CONTROL_PANEL_HEIGHT - btn_h) // 2

        # Start/Pause button (no unicode icons — avoids glyph rendering artifacts)
        self.start_button = Button(21, btn_y, 144, btn_h, "Start", self.font_small)

        # Reset button
        self.reset_button = Button(174, btn_y, 114, btn_h, "Reset", self.font_small)

        # Speed slider (continuous 0.1x–4.0x range)
        self.speed_slider = Slider(
            0, 0, 180, min_val=0.1, max_val=4.0, initial_val=1.0, label="Speed:"
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

        # Custom array button (accent text to distinguish from size toggles)
        custom_w = self.font_small.size("Custom")[0] + 36
        self.custom_button = Button(
            0, btn_y + 1, custom_w, 48, "Custom", self.font_small,
            text_color=Colors.TEXT_ACCENT
        )

        # Array input modal
        self.array_modal = ArrayModal(WINDOW_WIDTH, WINDOW_HEIGHT)

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
            (Colors.BAR_PIVOT, "Pivot"),
        ])

        self.running = True

    def _rebuild_layout(self, w, h):
        """Recalculate all layout positions for the given window dimensions."""
        self.width = w
        self.height = h

        # Clamp derived dimensions so rects never go negative
        canvas_y = HEADER_HEIGHT
        canvas_h = max(1, h - HEADER_HEIGHT - CONTROL_PANEL_HEIGHT)
        canvas_w = max(1, w - INFO_PANEL_WIDTH)
        self.canvas_rect = pygame.Rect(0, canvas_y, canvas_w, canvas_h)

        # Update all visualizers
        for viz in self.visualizers.values():
            viz.set_canvas_rect(self.canvas_rect)

        # Info panel — flush right, clamped height
        self.info_panel.rect = pygame.Rect(
            max(0, w - INFO_PANEL_WIDTH), canvas_y,
            INFO_PANEL_WIDTH, canvas_h
        )

        # Tab bar
        self.tab_bar.resize(w)

        # Control bar — anchored relative to window bottom
        control_y = max(HEADER_HEIGHT, h - CONTROL_PANEL_HEIGHT)
        self.control_y = control_y
        btn_h = 51
        btn_y = control_y + (CONTROL_PANEL_HEIGHT - btn_h) // 2
        gap = 21
        x = 21

        # Reposition control bar components sequentially (x-accumulation)
        self.start_button.rect.topleft = (x, btn_y)
        x += self.start_button.rect.width + 9

        self.reset_button.rect.topleft = (x, btn_y)
        x += self.reset_button.rect.width + gap

        self.div1_x = x
        x += gap

        # Speed slider — label is auto-drawn by Slider to the left of track
        speed_label_w = self.font_small.size("Speed:")[0] + 14
        slider_x = x + speed_label_w
        slider_y = control_y + CONTROL_PANEL_HEIGHT // 2
        self.speed_slider.set_position(slider_x, slider_y, 180)
        x += speed_label_w + 180 + gap

        self.div2_x = x
        x += gap

        self.algo_group.set_position(x, btn_y + 1)
        algo_width = sum(b.rect.width for b in self.algo_group.buttons) + 5 * (len(self.algo_group.buttons) - 1)
        x += algo_width + gap

        self.div3_x = x
        x += gap

        self.size_group.set_position(x, btn_y + 1)
        size_width = sum(b.rect.width for b in self.size_group.buttons) + 5 * (len(self.size_group.buttons) - 1)
        x += size_width + 12

        # Custom button — positioned after size group
        self.custom_button.rect.topleft = (x, btn_y + 1)

        # Track right edge of control bar content for hint collision check
        self.control_content_right = self.custom_button.rect.right

        # Keep modal centered on resize
        self.array_modal.resize(w, h)

    def _update_info_panel(self):
        viz = self.visualizers.get("Sorting")
        if viz and hasattr(viz, "get_algorithm_info"):
            info = viz.get_algorithm_info()
            self.info_panel.set_algorithm_info(
                info["name"], info["time_best"], info["time_avg"],
                info["time_worst"], info["space"], info["stable"]
            )
            self.info_panel.set_pseudocode_state(
                viz.algorithm_key, getattr(viz, "current_op_type", "")
            )

    def get_active_visualizer(self):
        tab_name = self.tab_bar.get_active_tab()
        return self.visualizers[tab_name]

    def _open_custom_modal(self):
        """Pause if running and open the custom array modal."""
        viz = self.visualizers["Sorting"]
        if viz.is_running:
            viz.toggle()
        self.array_modal.open(
            viz.array_size,
            viz.custom_source_array if viz.has_custom_array else None,
            viz.has_custom_array
        )

    def _apply_custom_array(self, array):
        """Load a custom array and update size button state."""
        viz = self.visualizers["Sorting"]
        viz.set_custom_array(array)
        # Re-select matching size button, or deselect all
        custom_len = str(len(array))
        if custom_len in SIZE_OPTIONS:
            idx = SIZE_OPTIONS.index(custom_len)
            self.size_group.deselect_all()
            self.size_group.active_index = idx
            self.size_group.buttons[idx].is_active = True
        else:
            self.size_group.deselect_all()
        self._update_info_panel()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # Window resize always processed
            if event.type == pygame.VIDEORESIZE:
                self._rebuild_layout(event.w, event.h)
                continue

            # Modal consumes all other events when open
            if self.array_modal.is_open():
                result = self.array_modal.handle_event(event)
                if result:
                    if result["action"] == "apply":
                        self._apply_custom_array(result["array"])
                    self.array_modal.close()
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
                elif event.key == pygame.K_SPACE:
                    self.get_active_visualizer().toggle()
                elif event.key == pygame.K_r:
                    self.get_active_visualizer().reset()
                elif event.key == pygame.K_RIGHT:
                    viz = self.get_active_visualizer()
                    if not viz.is_running and hasattr(viz, 'step_forward'):
                        viz.step_forward()
                elif event.key == pygame.K_LEFT:
                    viz = self.get_active_visualizer()
                    if not viz.is_running and hasattr(viz, 'step_backward'):
                        viz.step_backward()
                elif event.key == pygame.K_c:
                    if self.tab_bar.get_active_tab() == "Sorting":
                        self._open_custom_modal()

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

            if self.custom_button.handle_event(event):
                if self.tab_bar.get_active_tab() == "Sorting":
                    self._open_custom_modal()

            viz.handle_event(event)

    def update(self):
        # Modal backspace repeat (must run every frame when modal is open)
        if self.array_modal.is_open():
            self.array_modal.update()

        viz = self.get_active_visualizer()
        if viz.is_running and not viz.is_complete:
            # Continuous speed: BASE_SPEED * slider multiplier
            multiplier = self.speed_slider.get_value()
            dt = self.clock.get_time() / 1000.0
            ops_per_second = BASE_SPEED * multiplier
            self.step_accumulator += ops_per_second * dt
            while self.step_accumulator >= 1.0 and viz.is_running and not viz.is_complete:
                self.step_accumulator -= 1.0
                if hasattr(viz, 'step_forward'):
                    viz.step_forward()
                else:
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

        # Pass pointer/array data for variables panel
        if hasattr(viz, "current_pointers"):
            self.info_panel.set_variables(viz.current_pointers, viz.array)

        # Pass pseudocode state (algorithm key + current op type)
        if hasattr(viz, "current_op_type"):
            self.info_panel.set_pseudocode_state(viz.algorithm_key, viz.current_op_type)

        # Update start button text (plain text, no unicode icons)
        if viz.is_running:
            self.start_button.text = "Pause"
        else:
            self.start_button.text = "Start"

    def _draw_divider(self, x):
        """Draw a subtle vertical divider in the control bar."""
        pygame.draw.line(
            self.screen, (50, 50, 65),
            (x, self.control_y + 24),
            (x, self.control_y + CONTROL_PANEL_HEIGHT - 24), 1
        )

    def draw(self):
        self.screen.fill(Colors.BG)

        # Header (brand + tabs)
        self.tab_bar.draw(self.screen)

        # Active visualizer
        self.get_active_visualizer().draw(self.screen)

        # Info panel
        self.info_panel.draw(self.screen)

        # Control bar background — extends from control_y to window bottom
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()
        control_rect = pygame.Rect(0, self.control_y, screen_w, screen_h - self.control_y)
        pygame.draw.rect(self.screen, Colors.PANEL_BG, control_rect)
        # Top border
        pygame.draw.line(
            self.screen, (40, 40, 55),
            (0, self.control_y), (screen_w, self.control_y), 1
        )

        # Control bar components
        self.start_button.draw(self.screen)
        self.reset_button.draw(self.screen)
        self._draw_divider(self.div1_x)
        # Speed slider (draws its own "Speed:" label)
        self.speed_slider.draw(self.screen, self.font_small)
        self._draw_divider(self.div2_x)
        self.algo_group.draw(self.screen)
        self._draw_divider(self.div3_x)
        self.size_group.draw(self.screen)
        self.custom_button.draw(self.screen)

        # Modal overlay (drawn last, on top of everything)
        self.array_modal.draw(self.screen)

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
