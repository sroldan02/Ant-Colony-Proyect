# ============================================================
# Team: Ant Colony | Variant 13
# Members: Juan Camilo Méndez, Jonathan David Moreno, Salomé Roldán
# File: main.py — Pygame grid UI + game loop
# Entry point: python game/ui/main.py
# ============================================================
import subprocess
import json
import pygame
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from algorithms.backtracking import solve
from algorithms.greedy        import greedy_next
from ui.bridge                import write_input, run_engine, read_state

# ── Constants ───────────────────────────────────────────────
GRID_COLS   = 8
GRID_ROWS   = 8
CELL_SIZE   = 72
HUD_WIDTH   = 220
MARGIN      = 2

WIN_W = GRID_COLS * CELL_SIZE + HUD_WIDTH
WIN_H = GRID_ROWS * CELL_SIZE

FPS = 60
ANIM_DELAY = 0.12   # seconds between animation steps

# ── Colors ───────────────────────────────────────────────────
BG          = (18,  18,  24)
GRID_LINE   = (40,  40,  55)
EMPTY       = (28,  28,  38)
WALL_COL    = (55,  55,  70)
ANT_COL     = (255, 200,  50)
HOME_COL    = (220,  80,  80)
PATH_COL    = (70,  140, 255)
DISCARD_COL = (80,   80,  95)
PHERO_COL   = (80,  220, 160)
HUD_BG      = (22,  22,  30)
BTN_NORMAL  = (50,  50,  70)
BTN_HOVER   = (80,  80, 110)
BTN_ACTIVE  = (100, 160, 255)
TEXT_COL    = (220, 220, 230)
TEXT_DIM    = (120, 120, 140)
WHITE       = (255, 255, 255)

# ── Game state ────────────────────────────────────────────────
class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.grid_size   = (GRID_COLS, GRID_ROWS)
        self.ant_pos     = (0, 0)
        self.home_pos    = (7, 7)
        self.walls       = set()
        self.pheromones  = {}          # {(x,y): float 0..2}
        self.path        = []          # solution path
        self.discarded   = set()       # backtracked cells
        self.anim_index  = 0           # current animation step
        self.animating   = False
        self.solved      = False
        self.no_path     = False
        self.mode        = "SET_WALLS" # SET_WALLS | SET_PHERO | SET_START | SET_HOME
        self.status_msg  = "Draw walls, set pheromones, then RUN."


# ── Button helper ─────────────────────────────────────────────
class Button:
    def __init__(self, rect, label, color=BTN_NORMAL):
        self.rect   = pygame.Rect(rect)
        self.label  = label
        self.color  = color
        self.active = False

    def draw(self, surf, font):
        col = BTN_ACTIVE if self.active else self.color
        mx, my = pygame.mouse.get_pos()
        if self.rect.collidepoint(mx, my) and not self.active:
            col = BTN_HOVER
        pygame.draw.rect(surf, col, self.rect, border_radius=6)
        pygame.draw.rect(surf, (80, 80, 110), self.rect, 1, border_radius=6)
        txt = font.render(self.label, True, WHITE)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


# ── Drawing helpers ────────────────────────────────────────────
def cell_rect(x, y):
    return pygame.Rect(x * CELL_SIZE + MARGIN,
                       y * CELL_SIZE + MARGIN,
                       CELL_SIZE - MARGIN * 2,
                       CELL_SIZE - MARGIN * 2)


def phero_color(value):
    """Interpolate between EMPTY and PHERO_COL based on pheromone strength."""
    t = min(value / 2.0, 1.0)
    return tuple(int(EMPTY[i] + (PHERO_COL[i] - EMPTY[i]) * t) for i in range(3))


