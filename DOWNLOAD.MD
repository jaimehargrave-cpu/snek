# Download and Run Terminal Snake

A small Snake game that runs in your terminal, written in Python.

> **Keep in mind:** Make sure you have Python and any required packages installed for your operating system. Windows needs `windows-curses`; macOS and Linux generally already include `curses` with Python.

## 1. Install Python

You need Python 3. Check whether it is already installed by opening a terminal (Command Prompt or PowerShell on Windows) and running:

```bash
python --version
```

On macOS or Linux, try `python3 --version` if `python` is not recognized. If neither command works, install Python 3 from [python.org/downloads](https://www.python.org/downloads/) on Windows or macOS, or use your Linux distribution's software/package manager. On Windows, select **Add python.exe to PATH** in the installer.

## 2. Check for pip (Windows only for this game)

On Windows, this game needs the `windows-curses` package. Most Python installers include pip. Check with:

```bash
py -m pip --version
```

If pip is missing, try installing Python's bundled pip:

```bash
py -m ensurepip --upgrade
```

If `py` is not recognized, use `python` instead:

```bash
python -m ensurepip --upgrade
```

If that still does not work, rerun the Python installer and choose **Modify** to ensure pip is selected, or reinstall Python from [python.org](https://www.python.org/downloads/).

## 3. Install Windows terminal support

On Windows, run:

```bash
py -m pip install windows-curses
```

If you use `python` instead of `py`, run `python -m pip install windows-curses`.

On macOS and Linux, you usually do not need to install anything with pip; the `curses` module is included with Python.

## 4. Download and run the game

Download `snek.py` from this repository and open a terminal in the folder where you saved it. Then run:

**Windows:**

```bash
py snek.py
```

**macOS or Linux:**

```bash
python3 snek.py
```

If `python3` is not recognized, try `python snek.py`.

## Controls and options

At the start screen, press **Enter** to begin, **H** to toggle Hard mode, **S** to toggle sound, or **Q** to quit. During a round, use **Arrow keys** or **WASD** to move, **P** to pause, and **Q** to quit. Press **R** after game over to retry.

## Keep your high scores

The game saves the top five scores for each mode in `.snek_scores.json` in your home directory. Those scores stay on your computer and are not uploaded to the repository.
