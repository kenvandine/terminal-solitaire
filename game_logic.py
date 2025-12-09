import random
import copy
from enum import Enum
from typing import List, Optional, Tuple

class Suit(Enum):
    HEARTS = '♥'
    DIAMONDS = '♦'
    CLUBS = '♣'
    SPADES = '♠'

    @property
    def color(self):
        return 'RED' if self in (Suit.HEARTS, Suit.DIAMONDS) else 'BLACK'

class Rank(Enum):
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13

    def __str__(self):
        if self.value == 1: return 'A'
        if self.value == 11: return 'J'
        if self.value == 12: return 'Q'
        if self.value == 13: return 'K'
        return str(self.value)

class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
        self.face_up = False

    def flip(self):
        self.face_up = not self.face_up

    def show(self):
        self.face_up = True

    def hide(self):
        self.face_up = False

    def __repr__(self):
        return f"{self.rank}{self.suit.value}" if self.face_up else "[?]"

class Deck:
    def __init__(self):
        self.cards = [Card(s, r) for s in Suit for r in Rank]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self) -> Optional[Card]:
        return self.cards.pop() if self.cards else None

class SolitaireGame:
    def __init__(self):
        self.deck = Deck()
        self.tableau: List[List[Card]] = [[] for _ in range(7)]
        self.foundations: List[List[Card]] = [[] for _ in range(4)] 
        self.stock: List[Card] = []
        self.waste: List[Card] = []
        self.score = 0
        self.moves = 0
        self.history = []
        self.deal()

    def reset_game(self):
        """Resets the game state for a new deal."""
        self.deck = Deck()
        self.tableau: List[List[Card]] = [[] for _ in range(7)]
        self.foundations: List[List[Card]] = [[] for _ in range(4)]
        self.stock: List[Card] = []
        self.waste: List[Card] = []
        self.score = 0
        self.moves = 0
        self.history = []
        self.deal()

    def save_state(self):
        self.history.append({
            'tableau': copy.deepcopy(self.tableau),
            'foundations': copy.deepcopy(self.foundations),
            'stock': copy.deepcopy(self.stock),
            'waste': copy.deepcopy(self.waste),
            'score': self.score,
            'moves': self.moves
        })

    def undo(self) -> bool:
        if not self.history:
            return False

        state = self.history.pop()
        self.tableau = state['tableau']
        self.foundations = state['foundations']
        self.stock = state['stock']
        self.waste = state['waste']
        self.score = state['score']
        self.moves = state['moves']
        return True

    def deal(self):
        # Deal to tableau
        for i in range(7):
            for j in range(i + 1):
                card = self.deck.draw()
                if j == i:
                    card.show()
                self.tableau[i].append(card)
        
        # Remaining to stock
        while True:
            card = self.deck.draw()
            if not card:
                break
            self.stock.append(card)

    def draw_from_stock(self, record_undo=True):
        if record_undo:
            self.save_state()

        if not self.stock:
            # Recycle waste to stock
            if not self.waste:
                return # Empty stock and waste
            self.stock = list(reversed(self.waste))
            self.waste = []
            for card in self.stock:
                card.hide()
            self.score = max(0, self.score - 100)
        else:
            # Draw one card
            card = self.stock.pop()
            card.show()
            self.waste.append(card)
            self.moves += 1

    def can_move_to_tableau(self, card: Card, col_idx: int) -> bool:
        column = self.tableau[col_idx]
        if not column:
            return card.rank == Rank.KING
        
        top_card = column[-1]
        return (top_card.suit.color != card.suit.color) and \
               (top_card.rank.value == card.rank.value + 1)

    def can_move_to_foundation(self, card: Card, f_idx: int) -> bool:
        foundation = self.foundations[f_idx]
        if not foundation:
            return card.rank == Rank.ACE
        
        top_card = foundation[-1]
        return (top_card.suit == card.suit) and \
               (top_card.rank.value == card.rank.value - 1)

    def check_win(self) -> bool:
        return all(len(f) == 13 for f in self.foundations)

    def move_tableau_to_tableau(self, from_col: int, to_col: int, num_cards: int, record_undo=True) -> bool:
        if not (0 <= from_col < 7 and 0 <= to_col < 7):
            return False
        
        source_col = self.tableau[from_col]
        if len(source_col) < num_cards:
            return False
        
        cards_to_move = source_col[-num_cards:]
        base_card = cards_to_move[0]
        
        if self.can_move_to_tableau(base_card, to_col):
            if record_undo:
                self.save_state()

            # Execute move
            self.tableau[from_col] = source_col[:-num_cards]
            self.tableau[to_col].extend(cards_to_move)
            
            # Flip new top card of source if needed
            if self.tableau[from_col] and not self.tableau[from_col][-1].face_up:
                self.tableau[from_col][-1].show()
                self.score += 5
            
            self.moves += 1
            return True
        return False

    def move_waste_to_tableau(self, to_col: int, record_undo=True) -> bool:
        if not self.waste:
            return False
        
        card = self.waste[-1]
        if self.can_move_to_tableau(card, to_col):
            if record_undo:
                self.save_state()

            self.waste.pop()
            self.tableau[to_col].append(card)
            self.score += 5
            self.moves += 1
            return True
        return False

    def move_waste_to_foundation(self, f_idx: int, record_undo=True) -> bool:
        if not self.waste:
            return False
        
        card = self.waste[-1]
        if self.can_move_to_foundation(card, f_idx):
            if record_undo:
                self.save_state()

            self.waste.pop()
            self.foundations[f_idx].append(card)
            self.score += 10
            self.moves += 1
            return True
        return False

    def move_tableau_to_foundation(self, from_col: int, f_idx: int, record_undo=True) -> bool:
        if not self.tableau[from_col]:
            return False
        
        card = self.tableau[from_col][-1]
        if self.can_move_to_foundation(card, f_idx):
            if record_undo:
                self.save_state()

            self.tableau[from_col].pop()
            self.foundations[f_idx].append(card)
            self.score += 10
            
            # Flip new top card of source if needed
            if self.tableau[from_col] and not self.tableau[from_col][-1].face_up:
                self.tableau[from_col][-1].show()
                self.score += 5
            
            self.moves += 1
            return True
        return False

    def move_foundation_to_tableau(self, f_idx: int, to_col: int, record_undo=True) -> bool:
        if not self.foundations[f_idx]:
            return False
            
        card = self.foundations[f_idx][-1]
        if self.can_move_to_tableau(card, to_col):
            if record_undo:
                self.save_state()

            self.foundations[f_idx].pop()
            self.tableau[to_col].append(card)
            self.score = max(0, self.score - 15)
            self.moves += 1
            return True
        return False

    def auto_move_to_foundation(self) -> bool:
        # Save state once for the entire batch of auto-moves
        self.save_state()

        moved = False
        # Check waste
        if self.waste:
            for i in range(4):
                if self.move_waste_to_foundation(i, record_undo=False):
                    moved = True
                    break
        
        # Check tableau tips
        for i in range(7):
            if self.tableau[i]:
                for f in range(4):
                    if self.move_tableau_to_foundation(i, f, record_undo=False):
                        moved = True
                        break

        # If no moves actually happened, remove the redundant state save
        if not moved:
            self.history.pop()

        return moved
