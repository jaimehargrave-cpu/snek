#!/usr/bin/env python3
"""
Terminal Snake
--------------
Run: python3 snek.py (macOS/Linux) or py snek.py (Windows)
On Windows, install windows-curses first: py -m pip install windows-curses
"""

import curses
import json
import random
import time
from pathlib import Path

UP, DOWN, LEFT, RIGHT = (-1, 0), (1, 0), (0, -1), (0, 1)
KEYS = {
    curses.KEY_UP: UP, ord("w"): UP, ord("W"): UP,
    curses.KEY_DOWN: DOWN, ord("s"): DOWN, ord("S"): DOWN,
    curses.KEY_LEFT: LEFT, ord("a"): LEFT, ord("A"): LEFT,
    curses.KEY_RIGHT: RIGHT, ord("d"): RIGHT, ord("D"): RIGHT,
}

HEAD, BODY = "@@", "oo"
SCORE_FILE = Path.home() / ".snek_scores.json"
BERRY_TYPES = {
    "normal": {"glyph": "()", "points": 10, "color": 2, "effect": "grow"},
    "boost": {"glyph": "++", "points": 20, "color": 5, "effect": "boost"},
    "slow": {"glyph": "--", "points": 15, "color": 6, "effect": "slow"},
    "shield": {"glyph": "[]", "points": 15, "color": 7, "effect": "shield"},
}


def put(win, y, x, text, attr=0):
    """Draw text while safely ignoring terminal-edge errors."""
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass


def play_sound(enabled):
    """Use the terminal bell for simple, dependency-free sound effects."""
    if enabled:
        try:
            curses.beep()
        except curses.error:
            pass


def load_scores():
    try:
        data = json.loads(SCORE_FILE.read_text(encoding="utf-8"))
        return {
            mode: sorted((int(score) for score in data.get(mode, []) if int(score) >= 0), reverse=True)[:5]
            for mode in ("classic", "hard")
        }
    except (OSError, ValueError, TypeError):
        return {"classic": [], "hard": []}


