from abc import ABC, abstractmethod
from position import Position

class Piece(ABC):
    def __init__(self, position: Position, color: int):
        self.__position = position  # 0 = blanc, 1 = noir
        self.__color = color

    def getPosition(self):
        return self.__position

    def getColor(self):
        return self.__color

    def setPosition(self, position: Position):
        self.__position = position

    @abstractmethod
    def isValidMove(self, newPosition: Position, board) -> bool:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass
