# Download and Run Terminal Snake

A colorful Snake game that runs in your terminal, written in Python.

> **Reminder:** Use Python 3. Windows needs `windows-curses`; macOS and Linux generally include `curses` with Python.

## 1. Install Python

Check your Python version in a terminal (Command Prompt or PowerShell on Windows):

```bash
python --version
```

On macOS or Linux, try `python3 --version`. If Python is missing, install Python 3 from [python.org/downloads](https://www.python.org/downloads/) or your Linux distribution's package manager. On Windows, select **Add python.exe to PATH** in the installer.

## 2. Windows terminal support

Windows requires `windows-curses`. Check pip with:

```powershell
py -m pip --version
```

Install the package:

```powershell
py -m pip install windows-curses
```

If `py` is not recognized, use `python` instead. On macOS and Linux, no extra package is usually needed.

## 3. Download and run

Download `snek.py` from this repository and open a terminal in the folder where you saved it.

**Windows:**

```powershell
py snek.py
```

**macOS or Linux:**

```bash
python3 snek.py
```

## Start screen and controls

At the start screen, press **Enter** to play, **H** to switch modes, **B** to cycle board size, **C** to change snake color, **S** to toggle terminal-bell sounds, or **Q** to quit. During a round, use **Arrow keys** or **WASD** to move, **P** for the pause menu, and **Q** to end the round. After game over, press **R** to retry, **M** for the start screen, or **Q** to quit.

The game needs a terminal at least 38 columns wide and 22 rows tall. The board will scale down if the selected size does not fit.

## Scores

The top five scores for Classic and Hard mode are saved locally in `.snek_scores.json` in your home directory. Scores are not uploaded to GitHub.
