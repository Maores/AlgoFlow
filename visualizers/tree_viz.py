# visualizers/tree_viz.py - Tree visualizer with BST and Heap layout engines
import math
import pygame
from visualizers.base import BaseVisualizer
from config import (
    Colors, FONT_FAMILY,
    TREE_NODE_RADIUS, TREE_LEVEL_GAP, TREE_MIN_H_SPACING,
    TREE_EDGE_WIDTH, HEAP_STRIP_HEIGHT, DEFAULT_BST_VALUES,
)
from algorithms.trees import (
    TreeNode, serialize_tree, deserialize_tree,
    bst_from_values, TREE_ALGORITHM_INFO,
)
from algorithms.pseudocode import PSEUDOCODE


class TreeVisualizer(BaseVisualizer):
    """Visualizer for BST and Heap algorithms with time-travel support."""

    def __init__(self, canvas_rect):
        super().__init__(canvas_rect)

        # Fonts
        self.font_node = pygame.font.SysFont(FONT_FAMILY, 18, bold=True)
        self.font_index = pygame.font.SysFont(FONT_FAMILY, 14)
        self.font_strip = pygame.font.SysFont(FONT_FAMILY, 16, bold=True)
        self.font_strip_idx = pygame.font.SysFont(FONT_FAMILY, 12)

        # Mode: "bst" or "heap"
        self.mode = "bst"

        # BST state
        self.bst_root = None

        # Heap state
        self.heap_array = []

        # Shared visualization state
        self.node_colors = {}
        self.generator = None
        self.algorithm_key = "BST Insert"

        # Counters
        self.operations = 0
        self.comparisons = 0

        # Time-travel history
        self.history = []
        self.history_pos = -1

        # Status
        self.current_op_type = ""
        self.current_status = ""
        self.highlighted_lines = []

        self.reset()

    def reset(self):
        if self.mode == "bst":
            TreeNode.reset_counter()
            self.bst_root = bst_from_values(DEFAULT_BST_VALUES)
            self._reset_bst_colors()
        else:
            self.heap_array = []
            self.node_colors = {}

        self.generator = None
        self.history = []
        self.history_pos = -1
        self.operations = 0
        self.comparisons = 0
        self.is_running = False
        self.is_complete = False
        self.current_status = ""
        self.current_op_type = ""
        self.highlighted_lines = []

    def step(self):
        self.step_forward()

    def step_forward(self):
        if self.history_pos < len(self.history) - 1:
            self.history_pos += 1
            self._restore_snapshot(self.history[self.history_pos])
        elif self.generator is not None:
            try:
                op = next(self.generator)
                self._apply_operation(op)
                snap = self._take_snapshot()
                self.history.append(snap)
                self.history_pos = len(self.history) - 1
            except StopIteration:
                self.is_complete = True
                self.is_running = False

    def step_backward(self):
        if self.history_pos > 0:
            self.history_pos -= 1
            self._restore_snapshot(self.history[self.history_pos])
            self.is_complete = False

    def _apply_operation(self, op):
        op_type, target, msg, data = op

        # Reset colors to defaults first
        if self.mode == "bst":
            self._reset_bst_colors()
        else:
            self.node_colors = {}

        if self.mode == "bst":
            if op_type == "compare":
                if target is not None:
                    self.node_colors[target] = Colors.NODE_COMPARING
                self.comparisons += 1
            elif op_type == "insert":
                if target is not None:
                    self.node_colors[target] = Colors.NODE_FOUND
                if "new_root" in data:
                    self.bst_root = data["new_root"]
                self.operations += 1
            elif op_type == "highlight":
                if target is not None:
                    self.node_colors[target] = Colors.NODE_HIGHLIGHT
            elif op_type == "successor":
                if target is not None:
                    self.node_colors[target] = Colors.NODE_SUCCESSOR
            elif op_type == "copy":
                if target is not None:
                    self.node_colors[target] = Colors.NODE_HIGHLIGHT
                if "tree_snapshot" in data:
                    self.bst_root = deserialize_tree(data["tree_snapshot"])
            elif op_type == "remove":
                self.operations += 1
                if "new_root" in data:
                    self.bst_root = data["new_root"]
                elif "tree_snapshot" in data:
                    self.bst_root = deserialize_tree(data["tree_snapshot"])
            elif op_type == "found":
                if target is not None:
                    self.node_colors[target] = Colors.NODE_FOUND
                self.operations += 1
            elif op_type == "not_found":
                self.operations += 1
            elif op_type == "visit":
                if target is not None:
                    self.node_colors[target] = Colors.NODE_VISITED
            elif op_type == "done":
                self.is_complete = True
                self.is_running = False
        else:
            # Heap mode
            if "heap_array" in data:
                self.heap_array = list(data["heap_array"])

            if op_type == "compare":
                if target is not None:
                    self.node_colors[target] = Colors.NODE_COMPARING
                self.comparisons += 1
            elif op_type == "swap":
                if target is not None:
                    self.node_colors[target] = Colors.NODE_HIGHLIGHT
                self.operations += 1
            elif op_type == "error":
                pass
            elif op_type == "done":
                self.is_complete = True
                self.is_running = False

        self.current_op_type = op_type
        self.current_status = msg

        # Update highlighted pseudocode lines
        if self.algorithm_key in PSEUDOCODE:
            highlight_map = PSEUDOCODE[self.algorithm_key].get("highlight_map", {})
            self.highlighted_lines = list(highlight_map.get(op_type, []))
        else:
            self.highlighted_lines = []

    def _take_snapshot(self):
        return {
            "bst_root": serialize_tree(self.bst_root),
            "heap_array": list(self.heap_array),
            "node_colors": dict(self.node_colors),
            "operations": self.operations,
            "comparisons": self.comparisons,
            "current_status": self.current_status,
            "current_op_type": self.current_op_type,
            "highlighted_lines": list(self.highlighted_lines),
            "mode": self.mode,
        }

    def _restore_snapshot(self, snap):
        self.bst_root = deserialize_tree(snap["bst_root"])
        self.heap_array = list(snap["heap_array"])
        self.node_colors = dict(snap["node_colors"])
        self.operations = snap["operations"]
        self.comparisons = snap["comparisons"]
        self.current_status = snap["current_status"]
        self.current_op_type = snap["current_op_type"]
        self.highlighted_lines = list(snap["highlighted_lines"])

    # ------------------------------------------------------------------
    # BST Layout Engine
    # ------------------------------------------------------------------

    def _subtree_width(self, node):
        if node is None:
            return 0
        left_w = self._subtree_width(node.left)
        right_w = self._subtree_width(node.right)
        return max(left_w + right_w, TREE_NODE_RADIUS * 2)

    def _assign_positions(self, node, left_bound, depth, positions):
        if node is None:
            return
        left_w = self._subtree_width(node.left)
        x = left_bound + max(left_w, TREE_NODE_RADIUS)
        y = depth * TREE_LEVEL_GAP + TREE_NODE_RADIUS + 10
        positions[node.id] = (x, y)
        self._assign_positions(node.left, left_bound, depth + 1, positions)
        right_start = left_bound + left_w + TREE_MIN_H_SPACING
        self._assign_positions(node.right, right_start, depth + 1, positions)

    def _compute_bst_layout(self, root, canvas_rect):
        if root is None:
            return {}
        positions = {}
        self._assign_positions(root, 0, 0, positions)
        if not positions:
            return {}
        xs = [p[0] for p in positions.values()]
        ys = [p[1] for p in positions.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        tree_w = max(max_x - min_x, 1)
        tree_h = max(max_y - min_y, 1)
        scale_x = (canvas_rect.width - 60) / tree_w if tree_w > 0 else 1
        scale_y = (canvas_rect.height - 60) / tree_h if tree_h > 0 else 1
        scale = min(scale_x, scale_y, 1.5)
        offset_x = canvas_rect.x + (canvas_rect.width - tree_w * scale) / 2
        offset_y = canvas_rect.y + 30
        return {
            nid: (int(offset_x + (x - min_x) * scale), int(offset_y + (y - min_y) * scale))
            for nid, (x, y) in positions.items()
        }

    # ------------------------------------------------------------------
    # Heap Layout Engine
    # ------------------------------------------------------------------

    def _compute_heap_layout(self, heap_array, canvas_rect):
        positions = {}
        for i in range(len(heap_array)):
            depth = math.floor(math.log2(i + 1))
            pos_in_level = i - (2 ** depth - 1)
            nodes_in_level = 2 ** depth
            x = canvas_rect.x + int((pos_in_level + 0.5) * canvas_rect.width / nodes_in_level)
            y = canvas_rect.y + 30 + depth * TREE_LEVEL_GAP
            positions[i] = (x, y)
        return positions

    def _draw_heap_strip(self, surface, strip_rect):
        n = len(self.heap_array)
        if n == 0:
            return
        box_w = min(50, max(20, (strip_rect.width - 20) // n))
        total_w = n * box_w
        start_x = strip_rect.x + (strip_rect.width - total_w) // 2
        y = strip_rect.y + 5
        box_h = strip_rect.height - 20
        for i, val in enumerate(self.heap_array):
            x = start_x + i * box_w
            color = self.node_colors.get(i, Colors.NODE_DEFAULT)
            rect = pygame.Rect(x, y, box_w - 2, box_h)
            pygame.draw.rect(surface, color, rect, border_radius=4)
            pygame.draw.rect(surface, Colors.EDGE_COLOR, rect, width=1, border_radius=4)
            val_surf = self.font_strip.render(str(val), True, Colors.TEXT_PRIMARY)
            surface.blit(val_surf, val_surf.get_rect(center=rect.center))
            idx_surf = self.font_strip_idx.render(str(i), True, Colors.TEXT_SECONDARY)
            surface.blit(idx_surf, idx_surf.get_rect(centerx=rect.centerx, top=rect.bottom + 2))

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _collect_nodes(self, node):
        """Collect all nodes as list of (node_id, value, left_id, right_id)."""
        if node is None:
            return []
        result = []
        stack = [node]
        while stack:
            n = stack.pop()
            left_id = n.left.id if n.left else None
            right_id = n.right.id if n.right else None
            result.append((n.id, n.value, left_id, right_id))
            if n.right:
                stack.append(n.right)
            if n.left:
                stack.append(n.left)
        return result

    def draw(self, surface):
        if self.mode == "bst":
            self._draw_bst(surface)
        else:
            self._draw_heap(surface)

    def _draw_bst(self, surface):
        if self.bst_root is None:
            return
        positions = self._compute_bst_layout(self.bst_root, self.canvas_rect)
        if not positions:
            return
        nodes = self._collect_nodes(self.bst_root)

        # Draw edges
        for nid, val, left_id, right_id in nodes:
            if nid not in positions:
                continue
            px, py = positions[nid]
            if left_id is not None and left_id in positions:
                cx, cy = positions[left_id]
                pygame.draw.line(surface, Colors.EDGE_COLOR, (px, py), (cx, cy), TREE_EDGE_WIDTH)
            if right_id is not None and right_id in positions:
                cx, cy = positions[right_id]
                pygame.draw.line(surface, Colors.EDGE_COLOR, (px, py), (cx, cy), TREE_EDGE_WIDTH)

        # Draw nodes
        for nid, val, left_id, right_id in nodes:
            if nid not in positions:
                continue
            x, y = positions[nid]
            color = self.node_colors.get(nid, Colors.NODE_DEFAULT)
            pygame.draw.circle(surface, color, (x, y), TREE_NODE_RADIUS)
            val_surf = self.font_node.render(str(val), True, Colors.TEXT_PRIMARY)
            surface.blit(val_surf, val_surf.get_rect(center=(x, y)))

    def _draw_heap(self, surface):
        if not self.heap_array:
            return
        shrunk = pygame.Rect(
            self.canvas_rect.x, self.canvas_rect.y,
            self.canvas_rect.width, self.canvas_rect.height - HEAP_STRIP_HEIGHT
        )
        positions = self._compute_heap_layout(self.heap_array, shrunk)

        # Draw edges
        for i in range(1, len(self.heap_array)):
            parent = (i - 1) // 2
            if parent in positions and i in positions:
                pygame.draw.line(
                    surface, Colors.EDGE_COLOR,
                    positions[parent], positions[i], TREE_EDGE_WIDTH
                )

        # Draw nodes
        for i, val in enumerate(self.heap_array):
            if i not in positions:
                continue
            x, y = positions[i]
            color = self.node_colors.get(i, Colors.NODE_DEFAULT)
            pygame.draw.circle(surface, color, (x, y), TREE_NODE_RADIUS)
            val_surf = self.font_node.render(str(val), True, Colors.TEXT_PRIMARY)
            surface.blit(val_surf, val_surf.get_rect(center=(x, y)))

        # Draw array strip
        strip_rect = pygame.Rect(
            self.canvas_rect.x,
            self.canvas_rect.y + self.canvas_rect.height - HEAP_STRIP_HEIGHT,
            self.canvas_rect.width,
            HEAP_STRIP_HEIGHT
        )
        self._draw_heap_strip(surface, strip_rect)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_algorithm_info(self):
        return TREE_ALGORITHM_INFO.get(self.algorithm_key, {})

    def get_status(self):
        if self.is_complete:
            return "Complete"
        if self.current_status:
            return self.current_status
        if self.is_running:
            return "Running"
        return "Ready"

    def set_algorithm(self, key):
        self.algorithm_key = key

    def set_mode(self, mode):
        if mode != self.mode:
            self.mode = mode
            self.reset()

    def set_generator(self, gen):
        if self.generator is not None:
            self.history = []
            self.history_pos = -1
            self.operations = 0
            self.comparisons = 0
            self.is_complete = False
            self.current_status = ""
            self.current_op_type = ""
            self.highlighted_lines = []
        if self.mode == "bst":
            self._reset_bst_colors()
        else:
            self.node_colors = {}
        self.generator = gen

    def get_size(self):
        if self.mode == "bst":
            return self._count_nodes(self.bst_root)
        return len(self.heap_array)

    def get_height(self):
        if self.mode == "bst":
            return self._tree_height(self.bst_root)
        if not self.heap_array:
            return 0
        return math.floor(math.log2(len(self.heap_array))) + 1

    def handle_event(self, event):
        pass

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _count_nodes(self, node):
        if node is None:
            return 0
        return 1 + self._count_nodes(node.left) + self._count_nodes(node.right)

    def _tree_height(self, node):
        if node is None:
            return 0
        return 1 + max(self._tree_height(node.left), self._tree_height(node.right))

    def _reset_bst_colors(self):
        self.node_colors = {}
        if self.bst_root is None:
            return
        stack = [self.bst_root]
        while stack:
            n = stack.pop()
            self.node_colors[n.id] = Colors.NODE_DEFAULT
            if n.left:
                stack.append(n.left)
            if n.right:
                stack.append(n.right)
