from piece import Piece
from position import Position

class King(Piece):
    def __init__(self, position: Position, color: int):
        super().__init__(position, color)

    def isValidMove(self, newPosition: Position, board) -> bool:
        # TODO: déplacement d'1 case dans toutes les directions
        return True

    def __str__(self):
        return "K"
