import unittest
import sys
sys.path.append("..")
from board import Board
from position import Position

class TestBoard(unittest.TestCase):

    def setUp(self):
        self.board = Board()

    def test_initial_piece_at_e1(self):
        """Le Roi blanc doit être en e1 au départ"""
        piece = self.board.getPiece(Position("e", 1))
        self.assertIsNotNone(piece)
        self.assertEqual(str(piece), "K")

    def test_empty_square(self):
        """Une case vide doit retourner None"""
        piece = self.board.getPiece(Position("e", 4))
        self.assertIsNone(piece)

if __name__ == "__main__":
    unittest.main()
