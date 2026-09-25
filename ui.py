import curses
from game_logic import Card, Suit, Rank, SolitaireGame

MIN_CARD_W = 7
MIN_CARD_H = 5


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

        self._update_layout()

    def _update_layout(self):
        h, w = self.stdscr.getmaxyx()

        # Available width: reserve 2 cols left margin, 1 col right margin
        avail_w = w - 3
        avail_h = h - 2  # reserve 1 line top/bottom

        # Calculate card width to fill 7 columns
        card_w = (avail_w - 6) // 7
        card_w = max(card_w, MIN_CARD_W)

        gap = 1
        if card_w > MIN_CARD_W + 1:
            total_needed = 7 * MIN_CARD_W + 6
            extra = avail_w - total_needed
            if extra > 0:
                gap = 1 + extra // 7 // 2
                gap = min(gap, 4)
                card_w = (avail_w - 6 * gap) // 7
                card_w = max(card_w, MIN_CARD_W)

        # Card height scales but stays proportional
        card_h = min(avail_h // 3, avail_h - 30)
        card_h = max(card_h, MIN_CARD_H)
        card_h = min(card_h, 20)

        # Make cards roughly 5:7 width:height ratio
        ideal_w = int(card_h * 5 / 7)
        if ideal_w > card_w:
            card_w = min(ideal_w, (avail_w - 6 * gap) // 7)
        card_w = max(card_w, MIN_CARD_W)

        self.card_w = card_w
        self.card_h = card_h
        self.gap = gap
        self.margin_x = 2
        self.margin_y = 1

        # Top row Y position
        self.top_y = self.margin_y
        # Tableau Y position
        self.tableau_y = self.top_y + card_h + gap + 1

    def _safe_addstr(self, y, x, text, attr=None):
        """addstr that silently skips writes outside the terminal bounds."""
        max_y, max_x = self.stdscr.getmaxyx()
        if y < 0 or y >= max_y or x < 0 or x >= max_x:
            return
        if x + len(text) > max_x:
            text = text[:max(0, max_x - x)]
        if not text:
            return
        try:
            if attr:
                self.stdscr.addstr(y, x, text, attr)
            else:
                self.stdscr.addstr(y, x, text)
        except curses.error:
            pass

    def draw_card(self, y, x, card: Card, selected=False):
        w, h = self.card_w, self.card_h

        if card is None:
            for i in range(h):
                self._safe_addstr(y + i, x, " " * w, self.BACK_PAIR)
            label = "[]"
            self._safe_addstr(y + h // 2, x + max(0, (w - len(label)) // 2), label, self.BACK_PAIR)
            return

        if not card.face_up:
            for i in range(h):
                self._safe_addstr(y + i, x, "░" * w, self.BACK_PAIR)
            return

        # Face up card
        pair = self.RED_PAIR if card.suit.color == 'RED' else self.BLACK_PAIR
        if selected:
            pair = pair | curses.A_REVERSE

        # Background
        for i in range(h):
            self._safe_addstr(y + i, x, " " * w, pair)

        rank_str = str(card.rank)
        suit_str = card.suit.value
        bold = pair | curses.A_BOLD

        # Top-left: rank + suit
        self._safe_addstr(y, x, rank_str + suit_str, bold)
        # Bottom-right: suit + rank (right-aligned)
        br = suit_str + rank_str
        self._safe_addstr(y + h - 1, x + w - len(br), br, bold)

        # Center: rank above suit, both centered and bold
        center_row = y + h // 2
        self._safe_addstr(center_row - 1, x + max(0, (w - len(rank_str)) // 2), rank_str, bold)
        self._safe_addstr(center_row, x + max(0, (w - len(suit_str)) // 2), suit_str, pair)

    def draw_high_scores(self, scores):
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        title = "HIGH SCORES"
        start_y = max(1, h // 2 - 8)
        self._safe_addstr(start_y, (w - len(title)) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        header = f"{'Rank':<4} {'Score':<8} {'Moves':<8} {'Date':<20}"
        start_x = max(0, (w - len(header)) // 2)
        self._safe_addstr(start_y + 2, start_x, header, curses.A_BOLD)

        if not scores:
            no_scores = "No high scores yet!"
            self._safe_addstr(start_y + 4, (w - len(no_scores)) // 2, no_scores)
        else:
            for i, entry in enumerate(scores):
                line = f"{str(i+1) + '.':<4} {str(entry['score']):<8} {str(entry['moves']):<8} {entry['date']:<20}"
                self._safe_addstr(start_y + 4 + i, start_x, line)

        prompt = "Press any key to return"
        self._safe_addstr(h - 2, (w - len(prompt)) // 2, prompt, curses.A_BLINK)

        self.stdscr.refresh()
        self.stdscr.getch()

    def draw_game(self, game: SolitaireGame, cursor_pos, selection):
        self._update_layout()
        self.stdscr.clear()

        cw, ch = self.card_w, self.card_h
        gap = self.gap
        mx = self.margin_x

        stock_x = mx
        stock_y = self.top_y

        waste_x = mx + cw + gap
        waste_y = self.top_y

        found_x = mx + 2 * (cw + gap) + gap
        found_y = self.top_y

        # Draw Stock
        if game.stock:
            self.draw_card(stock_y, stock_x, game.stock[-1])
        else:
            self.draw_card(stock_y, stock_x, None)
            self._safe_addstr(stock_y + ch // 2, stock_x + cw // 2, "O", self.BACK_PAIR)

        # Draw Waste
        if game.waste:
            self.draw_card(waste_y, waste_x, game.waste[-1])
        else:
            self.draw_card(waste_y, waste_x, None)

        # Draw Foundations
        for i in range(4):
            fx = found_x + i * (cw + gap)
            if game.foundations[i]:
                self.draw_card(found_y, fx, game.foundations[i][-1])
            else:
                self.draw_card(found_y, fx, None)
                self._safe_addstr(found_y + ch // 2, fx + cw // 2, "F", self.BACK_PAIR)

        # Calculate dynamic overlap for tableau stacks
        max_y_avail = self.stdscr.getmaxyx()[0] - 6
        max_stack_height = max_y_avail - self.tableau_y

        max_needed = 0
        for i in range(7):
            needed = ch
            for card in game.tableau[i]:
                needed += 2 if card.face_up else 1
            if needed > max_needed:
                max_needed = needed

        if max_needed > max_stack_height and max_needed > ch:
            overlap = max(1, (max_needed - ch) // max(1, sum(len(game.tableau[i]) for i in range(7)) // 7 + 1))
            overlap = max(1, min(overlap, ch - 2))
        else:
            overlap = 2 if ch > MIN_CARD_H else 1

        # Draw Tableau and track each column's last card Y position
        col_last_y = [self.tableau_y] * 7
        bottom_y = self.tableau_y + ch

        for i in range(7):
            tx = mx + i * (cw + gap)
            ty = self.tableau_y

            if not game.tableau[i]:
                self.draw_card(ty, tx, None)
            else:
                card_y = ty
                for j, card in enumerate(game.tableau[i]):
                    last_y = card_y
                    self.draw_card(card_y, tx, card)
                    card_y += min(2, overlap) if card.face_up else 1
                col_last_y[i] = last_y
                col_bottom = last_y + ch
                if col_bottom > bottom_y:
                    bottom_y = col_bottom

        # Draw Cursor
        c_row, c_col = cursor_pos
        cx, cy = 0, 0

        if c_row == 0:
            if c_col == 0:
                cx, cy = stock_x, stock_y
            elif c_col == 1:
                cx, cy = waste_x, waste_y
            elif c_col >= 3:
                f_idx = c_col - 3
                cx = found_x + f_idx * (cw + gap)
                cy = found_y
        else:
            t_idx = c_col
            cx = mx + t_idx * (cw + gap)
            cy = col_last_y[t_idx]

        cursor_str = "^" * cw
        self._safe_addstr(cy + ch, cx, cursor_str, self.CURSOR_PAIR)

        info_y = bottom_y + 1

        if selection:
            self._safe_addstr(info_y, mx, f"Selected: {selection}", curses.A_BOLD)
        self._safe_addstr(info_y, mx + 20, f"Score: {game.score}", curses.A_BOLD)
        self._safe_addstr(info_y, mx + 40, f"Moves: {game.moves}", curses.A_BOLD)

        help_y = info_y + 2
        self._safe_addstr(help_y, mx, "Controls:", curses.A_BOLD | curses.A_UNDERLINE)
        self._safe_addstr(help_y + 1, mx + 1, "Arrows: Move Cursor  Space/Enter: Select/Move/Deal")
        self._safe_addstr(help_y + 2, mx + 1, "Double-Tap Space/Enter or Double-Click: Auto-Move Card")
        self._safe_addstr(help_y + 3, mx + 1, "S: Auto-Stack  U: Undo  R: Re-deal  H: High Scores  Q: Quit")

        self.stdscr.refresh()

    def screen_to_cursor(self, my, mx_click):
        """Convert mouse coordinates to (row, col) cursor position."""
        cw, ch = self.card_w, self.card_h
        gap = self.gap
        mx = self.margin_x

        new_row, new_col = -1, -1

        if self.top_y <= my < self.top_y + ch:
            stock_x = mx
            if stock_x <= mx_click < stock_x + cw:
                new_row, new_col = 0, 0
            waste_x = mx + cw + gap
            if waste_x <= mx_click < waste_x + cw:
                new_row, new_col = 0, 1
            found_x = mx + 2 * (cw + gap) + gap
            for i in range(4):
                fx = found_x + i * (cw + gap)
                if fx <= mx_click < fx + cw:
                    new_row, new_col = 0, 3 + i
        elif my >= self.tableau_y:
            for i in range(7):
                tx = mx + i * (cw + gap)
                if tx <= mx_click < tx + cw:
                    new_row, new_col = 1, i
                    break

        return new_row, new_col
