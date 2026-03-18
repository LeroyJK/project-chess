class Position:
    def __init__(self, column: str, row: int):
        self.__column = column
        self.__row = row

    def getColumn(self):
        return self.__column

    def getRow(self):
        return self.__row

    def setColumn(self, column: str):
        self.__column = column

    def setRow(self, row: int):
        self.__row = row

    def __str__(self):
        return f"{self.__column}{self.__row}"

    def __eq__(self, other):
        return self.__column == other.getColumn() and self.__row == other.getRow()
