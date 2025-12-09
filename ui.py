import curses
from game_logic import Card, Suit, Rank, SolitaireGame

CARD_WIDTH = 7
CARD_HEIGHT = 5

class Renderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)  # Hide cursor
        curses.start_color()
        curses.use_default_colors()
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        
        # Initialize colors
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)   # Red cards
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE) # Black cards
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Back of card / Empty slot
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK) # Background / Selection
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Selected Cursor

        self.RED_PAIR = curses.color_pair(1)
        self.BLACK_PAIR = curses.color_pair(2)
        self.BACK_PAIR = curses.color_pair(3)
        self.BG_PAIR = curses.color_pair(4)
        self.CURSOR_PAIR = curses.color_pair(5)

    def draw_card(self, y, x, card: Card, selected=False):
        if card is None:
            # Draw empty slot
            for i in range(CARD_HEIGHT):
                self.stdscr.addstr(y + i, x, " " * CARD_WIDTH, self.BACK_PAIR)
            self.stdscr.addstr(y + 2, x + 2, "[]", self.BACK_PAIR)
            return

        if not card.face_up:
            # Draw card back
            for i in range(CARD_HEIGHT):
                self.stdscr.addstr(y + i, x, "░" * CARD_WIDTH, self.BACK_PAIR)
            return

        # Draw face up card
        pair = self.RED_PAIR if card.suit.color == 'RED' else self.BLACK_PAIR
        if selected:
            pair = pair | curses.A_REVERSE

        # Background of card
        for i in range(CARD_HEIGHT):
            self.stdscr.addstr(y + i, x, " " * CARD_WIDTH, pair)

        # Rank and Suit
        rank_str = str(card.rank)
        suit_str = card.suit.value
        
        self.stdscr.addstr(y, x, rank_str, pair)
        self.stdscr.addstr(y, x + CARD_WIDTH - len(suit_str), suit_str, pair)
        
        # Center suit
        self.stdscr.addstr(y + 2, x + 3, suit_str, pair)
        
        # Bottom right rank (inverted)
        self.stdscr.addstr(y + CARD_HEIGHT - 1, x + CARD_WIDTH - len(rank_str), rank_str, pair)
        self.stdscr.addstr(y + CARD_HEIGHT - 1, x, suit_str, pair)

    def draw_game(self, game: SolitaireGame, cursor_pos, selection):
        self.stdscr.clear()
        
        # Draw Stock (0, 0)
        stock_y, stock_x = 1, 2
        if game.stock:
            self.draw_card(stock_y, stock_x, game.stock[-1]) # Should be face down usually, but logic handles face_up property
        else:
            self.draw_card(stock_y, stock_x, None) # Empty placeholder
            self.stdscr.addstr(stock_y + 2, stock_x + 2, "O", self.BACK_PAIR) # O for refresh?

        # Draw Waste (0, 1)
        waste_y, waste_x = 1, 10
        if game.waste:
            self.draw_card(waste_y, waste_x, game.waste[-1])
        else:
            self.draw_card(waste_y, waste_x, None)

        # Draw Foundations (0, 3-6)
        for i in range(4):
            f_y, f_x = 1, 26 + (i * 8)
            if game.foundations[i]:
                self.draw_card(f_y, f_x, game.foundations[i][-1])
            else:
                self.draw_card(f_y, f_x, None)
                self.stdscr.addstr(f_y + 2, f_x + 3, "F", self.BACK_PAIR)

        # Draw Tableau (1, 0-6)
        for i in range(7):
            t_x = 2 + (i * 8)
            t_y = 7
            
            if not game.tableau[i]:
                self.draw_card(t_y, t_x, None)
            else:
                for j, card in enumerate(game.tableau[i]):
                    # Stack cards
                    card_y = t_y + j  # Overlap by 1 line? Or 2? Let's try 1 line overlap (compact)
                    # Actually, if we want to see them, maybe 2 lines if face up?
                    # Let's stick to 1 line vertical offset for now.
                    
                    # If it's the last card, draw full height.
                    # If not, we might overwrite it with the next card.
                    # So we should draw from top to bottom.
                    self.draw_card(card_y, t_x, card)

        # Draw Cursor
        # cursor_pos = (row, col)
        # row 0: Stock, Waste, Gap, F1, F2, F3, F4
        # row 1: T1, T2, ... T7
        
        c_row, c_col = cursor_pos
        cx, cy = 0, 0
        
        if c_row == 0:
            if c_col == 0: # Stock
                cx, cy = stock_x, stock_y
            elif c_col == 1: # Waste
                cx, cy = waste_x, waste_y
            elif c_col >= 3: # Foundations
                f_idx = c_col - 3
                cx, cy = 26 + (f_idx * 8), 1
        else:
            # Tableau
            t_idx = c_col
            cx = 2 + (t_idx * 8)
            # cy should be at the bottom card of the column
            col_len = len(game.tableau[t_idx])
            if col_len > 0:
                cy = 7 + col_len - 1
            else:
                cy = 7

        # Draw cursor highlight
        self.stdscr.addstr(cy + CARD_HEIGHT, cx, "^^^^^^^", self.CURSOR_PAIR)
        
        # Calculate bottom-most line used by Tableau + Cursor
        max_y = 15 # Minimum height
        for i in range(7):
            col_len = len(game.tableau[i])
            # Last card starts at: 7 + max(0, col_len - 1)
            # Ends at: start + CARD_HEIGHT - 1
            # Cursor highlight is at: start + CARD_HEIGHT
            
            last_card_y = 7 + max(0, col_len - 1)
            cursor_y = last_card_y + CARD_HEIGHT
            if cursor_y > max_y:
                max_y = cursor_y
        
        # Add padding
        info_y = max_y + 2
        
        # Draw Selection Info
        if selection:
            self.stdscr.addstr(info_y, 2, f"Selected: {selection}", curses.A_BOLD)

        # Draw Score and Moves
        self.stdscr.addstr(info_y, 15, f"Score: {game.score}", curses.A_BOLD)
        self.stdscr.addstr(info_y, 35, f"Moves: {game.moves}", curses.A_BOLD)

        # Draw Help Text
        help_y = info_y + 2
        self.stdscr.addstr(help_y, 2, "Controls:", curses.A_BOLD | curses.A_UNDERLINE)
        self.stdscr.addstr(help_y + 1, 3, "Arrows: Move Cursor  Space/Enter: Select/Move/Deal")
        self.stdscr.addstr(help_y + 2, 3, "Double-Tap Space/Enter or Double-Click: Auto-Move Card")
        self.stdscr.addstr(help_y + 3, 3, "S: Auto-Stack  U: Undo  Q: Quit")

        self.stdscr.refresh()
