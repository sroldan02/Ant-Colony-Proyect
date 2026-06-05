# ============================================================
# Team: Ant Colony | 
# Members: Juan Camilo Méndez, Salomé Roldán
# File: backtracking.py — Backtracking solver: find path home
# ============================================================

from algorithms.greedy import greedy_sorted_neighbors


def solve(start, home, grid_size, walls, pheromones):
    """
    Find a path from start to home using Backtracking + Greedy ordering.

    Neighbors are sorted by pheromone (greedy) with Manhattan distance
    to home as tiebreaker, so the ant always prefers moving toward the
    nest when pheromone values are equal.

    Returns:
        path      : list of (x,y) from start to home, or []
        discarded : set of (x,y) cells that were backtracked
    """
    path      = [start]
    visited   = {start}
    discarded = set()

    def _backtrack(x, y):
        if (x, y) == home:
            return True

        candidates = greedy_sorted_neighbors(
            x, y, grid_size, walls, pheromones, visited, home=home
        )

        for (nx, ny) in candidates:
            visited.add((nx, ny))
            path.append((nx, ny))

            if _backtrack(nx, ny):
                return True

            # Dead end — backtrack
            path.pop()
            discarded.add((nx, ny))

        return False

    found = _backtrack(*start)
    return (path, discarded) if found else ([], discarded)
