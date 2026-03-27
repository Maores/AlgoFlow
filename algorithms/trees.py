"""Tree node data structures for AlgoFlow Trees tab.

This module is the foundation for all tree algorithm visualizations.
It provides:
  - TreeNode: binary tree node with unique ids (used for step snapshots)
  - serialize_tree / deserialize_tree: for time-travel (step backward)
  - bst_from_values: build a BST by sequential insertion

No Pygame dependency — pure Python only.
"""

from __future__ import annotations
from collections import deque
from typing import List, Dict, Optional


class TreeNode:
    """A binary tree node with a value and a unique auto-assigned id.

    The id is assigned from a class-level counter so that each node
    created during a session has a stable identity.  serialize_tree /
    deserialize_tree rely on these ids to reconstruct parent-child
    links without storing direct object references.
    """

    _counter: int = 0

    def __init__(self, value: int) -> None:
        self.value: int = value
        self.id: int = TreeNode._counter
        TreeNode._counter += 1
        self.left: Optional[TreeNode] = None
        self.right: Optional[TreeNode] = None

    @classmethod
    def reset_counter(cls) -> None:
        """Reset the id counter to 0.

        Used before deterministic tests and before building a fresh tree
        so that node ids are reproducible.
        """
        cls._counter = 0


# ---------------------------------------------------------------------------
# Serialize / Deserialize
# ---------------------------------------------------------------------------

def serialize_tree(root: Optional[TreeNode]) -> List[Dict]:
    """Return a list-of-dicts representation of the tree.

    Each dict has the keys:
        id       (int)       — stable node identity
        value    (int)       — the node's stored value
        left_id  (int|None)  — id of left child, or None
        right_id (int|None)  — id of right child, or None

    Returns [] for an empty tree (root is None).
    Traversal order: BFS (level-order), so the root is always first.
    """
    if root is None:
        return []

    result: List[Dict] = []
    queue: deque[TreeNode] = deque([root])

    while queue:
        node = queue.popleft()
        result.append({
            "id": node.id,
            "value": node.value,
            "left_id": node.left.id if node.left is not None else None,
            "right_id": node.right.id if node.right is not None else None,
        })
        if node.left is not None:
            queue.append(node.left)
        if node.right is not None:
            queue.append(node.right)

    return result


def deserialize_tree(data: List[Dict]) -> Optional[TreeNode]:
    """Reconstruct a TreeNode tree from the list produced by serialize_tree.

    Restores the exact ids, values, and parent-child relationships.
    Returns None if data is empty.
    """
    if not data:
        return None

    # Validate that every entry has the required keys before processing.
    required_keys = {"id", "value", "left_id", "right_id"}
    for node_data in data:
        if not required_keys.issubset(node_data.keys()):
            missing = required_keys - node_data.keys()
            raise ValueError(f"Invalid snapshot entry — missing keys: {missing}")

    # Pass 1: create all nodes (without links), keyed by id.
    nodes: Dict[int, TreeNode] = {}
    for record in data:
        node = TreeNode.__new__(TreeNode)
        node.id = record["id"]
        node.value = record["value"]
        node.left = None
        node.right = None
        nodes[node.id] = node

    # Pass 2: wire up left/right pointers.
    for record in data:
        node = nodes[record["id"]]
        node.left = nodes[record["left_id"]] if record["left_id"] is not None else None
        node.right = nodes[record["right_id"]] if record["right_id"] is not None else None

    # The root is the first entry (serialize always puts root first via BFS).
    return nodes[data[0]["id"]]


# ---------------------------------------------------------------------------
# BST construction
# ---------------------------------------------------------------------------

def _bst_insert(root: TreeNode, value: int) -> None:
    """Insert value into the BST rooted at root (standard, no balancing)."""
    current = root
    while True:
        if value < current.value:
            if current.left is None:
                current.left = TreeNode(value)
                return
            current = current.left
        else:  # duplicates go right by convention
            if current.right is None:
                current.right = TreeNode(value)
                return
            current = current.right


def bst_from_values(values: List[int]) -> Optional[TreeNode]:
    """Build a BST by sequentially inserting each value.

    Uses standard BST insertion (no balancing).  Does NOT reset the
    TreeNode counter — relies on whatever the current counter state is.
    Returns None for an empty list.
    Duplicate values are inserted to the right subtree.
    """
    if not values:
        return None

    root = TreeNode(values[0])
    for value in values[1:]:
        _bst_insert(root, value)

    return root


# ---------------------------------------------------------------------------
# BST generator algorithms
# ---------------------------------------------------------------------------

