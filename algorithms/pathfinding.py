"""Pathfinding algorithm generators.

Each function is a generator that yields 4-tuples:
    (op_type, cell, status_msg, data_dict)

op_type: "frontier", "visit", "update", "path", "no_path", "done"
cell: (row, col) tuple
status_msg: human-readable description
data_dict: algorithm-specific data (distance, cost, f/g/h, parent, etc.)

Grid format: 2D list where -1=wall, 1=empty (cost 1), >1=weighted (cost N).
Movement: 4-directional (up, down, left, right).
"""

from collections import deque

__all__ = ["bfs", "dfs"]


def _neighbors(row, col, rows, cols):
    """Yield valid 4-directional neighbors."""
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            yield nr, nc


def bfs(grid, start, end):
    """Breadth-first search. Ignores weights (all edges cost 1)."""
    rows, cols = len(grid), len(grid[0])
    sr, sc = start
    er, ec = end

    visited = set()
    parent = {}
    queue = deque()

    visited.add((sr, sc))
    queue.append((sr, sc))
    distance = {(sr, sc): 0}

    yield ("frontier", (sr, sc), f"Start at ({sr},{sc})",
           {"distance": 0, "parent": None})

    if (sr, sc) == (er, ec):
        path = [(sr, sc)]
        yield ("path", (sr, sc), "Tracing shortest path",
               {"path_length": 1})
        yield ("done", (), "Path found!",
               {"total_explored": len(visited),
                "path_length": 1, "total_cost": 0})
        return

    while queue:
        r, c = queue.popleft()
        dist = distance[(r, c)]

        yield ("visit", (r, c),
               f"Visiting ({r},{c}), distance={dist}",
               {"distance": dist, "queue_size": len(queue)})

        if (r, c) == (er, ec):
            path = []
            node = (er, ec)
            while node is not None:
                path.append(node)
                node = parent.get(node)
            path.reverse()

            for cell in path:
                yield ("path", cell, "Tracing shortest path",
                       {"path_length": len(path)})

            yield ("done", (), "Path found!",
                   {"total_explored": len(visited),
                    "path_length": len(path), "total_cost": len(path) - 1})
            return

        for nr, nc in _neighbors(r, c, rows, cols):
            if (nr, nc) not in visited and grid[nr][nc] != -1:
                visited.add((nr, nc))
                parent[(nr, nc)] = (r, c)
                distance[(nr, nc)] = dist + 1
                queue.append((nr, nc))

                yield ("frontier", (nr, nc),
                       f"Adding ({nr},{nc}) to queue, distance={dist + 1}",
                       {"distance": dist + 1, "parent": (r, c)})

    yield ("no_path", (), "No path exists from start to end",
           {"total_explored": len(visited)})


def dfs(grid, start, end):
    """Depth-first search. Ignores weights. Does NOT guarantee shortest path."""
    rows, cols = len(grid), len(grid[0])
    sr, sc = start
    er, ec = end

    visited = set()
    parent = {}
    stack = [(sr, sc)]
    distance = {(sr, sc): 0}

    yield ("frontier", (sr, sc), f"Start at ({sr},{sc})",
           {"distance": 0, "parent": None})

    while stack:
        r, c = stack.pop()

        if (r, c) in visited:
            continue
        visited.add((r, c))
        dist = distance[(r, c)]

        yield ("visit", (r, c),
               f"Visiting ({r},{c}), depth={dist}",
               {"distance": dist, "queue_size": len(stack)})

        if (r, c) == (er, ec):
            path = []
            node = (er, ec)
            while node is not None:
                path.append(node)
                node = parent.get(node)
            path.reverse()

            for cell in path:
                yield ("path", cell, "Tracing path",
                       {"path_length": len(path)})

            yield ("done", (), "Path found!",
                   {"total_explored": len(visited),
                    "path_length": len(path), "total_cost": len(path) - 1})
            return

        for nr, nc in _neighbors(r, c, rows, cols):
            if (nr, nc) not in visited and grid[nr][nc] != -1:
                if (nr, nc) not in distance:
                    parent[(nr, nc)] = (r, c)
                    distance[(nr, nc)] = dist + 1
                stack.append((nr, nc))

                yield ("frontier", (nr, nc),
                       f"Pushing ({nr},{nc}) to stack",
                       {"distance": dist + 1, "parent": (r, c)})

    yield ("no_path", (), "No path exists from start to end",
           {"total_explored": len(visited)})
