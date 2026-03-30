"""Tests for tree data structures and BST generators (Tasks 1, 2 & 3)."""

import pytest
from algorithms.trees import (
    TreeNode,
    serialize_tree,
    deserialize_tree,
    bst_from_values,
    bst_insert,
    bst_search,
    bst_delete,
    inorder_traversal,
    preorder_traversal,
    postorder_traversal,
    levelorder_traversal,
    TREE_ALGORITHM_INFO,
)


# ---------------------------------------------------------------------------
# TreeNode basic behavior
# ---------------------------------------------------------------------------

def test_treenode_unique_ids():
    """Two nodes created in sequence must have different ids."""
    a = TreeNode(10)
    b = TreeNode(20)
    assert a.id != b.id


def test_treenode_reset_counter():
    """After reset_counter(), the next node created gets id 0."""
    # Create some nodes to advance the counter
    TreeNode(1)
    TreeNode(2)
    TreeNode.reset_counter()
    node = TreeNode(99)
    assert node.id == 0


# ---------------------------------------------------------------------------
# serialize_tree
# ---------------------------------------------------------------------------

def test_serialize_empty():
    """serialize_tree(None) returns an empty list."""
    result = serialize_tree(None)
    assert result == []


def test_serialize_single_node():
    """A single root node serializes to one dict with no children."""
    root = TreeNode(42)
    result = serialize_tree(root)
    assert len(result) == 1
    record = result[0]
    assert record["id"] == 0
    assert record["value"] == 42
    assert record["left_id"] is None
    assert record["right_id"] is None


def test_serialize_includes_all_nodes():
    """serialize_tree includes every node in the tree."""
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(4)

    result = serialize_tree(root)
    assert len(result) == 4
    ids = {r["id"] for r in result}
    assert ids == {0, 1, 2, 3}


# ---------------------------------------------------------------------------
# serialize / deserialize round-trip
# ---------------------------------------------------------------------------

def test_serialize_deserialize_roundtrip():
    """Build a tree, serialize, deserialize, and verify structure matches."""
    #       10
    #      /  \
    #     5   15
    #    / \
    #   2   7
    root = TreeNode(10)
    root.left = TreeNode(5)
    root.right = TreeNode(15)
    root.left.left = TreeNode(2)
    root.left.right = TreeNode(7)

    data = serialize_tree(root)
    restored = deserialize_tree(data)

    assert restored is not None
    assert restored.value == 10
    assert restored.left.value == 5
    assert restored.right.value == 15
    assert restored.left.left.value == 2
    assert restored.left.right.value == 7
    # Leaf nodes have no children
    assert restored.right.left is None
    assert restored.right.right is None
    assert restored.left.left.left is None
    assert restored.left.left.right is None


def test_deserialize_empty():
    """deserialize_tree([]) returns None."""
    assert deserialize_tree([]) is None


def test_deserialize_preserves_ids():
    """Deserialized nodes keep their original ids."""
    root = TreeNode(10)
    root.left = TreeNode(5)
    original_root_id = root.id
    original_left_id = root.left.id

    data = serialize_tree(root)
    restored = deserialize_tree(data)

    assert restored.id == original_root_id
    assert restored.left.id == original_left_id


# ---------------------------------------------------------------------------
# bst_from_values
# ---------------------------------------------------------------------------

def test_bst_from_values_empty():
    """bst_from_values([]) returns None."""
    result = bst_from_values([])
    assert result is None


def test_bst_from_values_order():
    """bst_from_values([40, 20, 60]) builds a correct BST structure."""
    root = bst_from_values([40, 20, 60])

    assert root is not None
    assert root.value == 40
    assert root.left is not None
    assert root.left.value == 20
    assert root.right is not None
    assert root.right.value == 60
    # Leaf nodes have no children
    assert root.left.left is None
    assert root.left.right is None
    assert root.right.left is None
    assert root.right.right is None


def test_bst_from_values_deeper():
    """bst_from_values with more values places nodes at correct BST positions."""
    root = bst_from_values([50, 30, 70, 20, 40])
    #        50
    #       /  \
    #     30    70
    #    /  \
    #  20   40

    assert root.value == 50
    assert root.left.value == 30
    assert root.right.value == 70
    assert root.left.left.value == 20
    assert root.left.right.value == 40
    assert root.right.left is None
    assert root.right.right is None


def test_bst_from_values_does_not_reset_counter():
    """bst_from_values should NOT reset the counter — uses current counter state."""
    # Advance counter by 2
    TreeNode(99)
    TreeNode(99)
    root = bst_from_values([10])
    # The first node created by bst_from_values should get id 2 (not 0)
    assert root.id == 2


def test_bst_from_values_duplicate():
    """Duplicate values are inserted to the right subtree by convention."""
    root = bst_from_values([5, 5])
    assert root.right is not None
    assert root.right.value == 5


