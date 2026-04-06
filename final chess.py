import tkinter as tk
from tkinter import messagebox, filedialog
from dataclasses import dataclass
import json
import random

# =========================
# COULEURS MENU
# =========================
BG_COLOR = "#1e1e2f"
ACCENT = "#a599c9"
LIGHT = "#f8f4ff"
BUTTON = "#2e2e4d"

# =========================
# COULEURS JEU
# =========================
MAGNOLIA = "#F8F4FF"
WISTERIA = "#A599C9"
DEEP_WISTERIA = "#7C6B98"
SOFT_TEXT = "#6C6180"
MOVE_DOT = "#D8CDF0"
SELECT_BORDER = "#5F4E7B"

SQUARE_SIZE = 78
BOARD_PIXELS = SQUARE_SIZE * 8
FILES = "abcdefgh"

UNICODE_PIECES = {
    ("K", 0): "♔", ("Q", 0): "♕", ("R", 0): "♖", ("B", 0): "♗", ("N", 0): "♘", ("P", 0): "♙",
    ("K", 1): "♚", ("Q", 1): "♛", ("R", 1): "♜", ("B", 1): "♝", ("N", 1): "♞", ("P", 1): "♟",
}


# =========================
# LOGIQUE DES POSITIONS
# =========================
@dataclass(frozen=True)
class Position:
    column: str
    row: int

    def __str__(self):
        return f"{self.column}{self.row}"

    def to_xy(self):
        return FILES.index(self.column), 8 - self.row

    @staticmethod
    def from_xy(col: int, row_index: int):
        return Position(FILES[col], 8 - row_index)


# =========================
# PIECES
# =========================
class Piece:
    def __init__(self, position: Position, color: int):
        self._position = position
        self._color = color  # 0 = blanc, 1 = noir

    def getPosition(self):
        return self._position

    def setPosition(self, position: Position):
        self._position = position

    def getColor(self):
        return self._color

    def symbol(self):
        return UNICODE_PIECES[(str(self), self._color)]

    def is_inside(self, position: Position):
        return position.column in FILES and 1 <= position.row <= 8

    def is_same_color_at(self, board, position: Position):
        target = board.getPiece(position)
        return target is not None and target.getColor() == self._color

    def is_enemy_at(self, board, position: Position):
        target = board.getPiece(position)
        return target is not None and target.getColor() != self._color

    def isValidMove(self, newPosition: Position, board):
        raise NotImplementedError


class King(Piece):
    def __str__(self):
        return "K"

    def isValidMove(self, newPosition: Position, board):
        if not self.is_inside(newPosition) or self.is_same_color_at(board, newPosition):
            return False
        dc = abs(FILES.index(newPosition.column) - FILES.index(self.getPosition().column))
        dr = abs(newPosition.row - self.getPosition().row)
        return (dc != 0 or dr != 0) and dc <= 1 and dr <= 1


class Queen(Piece):
    def __str__(self):
        return "Q"

    def isValidMove(self, newPosition: Position, board):
        if not self.is_inside(newPosition) or self.is_same_color_at(board, newPosition):
            return False
        start = self.getPosition()
        dc = FILES.index(newPosition.column) - FILES.index(start.column)
        dr = newPosition.row - start.row
        if dc == 0 and dr == 0:
            return False
        if dc == 0 or dr == 0 or abs(dc) == abs(dr):
            return board.pathClear(start, newPosition)
        return False


class Rook(Piece):
    def __str__(self):
        return "R"

    def isValidMove(self, newPosition: Position, board):
        if not self.is_inside(newPosition) or self.is_same_color_at(board, newPosition):
            return False
        start = self.getPosition()
        if start == newPosition:
            return False
        if start.column != newPosition.column and start.row != newPosition.row:
            return False
        return board.pathClear(start, newPosition)


class Bishop(Piece):
    def __str__(self):
        return "B"

    def isValidMove(self, newPosition: Position, board):
        if not self.is_inside(newPosition) or self.is_same_color_at(board, newPosition):
            return False
        start = self.getPosition()
        dc = abs(FILES.index(newPosition.column) - FILES.index(start.column))
        dr = abs(newPosition.row - start.row)
        if dc == 0 or dc != dr:
            return False
        return board.pathClear(start, newPosition)


