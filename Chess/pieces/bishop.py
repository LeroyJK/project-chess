from piece import Piece
from position import Position

class Bishop(Piece):
    def __init__(self, position: Position, color: int):
        super().__init__(position, color)

    def isValidMove(self, newPosition: Position, board) -> bool:
        # TODO: déplacement en diagonale uniquement
        return True

    def __str__(self):
        return "B"
