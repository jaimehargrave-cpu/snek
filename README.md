# Terminal Snake

A colorful terminal Snake game written in Python. Eat berries, chain combos, dodge moving hazards, and aim for the high-score table.

## Setup and run

See [DOWNLOAD.MD](./DOWNLOAD.MD) for full setup instructions.

```bash
python3 snek.py
```

On Windows, install `windows-curses` with `py -m pip install windows-curses`, then run `py snek.py`.

## Features

- **Start screen:** choose Classic or Hard mode, board size, snake skin, and sound setting.
- **Modes:** Hard mode starts faster, includes more static and moving hazards, and gives you fewer lives.
- **Lives and shields:** you get three lives in Classic and two in Hard; a shield berry absorbs a collision and costs one life.
- **Six berries:** normal, boost, slow, shield, bonus, and shrink berries, each with a distinct glyph and effect.
- **Combos:** collect berries within five seconds of each other for bonus points.
- **Hazards:** avoid static `##` obstacles and moving `><` hazards.
- **Local leaderboard:** top five scores are saved separately by mode in `.snek_scores.json` in your home directory. Scores stay on your device.
- **Skins and board sizes:** cycle through four snake colors and three board sizes from the start screen.
- **Pause menu:** press **P** to resume or change the sound setting; **Q** ends the round.
- **New-record screen:** get a message when you beat your previous best.
- **Terminal-bell sound effects:** toggle on the start screen or pause menu.

## Controls

| Key | Action |
| --- | --- |
| Arrow keys or **WASD** | Move |
| **P** | Open pause menu |
| **Q** | Quit the current round |
| **R** | Retry after game over |
| **M** | Return to the start screen after game over |
| **H** | Toggle Classic/Hard mode on the start screen |
| **B** | Change board size on the start screen |
| **C** | Change snake color on the start screen |
| **S** | Toggle sound on the start screen or pause menu |

## Berry guide

| Berry | Glyph | Points | Effect |
| --- | --- | ---: | --- |
| Normal | `()` | 10 | Grows the snake |
| Boost | `++` | 20 | Speeds up the snake for 7 seconds |
| Slow | `--` | 15 | Slows the snake for 7 seconds |
| Shield | `[]` | 15 | Absorbs one collision and uses one life |
| Bonus | `**` | 50 | Gives a large score boost |
| Shrink | `<>` | 15 | Shortens the snake by up to two segments |

## Roadmap

- Add automated tests for game rules and scoring.
- Improve terminal resizing and accessibility.
- Consider additional levels, berry effects, and customization options.

## Requirements

- Python 3
- Windows only: `windows-curses`
- A terminal at least 38 columns wide and 22 rows tall