class Knight(Piece):
    def __str__(self):
        return "N"

    def isValidMove(self, newPosition: Position, board):
        if not self.is_inside(newPosition) or self.is_same_color_at(board, newPosition):
            return False
        start = self.getPosition()
        dc = abs(FILES.index(newPosition.column) - FILES.index(start.column))
        dr = abs(newPosition.row - start.row)
        return (dc, dr) in {(1, 2), (2, 1)}


class Pawn(Piece):
    def __str__(self):
        return "P"

    def isValidMove(self, newPosition: Position, board):
        if not self.is_inside(newPosition):
            return False

        start = self.getPosition()
        direction = 1 if self.getColor() == 0 else -1
        start_row = 2 if self.getColor() == 0 else 7

        dc = FILES.index(newPosition.column) - FILES.index(start.column)
        dr = newPosition.row - start.row
        target = board.getPiece(newPosition)

        if dc == 0:
            if dr == direction and target is None:
                return True
            if dr == 2 * direction and start.row == start_row and target is None:
                middle = Position(start.column, start.row + direction)
                return board.getPiece(middle) is None
            return False

        if abs(dc) == 1 and dr == direction:
            return target is not None and target.getColor() != self.getColor()

        return False


# =========================
# PLATEAU
# =========================
class Board:
    def __init__(self):
        self.__grid = {}
        self.__initBoard()

    def __initBoard(self):
        self.__grid.clear()

        # Blancs
        self.__grid["a1"] = Rook(Position("a", 1), 0)
        self.__grid["b1"] = Knight(Position("b", 1), 0)
        self.__grid["c1"] = Bishop(Position("c", 1), 0)
        self.__grid["d1"] = Queen(Position("d", 1), 0)
        self.__grid["e1"] = King(Position("e", 1), 0)
        self.__grid["f1"] = Bishop(Position("f", 1), 0)
        self.__grid["g1"] = Knight(Position("g", 1), 0)
        self.__grid["h1"] = Rook(Position("h", 1), 0)

        for col in FILES:
            self.__grid[f"{col}2"] = Pawn(Position(col, 2), 0)

        # Noirs
        self.__grid["a8"] = Rook(Position("a", 8), 1)
        self.__grid["b8"] = Knight(Position("b", 8), 1)
        self.__grid["c8"] = Bishop(Position("c", 8), 1)
        self.__grid["d8"] = Queen(Position("d", 8), 1)
        self.__grid["e8"] = King(Position("e", 8), 1)
        self.__grid["f8"] = Bishop(Position("f", 8), 1)
        self.__grid["g8"] = Knight(Position("g", 8), 1)
        self.__grid["h8"] = Rook(Position("h", 8), 1)

        for col in FILES:
            self.__grid[f"{col}7"] = Pawn(Position(col, 7), 1)

    def reset(self):
        self.__initBoard()

    def getPiece(self, position: Position):
        return self.__grid.get(str(position))

    def setPiece(self, position: Position, piece):
        if piece is None:
            self.__grid.pop(str(position), None)
        else:
            piece.setPosition(position)
            self.__grid[str(position)] = piece

    def removePiece(self, position: Position):
        self.__grid.pop(str(position), None)

    def getAllPieces(self):
        return list(self.__grid.values())

    def getPiecesByColor(self, color: int):
        return [piece for piece in self.__grid.values() if piece.getColor() == color]

    def getKingPosition(self, color: int):
        for piece in self.__grid.values():
            if isinstance(piece, King) and piece.getColor() == color:
                return piece.getPosition()
        return None

    def pathClear(self, start: Position, end: Position):
        start_col = FILES.index(start.column)
        end_col = FILES.index(end.column)
        start_row = start.row
        end_row = end.row

        step_col = 0 if start_col == end_col else (1 if end_col > start_col else -1)
        step_row = 0 if start_row == end_row else (1 if end_row > start_row else -1)

        current_col = start_col + step_col
        current_row = start_row + step_row

        while (current_col, current_row) != (end_col, end_row):
            pos = Position(FILES[current_col], current_row)
            if self.getPiece(pos) is not None:
                return False
            current_col += step_col
            current_row += step_row

        return True

    def movePiece(self, start: Position, end: Position):
        piece = self.getPiece(start)
        if piece is None:
            return False

        self.removePiece(start)
        self.removePiece(end)
        piece.setPosition(end)
        self.__grid[str(end)] = piece
        return True

    def clone(self):
        new_board = Board()
        new_board._Board__grid = {}

        mapping = {
            "K": King,
            "Q": Queen,
            "R": Rook,
            "B": Bishop,
            "N": Knight,
            "P": Pawn
        }

        for key, piece in self.__grid.items():
            cls = mapping[str(piece)]
            pos = piece.getPosition()
            new_piece = cls(Position(pos.column, pos.row), piece.getColor())
            new_board._Board__grid[key] = new_piece

        return new_board

    def to_dict(self):
        data = []
        for piece in self.__grid.values():
            pos = piece.getPosition()
            data.append({
                "type": str(piece),
                "color": piece.getColor(),
                "column": pos.column,
                "row": pos.row,
            })
        return data

    def from_dict(self, data):
        self.__grid = {}
        mapping = {
            "K": King,
            "Q": Queen,
            "R": Rook,
            "B": Bishop,
            "N": Knight,
            "P": Pawn
        }

        for item in data:
            cls = mapping[item["type"]]
            pos = Position(item["column"], item["row"])
            piece = cls(pos, item["color"])
            self.__grid[str(pos)] = piece


