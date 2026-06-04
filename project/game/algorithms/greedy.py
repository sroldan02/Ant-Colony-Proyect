# ============================================================
# Team: Ant Colony | Variant 13
# Members: Juan Camilo Méndez, Jonathan David Moreno, Salomé Roldán
# File: greedy.py — Greedy strategy: follow strongest pheromone
# ============================================================

def get_neighbors(x, y, grid_size, walls):
    """Return valid adjacent cells (up, down, left, right)."""
    cols, rows = grid_size
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    neighbors = []
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < cols and 0 <= ny < rows:
            if (nx, ny) not in walls:
                neighbors.append((nx, ny))
    return neighbors


def greedy_next(x, y, grid_size, walls, pheromones, visited):
    """
    Greedy choice: from current position, return the unvisited neighbor
    with the highest pheromone value.
    Returns (nx, ny) or None if all neighbors are visited/blocked.

    Complexity: O(k) where k = number of neighbors (max 4)
    """
    neighbors = get_neighbors(x, y, grid_size, walls)
    candidates = [(nx, ny) for (nx, ny) in neighbors if (nx, ny) not in visited]

    if not candidates:
        return None

    # Sort descending by pheromone value (greedy criterion)
    candidates.sort(key=lambda pos: pheromones.get(pos, 0.0), reverse=True)
    return candidates[0]


def greedy_sorted_neighbors(x, y, grid_size, walls, pheromones, visited):
    """
    Return ALL unvisited neighbors sorted by pheromone descending.
    Used by backtracking to determine the order in which to try candidates.

    Complexity: O(k log k)
    """
    neighbors = get_neighbors(x, y, grid_size, walls)
    candidates = [(nx, ny) for (nx, ny) in neighbors if (nx, ny) not in visited]
    candidates.sort(key=lambda pos: pheromones.get(pos, 0.0), reverse=True)
    return candidates