def draw_grid(surf, gs, anim_path, font_small):
    # Background
    surf.fill(BG, (0, 0, GRID_COLS * CELL_SIZE, WIN_H))

    for y in range(GRID_ROWS):
        for x in range(GRID_COLS):
            pos = (x, y)
            r   = cell_rect(x, y)

            # Base color
            if pos in gs.walls:
                color = WALL_COL
            elif gs.pheromones.get(pos, 0) > 0:
                color = phero_color(gs.pheromones[pos])
            else:
                color = EMPTY

            # Overlay: discarded (backtracked)
            if pos in gs.discarded and pos not in gs.walls:
                color = DISCARD_COL

            # Overlay: active path (only up to animation index)
            if anim_path and pos in anim_path:
                color = PATH_COL

            pygame.draw.rect(surf, color, r, border_radius=4)

            # Pheromone value label
            ph = gs.pheromones.get(pos, 0)
            if ph > 0 and pos not in gs.walls:
                lbl = font_small.render(f"{ph:.1f}", True, (30, 30, 30))
                surf.blit(lbl, lbl.get_rect(center=r.center))

    # Home
    hr = cell_rect(*gs.home_pos)
    pygame.draw.rect(surf, HOME_COL, hr, border_radius=4)
    pygame.draw.rect(surf, (255, 120, 100), hr, 2, border_radius=4)

    # Ant (animated position or start)
    if anim_path:
        ax, ay = anim_path[-1]
    else:
        ax, ay = gs.ant_pos
    ar = cell_rect(ax, ay)
    pygame.draw.ellipse(surf, ANT_COL, ar.inflate(-10, -10))
    pygame.draw.ellipse(surf, (255, 240, 100), ar.inflate(-18, -18), 2)

    # Grid lines
    for x in range(GRID_COLS + 1):
        pygame.draw.line(surf, GRID_LINE,
                         (x * CELL_SIZE, 0), (x * CELL_SIZE, WIN_H))
    for y in range(GRID_ROWS + 1):
        pygame.draw.line(surf, GRID_LINE,
                         (0, y * CELL_SIZE), (GRID_COLS * CELL_SIZE, y * CELL_SIZE))