# =========================
# REGLES
# =========================
class ChessRules:
    @staticmethod
    def is_check(board: Board, color: int):
        king_pos = board.getKingPosition(color)
        if king_pos is None:
            return True

        enemy_color = 1 - color
        for piece in board.getPiecesByColor(enemy_color):
            if piece.isValidMove(king_pos, board):
                return True

        return False

    @staticmethod
    def is_legal_move(board: Board, start: Position, end: Position, color: int):
        piece = board.getPiece(start)

        if piece is None or piece.getColor() != color:
            return False

        if not piece.isValidMove(end, board):
            return False

        test_board = board.clone()
        test_board.movePiece(start, end)

        return not ChessRules.is_check(test_board, color)

    @staticmethod
    def get_legal_moves(board: Board, position: Position):
        piece = board.getPiece(position)
        if piece is None:
            return []

        color = piece.getColor()
        moves = []

        for col in FILES:
            for row in range(1, 9):
                target = Position(col, row)
                if ChessRules.is_legal_move(board, position, target, color):
                    moves.append(target)

        return moves

    @staticmethod
    def has_any_legal_move(board: Board, color: int):
        for piece in board.getPiecesByColor(color):
            if ChessRules.get_legal_moves(board, piece.getPosition()):
                return True
        return False

    @staticmethod
    def is_checkmate(board: Board, color: int):
        return ChessRules.is_check(board, color) and not ChessRules.has_any_legal_move(board, color)

    @staticmethod
    def is_stalemate(board: Board, color: int):
        return not ChessRules.is_check(board, color) and not ChessRules.has_any_legal_move(board, color)


