# ============================================================
# Team: Ant Colony | 
# Members: Juan Camilo Méndez, Salomé Roldán
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


def greedy_next(x, y, grid_size, walls, pheromones, visited, home=None):
    """
    Greedy choice: return the unvisited neighbor with highest pheromone.
    Uses Manhattan distance to home as tiebreaker only when pheromone is equal.
    """
    candidates = greedy_sorted_neighbors(x, y, grid_size, walls, pheromones, visited, home)
    if not candidates:
        return None
    return candidates[0]


def greedy_sorted_neighbors(x, y, grid_size, walls, pheromones, visited, home=None):
    """
    Return ALL unvisited neighbors sorted by:
      1. Pheromone value descending  (PRIMARY criterion — always dominant)
      2. Manhattan distance to home ascending  (tiebreaker ONLY when pheromone is identical)

    Complexity: O(k log k), k <= 4
    """
    neighbors = get_neighbors(x, y, grid_size, walls)
    candidates = [(nx, ny) for (nx, ny) in neighbors if (nx, ny) not in visited]

    max_dist = grid_size[0] + grid_size[1]  # max possible Manhattan distance

    def sort_key(pos):
        phero = pheromones.get(pos, 0.0)
        dist  = abs(pos[0] - home[0]) + abs(pos[1] - home[1]) if home else 0
        # Normalize distance to [0,1] range so it never overrides pheromone
        norm_dist = dist / max_dist
        return (-phero, norm_dist)

    candidates.sort(key=sort_key)
    return candidates
