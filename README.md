# Foxfire Odyssey

A small 2D platformer built with [pygame](https://www.pygame.org/) and [pymunk](http://www.pymunk.org/). Guide the fox up through three levels, collect the gem in each one to unlock the way up, and avoid the patrolling opossums.

I made this for my Python exam. It's a simple project, but the code is commented so you can follow what's going on.

## Features

- Three levels with their own tile maps, enemies and terrain (grass and snow)
- Physics-based jumping and gravity (pymunk) with custom collision handling
- Patrolling enemies, a one-use teleport portal in level 3, and animated player, gem and portal sprites
- Main menu, settings and credits screens
- Settings for music, sound effects, trees (background decoration) and easy/hard difficulty
- Footstep sounds that change with the block you're standing on

## Requirements

- Python 3.8+
- `pygame`, `pymunk` and `numpy`

```bash
pip install pygame pymunk numpy
```

> **Windows only (for now):** asset paths in `main.py` are written with Windows-style backslashes (e.g. `Assets\Sprites\...`), so the game currently runs on Windows only. On macOS/Linux you'd need to change those paths to forward slashes and match the case of the folder names (`Assets/Sprites/...`).

## Running

Download and unpack the zip, then run `main.py` from the project folder:

```bash
python main.py
```

Run it from inside the project folder so the `Assets` directory can be found. The window has no title bar, so use the in-game **Quit** button to exit.

## Controls

| Input | Action |
| --- | --- |
| Left / Right arrow | Move |
| Space or Up arrow | Jump (only while on the ground) |
| Mouse | Click menu buttons |

## How to play

1. Press **Play** on the main menu.
2. Find the gem in the level to unlock the exit at the top of the screen.
3. Climb out of the top of the screen to move to the next level. You can also drop back down to the previous one.
4. Touching an enemy ends the run. Leaving the top of level 3 takes you back to the main menu.

## Project structure

| File / folder | What it is |
| --- | --- |
| `main.py` | The whole game: game states, sprite classes, physics setup and the main loop |
| `mapdata.py` | Tile maps for each level |
| `Assets/` | Sprites, environment art, UI graphics, music and sound effects |
| `TODO.txt` | My old dev notes (what's done and what was left to do) |

## Editing levels

Levels are plain lists of numbers in `mapdata.py`, one number per block, so they're easy to tweak. `-1` is air and `0`-`5` are the different grass, dirt, stone and snow blocks (the key is at the top of the file). The maps are stored upside-down: the first row is the bottom of the screen. Enemy and gem positions are set in the `Level1`/`Level2`/`Level3` methods in `main.py`.

## Known issues

These are the open items from `TODO.txt`, plus a few I noticed since:

- Collecting one gem can remove all gems on screen
- After restarting, the level 2 gem sometimes doesn't appear
- Enemy speeds are sometimes inconsistent when there are several enemies
- Footstep sounds reload block images every frame, which is wasteful
- Cherries were planned but never added

## Credits

Built with pygame and pymunk. There's also a credits screen reachable from the main menu.
