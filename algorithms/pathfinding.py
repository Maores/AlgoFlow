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

import heapq
from collections import deque

__all__ = ["bfs", "dfs", "dijkstra", "astar"]


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


def dijkstra(grid, start, end):
    """Dijkstra's algorithm. Respects cell weights."""
    rows, cols = len(grid), len(grid[0])
    sr, sc = start
    er, ec = end

    dist = {}
    parent = {}
    visited = set()
    counter = 0

    dist[(sr, sc)] = 0
    heap = [(0, counter, sr, sc)]
    counter += 1

    yield ("frontier", (sr, sc), f"Start at ({sr},{sc})",
           {"cost": 0, "parent": None})

    while heap:
        cost, _, r, c = heapq.heappop(heap)

        if (r, c) in visited:
            continue
        visited.add((r, c))

        yield ("visit", (r, c),
               f"Visiting ({r},{c}), cost={cost}",
               {"cost": cost, "queue_size": len(heap)})

        if (r, c) == (er, ec):
            path = []
            node = (er, ec)
            while node is not None:
                path.append(node)
                node = parent.get(node)
            path.reverse()

            for cell in path:
                yield ("path", cell, "Tracing cheapest path",
                       {"path_length": len(path)})

            yield ("done", (), f"Path found! Cost={cost}",
                   {"total_explored": len(visited),
                    "path_length": len(path), "total_cost": cost})
            return

        for nr, nc in _neighbors(r, c, rows, cols):
            if (nr, nc) not in visited and grid[nr][nc] != -1:
                cell_cost = grid[nr][nc]
                new_cost = cost + cell_cost
                if (nr, nc) not in dist or new_cost < dist[(nr, nc)]:
                    old_cost = dist.get((nr, nc))
                    dist[(nr, nc)] = new_cost
                    parent[(nr, nc)] = (r, c)
                    heapq.heappush(heap, (new_cost, counter, nr, nc))
                    counter += 1

                    if old_cost is not None:
                        yield ("update", (nr, nc),
                               f"Relaxing ({nr},{nc}): {old_cost} -> {new_cost}",
                               {"old_cost": old_cost, "cost": new_cost,
                                "parent": (r, c)})
                    else:
                        yield ("frontier", (nr, nc),
                               f"Adding ({nr},{nc}), cost={new_cost}",
                               {"cost": new_cost, "parent": (r, c)})

    yield ("no_path", (), "No path exists from start to end",
           {"total_explored": len(visited)})


def _manhattan(r1, c1, r2, c2):
    return abs(r1 - r2) + abs(c1 - c2)


def astar(grid, start, end):
    """A* search with Manhattan distance heuristic. Respects cell weights."""
    rows, cols = len(grid), len(grid[0])
    sr, sc = start
    er, ec = end

    g_score = {}
    parent = {}
    visited = set()
    counter = 0

    g_score[(sr, sc)] = 0
    h = _manhattan(sr, sc, er, ec)
    heap = [(h, counter, sr, sc)]
    counter += 1

    yield ("frontier", (sr, sc), f"Start at ({sr},{sc})",
           {"g": 0, "h": h, "f": h, "parent": None})

    while heap:
        f, _, r, c = heapq.heappop(heap)

        if (r, c) in visited:
            continue
        visited.add((r, c))
        g = g_score[(r, c)]

        yield ("visit", (r, c),
               f"Visiting ({r},{c}), g={g}, f={f}",
               {"g": g, "h": f - g, "f": f, "queue_size": len(heap)})

        if (r, c) == (er, ec):
            path = []
            node = (er, ec)
            while node is not None:
                path.append(node)
                node = parent.get(node)
            path.reverse()

            for cell in path:
                yield ("path", cell, "Tracing optimal path",
                       {"path_length": len(path)})

            yield ("done", (), f"Path found! Cost={g}",
                   {"total_explored": len(visited),
                    "path_length": len(path), "total_cost": g})
            return

        for nr, nc in _neighbors(r, c, rows, cols):
            if (nr, nc) not in visited and grid[nr][nc] != -1:
                cell_cost = grid[nr][nc]
                new_g = g + cell_cost
                if (nr, nc) not in g_score or new_g < g_score[(nr, nc)]:
                    old_g = g_score.get((nr, nc))
                    g_score[(nr, nc)] = new_g
                    parent[(nr, nc)] = (r, c)
                    h = _manhattan(nr, nc, er, ec)
                    new_f = new_g + h
                    heapq.heappush(heap, (new_f, counter, nr, nc))
                    counter += 1

                    if old_g is not None:
                        yield ("update", (nr, nc),
                               f"Relaxing ({nr},{nc}): g={old_g}->{new_g}, f={new_f}",
                               {"g": new_g, "h": h, "f": new_f,
                                "old_cost": old_g, "cost": new_g,
                                "parent": (r, c)})
                    else:
                        yield ("frontier", (nr, nc),
                               f"Adding ({nr},{nc}), g={new_g}, h={h}, f={new_f}",
                               {"g": new_g, "h": h, "f": new_f,
                                "parent": (r, c)})

    yield ("no_path", (), "No path exists from start to end",
           {"total_explored": len(visited)})