def draw_hud(surf, gs, buttons, font, font_small):
    hx = GRID_COLS * CELL_SIZE
    pygame.draw.rect(surf, HUD_BG, (hx, 0, HUD_WIDTH, WIN_H))
    pygame.draw.line(surf, GRID_LINE, (hx, 0), (hx, WIN_H))

    y_cur = 16

    # Title
    title = font.render("ANT COLONY", True, ANT_COL)
    surf.blit(title, (hx + HUD_WIDTH // 2 - title.get_width() // 2, y_cur))
    y_cur += 30
    sub = font_small.render("Variant 13", True, TEXT_DIM)
    surf.blit(sub, (hx + HUD_WIDTH // 2 - sub.get_width() // 2, y_cur))
    y_cur += 28

    pygame.draw.line(surf, GRID_LINE, (hx + 10, y_cur), (hx + HUD_WIDTH - 10, y_cur))
    y_cur += 12

    # Mode label
    mode_lbl = font_small.render("CURRENT MODE:", True, TEXT_DIM)
    surf.blit(mode_lbl, (hx + 10, y_cur))
    y_cur += 18
    mode_txt = font_small.render(gs.mode.replace("_", " "), True, BTN_ACTIVE)
    surf.blit(mode_txt, (hx + 10, y_cur))
    y_cur += 26

    pygame.draw.line(surf, GRID_LINE, (hx + 10, y_cur), (hx + HUD_WIDTH - 10, y_cur))
    y_cur += 12

    # Buttons
    for btn in buttons:
        btn.rect.topleft = (hx + 10, y_cur)
        btn.rect.width   = HUD_WIDTH - 20
        btn.rect.height  = 32
        btn.draw(surf, font_small)
        y_cur += 38

    pygame.draw.line(surf, GRID_LINE, (hx + 10, y_cur), (hx + HUD_WIDTH - 10, y_cur))
    y_cur += 12

    # Legend
    legend = [
        (ANT_COL,     "Ant"),
        (HOME_COL,    "Home / Nest"),
        (PATH_COL,    "Active path"),
        (DISCARD_COL, "Backtracked"),
        (PHERO_COL,   "Pheromone"),
        (WALL_COL,    "Wall"),
    ]
    lbl = font_small.render("LEGEND", True, TEXT_DIM)
    surf.blit(lbl, (hx + 10, y_cur))
    y_cur += 18
    for color, name in legend:
        pygame.draw.rect(surf, color, (hx + 10, y_cur + 3, 14, 14), border_radius=3)
        t = font_small.render(name, True, TEXT_COL)
        surf.blit(t, (hx + 30, y_cur))
        y_cur += 20

    y_cur += 6
    pygame.draw.line(surf, GRID_LINE, (hx + 10, y_cur), (hx + HUD_WIDTH - 10, y_cur))
    y_cur += 10

    # Status message (word-wrap simple)
    words  = gs.status_msg.split()
    line   = ""
    for w in words:
        test = line + w + " "
        if font_small.size(test)[0] > HUD_WIDTH - 20:
            surf.blit(font_small.render(line, True, TEXT_COL), (hx + 10, y_cur))
            y_cur += 17
            line = w + " "
        else:
            line = test
    if line:
        surf.blit(font_small.render(line, True, TEXT_COL), (hx + 10, y_cur))


# ── Main ──────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Ant Colony — CS1 Project")
    clock  = pygame.time.Clock()

    font       = pygame.font.SysFont("consolas", 15, bold=True)
    font_small = pygame.font.SysFont("consolas", 13)

    gs = GameState()

    # HUD buttons
    btn_walls  = Button((0, 0, 0, 32), "DRAW WALLS")
    btn_remw   = Button((0, 0, 0, 32), "REMOVE WALLS")
    btn_phero  = Button((0, 0, 0, 32), "ADD PHEROMONE")
    btn_remph  = Button((0, 0, 0, 32), "REMOVE PHERO")
    btn_start  = Button((0, 0, 0, 32), "SET START")
    btn_home   = Button((0, 0, 0, 32), "SET HOME")
    btn_run    = Button((0, 0, 0, 32), "RUN",   color=(60, 120, 60))
    btn_reset  = Button((0, 0, 0, 32), "RESET", color=(120, 60, 60))

    mode_buttons = [btn_walls, btn_remw, btn_phero, btn_remph, btn_start, btn_home]
    all_buttons  = mode_buttons + [btn_run, btn_reset]

    mode_map = {
        btn_walls : "SET_WALLS",
        btn_remw  : "REMOVE_WALLS",
        btn_phero : "SET_PHERO",
        btn_remph : "REMOVE_PHERO",
        btn_start : "SET_START",
        btn_home  : "SET_HOME",
    }

    btn_walls.active = True   # default mode

    # Animation state
    anim_path  = []
    anim_index = 0
    animating  = False
    last_step  = 0.0

    def activate_mode(btn):
        for b in mode_buttons:
            b.active = False
        btn.active = True
        gs.mode = mode_map[btn]

    def do_run():
        nonlocal anim_path, anim_index, animating, last_step
        gs.solved   = False
        gs.no_path  = False
        gs.discarded = set()
        anim_path   = []
        anim_index  = 0
        animating   = False

        # Write input.json and optionally run C++ engine
        write_input(gs.grid_size, gs.ant_pos, gs.home_pos,
                    gs.walls, gs.pheromones)
        run_engine()   # updates state.json (C++ stores trail + BST)

        # Python backtracking solver
        path, disc = solve(gs.ant_pos, gs.home_pos,
                           gs.grid_size, gs.walls, gs.pheromones)
        gs.discarded = disc

        if path:
            gs.path     = path
            gs.solved   = True
            anim_path   = []
            anim_index  = 0
            animating   = True
            last_step   = time.time()
            gs.status_msg = f"Path found! {len(path)} steps."
        else:
            gs.no_path    = True
            gs.status_msg = "No path to nest found."

    def handle_cell_click(mx, my):
        if mx >= GRID_COLS * CELL_SIZE:
            return
        cx = mx // CELL_SIZE
        cy = my // CELL_SIZE
        pos = (cx, cy)

        if gs.mode == "SET_WALLS":
            if pos != gs.ant_pos and pos != gs.home_pos:
                gs.walls.add(pos)
        elif gs.mode == "REMOVE_WALLS":
            gs.walls.discard(pos)
        elif gs.mode == "SET_PHERO":
            current = gs.pheromones.get(pos, 0.0)
            gs.pheromones[pos] = min(round(current + 0.5, 1), 2.0)
        elif gs.mode == "REMOVE_PHERO":
            gs.pheromones.pop(pos, None)
        elif gs.mode == "SET_START":
            if pos not in gs.walls and pos != gs.home_pos:
                gs.ant_pos = pos
                activate_mode(btn_walls)
        elif gs.mode == "SET_HOME":
            if pos not in gs.walls and pos != gs.ant_pos:
                gs.home_pos = pos
                activate_mode(btn_walls)

    running = True
    while running:
        clock.tick(FPS)
        now = time.time()
        # Advance animation
        if animating and gs.solved:
            if now - last_step >= ANIM_DELAY:
                if anim_index < len(gs.path):
                    anim_path = gs.path[:anim_index + 1]
                    anim_index += 1
                    last_step = now
                else:
                    animating = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Mouse drag for walls/pheromones
            if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
                handle_cell_click(*event.pos)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_cell_click(*event.pos)

                for btn in all_buttons:
                    if btn.is_clicked(event):
                        if btn in mode_buttons:
                            activate_mode(btn)
                        elif btn == btn_run:
                            do_run()
                        elif btn == btn_reset:
                            gs.reset()
                            anim_path  = []
                            anim_index = 0
                            animating  = False
                            activate_mode(btn_walls)

        draw_grid(screen, gs, anim_path, font_small)
        draw_hud(screen, gs, all_buttons, font, font_small)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()