# ---------------------------------------------------------------------------
# deserialize_tree input validation
# ---------------------------------------------------------------------------

def test_deserialize_missing_key_raises_value_error():
    """deserialize_tree raises ValueError if a required key is missing."""
    bad_data = [{"id": 0, "value": 10}]  # missing left_id and right_id
    with pytest.raises(ValueError, match="missing keys"):
        deserialize_tree(bad_data)


# ---------------------------------------------------------------------------
# bst_insert generator (Task 2)
# ---------------------------------------------------------------------------

def test_bst_insert_sequence():
    """Insert into an existing tree; verify op_type sequence ends with insert+done."""
    TreeNode.reset_counter()
    root = bst_from_values([50, 30, 70])
    #        50
    #       /  \
    #     30    70
    # Inserting 40 should: compare 50, compare 30, insert 40, done

    ops = list(bst_insert(root, 40))
    op_types = [op[0] for op in ops]

    assert op_types[-1] == "done"
    assert op_types[-2] == "insert"
    # There must be at least one compare before insert
    assert "compare" in op_types
    assert op_types.index("compare") < op_types.index("insert")


def test_bst_insert_at_root():
    """Inserting into an empty tree (None root) yields 'new_root' in the insert data."""
    ops = list(bst_insert(None, 10))
    insert_ops = [op for op in ops if op[0] == "insert"]
    assert len(insert_ops) == 1
    _, node_id, msg, data = insert_ops[0]
    assert "new_root" in data
    assert data["new_root"].value == 10


def test_bst_insert_updates_tree():
    """After consuming all yields the tree is correctly mutated in-place."""
    TreeNode.reset_counter()
    root = bst_from_values([50, 30, 70])

    # Exhaust the generator (mutations happen during iteration)
    list(bst_insert(root, 40))

    # 40 should be root.left.right
    assert root.left is not None
    assert root.left.value == 30
    assert root.left.right is not None
    assert root.left.right.value == 40

    # Also test a value that goes right
    list(bst_insert(root, 60))
    assert root.right.left is not None
    assert root.right.left.value == 60


def test_bst_insert_duplicate_goes_right():
    """Duplicate values are inserted to the right subtree."""
    TreeNode.reset_counter()
    root = bst_from_values([50])
    list(bst_insert(root, 50))
    assert root.right is not None
    assert root.right.value == 50


# ---------------------------------------------------------------------------
# bst_search generator (Task 2)
# ---------------------------------------------------------------------------

def test_bst_search_found():
    """Searching for an existing value produces a 'found' op."""
    TreeNode.reset_counter()
    root = bst_from_values([50, 30, 70])

    ops = list(bst_search(root, 30))
    op_types = [op[0] for op in ops]

    assert "found" in op_types
    assert op_types[-1] == "done"

    found_op = next(op for op in ops if op[0] == "found")
    assert found_op[1] == root.left.id  # 30 is root.left


def test_bst_search_not_found():
    """Searching for a missing value produces a 'not_found' op."""
    TreeNode.reset_counter()
    root = bst_from_values([50, 30, 70])

    ops = list(bst_search(root, 99))
    op_types = [op[0] for op in ops]

    assert "not_found" in op_types
    assert "found" not in op_types
    assert op_types[-1] == "done"

    not_found_op = next(op for op in ops if op[0] == "not_found")
    assert str(99) in not_found_op[2]


def test_bst_search_empty_tree():
    """Searching on an empty (None) tree immediately yields not_found then done."""
    ops = list(bst_search(None, 5))
    op_types = [op[0] for op in ops]

    assert op_types == ["not_found", "done"]
    assert ops[0][2] == "Tree is empty"
    assert ops[0][3]["tree_snapshot"] == []


# ---------------------------------------------------------------------------
# TREE_ALGORITHM_INFO (Task 2)
# ---------------------------------------------------------------------------

def test_tree_algo_info_keys():
    """TREE_ALGORITHM_INFO must contain all 9 required algorithm keys."""
    required_keys = {
        "BST Insert",
        "BST Delete",
        "BST Search",
        "Inorder",
        "Preorder",
        "Postorder",
        "Level-order",
        "Heap Insert",
        "Heap Extract",
    }
    assert required_keys == set(TREE_ALGORITHM_INFO.keys())


def test_tree_algo_info_structure():
    """Each entry in TREE_ALGORITHM_INFO must contain the expected metadata fields."""
    required_fields = {"name", "time_best", "time_worst", "time_average", "space", "description"}
    for key, info in TREE_ALGORITHM_INFO.items():
        missing = required_fields - info.keys()
        assert not missing, f"Entry '{key}' is missing fields: {missing}"


# ---------------------------------------------------------------------------
# bst_delete generator (Task 3)
# ---------------------------------------------------------------------------

