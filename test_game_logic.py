import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import patch
from game_logic import Card, Deck, SolitaireGame, Suit, Rank
from scores import ScoreManager

class TestSolitaireGame(unittest.TestCase):
    def setUp(self):
        self.game = SolitaireGame()

    # --- Card & Rank Tests ---
    def test_card_rank_strings(self):
        """Test string representation of Ranks (A, K, Q, J, 10, etc.)"""
        self.assertEqual(str(Rank.ACE), 'A')
        self.assertEqual(str(Rank.KING), 'K')
        self.assertEqual(str(Rank.QUEEN), 'Q')
        self.assertEqual(str(Rank.JACK), 'J')
        self.assertEqual(str(Rank.TEN), '10')
        self.assertEqual(str(Rank.TWO), '2')

    def test_card_repr(self):
        """Test card string representation when face up/down"""
        c = Card(Suit.HEARTS, Rank.ACE)
        self.assertEqual(repr(c), "[?]")
        c.show()
        self.assertEqual(repr(c), "A♥")
        c.hide()
        self.assertEqual(repr(c), "[?]")

    # --- Deck Tests ---
    def test_deck_creation(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)

    def test_deck_draw_empty(self):
        deck = Deck()
        # Draw all 52 cards
        for _ in range(52):
            self.assertIsNotNone(deck.draw())
        # Draw from empty deck
        self.assertIsNone(deck.draw())

    # --- Initialization Tests ---
    def test_initial_deal(self):
        """Verify the tableau setup and stock size after deal"""
        for i in range(7):
            self.assertEqual(len(self.game.tableau[i]), i + 1)
            # Top card should be face up
            self.assertTrue(self.game.tableau[i][-1].face_up)
            # Others should be face down
            for j in range(i):
                self.assertFalse(self.game.tableau[i][j].face_up)

        # Check stock size: 52 - 28 (tableau cards) = 24
        self.assertEqual(len(self.game.stock), 24)
        self.assertEqual(len(self.game.waste), 0)

    # --- Stock & Waste Tests ---
    def test_draw_from_stock(self):
        initial_stock_len = len(self.game.stock)
        self.game.draw_from_stock()
        self.assertEqual(len(self.game.stock), initial_stock_len - 1)
        self.assertEqual(len(self.game.waste), 1)
        self.assertTrue(self.game.waste[0].face_up)

    def test_recycle_waste(self):
        """Test recycling waste back to stock when stock is empty"""
        # Empty stock manually
        self.game.stock = []
        # Add a card to waste
        c1 = Card(Suit.SPADES, Rank.ACE)
        c1.show()
        self.game.waste = [c1]

        # Trigger recycle
        self.game.draw_from_stock()

        self.assertEqual(len(self.game.stock), 1)
        self.assertEqual(len(self.game.waste), 0)
        # Check if recycled card is face down
        self.assertFalse(self.game.stock[0].face_up)

    def test_draw_stock_fully_empty(self):
        """Test draw action when both stock and waste are empty"""
        self.game.stock = []
        self.game.waste = []
        self.game.draw_from_stock() # Should do nothing
        self.assertEqual(len(self.game.stock), 0)
        self.assertEqual(len(self.game.waste), 0)

    # --- Tableau Move Tests ---
    def test_move_tableau_to_tableau_valid(self):
        self.game.tableau = [[] for _ in range(7)]
        
        # Destination: King Spades
        k_spades = Card(Suit.SPADES, Rank.KING)
        k_spades.show()
        self.game.tableau[0].append(k_spades)
        
        # Source: Queen Hearts
        q_hearts = Card(Suit.HEARTS, Rank.QUEEN)
        q_hearts.show()
        self.game.tableau[1].append(q_hearts)
        
        success = self.game.move_tableau_to_tableau(1, 0, 1)
        self.assertTrue(success)
        self.assertEqual(len(self.game.tableau[0]), 2)
        self.assertEqual(len(self.game.tableau[1]), 0)

    def test_move_tableau_to_tableau_invalid_color(self):
        self.game.tableau = [[] for _ in range(7)]
        
        k_spades = Card(Suit.SPADES, Rank.KING)
        k_spades.show()
        self.game.tableau[0].append(k_spades)
        
        # Invalid: Black Queen on Black King
        q_clubs = Card(Suit.CLUBS, Rank.QUEEN)
        q_clubs.show()
        self.game.tableau[1].append(q_clubs)
        
        self.assertFalse(self.game.move_tableau_to_tableau(1, 0, 1))

    def test_move_tableau_to_tableau_invalid_rank(self):
        self.game.tableau = [[] for _ in range(7)]
        
        k_spades = Card(Suit.SPADES, Rank.KING)
        k_spades.show()
        self.game.tableau[0].append(k_spades)
        
        # Invalid: Jack on King (needs Queen)
        j_hearts = Card(Suit.HEARTS, Rank.JACK)
        j_hearts.show()
        self.game.tableau[1].append(j_hearts)
        
        self.assertFalse(self.game.move_tableau_to_tableau(1, 0, 1))

    def test_move_tableau_empty_col(self):
        self.game.tableau = [[] for _ in range(7)]

        # King to empty
        k_hearts = Card(Suit.HEARTS, Rank.KING)
        k_hearts.show()
        self.game.tableau[0].append(k_hearts)

        success = self.game.move_tableau_to_tableau(0, 1, 1)
        self.assertTrue(success)
        self.assertEqual(len(self.game.tableau[1]), 1)

        # Non-King to empty
        q_hearts = Card(Suit.HEARTS, Rank.QUEEN)
        q_hearts.show()
        self.game.tableau[2].append(q_hearts)

        success = self.game.move_tableau_to_tableau(2, 3, 1)
        self.assertFalse(success)

    def test_move_tableau_invalid_args(self):
        # Too many cards
        self.assertFalse(self.game.move_tableau_to_tableau(0, 1, 100))
        # Bad indices
        self.assertFalse(self.game.move_tableau_to_tableau(-1, 0, 1))
        self.assertFalse(self.game.move_tableau_to_tableau(0, 99, 1))

    # --- Waste to Tableau/Foundation Tests ---
    def test_move_waste_to_tableau(self):
        self.game.tableau = [[] for _ in range(7)]
        self.game.waste = []

        k_spades = Card(Suit.SPADES, Rank.KING)
        k_spades.show()
        self.game.tableau[0].append(k_spades)

        q_hearts = Card(Suit.HEARTS, Rank.QUEEN)
        q_hearts.show()
        self.game.waste.append(q_hearts)

        success = self.game.move_waste_to_tableau(0)
        self.assertTrue(success)
        self.assertEqual(len(self.game.tableau[0]), 2)
        self.assertEqual(len(self.game.waste), 0)

    def test_move_waste_to_tableau_empty(self):
        self.game.waste = []
        self.assertFalse(self.game.move_waste_to_tableau(0))

    def test_move_waste_to_tableau_invalid(self):
        self.game.tableau = [[] for _ in range(7)]
        self.game.waste = []

        k_spades = Card(Suit.SPADES, Rank.KING)
        k_spades.show()
        self.game.tableau[0].append(k_spades)

        # Invalid suit
        q_spades = Card(Suit.SPADES, Rank.QUEEN)
        q_spades.show()
        self.game.waste.append(q_spades)

        self.assertFalse(self.game.move_waste_to_tableau(0))

    def test_move_waste_to_foundation(self):
        self.game.foundations = [[] for _ in range(4)]
        self.game.waste = []

        a_hearts = Card(Suit.HEARTS, Rank.ACE)
        a_hearts.show()
        self.game.waste.append(a_hearts)

        success = self.game.move_waste_to_foundation(0)
        self.assertTrue(success)
        self.assertEqual(len(self.game.foundations[0]), 1)
        self.assertEqual(len(self.game.waste), 0)

    def test_move_waste_to_foundation_empty(self):
        self.game.waste = []
        self.assertFalse(self.game.move_waste_to_foundation(0))

    # --- Foundation Tests ---
    def test_move_tableau_to_foundation(self):
        self.game.tableau = [[] for _ in range(7)]
        self.game.foundations = [[] for _ in range(4)]

        a_hearts = Card(Suit.HEARTS, Rank.ACE)
        a_hearts.show()
        self.game.tableau[0].append(a_hearts)

        # Move Ace
        success = self.game.move_tableau_to_foundation(0, 0)
        self.assertTrue(success)
        self.assertEqual(len(self.game.foundations[0]), 1)

        # Move Two
        two_hearts = Card(Suit.HEARTS, Rank.TWO)
        two_hearts.show()
        self.game.tableau[0].append(two_hearts)

        success = self.game.move_tableau_to_foundation(0, 0)
        self.assertTrue(success)
        self.assertEqual(len(self.game.foundations[0]), 2)

    def test_move_tableau_to_foundation_invalid(self):
        self.game.tableau = [[] for _ in range(7)]
        self.game.foundations = [[] for _ in range(4)]

        two_hearts = Card(Suit.HEARTS, Rank.TWO)
        two_hearts.show()
        self.game.tableau[0].append(two_hearts)

        # Cannot move 2 to empty
        self.assertFalse(self.game.move_tableau_to_foundation(0, 0))

    def test_move_tableau_to_foundation_empty_col(self):
        self.game.tableau = [[] for _ in range(7)]
        self.assertFalse(self.game.move_tableau_to_foundation(0, 0))

    def test_move_foundation_to_tableau(self):
        self.game.tableau = [[] for _ in range(7)]
        self.game.foundations = [[] for _ in range(4)]

        k_spades = Card(Suit.SPADES, Rank.KING)
        k_spades.show()
        self.game.tableau[0].append(k_spades)

        q_hearts = Card(Suit.HEARTS, Rank.QUEEN)
        q_hearts.show()
        self.game.foundations[0].append(q_hearts)

        success = self.game.move_foundation_to_tableau(0, 0)
        self.assertTrue(success)
        self.assertEqual(len(self.game.tableau[0]), 2)
        self.assertEqual(len(self.game.foundations[0]), 0)

    def test_move_foundation_to_tableau_empty(self):
        self.game.foundations = [[] for _ in range(4)]
        self.assertFalse(self.game.move_foundation_to_tableau(0, 0))

    # --- Auto Move & Win ---
    def test_auto_move_to_foundation(self):
        self.game.tableau = [[] for _ in range(7)]
        self.game.waste = []
        self.game.foundations = [[] for _ in range(4)]

        # Setup: Ace in Waste, Ace in Tableau
        a_hearts = Card(Suit.HEARTS, Rank.ACE)
        a_hearts.show()
        self.game.waste.append(a_hearts)

        a_spades = Card(Suit.SPADES, Rank.ACE)
        a_spades.show()
        self.game.tableau[0].append(a_spades)

        # Should move both
        self.assertTrue(self.game.auto_move_to_foundation())

        # Check if foundations are populated
        count = sum(len(f) for f in self.game.foundations)
        self.assertEqual(count, 2)

    # --- Reset / Re-deal Tests ---
    def test_reset_game(self):
        """Test that resetting the game clears state and redeals"""
        # Modify state
        self.game.moves = 10
        self.game.score = 50
        self.game.history = [{'mock': 'state'}]

        # Trigger reset
        self.game.reset_game()

        # Verify reset
        self.assertEqual(self.game.moves, 0)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(len(self.game.history), 0)

        # Verify deck was redealt (full stock minus tableau cards)
        # 52 cards total - 28 tableau cards = 24 stock cards
        self.assertEqual(len(self.game.stock), 24)
        self.assertEqual(len(self.game.waste), 0)

    def test_check_win(self):
        self.assertFalse(self.game.check_win())
        # Fill foundations artificially
        for f in self.game.foundations:
            for _ in range(13):
                f.append(Card(Suit.HEARTS, Rank.ACE))
        self.assertTrue(self.game.check_win())

    # --- Undo Tests ---
    def test_undo_draw(self):
        """Test undoing a stock draw"""
        initial_stock = len(self.game.stock)
        self.game.draw_from_stock()

        self.assertTrue(self.game.undo())
        self.assertEqual(len(self.game.stock), initial_stock)
        self.assertEqual(len(self.game.waste), 0)

    def test_undo_empty_history(self):
        self.game.history = []
        self.assertFalse(self.game.undo())

    def test_undo_tableau_move(self):
        """Test undoing a card move between tableau columns"""
        self.game.tableau = [[] for _ in range(7)]

        k_spades = Card(Suit.SPADES, Rank.KING)
        k_spades.show()
        self.game.tableau[0].append(k_spades)

        q_hearts = Card(Suit.HEARTS, Rank.QUEEN)
        q_hearts.show()
        self.game.tableau[1].append(q_hearts)

        # Perform move
        self.game.move_tableau_to_tableau(1, 0, 1)
        self.assertEqual(len(self.game.tableau[1]), 0)

        # Undo
        self.game.undo()

        # Verify restoration
        self.assertEqual(len(self.game.tableau[1]), 1)
        restored_card = self.game.tableau[1][0]
        # Compare properties since objects might be regenerated by deepcopy
        self.assertEqual(restored_card.rank, q_hearts.rank)
        self.assertEqual(restored_card.suit, q_hearts.suit)
        self.assertEqual(restored_card.face_up, q_hearts.face_up)

    def test_undo_auto_move(self):
        """Ensure auto-move is treated as a single undoable action"""
        self.game.tableau = [[] for _ in range(7)]
        self.game.waste = []
        self.game.foundations = [[] for _ in range(4)]

        a_hearts = Card(Suit.HEARTS, Rank.ACE)
        a_hearts.show()
        self.game.waste.append(a_hearts)

        # Perform auto move
        self.game.auto_move_to_foundation()
        self.assertEqual(len(self.game.waste), 0)

        # Undo
        self.game.undo()
        self.assertEqual(len(self.game.waste), 1)
        self.assertEqual(self.game.waste[0].suit, Suit.HEARTS)

class TestScoreManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.original_env = os.environ.get('SNAP_USER_DATA')
        # Point the score manager to the temp directory via env var logic
        os.environ['SNAP_USER_DATA'] = self.test_dir

    def tearDown(self):
        # Restore env and remove temp dir
        if self.original_env:
            os.environ['SNAP_USER_DATA'] = self.original_env
        else:
            del os.environ['SNAP_USER_DATA']
        shutil.rmtree(self.test_dir)

    def test_save_and_load_scores(self):
        manager = ScoreManager()
        # Save a score
        manager.save_score(100, 50)

        # Verify it loaded in memory
        scores = manager.get_high_scores()
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]['score'], 100)
        self.assertEqual(scores[0]['moves'], 50)

        # Verify it persists to disk (reload)
        new_manager = ScoreManager()
        loaded_scores = new_manager.get_high_scores()
        self.assertEqual(len(loaded_scores), 1)
        self.assertEqual(loaded_scores[0]['score'], 100)

    def test_score_sorting_and_limit(self):
        manager = ScoreManager()
        # Save 12 scores
        for i in range(12):
            manager.save_score(i * 10, i + 5)

        scores = manager.get_high_scores()

        # Should be limited to 10
        self.assertEqual(len(scores), 10)

        # Top score should be the highest (110)
        self.assertEqual(scores[0]['score'], 110)
        # Lowest in top 10 should be 20
        self.assertEqual(scores[-1]['score'], 20)

if __name__ == '__main__':
    unittest.main()