# =========================
# MENU
# =========================
class Menu:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        self.root.geometry("700x760")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        self.mode = tk.StringVar()
        self.mode.set("player")

        self.create_ui()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_ui(self):
        title = tk.Label(
            self.root,
            text="CHESS",
            font=("Arial", 32, "bold"),
            fg=LIGHT,
            bg=BG_COLOR
        )
        title.pack(pady=80)

        subtitle = tk.Label(
            self.root,
            text="Choisis ton mode de jeu",
            font=("Arial", 16),
            fg=ACCENT,
            bg=BG_COLOR
        )
        subtitle.pack(pady=10)

        mode_frame = tk.Frame(self.root, bg=BG_COLOR)
        mode_frame.pack(pady=50)

        ia_button = tk.Radiobutton(
            mode_frame,
            text="IA",
            variable=self.mode,
            value="ai",
            font=("Arial", 14, "bold"),
            fg=LIGHT,
            bg=BUTTON,
            selectcolor=ACCENT,
            activebackground=BUTTON,
            activeforeground=LIGHT,
            width=14,
            height=2,
            indicatoron=0,
            bd=0
        )
        ia_button.grid(row=0, column=0, padx=10)

        player_button = tk.Radiobutton(
            mode_frame,
            text="Utilisateur",
            variable=self.mode,
            value="player",
            font=("Arial", 14, "bold"),
            fg=LIGHT,
            bg=BUTTON,
            selectcolor=ACCENT,
            activebackground=BUTTON,
            activeforeground=LIGHT,
            width=14,
            height=2,
            indicatoron=0,
            bd=0
        )
        player_button.grid(row=0, column=1, padx=10)

        start_button = tk.Button(
            self.root,
            text="START",
            font=("Arial", 16, "bold"),
            bg=ACCENT,
            fg="white",
            activebackground=ACCENT,
            activeforeground="white",
            width=15,
            height=2,
            bd=0,
            command=self.start_game
        )
        start_button.pack(pady=40)

    def start_game(self):
        chosen_mode = self.mode.get()

        if chosen_mode == "ai":
            messagebox.showinfo("Mode choisi", "Vous allez jouer contre l'IA")
        else:
            messagebox.showinfo("Mode choisi", "Vous allez jouer à deux joueurs")

        self.clear_window()
        ChessGUI(self.root, chosen_mode)


# =========================
# INTERFACE JEU
# =========================
class ChessGUI:
    def __init__(self, root, mode="player"):
        self.root = root
        self.mode = mode  # "ai" ou "player"

        self.root.title("Chess meri et lina")
        self.root.geometry("700x760")
        self.root.configure(bg=MAGNOLIA)
        self.root.resizable(False, False)

        self.board = Board()
        self.currentColor = 0  # 0 = blancs, 1 = noirs
        self.selectedPosition = None
        self.legalMoves = []

        self.build_ui()
        self.updateStatus()
        self.drawBoard()

    def build_ui(self):
        top = tk.Frame(self.root, bg=MAGNOLIA)
        top.pack(fill="x", padx=18, pady=(14, 8))

        self.titleLabel = tk.Label(
            top,
            text="Chess",
            font=("Georgia", 28, "bold"),
            bg=MAGNOLIA,
            fg=WISTERIA,
        )
        self.titleLabel.pack()

        mode_text = "Mode : IA" if self.mode == "ai" else "Mode : 2 joueurs"
        self.modeLabel = tk.Label(
            top,
            text=mode_text,
            font=("Helvetica", 12, "bold"),
            bg=MAGNOLIA,
            fg=SOFT_TEXT,
        )
        self.modeLabel.pack(pady=(4, 0))

        self.statusLabel = tk.Label(
            top,
            text="",
            font=("Helvetica", 12),
            bg=MAGNOLIA,
            fg=SOFT_TEXT,
        )
        self.statusLabel.pack(pady=(4, 0))

        self.canvas = tk.Canvas(
            self.root,
            width=BOARD_PIXELS,
            height=BOARD_PIXELS,
            bg=MAGNOLIA,
            highlightthickness=0,
        )
        self.canvas.pack(padx=18, pady=10)
        self.canvas.bind("<Button-1>", self.onClick)

        bottom = tk.Frame(self.root, bg=MAGNOLIA)
        bottom.pack(fill="x", padx=18, pady=(0, 16))

        btn_style = {
            "bg": WISTERIA,
            "fg": "white",
            "activebackground": DEEP_WISTERIA,
            "activeforeground": "white",
            "relief": "flat",
            "font": ("Helvetica", 10, "bold"),
            "cursor": "hand2",
            "padx": 10,
            "pady": 8,
            "bd": 0
        }

        tk.Button(bottom, text="Nouvelle partie", command=self.resetGame, **btn_style).pack(side="left", padx=(0, 8))
        tk.Button(bottom, text="Sauvegarder", command=self.saveGame, **btn_style).pack(side="left", padx=(0, 8))
        tk.Button(bottom, text="Charger", command=self.loadGame, **btn_style).pack(side="left", padx=(0, 8))
        tk.Button(bottom, text="Retour menu", command=self.backToMenu, **btn_style).pack(side="left")

        self.helpLabel = tk.Label(
            bottom,
            text="Clique une pièce puis une case valide",
            font=("Helvetica", 10),
            bg=MAGNOLIA,
            fg=SOFT_TEXT,
        )
        self.helpLabel.pack(side="right")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def backToMenu(self):
        self.clear_window()
        self.root.configure(bg=BG_COLOR)
        Menu(self.root)

    def resetGame(self):
        self.board.reset()
        self.currentColor = 0
        self.selectedPosition = None
        self.legalMoves = []
        self.updateStatus()
        self.drawBoard()

    def saveGame(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")]
        )
        if not filename:
            return

        data = {
            "currentColor": self.currentColor,
            "mode": self.mode,
            "board": self.board.to_dict(),
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        messagebox.showinfo("Sauvegarde", "Partie sauvegardée avec succès.")

    def loadGame(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not filename:
            return

        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.board.from_dict(data["board"])
        self.currentColor = data.get("currentColor", 0)
        self.mode = data.get("mode", self.mode)
        self.selectedPosition = None
        self.legalMoves = []

        self.modeLabel.config(text="Mode : IA" if self.mode == "ai" else "Mode : 2 joueurs")
        self.updateStatus()
        self.drawBoard()

        messagebox.showinfo("Chargement", "Partie chargée avec succès.")

        if self.mode == "ai" and self.currentColor == 1:
            self.root.after(500, self.ai_move)

    def drawBoard(self):
        self.canvas.delete("all")

        for row_index in range(8):
            for col_index in range(8):
                x1 = col_index * SQUARE_SIZE
                y1 = row_index * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE

                fill = MAGNOLIA if (row_index + col_index) % 2 == 0 else WISTERIA
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=fill)

                pos = Position.from_xy(col_index, row_index)

                if pos == self.selectedPosition:
                    self.canvas.create_rectangle(
                        x1 + 4, y1 + 4, x2 - 4, y2 - 4,
                        outline=SELECT_BORDER,
                        width=3
                    )

                if pos in self.legalMoves:
                    self.canvas.create_oval(
                        x1 + 28, y1 + 28, x2 - 28, y2 - 28,
                        fill=MOVE_DOT,
                        outline=""
                    )

                piece = self.board.getPiece(pos)
                if piece is not None:
                    if piece.getColor() == 0:
                        self.canvas.create_text(
                            x1 + SQUARE_SIZE / 2 + 1,
                            y1 + SQUARE_SIZE / 2 + 1,
                            text=piece.symbol(),
                            font=("Segoe UI Symbol", 34),
                            fill=DEEP_WISTERIA,
                        )
                        self.canvas.create_text(
                            x1 + SQUARE_SIZE / 2,
                            y1 + SQUARE_SIZE / 2,
                            text=piece.symbol(),
                            font=("Segoe UI Symbol", 34),
                            fill=MAGNOLIA,
                        )
                    else:
                        self.canvas.create_text(
                            x1 + SQUARE_SIZE / 2,
                            y1 + SQUARE_SIZE / 2,
                            text=piece.symbol(),
                            font=("Segoe UI Symbol", 34),
                            fill=DEEP_WISTERIA,
                        )

        for i, file_letter in enumerate(FILES):
            self.canvas.create_text(
                i * SQUARE_SIZE + SQUARE_SIZE / 2,
                BOARD_PIXELS - 8,
                text=file_letter,
                fill=SOFT_TEXT,
                font=("Helvetica", 10, "bold")
            )

        for i in range(8):
            self.canvas.create_text(
                10,
                i * SQUARE_SIZE + SQUARE_SIZE / 2,
                text=str(8 - i),
                fill=SOFT_TEXT,
                font=("Helvetica", 10, "bold")
            )

    def updateStatus(self, extra_text=""):
        turn = "Blancs" if self.currentColor == 0 else "Noirs"
        text = f"Tour des {turn}"

        if self.mode == "ai":
            if self.currentColor == 0:
                text += " (vous)"
            else:
                text += " (IA)"

        if ChessRules.is_check(self.board, self.currentColor):
            text += " — Échec"

        if extra_text:
            text += f" — {extra_text}"

        self.statusLabel.config(text=text)

    def finishIfNeeded(self):
        if ChessRules.is_checkmate(self.board, self.currentColor):
            winner = "Blancs" if self.currentColor == 1 else "Noirs"
            self.updateStatus("Échec et mat")
            messagebox.showinfo("Fin de partie", f"Échec et mat ! Les {winner} gagnent.")
            return True

        if ChessRules.is_stalemate(self.board, self.currentColor):
            self.updateStatus("Pat")
            messagebox.showinfo("Fin de partie", "Pat ! Match nul.")
            return True

        return False

    def get_all_legal_moves_for_color(self, color):
        all_moves = []

        for piece in self.board.getPiecesByColor(color):
            start = piece.getPosition()
            legal_moves = ChessRules.get_legal_moves(self.board, start)
            for end in legal_moves:
                all_moves.append((start, end))

        return all_moves

    def ai_move(self):
        if self.mode != "ai":
            return

        if self.currentColor != 1:
            return

        if self.finishIfNeeded():
            return

        all_moves = self.get_all_legal_moves_for_color(1)

        if not all_moves:
            self.finishIfNeeded()
            return

        # IA simple : choisit un coup au hasard
        start, end = random.choice(all_moves)
        self.board.movePiece(start, end)

        self.currentColor = 0
        self.selectedPosition = None
        self.legalMoves = []

        self.updateStatus("L'IA a joué")
        self.drawBoard()

        self.finishIfNeeded()
        self.updateStatus()
        self.drawBoard()

    def onClick(self, event):
        # Si mode IA et c'est au tour des noirs, le joueur ne peut pas cliquer
        if self.mode == "ai" and self.currentColor == 1:
            return

        col = event.x // SQUARE_SIZE
        row_index = event.y // SQUARE_SIZE

        if not (0 <= col < 8 and 0 <= row_index < 8):
            return

        clicked = Position.from_xy(col, row_index)
        clicked_piece = self.board.getPiece(clicked)

        if self.selectedPosition is None:
            if clicked_piece is None:
                return

            if clicked_piece.getColor() != self.currentColor:
                messagebox.showinfo("Tour incorrect", "Ce n'est pas le tour de cette pièce.")
                return

            self.selectedPosition = clicked
            self.legalMoves = ChessRules.get_legal_moves(self.board, clicked)
            self.drawBoard()
            return

        if clicked == self.selectedPosition:
            self.selectedPosition = None
            self.legalMoves = []
            self.drawBoard()
            return

        if clicked in self.legalMoves:
            self.board.movePiece(self.selectedPosition, clicked)
            self.selectedPosition = None
            self.legalMoves = []

            self.currentColor = 1 - self.currentColor
            self.updateStatus()
            self.drawBoard()

            if self.finishIfNeeded():
                return

            # Si mode IA, l'IA joue automatiquement après le joueur
            if self.mode == "ai" and self.currentColor == 1:
                self.updateStatus("L'IA réfléchit...")
                self.drawBoard()
                self.root.after(500, self.ai_move)
                return

            self.updateStatus()
            self.drawBoard()
            return

        if clicked_piece is not None and clicked_piece.getColor() == self.currentColor:
            self.selectedPosition = clicked
            self.legalMoves = ChessRules.get_legal_moves(self.board, clicked)
            self.drawBoard()
            return

        messagebox.showwarning("Coup invalide", "Déplacement interdit.")


# =========================
# LANCEMENT
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = Menu(root)
    root.mainloop()
