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
    GRID_SIZE_OPTIONS, DEFAULT_GRID_SIZE,
    BASE_SPEED,
    Colors
)
from ui.tab_bar import TabBar
from ui.button import Button
from ui.button_group import ButtonGroup
from ui.slider import Slider
from ui.info_panel import InfoPanel
from ui.array_modal import ArrayModal
from ui.help_modal import HelpModal
from visualizers.sorting_viz import SortingVisualizer
from visualizers.pathfinding_viz import PathfindingVisualizer
from visualizers.tree_viz import TreeVisualizer
from algorithms.sorting import ALGORITHM_INFO
from ui.text_input import TextInput
from algorithms.trees import (
    bst_insert, bst_delete, bst_search,
    inorder_traversal, preorder_traversal, postorder_traversal, levelorder_traversal,
    heap_insert, heap_extract_min,
)
from algorithms.pseudocode import PSEUDOCODE


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

        # Track active tab for detecting tab switches
        self._active_tab = self.tab_bar.get_active_tab()

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

        # ==================== Sorting control bar widgets ====================

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

        # Help button — positioned by _rebuild_layout at far right of control bar
        help_w = self.font_small.size("Help")[0] + 36
        self.help_button = Button(0, btn_y, help_w, btn_h, "Help", self.font_small,
                                  text_color=Colors.TEXT_ACCENT)

        # Help modal
        self.help_modal = HelpModal(WINDOW_WIDTH, WINDOW_HEIGHT)

        # ==================== Pathfinding control bar widgets ====================

        self.pf_start_btn = Button(21, btn_y, 144, btn_h, "Start", self.font_small)
        self.pf_reset_btn = Button(174, btn_y, 114, btn_h, "Reset", self.font_small)

        self.pf_speed_slider = Slider(
            0, 0, 180, min_val=0.1, max_val=4.0, initial_val=1.0, label="Speed:"
        )

        self.pf_algo_group = ButtonGroup(
            0, btn_y + 1, ["BFS", "DFS"], self.font_small, active_index=0
        )

        pf_size_default_idx = GRID_SIZE_OPTIONS.index(DEFAULT_GRID_SIZE)
        self.pf_size_group = ButtonGroup(
            0, btn_y + 1, ["Small", "Medium", "Large"], self.font_small, active_index=pf_size_default_idx
        )

        self.pf_preset_group = ButtonGroup(
            0, btn_y + 1, ["Random", "Maze", "Spiral", "Bottle"],
            self.font_small, active_index=0
        )
        self.pf_preset_group.deselect_all()
        # Map short labels back to full preset keys
        self._preset_label_map = {
            "Random": "Random", "Maze": "Maze", "Spiral": "Spiral",
            "Bottle": "Bottleneck",
        }

        pf_help_w = self.font_small.size("Help")[0] + 36
        self.pf_help_btn = Button(0, btn_y, pf_help_w, btn_h, "Help", self.font_small,
                                  text_color=Colors.TEXT_ACCENT)

        self.pf_edit_mode_group = ButtonGroup(
            0, 0, ["Wall", "Start", "End"], self.font_small, active_index=0
        )

        # Clear grid button for pathfinding
        pf_clear_w = self.font_small.size("Clear")[0] + 36
        self.pf_clear_btn = Button(0, btn_y, pf_clear_w, btn_h, "Clear", self.font_small,
                                   text_color=Colors.TEXT_ACCENT)

        # Pathfinding divider positions (set by _rebuild_layout)
        self.pf_div1_x = 0
        self.pf_div2_x = 0
        self.pf_div3_x = 0
        self.pf_div4_x = 0

        # ==================== Trees control bar widgets ====================

        self.tree_start_btn = Button(21, btn_y, 144, btn_h, "Start", self.font_small)
        self.tree_reset_btn = Button(174, btn_y, 114, btn_h, "Reset", self.font_small)

        self.tree_speed_slider = Slider(
            0, 0, 180, min_val=0.1, max_val=4.0, initial_val=1.0, label="Speed:"
        )

        # Mode switcher: BST or Heap
        self.tree_mode_group = ButtonGroup(
            0, btn_y + 1, ["BST", "Heap"], self.font_small, active_index=0
        )

        # BST operations (shown in BST mode)
        self.tree_bst_algo_group = ButtonGroup(
            0, btn_y + 1, ["Insert", "Delete", "Search"], self.font_small, active_index=0
        )

        # Heap operations (shown in Heap mode)
        self.tree_heap_algo_group = ButtonGroup(
            0, btn_y + 1, ["Insert", "Extract"], self.font_small, active_index=0
        )

        # Traversals (BST mode only)
        self.tree_traversal_group = ButtonGroup(
            0, btn_y + 1, ["Inorder", "Preorder", "Postorder", "Level"], self.font_small, active_index=-1
        )
        self.tree_traversal_group.deselect_all()

        # Value input + Go button
        self.tree_input = TextInput((0, btn_y + 4, 72, btn_h - 8), placeholder="val")
        self.tree_go_btn = Button(0, btn_y, 66, btn_h, "Go", self.font_small)

        # Help button
        tree_help_w = self.font_small.size("Help")[0] + 36
        self.tree_help_btn = Button(0, btn_y, tree_help_w, btn_h, "Help", self.font_small,
                                    text_color=Colors.TEXT_ACCENT)

        # Tree divider positions
        self.tree_div1_x = 0
        self.tree_div2_x = 0
        self.tree_div3_x = 0
        self.tree_div4_x = 0

        # Arrow key repeat state
        self.arrow_held = None           # "right" or "left" or None
        self.arrow_timer = 0
        self.arrow_initial_delay = 300   # ms before repeat starts
        self.arrow_repeat_interval = 60  # ms between repeated steps
        self.arrow_repeating = False

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

        tab = self.tab_bar.get_active_tab()

        if tab == "Sorting":
            self._layout_sorting_controls(btn_y, gap, w)
        elif tab == "Pathfinding":
            self._layout_pathfinding_controls(btn_y, gap, w)
        elif tab == "Trees":
            self._layout_trees_controls(btn_y, gap, w)

        # Keep modals centered on resize
        self.array_modal.resize(w, h)
        self.help_modal.resize(w, h)

    def _layout_sorting_controls(self, btn_y, gap, w):
        """Position all sorting control bar widgets."""
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
        slider_y = self.control_y + CONTROL_PANEL_HEIGHT // 2
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

        # Help button — bottom-right corner, vertically centered in control bar
        help_right_margin = 14
        self.help_button.rect.topright = (
            w - help_right_margin,
            self.control_y + (CONTROL_PANEL_HEIGHT - self.help_button.rect.height) // 2
        )

    def _layout_pathfinding_controls(self, btn_y, gap, w):
        """Position all pathfinding control bar widgets."""
        x = 21

        self.pf_start_btn.rect.topleft = (x, btn_y)
        x += self.pf_start_btn.rect.width + 9

        self.pf_reset_btn.rect.topleft = (x, btn_y)
        x += self.pf_reset_btn.rect.width + gap

        self.pf_div1_x = x
        x += gap

        # Speed slider
        speed_label_w = self.font_small.size("Speed:")[0] + 14
        slider_x = x + speed_label_w
        slider_y = self.control_y + CONTROL_PANEL_HEIGHT // 2
        self.pf_speed_slider.set_position(slider_x, slider_y, 180)
        x += speed_label_w + 180 + gap

        self.pf_div2_x = x
        x += gap

        # Algo group
        self.pf_algo_group.set_position(x, btn_y + 1)
        algo_width = sum(b.rect.width for b in self.pf_algo_group.buttons) + 5 * (len(self.pf_algo_group.buttons) - 1)
        x += algo_width + gap

        self.pf_div3_x = x
        x += gap

        # Size group
        self.pf_size_group.set_position(x, btn_y + 1)
        size_width = sum(b.rect.width for b in self.pf_size_group.buttons) + 5 * (len(self.pf_size_group.buttons) - 1)
        x += size_width + gap

        self.pf_div4_x = x
        x += gap

        # Preset group
        self.pf_preset_group.set_position(x, btn_y + 1)
        preset_width = sum(b.rect.width for b in self.pf_preset_group.buttons) + 5 * (len(self.pf_preset_group.buttons) - 1)
        x += preset_width + 12

        # Clear button
        self.pf_clear_btn.rect.topleft = (x, btn_y)
        x += self.pf_clear_btn.rect.width + gap

        # Help button — right-anchored, but pushed right if content would overlap
        help_right_margin = 14
        help_w = self.pf_help_btn.rect.width
        ideal_right = w - help_right_margin
        min_right = x + help_w  # minimum to avoid overlap
        help_right = max(ideal_right, min_right)
        self.pf_help_btn.rect.topright = (
            help_right,
            self.control_y + (CONTROL_PANEL_HEIGHT - self.pf_help_btn.rect.height) // 2
        )

        # Edit mode group — just below the header bar, with label
        canvas_left = self.canvas_rect.x
        edit_label_w = self.font_small.size("Draw:")[0] + 8
        edit_x = canvas_left + 12 + edit_label_w
        edit_y = HEADER_HEIGHT + 4
        self.pf_edit_mode_group.set_position(edit_x, edit_y)
        self.pf_edit_label_pos = (canvas_left + 12, edit_y + 8)

    def _layout_trees_controls(self, btn_y, gap, w):
        """Position all tree control bar widgets."""
        x = 21
        tree_viz = self.visualizers["Trees"]

        self.tree_start_btn.rect.topleft = (x, btn_y)
        x += self.tree_start_btn.rect.width + 9

        self.tree_reset_btn.rect.topleft = (x, btn_y)
        x += self.tree_reset_btn.rect.width + gap

        self.tree_div1_x = x
        x += gap

        # Speed slider
        speed_label_w = self.font_small.size("Speed:")[0] + 14
        slider_x = x + speed_label_w
        slider_y = self.control_y + CONTROL_PANEL_HEIGHT // 2
        self.tree_speed_slider.set_position(slider_x, slider_y, 180)
        x += speed_label_w + 180 + gap

        self.tree_div2_x = x
        x += gap

        # Mode group (BST/Heap)
        self.tree_mode_group.set_position(x, btn_y + 1)
        mode_width = sum(b.rect.width for b in self.tree_mode_group.buttons) + 5 * (len(self.tree_mode_group.buttons) - 1)
        x += mode_width + gap

        self.tree_div3_x = x
        x += gap

        # Operation/algo group (depends on mode)
        if tree_viz.mode == "bst":
            self.tree_bst_algo_group.set_position(x, btn_y + 1)
            algo_width = sum(b.rect.width for b in self.tree_bst_algo_group.buttons) + 5 * (len(self.tree_bst_algo_group.buttons) - 1)
            x += algo_width + 12

            # Traversal group
            self.tree_traversal_group.set_position(x, btn_y + 1)
            trav_width = sum(b.rect.width for b in self.tree_traversal_group.buttons) + 5 * (len(self.tree_traversal_group.buttons) - 1)
            x += trav_width + gap
        else:
            self.tree_heap_algo_group.set_position(x, btn_y + 1)
            algo_width = sum(b.rect.width for b in self.tree_heap_algo_group.buttons) + 5 * (len(self.tree_heap_algo_group.buttons) - 1)
            x += algo_width + gap

        self.tree_div4_x = x
        x += gap

        # Value input + Go button
        self.tree_input.rect.topleft = (x, btn_y + 4)
        self.tree_input.rect.width = 72
        self.tree_input.rect.height = self.tree_go_btn.rect.height - 8
        x += 72 + 6
        self.tree_go_btn.rect.topleft = (x, btn_y)
        x += self.tree_go_btn.rect.width + gap

        # Help button — right-anchored
        help_right_margin = 14
        self.tree_help_btn.rect.topright = (
            w - help_right_margin,
            self.control_y + (CONTROL_PANEL_HEIGHT - self.tree_help_btn.rect.height) // 2
        )

    def _update_info_panel(self):
        tab = self.tab_bar.get_active_tab()
        viz = self.get_active_visualizer()
        if tab == "Sorting":
            if hasattr(viz, 'get_algorithm_info'):
                self.info_panel.set_algorithm_info(viz.get_algorithm_info())
            self.info_panel.set_pseudocode_state(
                viz.algorithm_key, getattr(viz, "current_op_type", "")
            )
        elif tab == "Pathfinding":
            if hasattr(viz, 'get_algorithm_info'):
                self.info_panel.set_algorithm_info(viz.get_algorithm_info())
            self.info_panel.set_stats({
                "tab": "pathfinding",
                "cells_explored": viz.cells_explored,
                "frontier_size": getattr(viz, 'frontier_size', 0),
                "path_length": viz.path_length,
                "status": viz.get_status() if hasattr(viz, 'get_status') else ""
            })
            self.info_panel.set_pseudocode_state(
                viz.algorithm_key, getattr(viz, 'current_op_type', '')
            )
        elif tab == "Trees":
            if hasattr(viz, 'get_algorithm_info'):
                self.info_panel.set_algorithm_info(viz.get_algorithm_info())
            self.info_panel.set_stats({
                "tab": "trees",
                "operations": viz.operations,
                "comparisons": viz.comparisons,
                "tree_size": viz.get_size(),
                "tree_height": viz.get_height(),
            })
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

    def _on_tab_switch(self, new_tab):
        """Handle tab switch — pause running algorithms, update legend/info/layout."""
        # Pause any running algorithm in the tab we're leaving
        old_tab = self._active_tab
        if old_tab in self.visualizers:
            old_viz = self.visualizers[old_tab]
            if old_viz.is_running:
                old_viz.is_running = False

        self._active_tab = new_tab
        self._rebuild_layout(self.width, self.height)
        self._update_info_panel()

        if new_tab == "Sorting":
            # Clear pathfinding variables so Legend is visible
            self.info_panel.set_variables({}, [])
            self.info_panel.set_legend([
                (Colors.BAR_DEFAULT, "Default"),
                (Colors.BAR_COMPARING, "Comparing"),
                (Colors.BAR_SWAPPING, "Swapping"),
                (Colors.BAR_SORTED, "Sorted"),
                (Colors.BAR_PIVOT, "Pivot"),
            ])
        elif new_tab == "Pathfinding":
            # Clear sorting variables so Legend is visible
            self.info_panel.set_variables({}, [])
            self.info_panel.set_legend([
                (Colors.GRID_START, "Start"),
                (Colors.GRID_END, "End"),
                (Colors.GRID_WALL, "Wall"),
                (Colors.GRID_FRONTIER, "Frontier"),
                (Colors.GRID_VISITED, "Visited"),
                (Colors.GRID_PATH, "Path"),
            ])
        elif new_tab == "Trees":
            self.info_panel.set_variables({}, [])
            self.info_panel.set_legend([
                (Colors.NODE_DEFAULT, "Default"),
                (Colors.NODE_COMPARING, "Comparing"),
                (Colors.NODE_HIGHLIGHT, "Highlight"),
                (Colors.NODE_FOUND, "Found"),
                (Colors.NODE_NOT_FOUND, "Not Found"),
                (Colors.NODE_SUCCESSOR, "Successor"),
                (Colors.NODE_VISITED, "Visited"),
            ])

    def _do_arrow_step(self):
        """Execute one arrow-key step in the held direction."""
        viz = self.get_active_visualizer()
        if viz.is_running:
            return
        if self.arrow_held == "right" and hasattr(viz, 'step_forward'):
            viz.step_forward()
        elif self.arrow_held == "left" and hasattr(viz, 'step_backward'):
            viz.step_backward()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # Window resize always processed
            if event.type == pygame.VIDEORESIZE:
                self._rebuild_layout(event.w, event.h)
                continue

            # Help modal consumes events when open
            if self.help_modal.is_open():
                result = self.help_modal.handle_event(event)
                if result and result["action"] == "close":
                    self.help_modal.close()
                continue

            # Array modal consumes all other events when open
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
                    self.arrow_held = "right"
                    self.arrow_timer = pygame.time.get_ticks()
                    self.arrow_repeating = False
                elif event.key == pygame.K_LEFT:
                    viz = self.get_active_visualizer()
                    if not viz.is_running and hasattr(viz, 'step_backward'):
                        viz.step_backward()
                    self.arrow_held = "left"
                    self.arrow_timer = pygame.time.get_ticks()
                    self.arrow_repeating = False
                elif event.key == pygame.K_c:
                    if self.tab_bar.get_active_tab() == "Sorting":
                        self._open_custom_modal()
                elif event.key == pygame.K_h:
                    self.help_modal.open(tab=self.tab_bar.get_active_tab())

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_RIGHT, pygame.K_LEFT):
                    self.arrow_held = None
                    self.arrow_repeating = False

            # Tab bar — detect tab switches
            tab_changed = self.tab_bar.handle_event(event)
            if tab_changed:
                new_tab = self.tab_bar.get_active_tab()
                self._on_tab_switch(new_tab)

            tab = self.tab_bar.get_active_tab()
            viz = self.get_active_visualizer()

            if tab == "Sorting":
                # --- Sorting control bar events ---
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
                    self._open_custom_modal()

                if self.help_button.handle_event(event):
                    self.help_modal.open(tab="Sorting")

            elif tab == "Pathfinding":
                # --- Pathfinding control bar events ---
                if self.pf_start_btn.handle_event(event):
                    viz.toggle()

                if self.pf_reset_btn.handle_event(event):
                    viz.reset()

                self.pf_speed_slider.handle_event(event)

                algo_change = self.pf_algo_group.handle_event(event)
                if algo_change and hasattr(viz, "set_algorithm"):
                    viz.set_algorithm(algo_change)
                    self._update_info_panel()

                size_change = self.pf_size_group.handle_event(event)
                if size_change and hasattr(viz, "set_grid_size"):
                    viz.set_grid_size(size_change)

                preset_change = self.pf_preset_group.handle_event(event)
                if preset_change:
                    if hasattr(viz, "load_preset"):
                        preset_key = self._preset_label_map.get(preset_change, preset_change)
                        viz.load_preset(preset_key)

                if self.pf_clear_btn.handle_event(event):
                    viz.clear_grid()

                edit_change = self.pf_edit_mode_group.handle_event(event)
                if edit_change:
                    viz.edit_mode = edit_change.lower()

                if self.pf_help_btn.handle_event(event):
                    self.help_modal.open(tab="Pathfinding")

                # Only forward mouse events to the visualizer if they are
                # outside the edit toolbar area (prevents accidental wall
                # placement when clicking Wall/Start/End buttons).
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                    toolbar_btns = self.pf_edit_mode_group.buttons
                    if toolbar_btns and any(b.rect.collidepoint(event.pos) for b in toolbar_btns):
                        continue  # skip viz.handle_event for this event
                viz.handle_event(event)
                continue

            elif tab == "Trees":
                tree_viz = viz

                if self.tree_start_btn.handle_event(event):
                    tree_viz.toggle()

                if self.tree_reset_btn.handle_event(event):
                    tree_viz.reset()

                self.tree_speed_slider.handle_event(event)

                mode_change = self.tree_mode_group.handle_event(event)
                if mode_change:
                    new_mode = mode_change.lower()
                    tree_viz.set_mode(new_mode)
                    self._rebuild_layout(self.width, self.height)
                    self._update_info_panel()

                if tree_viz.mode == "bst":
                    algo_change = self.tree_bst_algo_group.handle_event(event)
                    if algo_change:
                        algo_map = {"Insert": "BST Insert", "Delete": "BST Delete", "Search": "BST Search"}
                        tree_viz.set_algorithm(algo_map.get(algo_change, algo_change))
                        self.tree_traversal_group.deselect_all()
                        self._update_info_panel()

                    trav_change = self.tree_traversal_group.handle_event(event)
                    if trav_change:
                        trav_map = {"Inorder": "Inorder", "Preorder": "Preorder",
                                    "Postorder": "Postorder", "Level": "Level-order"}
                        tree_viz.set_algorithm(trav_map.get(trav_change, trav_change))
                        self.tree_bst_algo_group.deselect_all()
                        self._update_info_panel()
                else:
                    algo_change = self.tree_heap_algo_group.handle_event(event)
                    if algo_change:
                        algo_map = {"Insert": "Heap Insert", "Extract": "Heap Extract"}
                        tree_viz.set_algorithm(algo_map.get(algo_change, algo_change))
                        self._update_info_panel()

                if self.tree_go_btn.handle_event(event):
                    self._execute_tree_operation()

                # Enter key also triggers Go
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if self.tree_input.focused:
                        self._execute_tree_operation()

                self.tree_input.handle_event(event)

                if self.tree_help_btn.handle_event(event):
                    self.help_modal.open(tab="Trees")

                tree_viz.handle_event(event)
                continue

            viz.handle_event(event)

    def _execute_tree_operation(self):
        """Create and set the appropriate tree generator based on current algorithm."""
        tree_viz = self.visualizers["Trees"]
        algo = tree_viz.algorithm_key

        # Traversals don't need a value input
        if algo in ("Inorder", "Preorder", "Postorder", "Level-order"):
            gen_map = {
                "Inorder": inorder_traversal,
                "Preorder": preorder_traversal,
                "Postorder": postorder_traversal,
                "Level-order": levelorder_traversal,
            }
            gen = gen_map[algo](tree_viz.bst_root)
            tree_viz.set_generator(gen)
            tree_viz.is_running = True
            self._update_info_panel()
            return

        # Heap Extract doesn't need a value
        if tree_viz.mode == "heap" and algo == "Heap Extract":
            gen = heap_extract_min(tree_viz.heap_array)
            tree_viz.set_generator(gen)
            tree_viz.is_running = True
            self._update_info_panel()
            return

        # Operations that need a value
        val = self.tree_input.get_int_value()
        if val is None:
            return

        if tree_viz.mode == "bst":
            if algo == "BST Insert":
                if tree_viz.get_height() >= tree_viz.MAX_BST_DEPTH:
                    tree_viz.current_status = f"Max depth ({tree_viz.MAX_BST_DEPTH}) reached"
                    return
                gen = bst_insert(tree_viz.bst_root, val)
            elif algo == "BST Delete":
                gen = bst_delete(tree_viz.bst_root, val)
            elif algo == "BST Search":
                gen = bst_search(tree_viz.bst_root, val)
            else:
                return
        else:
            if algo == "Heap Insert":
                gen = heap_insert(tree_viz.heap_array, val)
            else:
                return

        tree_viz.set_generator(gen)
        tree_viz.is_running = True
        self.tree_input.clear()
        self._update_info_panel()

    def update(self):
        # Continuous arrow key stepping
        if self.arrow_held and not self.array_modal.is_open() and not self.help_modal.is_open():
            viz = self.get_active_visualizer()
            if not viz.is_running:
                now = pygame.time.get_ticks()
                elapsed = now - self.arrow_timer
                if not self.arrow_repeating:
                    if elapsed >= self.arrow_initial_delay:
                        self.arrow_repeating = True
                        self.arrow_timer = now
                        self._do_arrow_step()
                else:
                    if elapsed >= self.arrow_repeat_interval:
                        self.arrow_timer = now
                        self._do_arrow_step()

        # Modal backspace repeat (must run every frame when modal is open)
        if self.array_modal.is_open():
            self.array_modal.update()

        tab = self.tab_bar.get_active_tab()
        viz = self.get_active_visualizer()

        if viz.is_running and not viz.is_complete:
            # Use the correct speed slider depending on active tab
            if tab == "Pathfinding":
                multiplier = self.pf_speed_slider.get_value()
            elif tab == "Trees":
                multiplier = self.tree_speed_slider.get_value()
            else:
                multiplier = self.speed_slider.get_value()

            # Continuous speed: BASE_SPEED * slider multiplier
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

        # Update info panel stats — tab-aware
        if tab == "Sorting":
            if hasattr(viz, "get_status"):
                self.info_panel.set_stats({
                    "tab": "sorting",
                    "comparisons": getattr(viz, "comparisons", 0),
                    "swaps": getattr(viz, "swaps", 0),
                    "status": viz.get_status() if hasattr(viz, "get_status") else "",
                })

            # Pass pointer/array data for variables panel
            if hasattr(viz, "current_pointers"):
                self.info_panel.set_variables(viz.current_pointers, viz.array)

        elif tab == "Pathfinding":
            self.info_panel.set_stats({
                "tab": "pathfinding",
                "cells_explored": viz.cells_explored,
                "frontier_size": getattr(viz, 'frontier_size', 0),
                "path_length": viz.path_length,
                "status": viz.get_status() if hasattr(viz, 'get_status') else ""
            })

        elif tab == "Trees":
            self.info_panel.set_stats({
                "tab": "trees",
                "operations": viz.operations,
                "comparisons": viz.comparisons,
                "tree_size": viz.get_size(),
                "tree_height": viz.get_height(),
            })
            # Update text input cursor blink
            self.tree_input.update(self.clock.get_time())

        # Pass pseudocode state (algorithm key + current op type)
        if hasattr(viz, "current_op_type"):
            self.info_panel.set_pseudocode_state(viz.algorithm_key, viz.current_op_type)

        # Update start button text (plain text, no unicode icons)
        if tab == "Sorting":
            self.start_button.text = "Pause" if viz.is_running else "Start"
        elif tab == "Pathfinding":
            self.pf_start_btn.text = "Pause" if viz.is_running else "Start"
        elif tab == "Trees":
            self.tree_start_btn.text = "Pause" if viz.is_running else "Start"



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

        tab = self.tab_bar.get_active_tab()

        if tab == "Sorting":
            # Sorting control bar components
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
            self.help_button.draw(self.screen)

        elif tab == "Pathfinding":
            # Pathfinding control bar components
            self.pf_start_btn.draw(self.screen)
            self.pf_reset_btn.draw(self.screen)
            self._draw_divider(self.pf_div1_x)
            self.pf_speed_slider.draw(self.screen, self.font_small)
            self._draw_divider(self.pf_div2_x)
            self.pf_algo_group.draw(self.screen)
            self._draw_divider(self.pf_div3_x)
            self.pf_size_group.draw(self.screen)
            self._draw_divider(self.pf_div4_x)
            self.pf_preset_group.draw(self.screen)
            self.pf_clear_btn.draw(self.screen)
            self.pf_help_btn.draw(self.screen)
            # Edit mode toolbar above the canvas (with label)
            label_surf = self.font_small.render("Draw:", True, Colors.TEXT_SECONDARY)
            self.screen.blit(label_surf, self.pf_edit_label_pos)
            self.pf_edit_mode_group.draw(self.screen)

        elif tab == "Trees":
            tree_viz = self.visualizers["Trees"]
            self.tree_start_btn.draw(self.screen)
            self.tree_reset_btn.draw(self.screen)
            self._draw_divider(self.tree_div1_x)
            self.tree_speed_slider.draw(self.screen, self.font_small)
            self._draw_divider(self.tree_div2_x)
            self.tree_mode_group.draw(self.screen)
            self._draw_divider(self.tree_div3_x)
            if tree_viz.mode == "bst":
                self.tree_bst_algo_group.draw(self.screen)
                self.tree_traversal_group.draw(self.screen)
            else:
                self.tree_heap_algo_group.draw(self.screen)
            self._draw_divider(self.tree_div4_x)
            self.tree_input.draw(self.screen)
            self.tree_go_btn.draw(self.screen)
            self.tree_help_btn.draw(self.screen)

        # Modal overlays (drawn last, on top of everything)
        self.array_modal.draw(self.screen)
        self.help_modal.draw(self.screen)

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
