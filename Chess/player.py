class Player:
    def __init__(self, name: str, color: int):
        self.__name = name
        self.__color = color  # 0 = blanc, 1 = noir

    def getName(self):
        return self.__name

    def getColor(self):
        return self.__color

    def askMove(self) -> str:
        """Demande au joueur de saisir son coup (ex: 'Nb1 Nc3')"""
        move = input(f"{self.__name} ({'Blanc' if self.__color == 0 else 'Noir'}), entrez votre coup: ")
        return move


class AIPlayer(Player):
    def __init__(self, color: int):
        super().__init__("AI", color)

    def askMove(self) -> str:
        """Génère un mouvement aléatoire"""
        import random
        # TODO: implémenter une IA plus intelligente
        cols = "abcdefgh"
        piece_ids = ["K", "Q", "B", "N", "R", "P"]
        move = (f"{random.choice(piece_ids)}{random.choice(cols)}{random.randint(1,8)} "
                f"{random.choice(cols)}{random.randint(1,8)}")
        return move
