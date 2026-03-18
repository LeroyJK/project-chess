from piece import Piece
from position import Position

class Knight(Piece):
    def __init__(self, position: Position, color: int):
        super().__init__(position, color)

    def isValidMove(self, newPosition: Position, board) -> bool:
        # TODO: déplacement en L (peut sauter par-dessus les pièces)
        return True

    def __str__(self):
        return "N"
