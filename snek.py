#!/usr/bin/env python3
"""Terminal Snake — run with `python3 snek.py` or `py snek.py` on Windows."""

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
BOARD_SIZES = ((12, 20), (16, 28), (20, 36))
SKINS = ("Green", "Cyan", "Magenta", "Yellow")
SKIN_COLORS = (1, 3, 5, 4)
BERRY_TYPES = {
    "normal": {"glyph": "()", "points": 10, "color": 2, "effect": "grow"},
    "boost": {"glyph": "++", "points": 20, "color": 5, "effect": "boost"},
    "slow": {"glyph": "--", "points": 15, "color": 6, "effect": "slow"},
    "shield": {"glyph": "[]", "points": 15, "color": 7, "effect": "shield"},
    "bonus": {"glyph": "**", "points": 50, "color": 4, "effect": "bonus"},
    "shrink": {"glyph": "<> ", "points": 15, "color": 3, "effect": "shrink"},
}


def put(win, y, x, text, attr=0):
    """Draw text while safely ignoring terminal-edge errors."""
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass


def play_sound(enabled):
    """Use the terminal bell for dependency-free sound effects."""
    if enabled:
        try:
            curses.beep()
        except curses.error:
            pass


def load_scores():
    try:
        data = json.loads(SCORE_FILE.read_text(encoding="utf-8"))
        scores = {}
        for mode in ("classic", "hard"):
            values = data.get(mode, [])
            scores[mode] = sorted((int(value) for value in values if int(value) >= 0), reverse=True)[:5]
        return scores
    except (OSError, ValueError, TypeError, AttributeError):
        return {"classic": [], "hard": []}