def test_bst_delete_leaf():
    """Delete a leaf node: expect exactly highlight, remove, done (3 yields after compares)."""
    TreeNode.reset_counter()
    #        50
    #       /  \
    #     30    70
    root = bst_from_values([50, 30, 70])
    leaf_id = root.left.id  # 30 is a leaf

    ops = list(bst_delete(root, 30))
    op_types = [op[0] for op in ops]

    # Last three ops must be highlight, remove, done
    assert op_types[-3] == "highlight"
    assert op_types[-2] == "remove"
    assert op_types[-1] == "done"

    # Highlight message indicates leaf node
    highlight_op = next(op for op in ops if op[0] == "highlight")
    assert "leaf" in highlight_op[2]

    # Remove op carries the correct node id
    remove_op = next(op for op in ops if op[0] == "remove")
    assert remove_op[1] == leaf_id

    # Tree structure after deletion: 30 should be gone
    assert root.left is None
    assert root.value == 50
    assert root.right.value == 70


def test_bst_delete_one_child():
    """Delete a node that has exactly one child; verify child is promoted."""
    TreeNode.reset_counter()
    #        50
    #       /  \
    #     30    70
    #       \
    #       40
    root = bst_from_values([50, 30, 70, 40])
    node_30_id = root.left.id

    ops = list(bst_delete(root, 30))
    op_types = [op[0] for op in ops]

    assert op_types[-3] == "highlight"
    assert op_types[-2] == "remove"
    assert op_types[-1] == "done"

    highlight_op = next(op for op in ops if op[0] == "highlight")
    assert "one child" in highlight_op[2]

    remove_op = next(op for op in ops if op[0] == "remove")
    assert remove_op[1] == node_30_id

    # After deletion, 40 should now be root's left child
    assert root.left is not None
    assert root.left.value == 40


def test_bst_delete_two_children():
    """Delete node with two children: must yield exactly 5 ops after compares."""
    TreeNode.reset_counter()
    #        50
    #       /  \
    #     30    70
    #    /  \
    #   20   40
    root = bst_from_values([50, 30, 70, 20, 40])
    target_id = root.left.id  # 30, has two children

    ops = list(bst_delete(root, 30))
    op_types = [op[0] for op in ops]

    # The final 5 ops must be: highlight, successor, copy, remove, done
    assert op_types[-5] == "highlight"
    assert op_types[-4] == "successor"
    assert op_types[-3] == "copy"
    assert op_types[-2] == "remove"
    assert op_types[-1] == "done"

    highlight_op = next(op for op in ops if op[0] == "highlight")
    assert "two children" in highlight_op[2]
    assert highlight_op[1] == target_id

    successor_op = next(op for op in ops if op[0] == "successor")
    # In-order successor of 30 is 40 (go right to 40, no left subtree)
    assert successor_op[2] == "Found in-order successor: 40"

    copy_op = next(op for op in ops if op[0] == "copy")
    assert copy_op[1] == target_id

    remove_op = next(op for op in ops if op[0] == "remove")
    assert remove_op[2] == "Removed successor"

    # After deletion, node that was 30 now holds 40, and old 40 node is gone
    assert root.left.value == 40
    assert root.left.right is None  # old 40 is removed


def test_bst_delete_root_leaf():
    """Delete the root when it is also a leaf: remove yield must include new_root=None."""
    TreeNode.reset_counter()
    root = bst_from_values([42])

    ops = list(bst_delete(root, 42))
    op_types = [op[0] for op in ops]

    assert op_types[-3] == "highlight"
    assert op_types[-2] == "remove"
    assert op_types[-1] == "done"

    remove_op = next(op for op in ops if op[0] == "remove")
    assert "new_root" in remove_op[3]
    assert remove_op[3]["new_root"] is None


def test_bst_delete_not_found():
    """Searching for a non-existent value must produce a not_found yield."""
    TreeNode.reset_counter()
    root = bst_from_values([50, 30, 70])

    ops = list(bst_delete(root, 99))
    op_types = [op[0] for op in ops]

    assert "not_found" in op_types
    assert op_types[-1] == "done"
    # Tree must be unchanged
    assert root.value == 50
    assert root.left.value == 30
    assert root.right.value == 70


def test_bst_delete_empty():
    """Delete from an empty tree: first yield must be not_found immediately."""
    ops = list(bst_delete(None, 5))
    op_types = [op[0] for op in ops]

    assert op_types[0] == "not_found"
    assert op_types[1] == "done"
    assert ops[0][2] == "Tree is empty"
    assert ops[0][3]["tree_snapshot"] == []


