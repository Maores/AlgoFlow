"""Tree node data structures and BST generator algorithms for AlgoFlow Trees tab.

This module is the foundation for all tree algorithm visualizations.
It provides:
  - TreeNode: binary tree node with unique ids (used for step snapshots)
  - serialize_tree / deserialize_tree: for time-travel (step backward)
  - bst_from_values: build a BST by sequential insertion
  - bst_insert: step-by-step BST insertion generator
  - bst_delete: step-by-step BST deletion generator (leaf/one-child/two-children)
  - bst_search: step-by-step BST search generator
  - TREE_ALGORITHM_INFO: metadata dict for all supported tree algorithms

No Pygame dependency — pure Python only.
"""

from __future__ import annotations
from collections import deque
from typing import Generator, Optional, Dict, Any, List, Tuple


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

def bst_insert(root: Optional[TreeNode], value: int) -> Generator[Tuple[str, Optional[int], str, Dict[str, Any]], None, None]:
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


def bst_delete(root: Optional[TreeNode], value: int) -> Generator[Tuple[str, Optional[int], str, Dict[str, Any]], None, None]:
    """Generator that yields step-by-step animation ops for BST deletion.

    Each yield is a 4-tuple: (op_type, node_id, message, data_dict).
    The generator mutates the tree in-place.

    Yield op_types:
        "compare"   — currently examining this node during search phase
        "highlight" — found the target node (before any mutation)
        "successor" — in-order successor identified (two-children case)
        "copy"      — successor's value has been copied to target node
        "remove"    — node has been physically removed / replaced
        "not_found" — value is not in the tree
        "done"      — operation finished

    Special data keys:
        "new_root"  — present in "remove" yield when the root itself is
                      removed or replaced; value is the new root node or None.
    """
    # --- Empty tree ----------------------------------------------------------
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
            f"Delete {value} complete",
            {"tree_snapshot": []},
        )
        return

    # --- Walk down the tree, tracking parent --------------------------------
    current: Optional[TreeNode] = root
    parent: Optional[TreeNode] = None
    went_left: Optional[bool] = None  # which side of parent we're on

    while current is not None:
        yield (
            "compare",
            current.id,
            f"Compare {value} with {current.value}",
            {"tree_snapshot": serialize_tree(root)},
        )
        if value == current.value:
            break
        parent = current
        if value < current.value:
            went_left = True
            current = current.left
        else:
            went_left = False
            current = current.right
    else:
        # Loop finished without a break → value not found
        yield (
            "not_found",
            None,
            f"{value} not in tree",
            {"tree_snapshot": serialize_tree(root)},
        )
        yield (
            "done",
            None,
            f"Delete {value} complete",
            {"tree_snapshot": serialize_tree(root)},
        )
        return

    # --- current is the node to delete --------------------------------------
    target = current

    # ---- CASE: TWO CHILDREN ------------------------------------------------
    if target.left is not None and target.right is not None:
        # Step 1: highlight the target
        yield (
            "highlight",
            target.id,
            f"Found {value} — two children",
            {"tree_snapshot": serialize_tree(root)},
        )

        # Find in-order successor: go right once, then leftmost
        succ_parent: TreeNode = target
        # Safe: target.right is guaranteed non-None by two-children guard above
        successor: TreeNode = target.right
        while successor.left is not None:
            succ_parent = successor
            successor = successor.left

        # Step 2: identify the successor (tree still unchanged)
        yield (
            "successor",
            successor.id,
            f"Found in-order successor: {successor.value}",
            {"tree_snapshot": serialize_tree(root)},
        )

        # Copy successor value into target
        target.value = successor.value

        # Step 3: snapshot after copy (target shows new value)
        yield (
            "copy",
            target.id,
            f"Copied {successor.value} to node",
            {"tree_snapshot": serialize_tree(root)},
        )

        # Now delete the successor node (has at most a right child)
        successor_id = successor.id
        # The successor's only possible child is its right child
        successor_child = successor.right
        if succ_parent is target:
            # Successor was target.right itself (no left subtree under right)
            succ_parent.right = successor_child
        else:
            succ_parent.left = successor_child

        # Step 4: snapshot after successor removal
        yield (
            "remove",
            successor_id,
            "Removed successor",
            {"tree_snapshot": serialize_tree(root)},
        )
        yield (
            "done",
            None,
            f"Deleted {value}",
            {"tree_snapshot": serialize_tree(root)},
        )
        return

    # ---- CASE: LEAF (no children) or ONE CHILD ----------------------------
    # Determine the replacement child (None for leaf, the existing child otherwise)
    if target.left is None and target.right is None:
        case_label = "leaf node"
        child = None
    elif target.left is not None:
        case_label = "one child"
        child = target.left
    else:
        case_label = "one child"
        child = target.right

    yield (
        "highlight",
        target.id,
        f"Found {value} — {case_label}",
        {"tree_snapshot": serialize_tree(root)},
    )

    # Perform the removal / replacement
    target_id = target.id
    is_root = (parent is None)

    if is_root:
        # Removing/replacing the root: splice child into root position
        # We cannot reassign the root variable here, so we signal via new_root.
        # The mutation itself (replacing the root) is communicated to the caller
        # via "new_root" in the remove yield's data dict.
        remove_msg = (
            f"Removed {value}"
            if child is None
            else f"Replaced {value} with child"
        )
        # Physically update the root in-place when it has one child:
        # copy child's data into root so the caller's reference stays valid,
        # OR rely on the caller to use new_root.
        yield (
            "remove",
            target_id,
            remove_msg,
            {
                "tree_snapshot": serialize_tree(child),  # snapshot of new tree
                "new_root": child,
            },
        )
    else:
        # Non-root removal
        if went_left:
            parent.left = child
        else:
            parent.right = child

        remove_msg = (
            f"Removed {value}"
            if child is None
            else f"Replaced {value} with child"
        )
        yield (
            "remove",
            target_id,
            remove_msg,
            {"tree_snapshot": serialize_tree(root)},
        )

    # For root replacement, snapshot uses child (new root); same state as remove yield — intentional
    yield (
        "done",
        None,
        f"Deleted {value}",
        {"tree_snapshot": serialize_tree(root if not is_root else child)},
    )


