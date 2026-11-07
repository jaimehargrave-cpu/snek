# Terminal Snake

A colorful Snake game that runs in your terminal, written in Python. Eat berries to score points, grow longer, and avoid your tail and obstacles.

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

## Features

- **Start screen:** press **Enter** to play, **H** to switch modes, **S** to toggle terminal-bell sounds, or **Q** to quit.
- **Classic and Hard modes:** Hard mode starts faster and has more obstacles.
- **Special berries:** normal berries grow the snake; boost berries speed it up; slow berries slow it down; shield berries protect against one collision.
- **Obstacles:** avoid blocks shown as `##`.
- **Local high scores:** the top five scores for each mode are saved on your computer in `.snek_scores.json` in your home directory.

## Controls

| Key | Action |
| --- | --- |
| Arrow keys or **WASD** | Move |
| **P** | Pause or resume |
| **Q** | Quit the current round |
| **R** | Retry after game over |

## Roadmap

Ideas for future improvements—these are not implemented yet:

- Add more berry types and special effects.
- Let players choose board size or customize colors.
- Add a pause menu with options and a resume prompt.
- Add automated tests for game rules and scoring.
- Improve terminal resizing and accessibility.

## Requirements

- Python 3
- Windows only: `windows-curses` (`py -m pip install windows-curses`)
- A terminal window large enough to display the board