def bst_insert(root: Optional[TreeNode], value: int):
    """Generator that yields step-by-step animation ops for BST insertion.

    Each yield is a 4-tuple: (op_type, node_id, message, data_dict).
    The generator mutates the tree in-place.  When inserting at root
    (root is None), the insert yield includes "new_root" in its data dict
    so the caller can update their own reference.

    Yield op_types:
        "compare"  — currently examining this node
        "insert"   — new node has been attached
        "done"     — operation finished
    """
    if root is None:
        new_node = TreeNode(value)
        yield (
            "insert",
            new_node.id,
            f"Insert {value}",
            {"tree_snapshot": serialize_tree(new_node), "new_root": new_node},
        )
        yield (
            "done",
            None,
            f"Inserted {value}",
            {"tree_snapshot": serialize_tree(new_node)},
        )
        return

    current = root
    parent = None
    went_left = None

    while current is not None:
        yield (
            "compare",
            current.id,
            f"Compare {value} with {current.value}",
            {"tree_snapshot": serialize_tree(root)},
        )
        parent = current
        if value < current.value:
            went_left = True
            current = current.left
        else:
            went_left = False
            current = current.right

    # Attach the new node to the parent.
    new_node = TreeNode(value)
    if went_left:
        parent.left = new_node
    else:
        parent.right = new_node

    yield (
        "insert",
        new_node.id,
        f"Insert {value}",
        {"tree_snapshot": serialize_tree(root)},
    )
    yield (
        "done",
        None,
        f"Inserted {value}",
        {"tree_snapshot": serialize_tree(root)},
    )


def bst_search(root: Optional[TreeNode], value: int):
    """Generator that yields step-by-step animation ops for BST search.

    Each yield is a 4-tuple: (op_type, node_id, message, data_dict).

    Yield op_types:
        "compare"   — currently examining this node
        "found"     — value exists at this node
        "not_found" — value is not in the tree
        "done"      — operation finished
    """
    if root is None:
        yield (
            "not_found",
            None,
            "Tree is empty",
            {"tree_snapshot": []},
        )
        yield (
            "done",
            None,
            "Search complete",
            {"tree_snapshot": []},
        )
        return

    current = root
    while current is not None:
        yield (
            "compare",
            current.id,
            f"Compare {value} with {current.value}",
            {"tree_snapshot": serialize_tree(root)},
        )
        if value == current.value:
            yield (
                "found",
                current.id,
                f"Found {value}",
                {"tree_snapshot": serialize_tree(root)},
            )
            yield (
                "done",
                current.id,
                "Search complete",
                {"tree_snapshot": serialize_tree(root)},
            )
            return
        elif value < current.value:
            current = current.left
        else:
            current = current.right

    yield (
        "not_found",
        None,
        f"{value} not in tree",
        {"tree_snapshot": serialize_tree(root)},
    )
    yield (
        "done",
        None,
        "Search complete",
        {"tree_snapshot": serialize_tree(root)},
    )


# ---------------------------------------------------------------------------
# Algorithm metadata
# ---------------------------------------------------------------------------

TREE_ALGORITHM_INFO = {
    "BST Insert": {
        "name": "BST Insert",
        "time_best": "O(log n)",
        "time_worst": "O(n)",
        "time_average": "O(log n)",
        "space": "O(h)",
        "description": "Insert value maintaining BST property",
    },
    "BST Delete": {
        "name": "BST Delete",
        "time_best": "O(log n)",
        "time_worst": "O(n)",
        "time_average": "O(log n)",
        "space": "O(h)",
        "description": "Remove value, restructure as needed",
    },
    "BST Search": {
        "name": "BST Search",
        "time_best": "O(1)",
        "time_worst": "O(n)",
        "time_average": "O(log n)",
        "space": "O(1)",
        "description": "Find value by comparing at each node",
    },
    "Inorder": {
        "name": "Inorder Traversal",
        "time_best": "O(n)",
        "time_worst": "O(n)",
        "time_average": "O(n)",
        "space": "O(h)",
        "description": "Left → Root → Right",
    },
    "Preorder": {
        "name": "Preorder Traversal",
        "time_best": "O(n)",
        "time_worst": "O(n)",
        "time_average": "O(n)",
        "space": "O(h)",
        "description": "Root → Left → Right",
    },
    "Postorder": {
        "name": "Postorder Traversal",
        "time_best": "O(n)",
        "time_worst": "O(n)",
        "time_average": "O(n)",
        "space": "O(h)",
        "description": "Left → Right → Root",
    },
    "Level-order": {
        "name": "Level-order Traversal",
        "time_best": "O(n)",
        "time_worst": "O(n)",
        "time_average": "O(n)",
        "space": "O(n)",
        "description": "Breadth-first, level by level",
    },
    "Heap Insert": {
        "name": "Heap Insert",
        "time_best": "O(1)",
        "time_worst": "O(log n)",
        "time_average": "O(log n)",
        "space": "O(1)",
        "description": "Append and sift up to restore heap",
    },
    "Heap Extract": {
        "name": "Heap Extract-Min",
        "time_best": "O(log n)",
        "time_worst": "O(log n)",
        "time_average": "O(log n)",
        "space": "O(1)",
        "description": "Remove min, sift down to restore heap",
    },
}
