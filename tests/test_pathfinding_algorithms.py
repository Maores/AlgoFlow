"""Tests for pathfinding algorithm generators."""


def make_grid(rows, cols, walls=None, weights=None):
    """Create a simple grid for testing.
    Returns 2D list: 0=empty, -1=wall, >1=weighted cost.
    Default empty cell cost is 1.
    """
    grid = [[1] * cols for _ in range(rows)]
    if walls:
        for r, c in walls:
            grid[r][c] = -1
    if weights:
        for (r, c), cost in weights.items():
            grid[r][c] = cost
    return grid


def collect_ops(generator):
    """Collect all operations from a generator into a list."""
    return list(generator)


def test_bfs_simple_path():
    """BFS finds shortest path on a simple 5x5 grid."""
    from algorithms.pathfinding import bfs
    grid = make_grid(5, 5)
    start = (0, 0)
    end = (4, 4)
    ops = collect_ops(bfs(grid, start, end))
    op_types = [op[0] for op in ops]
    assert "done" in op_types
    assert "path" in op_types
    path_cells = [op[1] for op in ops if op[0] == "path"]
    assert start in path_cells
    assert end in path_cells
    done_op = [op for op in ops if op[0] == "done"][0]
    assert done_op[3]["path_length"] == 9  # 9 cells including start and end


def test_bfs_no_path():
    """BFS reports no_path when end is unreachable."""
    from algorithms.pathfinding import bfs
    walls = [(2, c) for c in range(5)]
    grid = make_grid(5, 5, walls=walls)
    ops = collect_ops(bfs(grid, (0, 0), (4, 4)))
    op_types = [op[0] for op in ops]
    assert "no_path" in op_types
    assert "path" not in op_types


def test_bfs_yields_frontier_and_visit():
    """BFS yields frontier and visit operations."""
    from algorithms.pathfinding import bfs
    grid = make_grid(3, 3)
    ops = collect_ops(bfs(grid, (0, 0), (2, 2)))
    op_types = [op[0] for op in ops]
    assert "frontier" in op_types
    assert "visit" in op_types


def test_bfs_4_tuple_format():
    """Each yielded operation is a 4-tuple with correct types."""
    from algorithms.pathfinding import bfs
    grid = make_grid(3, 3)
    ops = collect_ops(bfs(grid, (0, 0), (2, 2)))
    for op in ops:
        assert len(op) == 4, f"Expected 4-tuple, got {len(op)}-tuple: {op}"
        op_type, cell, msg, data = op
        assert isinstance(op_type, str)
        assert isinstance(msg, str)
        assert isinstance(data, dict)


def test_bfs_ignores_weights():
    """BFS treats weighted cells as passable with cost 1."""
    from algorithms.pathfinding import bfs
    weights = {(1, 1): 5}
    grid = make_grid(3, 3, weights=weights)
    ops = collect_ops(bfs(grid, (0, 0), (2, 2)))
    op_types = [op[0] for op in ops]
    assert "done" in op_types
    path_cells = [op[1] for op in ops if op[0] == "path"]
    assert len(path_cells) > 0


def test_bfs_start_equals_end():
    """BFS handles start == end gracefully."""
    from algorithms.pathfinding import bfs
    grid = make_grid(3, 3)
    ops = collect_ops(bfs(grid, (1, 1), (1, 1)))
    op_types = [op[0] for op in ops]
    assert "done" in op_types
    done_op = [op for op in ops if op[0] == "done"][0]
    assert done_op[3]["path_length"] == 1


def test_dfs_finds_path():
    """DFS finds a path (not necessarily shortest) on a simple grid."""
    from algorithms.pathfinding import dfs
    grid = make_grid(5, 5)
    ops = collect_ops(dfs(grid, (0, 0), (4, 4)))
    op_types = [op[0] for op in ops]
    assert "done" in op_types
    assert "path" in op_types
    path_cells = [op[1] for op in ops if op[0] == "path"]
    assert (0, 0) in path_cells
    assert (4, 4) in path_cells


