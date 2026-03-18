from piece import Piece
from position import Position

class Pawn(Piece):
    def __init__(self, position: Position, color: int):
        super().__init__(position, color)

    def isValidMove(self, newPosition: Position, board) -> bool:
        # TODO: avance d'1 case (2 au départ), capture en diagonale
        return True

    def __str__(self):
        return "P"
