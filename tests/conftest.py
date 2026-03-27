import pytest
from algorithms.trees import TreeNode


@pytest.fixture(autouse=True)
def reset_tree_counter():
    TreeNode.reset_counter()
    yield
