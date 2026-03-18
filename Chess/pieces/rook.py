from piece import Piece
from position import Position

class Rook(Piece):
    def __init__(self, position: Position, color: int):
        super().__init__(position, color)

    def isValidMove(self, newPosition: Position, board) -> bool:
        # TODO: déplacement en lignes droites (horizontal/vertical)
        return True

    def __str__(self):
        return "R"
