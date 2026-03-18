import unittest
import sys
sys.path.append("..")
from position import Position

class TestPosition(unittest.TestCase):

    def test_str(self):
        pos = Position("e", 1)
        self.assertEqual(str(pos), "e1")

    def test_equality(self):
        pos1 = Position("a", 3)
        pos2 = Position("a", 3)
        self.assertEqual(pos1, pos2)

    def test_getters(self):
        pos = Position("d", 5)
        self.assertEqual(pos.getColumn(), "d")
        self.assertEqual(pos.getRow(), 5)

if __name__ == "__main__":
    unittest.main()