# ---------------------------------------------------------------------------
# Traversal generators
# ---------------------------------------------------------------------------

def inorder_traversal(root: Optional[TreeNode]) -> Generator[Tuple[str, Optional[int], str, Dict[str, Any]], None, None]:
    """Generator yielding step-by-step inorder traversal: left -> visit -> right."""
    if root is None:
        yield ("done", None, "Tree is empty", {"tree_snapshot": []})
        return

    def _inorder(node: TreeNode) -> Generator[Tuple[str, Optional[int], str, Dict[str, Any]], None, None]:
        if node.left:
            yield from _inorder(node.left)
        yield ("visit", node.id, f"Visit {node.value}", {"tree_snapshot": serialize_tree(root)})
        if node.right:
            yield from _inorder(node.right)

    yield from _inorder(root)
    yield ("done", None, "Inorder traversal complete", {"tree_snapshot": serialize_tree(root)})


def preorder_traversal(root: Optional[TreeNode]) -> Generator[Tuple[str, Optional[int], str, Dict[str, Any]], None, None]:
    """Generator yielding step-by-step preorder traversal: visit -> left -> right."""
    if root is None:
        yield ("done", None, "Tree is empty", {"tree_snapshot": []})
        return

    def _preorder(node: TreeNode) -> Generator[Tuple[str, Optional[int], str, Dict[str, Any]], None, None]:
        yield ("visit", node.id, f"Visit {node.value}", {"tree_snapshot": serialize_tree(root)})
        if node.left:
            yield from _preorder(node.left)
        if node.right:
            yield from _preorder(node.right)

    yield from _preorder(root)
    yield ("done", None, "Preorder traversal complete", {"tree_snapshot": serialize_tree(root)})


def postorder_traversal(root: Optional[TreeNode]) -> Generator[Tuple[str, Optional[int], str, Dict[str, Any]], None, None]:
    """Generator yielding step-by-step postorder traversal: left -> right -> visit."""
    if root is None:
        yield ("done", None, "Tree is empty", {"tree_snapshot": []})
        return

    def _postorder(node: TreeNode) -> Generator[Tuple[str, Optional[int], str, Dict[str, Any]], None, None]:
        if node.left:
            yield from _postorder(node.left)
        if node.right:
            yield from _postorder(node.right)
        yield ("visit", node.id, f"Visit {node.value}", {"tree_snapshot": serialize_tree(root)})

    yield from _postorder(root)
    yield ("done", None, "Postorder traversal complete", {"tree_snapshot": serialize_tree(root)})


def levelorder_traversal(root: Optional[TreeNode]) -> Generator[Tuple[str, Optional[int], str, Dict[str, Any]], None, None]:
    """Generator yielding step-by-step level-order (BFS) traversal."""
    if root is None:
        yield ("done", None, "Tree is empty", {"tree_snapshot": []})
        return

    queue: deque[TreeNode] = deque([root])
    while queue:
        node = queue.popleft()
        yield ("visit", node.id, f"Visit {node.value}", {"tree_snapshot": serialize_tree(root)})
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)

    yield ("done", None, "Level-order traversal complete", {"tree_snapshot": serialize_tree(root)})


def bst_search(root: Optional[TreeNode], value: int) -> Generator[Tuple[str, Optional[int], str, Dict[str, Any]], None, None]:
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
                None,
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
