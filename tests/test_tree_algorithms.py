"""Tests for tree data structures (Task 1: TreeNode, serialize/deserialize, bst_from_values)."""

import pytest
from algorithms.trees import TreeNode, serialize_tree, deserialize_tree, bst_from_values


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
