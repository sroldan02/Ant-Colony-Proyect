# ============================================================
# Team: Ant Colony | Variant 13
# Members: Juan Camilo Méndez, Jonathan David Moreno, Salomé Roldán
# File: bridge.py — JSON bridge: Python <-> C++ communication
# ============================================================

import json
import os
import subprocess

INPUT_PATH  = os.path.join(os.path.dirname(__file__), "../../data/input.json")
STATE_PATH  = os.path.join(os.path.dirname(__file__), "../../data/state.json")
_engine_name = "ant.exe" if os.name == "nt" else "ant"
ENGINE_PATH = os.path.join(os.path.dirname(__file__), "../../engine", _engine_name)


def write_input(grid_size, ant_pos, home_pos, walls, pheromones):
    """
    Write input.json for the C++ engine.
    pheromones: dict {(x,y): float}
    walls: list/set of (x,y)
    """
    data = {
        "grid_size"  : list(grid_size),
        "ant_pos"    : list(ant_pos),
        "home_pos"   : list(home_pos),
        "walls"      : [list(w) for w in walls],
        "pheromones" : {f"{x},{y}": v for (x, y), v in pheromones.items()}
    }
    with open(INPUT_PATH, "w") as f:
        json.dump(data, f, indent=4)


def run_engine():
    """
    Execute the C++ engine binary.
    The engine reads input.json and writes state.json.
    """
    if not os.path.exists(ENGINE_PATH):
        print(f"[bridge] WARNING: engine not found at {ENGINE_PATH}")
        return False
    result = subprocess.run([ENGINE_PATH], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[bridge] Engine error: {result.stderr}")
        return False
    return True


def read_state():
    """
    Read state.json written by the C++ engine.
    Returns a dict with keys: status, current_pos, path
    """
    if not os.path.exists(STATE_PATH):
        return None
    with open(STATE_PATH, "r") as f:
        return json.load(f)