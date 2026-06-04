# ============================================================
# Team: Ant Colony | Variant 13
# Members: Juan Camilo Méndez, Jonathan David Moreno, Salomé Roldán
# File: backtracking.py — Backtracking solver: find path home
# ============================================================

from algorithms.greedy import greedy_sorted_neighbors


def solve(start, home, grid_size, walls, pheromones):
    """
    Find a path from start to home using Backtracking + Greedy ordering.

    At each step, neighbors are sorted by pheromone value (greedy heuristic)
    so the most promising branch is always tried first. If a dead end is
    reached, the algorithm backtracks and tries the next candidate.

    Parameters:
        start      : (x, y) tuple — ant's starting position
        home       : (x, y) tuple — nest position
        grid_size  : (cols, rows) tuple
        walls      : set of (x, y) wall positions
        pheromones : dict {(x,y): float} pheromone values

    Returns:
        path       : list of (x, y) tuples from start to home, or []
        discarded  : set of (x, y) cells that were visited but backtracked

    Complexity: O(b^d) worst case, b = branching factor, d = solution depth
    """
    path      = [start]
    visited   = {start}
    discarded = set()

    def _backtrack(x, y):
        if (x, y) == home:
            return True

        candidates = greedy_sorted_neighbors(x, y, grid_size, walls, pheromones, visited)

        for (nx, ny) in candidates:
            visited.add((nx, ny))
            path.append((nx, ny))

            if _backtrack(nx, ny):
                return True

            # Dead end — backtrack
            path.pop()
            discarded.add((nx, ny))
            # Do NOT remove from visited: prevents revisiting dead-end cells

        return False

    found = _backtrack(*start)

    if found:
        return path, discarded
    else:
        return [], discarded
