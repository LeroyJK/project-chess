from position import Position
from pieces.king import King
from pieces.queen import Queen
from pieces.bishop import Bishop
from pieces.knight import Knight
from pieces.rook import Rook
from pieces.pawn import Pawn

class Board:
    def __init__(self):
        # Dictionnaire : clé = "e1" (str position), valeur = pièce
        self.__grid = {}
        self.__initBoard()

    def __initBoard(self):
        # Pièces blanches (color=0)
        self.__grid["a1"] = Rook(Position("a", 1), 0)
        self.__grid["b1"] = Knight(Position("b", 1), 0)
        self.__grid["c1"] = Bishop(Position("c", 1), 0)
        self.__grid["d1"] = Queen(Position("d", 1), 0)
        self.__grid["e1"] = King(Position("e", 1), 0)
        self.__grid["f1"] = Bishop(Position("f", 1), 0)
        self.__grid["g1"] = Knight(Position("g", 1), 0)
        self.__grid["h1"] = Rook(Position("h", 1), 0)
        for col in "abcdefgh":
            self.__grid[f"{col}2"] = Pawn(Position(col, 2), 0)

        # Pièces noires (color=1)
        self.__grid["a8"] = Rook(Position("a", 8), 1)
        self.__grid["b8"] = Knight(Position("b", 8), 1)
        self.__grid["c8"] = Bishop(Position("c", 8), 1)
        self.__grid["d8"] = Queen(Position("d", 8), 1)
        self.__grid["e8"] = King(Position("e", 8), 1)
        self.__grid["f8"] = Bishop(Position("f", 8), 1)
        self.__grid["g8"] = Knight(Position("g", 8), 1)
        self.__grid["h8"] = Rook(Position("h", 8), 1)
        for col in "abcdefgh":
            self.__grid[f"{col}7"] = Pawn(Position(col, 7), 1)

    def getPosition(self, piece):
        """Retourne la Position d'une pièce, ou None si capturée"""
        for key, p in self.__grid.items():
            if p == piece:
                return p.getPosition()
        return None

    def getPiece(self, position: Position):
        """Retourne la pièce à une position, ou None si vide"""
        key = str(position)
        return self.__grid.get(key, None)

    def setPiece(self, position: Position, piece):
        """Place une pièce à une position"""
        self.__grid[str(position)] = piece

    def removePiece(self, position: Position):
        """Retire une pièce de l'échiquier (capturée)"""
        key = str(position)
        if key in self.__grid:
            del self.__grid[key]

    def display(self):
        """Affiche l'échiquier en mode texte"""
        print("  a b c d e f g h")
        for row in range(8, 0, -1):
            line = f"{row} "
            for col in "abcdefgh":
                piece = self.__grid.get(f"{col}{row}", None)
                if piece is None:
                    line += ". "
                else:
                    symbol = piece.__str__()
                    line += (symbol.upper() if piece.getColor() == 0 else symbol.lower()) + " "
            print(line)
        print()
