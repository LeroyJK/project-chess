from board import Board
from player import Player, AIPlayer
import json

class Chess:
    def __init__(self):
        self.__board = Board()
        self.__players = []        # liste de 2 Player
        self.__currentPlayer = None

    def initPlayers(self):
        """Initialise les deux joueurs"""
        for i, color in enumerate([0, 1]):
            name = input(f"Nom du joueur {i+1} (entrez 'AI' pour un joueur automatique): ")
            if name == "AI":
                self.__players.append(AIPlayer(color))
            else:
                self.__players.append(Player(name, color))
        self.__currentPlayer = self.__players[0]

    def displayBoard(self):
        """Affiche l'échiquier"""
        self.__board.display()

    def isValidMove(self, move: str) -> bool:
        """Vérifie si le coup saisi est valide"""
        # TODO: parser la chaîne move et appeler piece.isValidMove()
        return True

    def isCheckMate(self) -> bool:
        """Vérifie si un joueur est échec et mat"""
        # TODO: implémenter la logique d'échec et mat
        return False

    def updateBoard(self, move: str):
        """Met à jour l'échiquier après un coup valide"""
        # TODO: parser move et déplacer la pièce sur le board
        pass

    def switchPlayer(self):
        """Passe au joueur suivant"""
        if self.__currentPlayer == self.__players[0]:
            self.__currentPlayer = self.__players[1]
        else:
            self.__currentPlayer = self.__players[0]

    def saveGame(self, filename: str = "save/savegame.json"):
        """Sauvegarde la partie dans un fichier JSON"""
        # TODO: sérialiser l'état du board
        pass

    def loadGame(self, filename: str = "save/savegame.json"):
        """Charge une partie depuis un fichier JSON"""
        # TODO: désérialiser et restaurer l'état du board
        pass

    def play(self):
        """Boucle principale du jeu"""
        self.initPlayers()
        while not self.isCheckMate():
            self.displayBoard()
            move = ""
            while not self.isValidMove(move):
                move = self.__currentPlayer.askMove()
            self.updateBoard(move)
            self.switchPlayer()
        print("Échec et mat !")