def save_score(scores, mode, score):
    scores.setdefault(mode, []).append(score)
    scores[mode] = sorted(scores[mode], reverse=True)[:5]
    try:
        SCORE_FILE.write_text(json.dumps(scores, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def score_for_berry(points, combo):
    """Add a small, capped bonus for consecutive berries."""
    return points + min(max(combo - 1, 0), 4) * 5


def is_collision(head, rows, cols, snake, obstacles, hazards, eating=False):
    """Return whether a move hits a wall, body, obstacle, or moving hazard."""
    body = snake if eating else snake[:-1]
    return (
        not (0 <= head[0] < rows and 0 <= head[1] < cols)
        or head in body or head in obstacles or head in hazards
    )


def draw_frame(win, y0, x0, rows, cols):
    width = cols * 2
    put(win, y0, x0, "+" + "-" * width + "+", curses.color_pair(3))
    for r in range(rows):
        put(win, y0 + 1 + r, x0, "|", curses.color_pair(3))
        put(win, y0 + 1 + r, x0 + width + 1, "|", curses.color_pair(3))
    put(win, y0 + rows + 1, x0, "+" + "-" * width + "+", curses.color_pair(3))


def spawn_obstacles(rows, cols, snake, hard_mode):
    occupied = set(snake)
    center = (rows // 2, cols // 2)
    free = [(r, c) for r in range(rows) for c in range(cols)
            if (r, c) not in occupied and abs(r - center[0]) + abs(c - center[1]) > 4]
    count = min((20 if hard_mode else 8), max((12 if hard_mode else 4), (rows * cols) // (18 if hard_mode else 30)))
    return set(random.sample(free, min(count, len(free))))


def spawn_food(snake, rows, cols, obstacles, hazards=()):
    occupied = set(snake) | set(obstacles) | set(hazards)
    free = [(r, c) for r in range(rows) for c in range(cols) if (r, c) not in occupied]
    if not free:
        return None, None
    berry = random.choices(list(BERRY_TYPES), weights=[50, 15, 12, 9, 7, 7], k=1)[0]
    return random.choice(free), berry


def spawn_hazards(rows, cols, snake, obstacles, food=None, count=2):
    blocked = set(snake) | set(obstacles)
    if food:
        blocked.add(food)
    choices = [(r, c) for r in range(rows) for c in range(cols) if (r, c) not in blocked]
    return set(random.sample(choices, min(count, len(choices))))


def move_hazards(hazards, rows, cols, snake, obstacles, food):
    blocked = set(snake) | set(obstacles)
    if food:
        blocked.add(food)
    available = [(r, c) for r in range(rows) for c in range(cols) if (r, c) not in blocked]
    if not available:
        return hazards
    count = len(hazards)
    return set(random.sample(available, min(count, len(available))))


def start_screen(stdscr, scores, sound_enabled, board_index, skin_index):
    hard_mode = False
    stdscr.nodelay(False)
    while True:
        stdscr.erase()
        sh, sw = stdscr.getmaxyx()
        x = max(0, (sw - 54) // 2)
        y = max(0, sh // 2 - 10)
        put(stdscr, y, x, "TERMINAL SNAKE V2", curses.color_pair(4) | curses.A_BOLD)
        put(stdscr, y + 2, x, "Eat berries, build combos, and dodge hazards!")
        mode = "HARD" if hard_mode else "CLASSIC"
        put(stdscr, y + 4, x, f"Mode: {mode} (H)   Board: {('Small', 'Medium', 'Large')[board_index]} (B)")
        put(stdscr, y + 5, x, f"Snake skin: {SKINS[skin_index]} (C)   Terminal bell: {'ON' if sound_enabled else 'OFF'} (S)")
        put(stdscr, y + 7, x, f"Top {mode} scores:", curses.A_BOLD)
        entries = scores.get("hard" if hard_mode else "classic", [])
        if entries:
            for i, score in enumerate(entries[:5], 1):
                put(stdscr, y + 8 + i, x, f"{i}. {score}")
        else:
            put(stdscr, y + 9, x, "No scores yet — set the first one!")
        put(stdscr, y + 16, x, "ENTER start  H mode  B board  C skin  S sound  Q quit", curses.color_pair(3))
        stdscr.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_ENTER, 10, 13):
            return hard_mode, sound_enabled, board_index, skin_index, False
        if key in (ord("h"), ord("H")):
            hard_mode = not hard_mode
        elif key in (ord("b"), ord("B")):
            board_index = (board_index + 1) % len(BOARD_SIZES)
        elif key in (ord("c"), ord("C")):
            skin_index = (skin_index + 1) % len(SKINS)
        elif key in (ord("s"), ord("S")):
            sound_enabled = not sound_enabled
        elif key in (ord("q"), ord("Q")):
            return hard_mode, sound_enabled, board_index, skin_index, True


def pause_menu(stdscr, sound_enabled):
    stdscr.nodelay(False)
    while True:
        stdscr.erase()
        y = max(0, stdscr.getmaxyx()[0] // 2 - 3)
        x = max(0, stdscr.getmaxyx()[1] // 2 - 16)
        put(stdscr, y, x, "PAUSED", curses.A_BOLD | curses.A_REVERSE)
        put(stdscr, y + 2, x, "P resume   S sound: " + ("ON" if sound_enabled else "OFF"))
        put(stdscr, y + 3, x, "Q end round")
        stdscr.refresh()
        key = stdscr.getch()
        if key in (ord("p"), ord("P"), 10, 13):
            return "resume", sound_enabled
        if key in (ord("s"), ord("S")):
            sound_enabled = not sound_enabled
        elif key in (ord("q"), ord("Q")):
            return "quit", sound_enabled


def play(stdscr, high_score, hard_mode, sound_enabled, board_size, skin_index):
    sh, sw = stdscr.getmaxyx()
    requested_rows, requested_cols = board_size
    rows = max(8, min(requested_rows, sh - 6))
    cols = max(8, min(requested_cols, (sw - 4) // 2))
    y0 = max(2, (sh - rows - 2) // 2)
    x0 = max(0, (sw - (cols * 2 + 2)) // 2)
    center = (rows // 2, cols // 2)
    snake = [center, (center[0], center[1] - 1), (center[0], center[1] - 2)]
    direction = pending = RIGHT
    obstacles = spawn_obstacles(rows, cols, snake, hard_mode)
    hazards = spawn_hazards(rows, cols, snake, obstacles, count=3 if hard_mode else 2)
    food, food_kind = spawn_food(snake, rows, cols, obstacles, hazards)
    score, lives, combo = 0, (2 if hard_mode else 3), 0
    combo_time = boost_until = slow_until = next_hazard_move = 0.0
    shields = 0

    while True:
        stdscr.erase()
        mode_name = "HARD" if hard_mode else "CLASSIC"
        status = f"SCORE {score}  HI {max(score, high_score)}  LIVES {lives}  COMBO x{combo}"
        if shields:
            status += f"  SHIELD x{shields}"
        put(stdscr, y0 - 2, x0, f" SNEK V2 — {mode_name} — {SKINS[skin_index]} ", curses.color_pair(4) | curses.A_BOLD)
        put(stdscr, y0 - 1, x0, status, curses.color_pair(SKIN_COLORS[skin_index]) | curses.A_BOLD)
        draw_frame(stdscr, y0, x0, rows, cols)
        for r, c in obstacles:
            put(stdscr, y0 + 1 + r, x0 + 1 + c * 2, "##", curses.color_pair(3) | curses.A_BOLD)
        for r, c in hazards:
            put(stdscr, y0 + 1 + r, x0 + 1 + c * 2, "><", curses.color_pair(2) | curses.A_BOLD)
        if food:
            berry = BERRY_TYPES[food_kind]
            put(stdscr, y0 + 1 + food[0], x0 + 1 + food[1] * 2, berry["glyph"], curses.color_pair(berry["color"]) | curses.A_BOLD)
        for i, (r, c) in enumerate(snake):
            put(stdscr, y0 + 1 + r, x0 + 1 + c * 2, HEAD if i == 0 else BODY,
                curses.color_pair(SKIN_COLORS[skin_index]) | (curses.A_BOLD if i == 0 else 0))
        now = time.monotonic()
        active = [label for label, deadline in (("BOOST", boost_until), ("SLOW", slow_until)) if now < deadline]
        footer = "[WASD/Arrows] move  [P] pause  [Q] quit  Hazards: ><"
        if active:
            footer += "  " + " ".join(active)
        put(stdscr, y0 + rows + 3, x0, footer, curses.color_pair(3))
        stdscr.refresh()

        now = time.monotonic()
        delay = max(0.045, 0.14 - score * 0.0015)
        if hard_mode:
            delay *= 0.78
        if now < boost_until:
            delay *= 0.72
        if now < slow_until:
            delay *= 1.4
        end = time.monotonic() + delay
        while time.monotonic() < end:
            key = stdscr.getch()
            if key in (ord("q"), ord("Q")):
                return score, True
            if key in (ord("p"), ord("P")):
                action, sound_enabled = pause_menu(stdscr, sound_enabled)
                stdscr.nodelay(True)
                if action == "quit":
                    return score, True
                break
            if key in KEYS:
                new = KEYS[key]
                if (new[0] + direction[0], new[1] + direction[1]) != (0, 0):
                    pending = new
            time.sleep(0.005)
        else:
            pass
        # A pause breaks the input loop; do not advance the snake on that frame.
        if time.monotonic() >= end or key in (ord("p"), ord("P")):
            if key in (ord("p"), ord("P")):
                continue

        direction = pending
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        eating = head == food if food else False
        if is_collision(head, rows, cols, snake, obstacles, hazards, eating):
            if shields:
                shields -= 1
                lives -= 1
            else:
                lives -= 1
            if lives <= 0:
                play_sound(sound_enabled)
                return score, False
            snake = [center, (center[0], center[1] - 1), (center[0], center[1] - 2)]
            direction = pending = RIGHT
            if food in snake or food in obstacles or food in hazards:
                food, food_kind = spawn_food(snake, rows, cols, obstacles, hazards)
            continue

        snake.insert(0, head)
        if eating:
            now = time.monotonic()
            combo = combo + 1 if now - combo_time <= 5 else 1
            combo_time = now
            berry = BERRY_TYPES[food_kind]
            score += score_for_berry(berry["points"], combo)
            play_sound(sound_enabled)
            effect = berry["effect"]
            if effect == "boost":
                boost_until = now + 7
            elif effect == "slow":
                slow_until = now + 7
            elif effect == "shield":
                shields += 1
            elif effect == "shrink":
                for _ in range(min(2, len(snake) - 1)):
                    snake.pop()
            if effect != "shrink":
                # Eating berries normally grows the snake.
                pass
            food, food_kind = spawn_food(snake, rows, cols, obstacles, hazards)
            if food is None:
                return score, False
        else:
            snake.pop()

        if time.monotonic() >= next_hazard_move:
            hazards = move_hazards(hazards, rows, cols, snake, obstacles, food)
            next_hazard_move = time.monotonic() + (0.65 if hard_mode else 1.0)


def game_over(stdscr, score, high_score, new_record):
    sh, sw = stdscr.getmaxyx()
    lines = ["+------------------------------+", "|          GAME OVER           |",
             f"|       score: {score:<6}           |", f"|       best:  {high_score:<6}           |",
             "|        [R] retry             |", "|        [M] menu   [Q] quit   |", "+------------------------------+"]
    y = max(0, sh // 2 - len(lines) // 2)
    x = max(0, sw // 2 - len(lines[0]) // 2)
    for i, line in enumerate(lines):
        put(stdscr, y + i, x, line, curses.color_pair(4 if new_record else 2) | curses.A_BOLD)
    if new_record:
        put(stdscr, y + len(lines), x, "NEW HIGH SCORE!", curses.color_pair(4) | curses.A_BOLD)
    stdscr.refresh()
    stdscr.nodelay(False)
    while True:
        key = stdscr.getch()
        if key in (ord("r"), ord("R")):
            stdscr.nodelay(True)
            return "retry"
        if key in (ord("m"), ord("M")):
            return "menu"
        if key in (ord("q"), ord("Q")):
            return "quit"


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
    colors = (curses.COLOR_GREEN, curses.COLOR_RED, curses.COLOR_CYAN, curses.COLOR_YELLOW,
              curses.COLOR_MAGENTA, curses.COLOR_BLUE, curses.COLOR_WHITE)
    for pair, fg in enumerate(colors, 1):
        try:
            curses.init_pair(pair, fg, background)
        except curses.error:
            pass

    if curses.LINES < 22 or curses.COLS < 38:
        stdscr.nodelay(False)
        put(stdscr, 0, 0, "Terminal too small. Please resize to at least 38 columns by 22 rows.")
        stdscr.getch()
        return

    scores = load_scores()
    sound_enabled, board_index, skin_index = True, 1, 0
    while True:
        hard_mode, sound_enabled, board_index, skin_index, quit_game = start_screen(
            stdscr, scores, sound_enabled, board_index, skin_index)
        if quit_game:
            break
        mode = "hard" if hard_mode else "classic"
        board_size = BOARD_SIZES[board_index]
        previous_best = max(scores.get(mode, [0]))
        while True:
            score, quit_round = play(stdscr, previous_best, hard_mode, sound_enabled, board_size, skin_index)
            new_record = score > previous_best
            save_score(scores, mode, score)
            best = max(scores.get(mode, [0]))
            if quit_round:
                break
            result = game_over(stdscr, score, best, new_record)
            if result == "retry":
                previous_best = best
                continue
            if result == "quit":
                return
            break


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
