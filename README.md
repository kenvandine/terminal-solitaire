# Terminal Solitaire

A feature-rich, terminal-based implementation of the classic Klondike Solitaire game, written in Python using `curses`.

![Solitaire](https://github.com/kenvandine/terminal-solitaire/blob/main/screenshot.png)

## Features

-   **Classic Gameplay**: Standard Klondike rules with a 52-card deck.
-   **Terminal UI**: Colorful and responsive text-based interface.
-   **Undo Support**: Make a mistake? Press 'U' to revert your last move.
-   **Mouse Support**: Full mouse interaction for selecting, moving, and dealing cards.
-   **Smart Controls**:
    -   **Double-Click / Double-Tap**: Automatically move cards to the best available spot (Foundation or Tableau).
    -   **Auto-Stack**: Press 'S' to automatically move all possible cards to Foundations.
-   **High Scores**: Tracks your top 10 scores and moves locally.
-   **Cross-Platform**: Runs on Linux and macOS (any terminal with `curses` support).

## Requirements

-   Python 3.6+
-   A terminal with color support

## Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/kenvandine/terminal-solitaire.git](https://github.com/kenvandine/terminal-solitaire.git)
    cd terminal-solitaire
    ```

2.  No external dependencies are required beyond the standard Python library.

## How to Play

Run the game using Python:
```bash
python3 solitaire.py
````

### Controls

| Key / Action | Function |
| :--- | :--- |
| **Arrow Keys** | Move the cursor around the board. |
| **Space** / **Enter** | Select a card/pile, move the selected card, or deal from Stock. |
| **Double-Tap Space/Enter** | Automatically move the card under cursor to a Foundation or Tableau. |
| **S** | Auto-move all eligible cards to Foundations. |
| **R** | Re-deal a new game. |
| **U** | Undo the last action. |
| **Q** | Quit the game. |

### Mouse Controls

  - **Click**: Select a card/pile or move the selected card. Click Stock to deal.
  - **Double-Click**: Automatically move the clicked card to a Foundation or Tableau.

## Testing

The project includes a comprehensive suite of unit tests ensuring the game logic works correctly, including movement rules, scoring, and the undo history.

To run the tests:

```bash
python3 -m unittest test_game_logic.py
```

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3). See the [LICENSE](https://github.com/kenvandine/terminal-solitaire/blob/main/LICENSE) file for details.

```
```

