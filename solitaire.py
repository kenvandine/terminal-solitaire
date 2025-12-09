#!/usr/bin/python
import curses
import sys
import time
from game_logic import SolitaireGame
from ui import Renderer
from scores import ScoreManager

def try_auto_move(game, row, col):
    # Waste -> Foundation or Tableau
    if row == 0 and col == 1:
        # Try Foundation
        for f in range(4):
            if game.move_waste_to_foundation(f):
                return True
        # Try Tableau
        for t in range(7):
            if game.move_waste_to_tableau(t):
                return True
    
    # Tableau -> Foundation or Tableau
    elif row == 1:
        src_col = col
        # Try Foundation (only top card)
        for f in range(4):
            if game.move_tableau_to_foundation(src_col, f):
                return True
        
        # Try Tableau
        # Try moving stack
        src_pile = game.tableau[src_col]
        face_up_count = 0
        for c in reversed(src_pile):
            if c.face_up: face_up_count += 1
            else: break
        
        if face_up_count > 0:
            for t in range(7):
                if t == src_col: continue
                # Try moving whole stack
                if game.move_tableau_to_tableau(src_col, t, face_up_count):
                    return True
    return False

def run_game(stdscr):
    # Minimum required dimensions
    MIN_H, MIN_W = 40, 60

    while True:
        h, w = stdscr.getmaxyx()
        if h >= MIN_H and w >= MIN_W:
            break

        stdscr.clear()
        msg1 = f"Terminal is too small ({w}x{h})."
        msg2 = f"Please resize to at least {MIN_W}x{MIN_H}."

        # Center the text
        stdscr.addstr(h // 2 - 1, max(0, (w - len(msg1)) // 2), msg1)
        stdscr.addstr(h // 2, max(0, (w - len(msg2)) // 2), msg2)
        stdscr.refresh()

        # Wait for resize event or any key
        key = stdscr.getch()
        if key == curses.KEY_RESIZE:
            curses.update_lines_cols() # Ensure curses knows about the new size

    game = SolitaireGame()
    renderer = Renderer(stdscr)
    score_manager = ScoreManager()
    
    # Cursor position: (row, col)
    # Row 0: Top area (Stock=0, Waste=1, F1=3, F2=4, F3=5, F4=6)
    # Row 1: Tableau (0-6)
    cursor_row = 1
    cursor_col = 0
    
    selection = None # (row, col)
    last_action_time = 0
    
    while True:
        renderer.draw_game(game, (cursor_row, cursor_col), selection)
        
        key = stdscr.getch()
        
        # Handle Terminal Resize Event
        if key == curses.KEY_RESIZE:
            stdscr.clear()
            continue

        if key == ord('q'):
            break

        # --- High Scores ---
        elif key == ord('h') or key == ord('H'):
            renderer.draw_high_scores(score_manager.get_high_scores())
            # Clear screen upon return to ensure clean redraw of the game
            stdscr.clear()
        # -------------------

        # --- Undo Handling ---
        elif key == ord('u') or key == ord('U'):
            if game.undo():
                selection = None # Reset selection to prevent state mismatches
        # ---------------------
        
        elif key == curses.KEY_UP:
            if cursor_row == 1:
                cursor_row = 0
                # Map tableau col to top row roughly
                if cursor_col <= 1: cursor_col = cursor_col # 0,1 -> 0,1
                elif cursor_col == 2: cursor_col = 1 # Gap -> Waste
                elif cursor_col >= 3: cursor_col = cursor_col # 3-6 -> 3-6
        
        elif key == curses.KEY_DOWN:
            if cursor_row == 0:
                cursor_row = 1
                # Map top row to tableau
                if cursor_col == 2: cursor_col = 2 # Gap -> T3
                # 0,1 -> 0,1; 3-6 -> 3-6. Matches well.
        
        elif key == curses.KEY_LEFT:
            if cursor_col > 0:
                cursor_col -= 1
                if cursor_row == 0 and cursor_col == 2: # Skip gap at 2 in top row
                    cursor_col = 1
        
        elif key == curses.KEY_RIGHT:
            max_col = 6
            if cursor_col < max_col:
                cursor_col += 1
                if cursor_row == 0 and cursor_col == 2: # Skip gap at 2 in top row
                    cursor_col = 3

        elif key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                
                # Map coordinates to cursor_row, cursor_col
                new_row, new_col = -1, -1
                
                # Top Row (Stock, Waste, Foundations)
                if my >= 1 and my <= 5: # Card height is 5
                    if 2 <= mx < 9: # Stock
                        new_row, new_col = 0, 0
                    elif 10 <= mx < 17: # Waste
                        new_row, new_col = 0, 1
                    elif mx >= 26: # Foundations
                        # 26 + i*8
                        f_idx = (mx - 26) // 8
                        if 0 <= f_idx < 4:
                            # Check if within card width
                            offset = (mx - 26) % 8
                            if offset < 7:
                                new_row, new_col = 0, 3 + f_idx
                
                # Tableau
                elif my >= 7:
                    # 2 + i*8
                    if mx >= 2:
                        t_idx = (mx - 2) // 8
                        if 0 <= t_idx < 7:
                            offset = (mx - 2) % 8
                            if offset < 7:
                                new_row, new_col = 1, t_idx
                
                if new_row != -1 and new_col != -1:
                    cursor_row, cursor_col = new_row, new_col
                    
                    # Handle Double Click
                    if bstate & curses.BUTTON1_DOUBLE_CLICKED:
                        if try_auto_move(game, cursor_row, cursor_col):
                            selection = None
                        elif cursor_row == 0 and cursor_col == 0:
                            # Double click on Stock -> Deal
                            game.draw_from_stock()
                            selection = None
                    else:
                        # Single Click -> Trigger action (simulate Space)
                        key = ord(' ')
            except curses.error:
                pass

        elif key == ord(' ') or key == curses.KEY_ENTER or key == 10 or key == 13: # Action
            current_time = time.time()
            is_double_tap = (current_time - last_action_time) < 0.3
            last_action_time = current_time

            if is_double_tap:
                if try_auto_move(game, cursor_row, cursor_col):
                    selection = None
                    last_action_time = 0 # Reset to prevent triple-tap issues
                    continue

            # Handle Stock Draw
            if cursor_row == 0 and cursor_col == 0:
                game.draw_from_stock()
                selection = None
                continue
            
            if selection is None:
                # Select current
                # Check if valid selection
                valid = False
                if cursor_row == 0:
                    if cursor_col == 1: # Waste
                        if game.waste: valid = True
                    elif cursor_col >= 3: # Foundation
                        f_idx = cursor_col - 3
                        if game.foundations[f_idx]: valid = True
                else: # Tableau
                    if game.tableau[cursor_col]: valid = True
                
                if valid:
                    selection = (cursor_row, cursor_col)
            else:
                # Try move
                src_row, src_col = selection
                dst_row, dst_col = cursor_row, cursor_col
                
                success = False
                
                # Source: Waste
                if src_row == 0 and src_col == 1:
                    if dst_row == 1: # To Tableau
                        success = game.move_waste_to_tableau(dst_col)
                    elif dst_row == 0 and dst_col >= 3: # To Foundation
                        success = game.move_waste_to_foundation(dst_col - 3)
                
                # Source: Foundation
                elif src_row == 0 and src_col >= 3:
                    f_idx = src_col - 3
                    if dst_row == 1: # To Tableau
                        success = game.move_foundation_to_tableau(f_idx, dst_col)
                
                # Source: Tableau
                elif src_row == 1:
                    if dst_row == 1: # To Tableau
                        src_pile = game.tableau[src_col]
                        # Find how many cards are face up
                        face_up_count = 0
                        for c in reversed(src_pile):
                            if c.face_up: face_up_count += 1
                            else: break
                        
                        # Try to move the whole face-up stack
                        if game.move_tableau_to_tableau(src_col, dst_col, face_up_count):
                            success = True
                        else:
                            # Try moving 1 card
                            if face_up_count > 1:
                                if game.move_tableau_to_tableau(src_col, dst_col, 1):
                                    success = True
                    
                    elif dst_row == 0 and dst_col >= 3: # To Foundation
                        success = game.move_tableau_to_foundation(src_col, dst_col - 3)

                if success:
                    selection = None
                else:
                    selection = None

        elif key == ord('s') or key == ord('S'): # Auto-stack
            game.auto_move_to_foundation()

        elif key == ord('r') or key == ord('R'): # Re-deal
            game.reset_game()
            selection = None
            last_action_time = 0
            # Reset cursor to starting position (optional, but good for UX)
            cursor_row = 1
            cursor_col = 0

        if game.check_win():
            # Draw one last time
            renderer.draw_game(game, (cursor_row, cursor_col), selection)
            
            # Save Score
            score_manager.save_score(game.score, game.moves)
            
            # Show win message
            stdscr.addstr(10, 30, "YOU WIN!", curses.A_BOLD | curses.color_pair(1))
            stdscr.addstr(11, 25, f"Score: {game.score}  Moves: {game.moves}", curses.A_BOLD)
            stdscr.addstr(12, 25, "Press Q to Quit", curses.A_BOLD)
            stdscr.refresh()
            while True:
                if stdscr.getch() == ord('q'):
                    return

def main():
    curses.wrapper(run_game)

if __name__ == '__main__':
    main()