def test_bst_delete_two_children_snapshots():
    """Verify snapshot integrity across the 4 steps of a two-children deletion."""
    TreeNode.reset_counter()
    #        50
    #       /  \
    #     30    70
    #    /  \
    #   20   40
    root = bst_from_values([50, 30, 70, 20, 40])

    ops = list(bst_delete(root, 30))

    highlight_op = next(op for op in ops if op[0] == "highlight")
    successor_op = next(op for op in ops if op[0] == "successor")
    copy_op = next(op for op in ops if op[0] == "copy")
    remove_op = next(op for op in ops if op[0] == "remove")

    # Step 1 (highlight): tree snapshot must still show 30 at the target node
    h_snapshot = {rec["id"]: rec for rec in highlight_op[3]["tree_snapshot"]}
    target_id = root.left.id  # node that originally was 30, now holds 40 after copy
    # At highlight step the target node's value should be 30
    # We find the record whose id matches the node that WAS 30.
    # Since we haven't mutated yet, look for value==30 in the snapshot.
    values_in_highlight = {rec["value"] for rec in highlight_op[3]["tree_snapshot"]}
    assert 30 in values_in_highlight

    # Step 2 (successor): tree still unchanged — 30 still present
    values_in_successor = {rec["value"] for rec in successor_op[3]["tree_snapshot"]}
    assert 30 in values_in_successor
    assert 40 in values_in_successor

    # Step 3 (copy): target now shows successor's value (40), old 40 still present
    # After copy: node formerly holding 30 now holds 40, and old successor (40) still exists
    copy_snapshot_values = [rec["value"] for rec in copy_op[3]["tree_snapshot"]]
    # There must now be TWO nodes with value 40 in the snapshot
    assert copy_snapshot_values.count(40) == 2

    # Step 4 (remove): successor is gone — only one 40 remains
    remove_snapshot_values = [rec["value"] for rec in remove_op[3]["tree_snapshot"]]
    assert remove_snapshot_values.count(40) == 1
    # And 30 must be gone
    assert 30 not in remove_snapshot_values


# ---------------------------------------------------------------------------
# Traversal generators (Task 4)
# ---------------------------------------------------------------------------

def _build_test_tree():
    """Build BST from [40, 20, 60, 10, 30, 50, 70] with deterministic ids."""
    TreeNode.reset_counter()
    return bst_from_values([40, 20, 60, 10, 30, 50, 70])


def _visit_values(ops):
    """Extract the visited values (from message) in order from traversal ops."""
    return [int(op[2].split()[-1]) for op in ops if op[0] == "visit"]


def test_inorder_traversal_order():
    """Inorder traversal visits nodes in sorted order: [10, 20, 30, 40, 50, 60, 70]."""
    root = _build_test_tree()
    ops = list(inorder_traversal(root))
    assert _visit_values(ops) == [10, 20, 30, 40, 50, 60, 70]


def test_preorder_traversal_order():
    """Preorder traversal visits root first: [40, 20, 10, 30, 60, 50, 70]."""
    root = _build_test_tree()
    ops = list(preorder_traversal(root))
    assert _visit_values(ops) == [40, 20, 10, 30, 60, 50, 70]


def test_postorder_traversal_order():
    """Postorder traversal visits root last: [10, 30, 20, 50, 70, 60, 40]."""
    root = _build_test_tree()
    ops = list(postorder_traversal(root))
    assert _visit_values(ops) == [10, 30, 20, 50, 70, 60, 40]


def test_levelorder_traversal_order():
    """Level-order traversal visits by level: [40, 20, 60, 10, 30, 50, 70]."""
    root = _build_test_tree()
    ops = list(levelorder_traversal(root))
    assert _visit_values(ops) == [40, 20, 60, 10, 30, 50, 70]


def test_traversal_empty_tree():
    """Each traversal on None yields only a done tuple with empty snapshot."""
    for traversal_fn in [inorder_traversal, preorder_traversal, postorder_traversal, levelorder_traversal]:
        ops = list(traversal_fn(None))
        assert len(ops) == 1
        assert ops[0][0] == "done"
        assert ops[0][3]["tree_snapshot"] == []


def test_traversal_yields_have_snapshot():
    """Every yield from every traversal must include 'tree_snapshot' in data."""
    root = _build_test_tree()
    for traversal_fn in [inorder_traversal, preorder_traversal, postorder_traversal, levelorder_traversal]:
        ops = list(traversal_fn(root))
        for op in ops:
            assert "tree_snapshot" in op[3], f"{traversal_fn.__name__} yield missing tree_snapshot: {op}"


def test_traversal_single_node():
    """Traversal on a single node yields exactly one visit + one done."""
    TreeNode.reset_counter()
    root = TreeNode(42)
    for traversal_fn in [inorder_traversal, preorder_traversal, postorder_traversal, levelorder_traversal]:
        ops = list(traversal_fn(root))
        op_types = [op[0] for op in ops]
        assert op_types == ["visit", "done"], f"{traversal_fn.__name__} got {op_types}"
        assert ops[0][1] == root.id
        assert ops[0][2] == "Visit 42"