def save_score(scores, mode, score):
    scores.setdefault(mode, []).append(score)
    scores[mode] = sorted(scores[mode], reverse=True)[:5]
    try:
        SCORE_FILE.write_text(json.dumps(scores, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass  # The game remains playable if the score file cannot be saved.


def draw_frame(win, y0, x0, rows, cols):
    width = cols * 2
    put(win, y0, x0, "+" + "-" * width + "+", curses.color_pair(3))
    for r in range(rows):
        put(win, y0 + 1 + r, x0, "|", curses.color_pair(3))
        put(win, y0 + 1 + r, x0 + width + 1, "|", curses.color_pair(3))
    put(win, y0 + rows + 1, x0, "+" + "-" * width + "+", curses.color_pair(3))


def spawn_obstacles(rows, cols, snake, hard_mode):
    free = [(r, c) for r in range(rows) for c in range(cols) if (r, c) not in snake]
    count = min((20 if hard_mode else 8), max((12 if hard_mode else 4), (rows * cols) // (18 if hard_mode else 30)))
    count = min(count, len(free))
    return set(random.sample(free, count))


def spawn_food(snake, rows, cols, obstacles):
    occupied = set(snake) | obstacles
    free = [(r, c) for r in range(rows) for c in range(cols) if (r, c) not in occupied]
    if not free:
        return None, None
    cell = random.choice(free)
    berry = random.choices(list(BERRY_TYPES), weights=[60, 15, 15, 10], k=1)[0]
    return cell, berry


def start_screen(stdscr, scores, sound_enabled):
    hard_mode = False
    stdscr.nodelay(False)
    while True:
        stdscr.erase()
        sh, sw = stdscr.getmaxyx()
        x = max(0, (sw - 48) // 2)
        y = max(0, sh // 2 - 9)
        put(stdscr, y, x, "TERMINAL SNAKE", curses.color_pair(4) | curses.A_BOLD)
        put(stdscr, y + 2, x, "Eat berries, avoid walls, and grow your snake.")
        put(stdscr, y + 4, x, f"Mode: {'HARD' if hard_mode else 'CLASSIC'}  (H toggles)", curses.color_pair(5) | curses.A_BOLD)
        put(stdscr, y + 5, x, f"Terminal bell sounds: {'ON' if sound_enabled else 'OFF'}  (S toggles)")
        put(stdscr, y + 7, x, "High scores:", curses.A_BOLD)
        mode = "hard" if hard_mode else "classic"
        entries = scores.get(mode, [])
        if entries:
            for i, score in enumerate(entries[:5], 1):
                put(stdscr, y + 8 + i, x, f"{i}. {score}")
        else:
            put(stdscr, y + 9, x, "No scores yet — set the first one!")
        put(stdscr, y + 15, x, "ENTER start   H mode   S sound   Q quit", curses.color_pair(3))
        stdscr.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_ENTER, 10, 13):
            return hard_mode, sound_enabled, False
        if key in (ord("h"), ord("H")):
            hard_mode = not hard_mode
        elif key in (ord("s"), ord("S")):
            sound_enabled = not sound_enabled
        elif key in (ord("q"), ord("Q")):
            return hard_mode, sound_enabled, True


def play(stdscr, high_score, hard_mode, sound_enabled):
    sh, sw = stdscr.getmaxyx()
    rows = max(8, min(sh - 6, 20))
    cols = max(8, min((sw - 4) // 2, 30))
    y0 = max(2, (sh - rows - 2) // 2)
    x0 = max(0, (sw - (cols * 2 + 2)) // 2)

    snake = [(rows // 2, cols // 2 - i) for i in range(3)]
    direction = pending = RIGHT
    obstacles = spawn_obstacles(rows, cols, snake, hard_mode)
    food, food_kind = spawn_food(snake, rows, cols, obstacles)
    score = 0
    paused = False
    shield_charges = 0
    boost_until = slow_until = 0.0

    while True:
        stdscr.erase()
        mode_label = "HARD" if hard_mode else "CLASSIC"
        put(stdscr, y0 - 2, x0, f" SNAKE.EXE — {mode_label} ", curses.color_pair(4) | curses.A_BOLD)
        status = f"SCORE:{score:04d}  HI:{max(score, high_score):04d}"
        if shield_charges:
            status += f"  SHIELD x{shield_charges}"
        put(stdscr, y0 - 1, x0, status, curses.color_pair(1))
        draw_frame(stdscr, y0, x0, rows, cols)
        for r, c in obstacles:
            put(stdscr, y0 + 1 + r, x0 + 1 + c * 2, "##", curses.color_pair(3) | curses.A_BOLD)
        if food:
            berry = BERRY_TYPES[food_kind]
            put(stdscr, y0 + 1 + food[0], x0 + 1 + food[1] * 2, berry["glyph"],
                curses.color_pair(berry["color"]) | curses.A_BOLD)
        for i, (r, c) in enumerate(snake):
            put(stdscr, y0 + 1 + r, x0 + 1 + c * 2, HEAD if i == 0 else BODY,
                curses.color_pair(1) | (curses.A_BOLD if i == 0 else 0))
        now = time.monotonic()
        effects = []
        if now < boost_until:
            effects.append("BOOST")
        if now < slow_until:
            effects.append("SLOW")
        footer = "[WASD/Arrows] move  [P] pause  [Q] quit"
        if effects:
            footer += "  " + " ".join(effects)
        put(stdscr, y0 + rows + 3, x0, footer, curses.color_pair(3))
        if paused:
            put(stdscr, y0 + rows // 2, x0 + cols - 3, " PAUSED ", curses.color_pair(4) | curses.A_REVERSE)
        stdscr.refresh()

        now = time.monotonic()
        delay = max(0.04, 0.14 - score * 0.003)
        if hard_mode:
            delay *= 0.78
        if now < boost_until:
            delay *= 0.72
        if now < slow_until:
            delay *= 1.45
        end = time.monotonic() + delay
        while time.monotonic() < end:
            key = stdscr.getch()
            if key in (ord("q"), ord("Q")):
                return score, True
            if key in (ord("p"), ord("P")):
                paused = not paused
            if key in KEYS and not paused:
                new = KEYS[key]
                if (new[0] + direction[0], new[1] + direction[1]) != (0, 0):
                    pending = new
            time.sleep(0.005)
        if paused:
            continue

        direction = pending
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        will_eat = head == food if food else False
        body_check = snake if will_eat else snake[:-1]
        collision = not (0 <= head[0] < rows and 0 <= head[1] < cols) or head in body_check or head in obstacles
        if collision:
            if shield_charges:
                shield_charges -= 1
                snake = [(rows // 2, cols // 2 - i) for i in range(3)]
                direction = pending = RIGHT
                if food in snake:
                    food, food_kind = spawn_food(snake, rows, cols, obstacles)
                continue
            play_sound(sound_enabled)
            return score, False

        snake.insert(0, head)
        if will_eat:
            berry = BERRY_TYPES[food_kind]
            score += berry["points"]
            play_sound(sound_enabled)
            if berry["effect"] == "boost":
                boost_until = time.monotonic() + 7
            elif berry["effect"] == "slow":
                slow_until = time.monotonic() + 7
            elif berry["effect"] == "shield":
                shield_charges += 1
            food, food_kind = spawn_food(snake, rows, cols, obstacles)
            if food is None:
                return score, False
        else:
            snake.pop()


def game_over(stdscr, score, high_score):
    sh, sw = stdscr.getmaxyx()
    lines = [
        "+--------------------------+",
        "|        GAME  OVER        |",
        f"|   score: {score:<5} hi: {high_score:<5}  |",
        "|                          |",
        "|   [R] retry   [Q] quit   |",
        "+--------------------------+",
    ]
    y = max(0, sh // 2 - len(lines) // 2)
    x = max(0, sw // 2 - len(lines[0]) // 2)
    for i, line in enumerate(lines):
        put(stdscr, y + i, x, line, curses.color_pair(2) | curses.A_BOLD)
    stdscr.refresh()
    stdscr.nodelay(False)
    while True:
        key = stdscr.getch()
        if key in (ord("r"), ord("R")):
            stdscr.nodelay(True)
            return True
        if key in (ord("q"), ord("Q")):
            return False


def main(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    stdscr.keypad(True)
    curses.start_color()
    try:
        curses.use_default_colors()
        background = -1
    except curses.error:
        background = curses.COLOR_BLACK
    for pair, fg in ((1, curses.COLOR_GREEN), (2, curses.COLOR_RED), (3, curses.COLOR_CYAN),
                     (4, curses.COLOR_YELLOW), (5, curses.COLOR_MAGENTA), (6, curses.COLOR_BLUE),
                     (7, curses.COLOR_WHITE)):
        try:
            curses.init_pair(pair, fg, background)
        except curses.error:
            pass

    if curses.LINES < 16 or curses.COLS < 30:
        stdscr.nodelay(False)
        put(stdscr, 0, 0, "Terminal too small. Resize and rerun.")
        stdscr.getch()
        return

    scores = load_scores()
    sound_enabled = True
    while True:
        hard_mode, sound_enabled, quit_game = start_screen(stdscr, scores, sound_enabled)
        if quit_game:
            break
        mode = "hard" if hard_mode else "classic"
        high_score = max(scores.get(mode, [0]))
        while True:
            score, quit_round = play(stdscr, high_score, hard_mode, sound_enabled)
            save_score(scores, mode, score)
            high_score = max(high_score, score)
            if quit_round or not game_over(stdscr, score, high_score):
                break


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
