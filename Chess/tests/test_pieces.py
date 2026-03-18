import unittest
import sys
sys.path.append("..")
from position import Position
from board import Board
from pieces.knight import Knight
from pieces.pawn import Pawn

class TestKnight(unittest.TestCase):

    def setUp(self):
        self.board = Board()

    def test_str(self):
        knight = Knight(Position("b", 1), 0)
        self.assertEqual(str(knight), "N")

    def test_valid_move_placeholder(self):
        """isValidMove retourne True (placeholder)"""
        knight = Knight(Position("b", 1), 0)
        self.assertTrue(knight.isValidMove(Position("c", 3), self.board))

if __name__ == "__main__":
    unittest.main()
