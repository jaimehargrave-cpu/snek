# Terminal Snake

A colorful Snake game that runs in your terminal, written in Python. Eat berries to score points, grow longer, and try to avoid the walls, your tail, and obstacles.

## Download and setup

See [DOWNLOAD.MD](./DOWNLOAD.MD) for step-by-step instructions to install Python, install the Windows terminal requirement if needed, download the game, and run it.

## Start the game

From the directory containing `snek.py`, run:

```bash
python3 snek.py
```

On Windows, install `windows-curses` once with `py -m pip install windows-curses`, then run:

```powershell
py snek.py
```

## Start screen

- Press **Enter** to play.
- Press **H** to switch between **Classic** and **Hard** mode.
- Press **S** to turn terminal-bell sound effects on or off.
- Press **Q** to quit.

Hard mode starts faster and places more obstacles on the board.

## Controls

| Key | Action |
| --- | --- |
| Arrow keys or **WASD** | Move |
| **P** | Pause or resume |
| **Q** | Quit the current round |
| **R** | Retry after game over |

## Berries and effects

| Berry | Appearance | Points | Effect |
| --- | --- | ---: | --- |
| Normal | `()` | 10 | Adds to your score and grows the snake |
| Boost | `++` | 20 | Temporarily speeds up the snake |
| Slow | `--` | 15 | Temporarily slows down the snake |
| Shield | `[]` | 15 | Blocks one collision and returns the snake to the center |

Obstacles are shown as `##`. Hitting an obstacle, the edge, or your own body ends the round unless a shield absorbs the collision.

## High scores and sound

The game keeps the top five scores separately for Classic and Hard mode in `.snek_scores.json` in your home directory. Scores are stored on your computer, not uploaded to GitHub. If the file cannot be written, the game still works but scores will not persist.

Sound effects use your terminal's bell. Some terminal applications or system settings mute the bell; toggle it from the start screen with **S**.

## Requirements

- Python 3
- Windows only: `windows-curses` (`py -m pip install windows-curses`)
- A terminal window large enough to display the board
