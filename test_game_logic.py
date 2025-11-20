import unittest
from game_logic import Card, Deck, SolitaireGame, Suit, Rank

class TestSolitaireGame(unittest.TestCase):
    def setUp(self):
        self.game = SolitaireGame()

    def test_deck_creation(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)

    def test_initial_deal(self):
        # Check tableau sizes: 1, 2, 3, 4, 5, 6, 7
        for i in range(7):
            self.assertEqual(len(self.game.tableau[i]), i + 1)
            # Top card should be face up
            self.assertTrue(self.game.tableau[i][-1].face_up)
            # Others should be face down
            for j in range(i):
                self.assertFalse(self.game.tableau[i][j].face_up)
        
        # Check stock size: 52 - (1+2+3+4+5+6+7) = 52 - 28 = 24
        self.assertEqual(len(self.game.stock), 24)
        self.assertEqual(len(self.game.waste), 0)

    def test_draw_from_stock(self):
        initial_stock_len = len(self.game.stock)
        self.game.draw_from_stock()
        self.assertEqual(len(self.game.stock), initial_stock_len - 1)
        self.assertEqual(len(self.game.waste), 1)
        self.assertTrue(self.game.waste[0].face_up)

    def test_recycle_waste(self):
        # Move all stock to waste
        while self.game.stock:
            self.game.draw_from_stock()
        
        self.assertEqual(len(self.game.stock), 0)
        self.assertEqual(len(self.game.waste), 24)
        
        # Trigger recycle
        self.game.draw_from_stock()
        self.assertEqual(len(self.game.stock), 24)
        self.assertEqual(len(self.game.waste), 0)
        # Check if recycled cards are face down
        self.assertFalse(self.game.stock[0].face_up)

    def test_valid_tableau_move(self):
        # Setup a specific scenario
        # Clear tableau for easier testing
        self.game.tableau = [[] for _ in range(7)]
        
        # Black King
        k_spades = Card(Suit.SPADES, Rank.KING)
        k_spades.show()
        self.game.tableau[0].append(k_spades)
        
        # Red Queen
        q_hearts = Card(Suit.HEARTS, Rank.QUEEN)
        q_hearts.show()
        self.game.tableau[1].append(q_hearts)
        
        # Move Queen to King
        success = self.game.move_tableau_to_tableau(1, 0, 1)
        self.assertTrue(success)
        self.assertEqual(len(self.game.tableau[0]), 2)
        self.assertEqual(len(self.game.tableau[1]), 0)
        self.assertEqual(self.game.tableau[0][-1], q_hearts)

    def test_invalid_tableau_move_color(self):
        self.game.tableau = [[] for _ in range(7)]
        
        # Black King
        k_spades = Card(Suit.SPADES, Rank.KING)
        k_spades.show()
        self.game.tableau[0].append(k_spades)
        
        # Black Queen (Invalid move)
        q_clubs = Card(Suit.CLUBS, Rank.QUEEN)
        q_clubs.show()
        self.game.tableau[1].append(q_clubs)
        
        success = self.game.move_tableau_to_tableau(1, 0, 1)
        self.assertFalse(success)
        self.assertEqual(len(self.game.tableau[0]), 1)

    def test_invalid_tableau_move_rank(self):
        self.game.tableau = [[] for _ in range(7)]
        
        # Black King
        k_spades = Card(Suit.SPADES, Rank.KING)
        k_spades.show()
        self.game.tableau[0].append(k_spades)
        
        # Red Jack (Invalid rank, needs Queen)
        j_hearts = Card(Suit.HEARTS, Rank.JACK)
        j_hearts.show()
        self.game.tableau[1].append(j_hearts)
        
        success = self.game.move_tableau_to_tableau(1, 0, 1)
        self.assertFalse(success)

    def test_foundation_move(self):
        self.game.tableau = [[] for _ in range(7)]
        self.game.foundations = [[] for _ in range(4)]
        
        # Ace of Hearts
        a_hearts = Card(Suit.HEARTS, Rank.ACE)
        a_hearts.show()
        self.game.tableau[0].append(a_hearts)
        
        # Move to foundation (assuming index 0 is for hearts or any empty one if we implemented it that way, 
        # but current logic checks suit match if not empty. If empty, accepts Ace.
        # My implementation: `can_move_to_foundation` checks if empty -> Ace.
        
        success = self.game.move_tableau_to_foundation(0, 0)
        self.assertTrue(success)
        self.assertEqual(len(self.game.foundations[0]), 1)
        self.assertEqual(self.game.foundations[0][0], a_hearts)
        
        # Two of Hearts
        two_hearts = Card(Suit.HEARTS, Rank.TWO)
        two_hearts.show()
        self.game.tableau[1].append(two_hearts)
        
        success = self.game.move_tableau_to_foundation(1, 0)
        self.assertTrue(success)
        self.assertEqual(len(self.game.foundations[0]), 2)

if __name__ == '__main__':
    unittest.main()