def test_dfs_no_path():
    """DFS reports no_path when end is unreachable."""
    from algorithms.pathfinding import dfs
    walls = [(2, c) for c in range(5)]
    grid = make_grid(5, 5, walls=walls)
    ops = collect_ops(dfs(grid, (0, 0), (4, 4)))
    op_types = [op[0] for op in ops]
    assert "no_path" in op_types


def test_dfs_4_tuple_format():
    """DFS yields valid 4-tuples."""
    from algorithms.pathfinding import dfs
    grid = make_grid(3, 3)
    ops = collect_ops(dfs(grid, (0, 0), (2, 2)))
    for op in ops:
        assert len(op) == 4
        op_type, cell, msg, data = op
        assert isinstance(op_type, str)
        assert isinstance(msg, str)
        assert isinstance(data, dict)


def test_dijkstra_finds_cheapest_path():
    from algorithms.pathfinding import dijkstra
    weights = {(2, c): 5 for c in range(5)}
    grid = make_grid(5, 5, weights=weights)
    ops = collect_ops(dijkstra(grid, (0, 0), (4, 4)))
    op_types = [op[0] for op in ops]
    assert "done" in op_types
    done_op = [op for op in ops if op[0] == "done"][0]
    assert done_op[3]["path_length"] > 0
    assert done_op[3]["total_cost"] > 0


def test_dijkstra_prefers_cheap_route():
    from algorithms.pathfinding import dijkstra
    grid = make_grid(3, 3, weights={(1, 1): 5})
    ops = collect_ops(dijkstra(grid, (0, 0), (2, 2)))
    path_cells = [op[1] for op in ops if op[0] == "path"]
    assert (1, 1) not in path_cells


def test_dijkstra_no_path():
    from algorithms.pathfinding import dijkstra
    walls = [(2, c) for c in range(5)]
    grid = make_grid(5, 5, walls=walls)
    ops = collect_ops(dijkstra(grid, (0, 0), (4, 4)))
    op_types = [op[0] for op in ops]
    assert "no_path" in op_types


def test_dijkstra_yields_update_ops():
    from algorithms.pathfinding import dijkstra
    grid = make_grid(3, 3)
    ops = collect_ops(dijkstra(grid, (0, 0), (2, 2)))
    op_types = [op[0] for op in ops]
    assert "visit" in op_types
    assert "frontier" in op_types


def test_astar_finds_optimal_path():
    from algorithms.pathfinding import astar
    grid = make_grid(5, 5)
    ops = collect_ops(astar(grid, (0, 0), (4, 4)))
    op_types = [op[0] for op in ops]
    assert "done" in op_types
    done_op = [op for op in ops if op[0] == "done"][0]
    assert done_op[3]["path_length"] == 9


def test_astar_explores_less_than_bfs():
    from algorithms.pathfinding import astar, bfs
    grid = make_grid(10, 10)
    start, end = (0, 0), (9, 9)
    bfs_ops = collect_ops(bfs(grid, start, end))
    astar_ops = collect_ops(astar(grid, start, end))
    bfs_visited = len([op for op in bfs_ops if op[0] == "visit"])
    astar_visited = len([op for op in astar_ops if op[0] == "visit"])
    assert astar_visited <= bfs_visited


def test_astar_with_weights():
    from algorithms.pathfinding import astar
    grid = make_grid(3, 3, weights={(1, 1): 5})
    ops = collect_ops(astar(grid, (0, 0), (2, 2)))
    path_cells = [op[1] for op in ops if op[0] == "path"]
    assert (1, 1) not in path_cells


def test_astar_no_path():
    from algorithms.pathfinding import astar
    walls = [(2, c) for c in range(5)]
    grid = make_grid(5, 5, walls=walls)
    ops = collect_ops(astar(grid, (0, 0), (4, 4)))
    op_types = [op[0] for op in ops]
    assert "no_path" in op_types


def test_astar_yields_f_g_h():
    from algorithms.pathfinding import astar
    grid = make_grid(3, 3)
    ops = collect_ops(astar(grid, (0, 0), (2, 2)))
    frontier_ops = [op for op in ops if op[0] == "frontier"]
    for op in frontier_ops:
        data = op[3]
        assert "g" in data
        assert "h" in data
        assert "f" in data
        assert data["f"] == data["g"] + data["h"]
