# Terminal Solitaire

A feature-rich, terminal-based implementation of the classic Klondike Solitaire game, written in Python using `curses`.

![Solitaire TUI](https://placeholder.com/solitaire_screenshot.png)

## Features

-   **Classic Gameplay**: Standard Klondike rules with a 52-card deck.
-   **Terminal UI**: Colorful and responsive text-based interface.
-   **Mouse Support**: Full mouse interaction for selecting, moving, and dealing cards.
-   **Smart Controls**:
    -   **Double-Click / Double-Tap**: Automatically move cards to the best available spot (Foundation or Tableau).
    -   **Auto-Stack**: Press 'S' to automatically move all possible cards to Foundations.
-   **High Scores**: Tracks your top 10 scores and moves locally.
-   **Cross-Platform**: Runs on Linux and macOS (any terminal with `curses` support).

## Requirements

-   Python 3.6+
-   Terminal with minimum size of **80x24**

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/terminal-solitaire.git
cd terminal-solitaire
```

## How to Play

Run the game:

```bash
python3 solitaire.py
```

### Controls

| Key | Action |
| --- | --- |
| **Arrow Keys** | Move cursor |
| **Space / Enter** | Select card / Move card / Deal from Stock |
| **Double-Tap Space/Enter** | Auto-move card to Foundation or Tableau |
| **Double-Click Mouse** | Auto-move card / Deal from Stock |
| **S** | Auto-stack all valid cards to Foundations |
| **R** | Redeal (Start a new game) |
| **Q** | Quit game |
| **Mouse Click** | Select / Move / Deal |

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3). See the [LICENSE](LICENSE) file for details.
