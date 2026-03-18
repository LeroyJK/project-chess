from piece import Piece
from position import Position

class Queen(Piece):
    def __init__(self, position: Position, color: int):
        super().__init__(position, color)

    def isValidMove(self, newPosition: Position, board) -> bool:
        # TODO: combinaison Tour + Fou (lignes droites + diagonales)
        return True

    def __str__(self):
        return "Q"
