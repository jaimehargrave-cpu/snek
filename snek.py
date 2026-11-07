#!/usr/bin/env python3
"""
Terminal Snake
--------------
Controls: Arrow keys or WASD to move, P to pause, Q to quit.
Run:      python3 snake.py
Windows:  pip install windows-curses   (then run the same way)
"""

import curses
import random
import time

UP, DOWN, LEFT, RIGHT = (-1, 0), (1, 0), (0, -1), (0, 1)

KEYS = {
    curses.KEY_UP: UP, ord("w"): UP, ord("W"): UP,
    curses.KEY_DOWN: DOWN, ord("s"): DOWN, ord("S"): DOWN,
    curses.KEY_LEFT: LEFT, ord("a"): LEFT, ord("A"): LEFT,
    curses.KEY_RIGHT: RIGHT, ord("d"): RIGHT, ord("D"): RIGHT,
}

HEAD, BODY = "@@", "oo"
BERRY_TYPES = {
    "normal": {"glyph": "()", "points": 10, "color": 2, "effect": "grow"},
    "boost": {"glyph": "++", "points": 20, "color": 5, "effect": "boost"},
    "slow": {"glyph": "--", "points": 15, "color": 6, "effect": "slow"},
    "shield": {"glyph": "[]", "points": 15, "color": 7, "effect": "shield"},
}


def put(win, y, x, text, attr=0):
    """addstr that ignores errors at screen edges."""
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass


def draw_frame(win, y0, x0, rows, cols):
    width = cols * 2
    put(win, y0, x0, "+" + "-" * width + "+", curses.color_pair(3))
    for r in range(rows):
        put(win, y0 + 1 + r, x0, "|", curses.color_pair(3))
        put(win, y0 + 1 + r, x0 + width + 1, "|", curses.color_pair(3))
    put(win, y0 + rows + 1, x0, "+" + "-" * width + "+", curses.color_pair(3))


def spawn_obstacles(rows, cols, snake):
    free = [(r, c) for r in range(rows) for c in range(cols) if (r, c) not in snake]
    if not free:
        return set()
    count = min(8, max(4, (rows * cols) // 30))
    obstacles = set()
    for _ in range(count):
        if not free:
            break
        cell = random.choice(free)
        free.remove(cell)
        obstacles.add(cell)
    return obstacles


def spawn_food(snake, rows, cols, obstacles):
    free = [(r, c) for r in range(rows) for c in range(cols)
            if (r, c) not in snake and (r, c) not in obstacles]
    if not free:
        return None, None
    cell = random.choice(free)
    berry = random.choices(
        list(BERRY_TYPES.keys()),
        weights=[60, 15, 15, 10],
        k=1,
    )[0]
    return cell, berry


def play(stdscr, high_score):
    sh, sw = stdscr.getmaxyx()
    rows = max(8, min(sh - 6, 20))
    cols = max(8, min((sw - 4) // 2, 30))
    y0 = max(2, (sh - rows - 2) // 2)
    x0 = max(0, (sw - (cols * 2 + 2)) // 2)

    snake = [(rows // 2, cols // 2 - i) for i in range(3)]
    direction = RIGHT
    pending = RIGHT
    obstacles = spawn_obstacles(rows, cols, snake)
    food, food_kind = spawn_food(snake, rows, cols, obstacles)
    score = 0
    paused = False
    shield_charges = 0
    boost_until = 0.0
    slow_until = 0.0

    stdscr.erase()
    while True:
        stdscr.erase()
        title = " SNAKE.EXE "
        put(stdscr, y0 - 2, x0, title, curses.color_pair(4) | curses.A_BOLD)
        status = f"SCORE:{score:04d}  HI:{max(score, high_score):04d}"
        if shield_charges > 0:
            status += "  SHIELD"
        put(stdscr, y0 - 1, x0, status, curses.color_pair(1))
        draw_frame(stdscr, y0, x0, rows, cols)

        for r, c in obstacles:
            put(stdscr, y0 + 1 + r, x0 + 1 + c * 2, "##", curses.color_pair(3) | curses.A_BOLD)

        if food:
            berry = BERRY_TYPES[food_kind]
            put(stdscr, y0 + 1 + food[0], x0 + 1 + food[1] * 2, berry["glyph"],
                curses.color_pair(berry["color"]) | curses.A_BOLD)
        for i, (r, c) in enumerate(snake):
            if i == 0:
                put(stdscr, y0 + 1 + r, x0 + 1 + c * 2, HEAD,
                    curses.color_pair(1) | curses.A_BOLD)
            else:
                put(stdscr, y0 + 1 + r, x0 + 1 + c * 2, BODY, curses.color_pair(1))

        footer = "[WASD/Arrows] move  [P] pause  [Q] quit"
        if time.monotonic() < boost_until:
            footer += "  BOOST"
        elif time.monotonic() < slow_until:
            footer += "  SLOW"
        put(stdscr, y0 + rows + 3, x0, footer, curses.color_pair(3))
        if paused:
            put(stdscr, y0 + rows // 2, x0 + cols - 3, " PAUSED ",
                curses.color_pair(4) | curses.A_REVERSE)
        stdscr.refresh()

        now = time.monotonic()
        delay = max(0.04, 0.14 - score * 0.003)
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
        if not (0 <= head[0] < rows and 0 <= head[1] < cols):
            if shield_charges > 0:
                shield_charges -= 1
                continue
            return score, False

        if head in body_check or head in obstacles:
            if shield_charges > 0:
                shield_charges -= 1
                continue
            return score, False

        snake.insert(0, head)
        if will_eat:
            berry = BERRY_TYPES[food_kind]
            score += berry["points"]
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
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)   # snake / status
    curses.init_pair(2, curses.COLOR_RED, -1)     # food / game over
    curses.init_pair(3, curses.COLOR_CYAN, -1)    # frame / hints
    curses.init_pair(4, curses.COLOR_YELLOW, -1)  # title
    curses.init_pair(5, curses.COLOR_MAGENTA, -1) # boost berry
    curses.init_pair(6, curses.COLOR_BLUE, -1)    # slow berry
    curses.init_pair(7, curses.COLOR_WHITE, -1)   # shield berry

    sh, sw = stdscr.getmaxyx()
    if sh < 16 or sw < 30:
        stdscr.nodelay(False)
        put(stdscr, 0, 0, "Terminal too small. Resize and rerun.")
        stdscr.getch()
        return

    high_score = 0
    while True:
        score, quit_game = play(stdscr, high_score)
        high_score = max(high_score, score)
        if quit_game or not game_over(stdscr, score, high_score):
            break


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass

