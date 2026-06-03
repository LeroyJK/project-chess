import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from dataclasses import dataclass
import json
import random
import threading
import time

# =========================
# COULEURS MENU
# =========================
BG_COLOR = "#1e1e2f"
ACCENT = "#c99b99"
LIGHT = "#000000"
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
TIMER_NORMAL = "#4a4a6a"
TIMER_WARNING = "#c0392b"
TIMER_OK = "#27ae60"

SQUARE_SIZE = 78
BOARD_PIXELS = SQUARE_SIZE * 8
FILES = "abcdefgh"

UNICODE_PIECES = {
    ("K", 0): "♔", ("Q", 0): "♕", ("R", 0): "♖", ("B", 0): "♗", ("N", 0): "♘", ("P", 0): "♙",
    ("K", 1): "♚", ("Q", 1): "♛", ("R", 1): "♜", ("B", 1): "♝", ("N", 1): "♞", ("P", 1): "♟",
}

# Modes chrono : (label, type, secondes_total_par_joueur, secondes_par_coup)
# type: "total" = budget global par joueur | "per_move" = limite par coup
CLOCK_MODES = {
    "Pas de chrono":     None,
    "Blitz — 1 min":     ("total",    60,  None),
    "Normal — 10 min":   ("total",   600,  None),
    "10 sec / coup":     ("per_move", None, 10),
}

# =========================
# PUZZLES
# =========================
PUZZLES = [
    {
        "name": "Puzzle 1 — Mat en 1",
        "description": "Les Blancs jouent. Trouvez le mat en 1 coup !",
        "board": [
            {"type": "K", "color": 0, "column": "e", "row": 1, "has_moved": True},
            {"type": "Q", "color": 0, "column": "h", "row": 7, "has_moved": True},
            {"type": "K", "color": 1, "column": "e", "row": 8, "has_moved": True},
            {"type": "R", "color": 1, "column": "a", "row": 8, "has_moved": True},
        ],
        "solution": ("h7", "h8"),
        "player_color": 0,
    },
    {
        "name": "Puzzle 2 — Fourchette de cavalier",
        "description": "Les Blancs jouent. Gagnez la dame adverse avec une fourchette de cavalier !",
        "board": [
            {"type": "K", "color": 0, "column": "e", "row": 1, "has_moved": True},
            {"type": "N", "color": 0, "column": "f", "row": 3, "has_moved": True},
            {"type": "K", "color": 1, "column": "e", "row": 8, "has_moved": True},
            {"type": "Q", "color": 1, "column": "d", "row": 5, "has_moved": True},
            {"type": "R", "color": 1, "column": "h", "row": 8, "has_moved": True},
        ],
        "solution": ("f3", "e5"),
        "player_color": 0,
    },
    {
        "name": "Puzzle 3 — Promotion décisive",
        "description": "Les Blancs jouent. Promotionnez votre pion pour gagner !",
        "board": [
            {"type": "K", "color": 0, "column": "a", "row": 1, "has_moved": True},
            {"type": "P", "color": 0, "column": "e", "row": 7, "has_moved": True},
            {"type": "K", "color": 1, "column": "h", "row": 8, "has_moved": True},
        ],
        "solution": ("e7", "e8"),
        "player_color": 0,
    },
    {
        "name": "Puzzle 4 — Clouage gagnant",
        "description": "Les Blancs jouent. Utilisez la tour pour clouer et gagner du matériel !",
        "board": [
            {"type": "K", "color": 0, "column": "g", "row": 1, "has_moved": True},
            {"type": "R", "color": 0, "column": "a", "row": 1, "has_moved": False},
            {"type": "K", "color": 1, "column": "e", "row": 8, "has_moved": True},
            {"type": "Q", "color": 1, "column": "e", "row": 5, "has_moved": True},
            {"type": "N", "color": 1, "column": "e", "row": 3, "has_moved": True},
        ],
        "solution": ("a1", "e1"),
        "player_color": 0,
    },
]

# =========================
# POSITION
# =========================
@dataclass(frozen=True)
class Position:
    column: str
    row: int

    def __str__(self): return f"{self.column}{self.row}"
    def to_xy(self): return FILES.index(self.column), 8 - self.row

    @staticmethod
    def from_xy(col: int, row_index: int):
        return Position(FILES[col], 8 - row_index)


# =========================
# PIECES
# =========================
class Piece:
    def __init__(self, position, color):
        self._position = position
        self._color = color
        self.has_moved = False

    def getPosition(self): return self._position
    def setPosition(self, p): self._position = p
    def getColor(self): return self._color
    def symbol(self): return UNICODE_PIECES[(str(self), self._color)]
    def is_inside(self, p): return p.column in FILES and 1 <= p.row <= 8
    def is_same_color_at(self, board, p):
        t = board.getPiece(p); return t is not None and t.getColor() == self._color
    def isValidMove(self, newPos, board): raise NotImplementedError


class King(Piece):
    def __str__(self): return "K"
    def isValidMove(self, newPos, board):
        if not self.is_inside(newPos) or self.is_same_color_at(board, newPos): return False
        dc = abs(FILES.index(newPos.column) - FILES.index(self.getPosition().column))
        dr = abs(newPos.row - self.getPosition().row)
        if (dc != 0 or dr != 0) and dc <= 1 and dr <= 1: return True
        if dr == 0 and dc == 2 and not self.has_moved: return self._can_castle(newPos, board)
        return False

    def _can_castle(self, newPos, board):
        start = self.getPosition(); color = self.getColor()
        king_col = FILES.index(start.column); target_col = FILES.index(newPos.column)
        row = start.row
        rook_pos = Position("h", row) if target_col > king_col else Position("a", row)
        rook = board.getPiece(rook_pos)
        if rook is None or str(rook) != "R" or rook.getColor() != color or rook.has_moved: return False
        step = 1 if target_col > king_col else -1
        for c in range(king_col + step, FILES.index(rook_pos.column), step):
            if board.getPiece(Position(FILES[c], row)) is not None: return False
        return True


class Queen(Piece):
    def __str__(self): return "Q"
    def isValidMove(self, newPos, board):
        if not self.is_inside(newPos) or self.is_same_color_at(board, newPos): return False
        s = self.getPosition()
        dc = FILES.index(newPos.column) - FILES.index(s.column)
        dr = newPos.row - s.row
        if dc == 0 and dr == 0: return False
        if dc == 0 or dr == 0 or abs(dc) == abs(dr): return board.pathClear(s, newPos)
        return False


class Rook(Piece):
    def __str__(self): return "R"
    def isValidMove(self, newPos, board):
        if not self.is_inside(newPos) or self.is_same_color_at(board, newPos): return False
        s = self.getPosition()
        if s == newPos: return False
        if s.column != newPos.column and s.row != newPos.row: return False
        return board.pathClear(s, newPos)


class Bishop(Piece):
    def __str__(self): return "B"
    def isValidMove(self, newPos, board):
        if not self.is_inside(newPos) or self.is_same_color_at(board, newPos): return False
        s = self.getPosition()
        dc = abs(FILES.index(newPos.column) - FILES.index(s.column))
        dr = abs(newPos.row - s.row)
        if dc == 0 or dc != dr: return False
        return board.pathClear(s, newPos)


class Knight(Piece):
    def __str__(self): return "N"
    def isValidMove(self, newPos, board):
        if not self.is_inside(newPos) or self.is_same_color_at(board, newPos): return False
        s = self.getPosition()
        dc = abs(FILES.index(newPos.column) - FILES.index(s.column))
        dr = abs(newPos.row - s.row)
        return (dc, dr) in {(1, 2), (2, 1)}


class Pawn(Piece):
    def __str__(self): return "P"
    def isValidMove(self, newPos, board):
        if not self.is_inside(newPos): return False
        s = self.getPosition()
        direction = 1 if self.getColor() == 0 else -1
        start_row = 2 if self.getColor() == 0 else 7
        dc = FILES.index(newPos.column) - FILES.index(s.column)
        dr = newPos.row - s.row
        target = board.getPiece(newPos)
        if dc == 0:
            if dr == direction and target is None: return True
            if dr == 2 * direction and s.row == start_row and target is None:
                mid = Position(s.column, s.row + direction)
                return board.getPiece(mid) is None
            return False
        if abs(dc) == 1 and dr == direction:
            if target is not None and target.getColor() != self.getColor(): return True
            ep = board.get_en_passant_target()
            if ep is not None and newPos == ep: return True
        return False


# =========================
# PLATEAU
# =========================
class Board:
    def __init__(self):
        self.__grid = {}
        self._en_passant_target = None
        self.__initBoard()

    def get_en_passant_target(self): return self._en_passant_target
    def set_en_passant_target(self, pos): self._en_passant_target = pos

    def __initBoard(self):
        self.__grid.clear()
        self._en_passant_target = None
        placements = [
            ("a1", Rook, 0), ("b1", Knight, 0), ("c1", Bishop, 0), ("d1", Queen, 0),
            ("e1", King, 0), ("f1", Bishop, 0), ("g1", Knight, 0), ("h1", Rook, 0),
            ("a8", Rook, 1), ("b8", Knight, 1), ("c8", Bishop, 1), ("d8", Queen, 1),
            ("e8", King, 1), ("f8", Bishop, 1), ("g8", Knight, 1), ("h8", Rook, 1),
        ]
        for key, cls, color in placements:
            col, row = key[0], int(key[1])
            self.__grid[key] = cls(Position(col, row), color)
        for col in FILES:
            self.__grid[f"{col}2"] = Pawn(Position(col, 2), 0)
            self.__grid[f"{col}7"] = Pawn(Position(col, 7), 1)

    def reset(self): self.__initBoard()
    def getPiece(self, pos): return self.__grid.get(str(pos))
    def setPiece(self, pos, piece):
        if piece is None: self.__grid.pop(str(pos), None)
        else: piece.setPosition(pos); self.__grid[str(pos)] = piece
    def removePiece(self, pos): self.__grid.pop(str(pos), None)
    def getAllPieces(self): return list(self.__grid.values())
    def getPiecesByColor(self, color): return [p for p in self.__grid.values() if p.getColor() == color]
    def getKingPosition(self, color):
        for p in self.__grid.values():
            if isinstance(p, King) and p.getColor() == color: return p.getPosition()
        return None

    def pathClear(self, start, end):
        sc = FILES.index(start.column); ec = FILES.index(end.column)
        sr = start.row; er = end.row
        sc_ = 0 if sc == ec else (1 if ec > sc else -1)
        sr_ = 0 if sr == er else (1 if er > sr else -1)
        cc, cr = sc + sc_, sr + sr_
        while (cc, cr) != (ec, er):
            if self.getPiece(Position(FILES[cc], cr)) is not None: return False
            cc += sc_; cr += sr_
        return True

    def movePiece(self, start, end):
        piece = self.getPiece(start)
        if piece is None: return False
        new_ep = None

        # En passant capture
        if str(piece) == "P":
            ep = self._en_passant_target
            if ep is not None and end == ep:
                self.removePiece(Position(end.column, start.row))
            direction = 1 if piece.getColor() == 0 else -1
            if abs(end.row - start.row) == 2:
                new_ep = Position(start.column, start.row + direction)

        # Roque
        if str(piece) == "K":
            dc = FILES.index(end.column) - FILES.index(start.column)
            if abs(dc) == 2:
                row = start.row
                if dc > 0:
                    rook_s = Position("h", row); rook_e = Position("f", row)
                else:
                    rook_s = Position("a", row); rook_e = Position("d", row)
                rook = self.getPiece(rook_s)
                self.removePiece(rook_s)
                rook.setPosition(rook_e); rook.has_moved = True
                self.__grid[str(rook_e)] = rook

        self.removePiece(start); self.removePiece(end)
        piece.setPosition(end); piece.has_moved = True
        self.__grid[str(end)] = piece
        self._en_passant_target = new_ep
        return True

    def clone(self):
        nb = Board(); nb._Board__grid = {}
        nb._en_passant_target = self._en_passant_target
        mapping = {"K": King, "Q": Queen, "R": Rook, "B": Bishop, "N": Knight, "P": Pawn}
        for key, piece in self.__grid.items():
            cls = mapping[str(piece)]; pos = piece.getPosition()
            np_ = cls(Position(pos.column, pos.row), piece.getColor())
            np_.has_moved = piece.has_moved
            nb._Board__grid[key] = np_
        return nb

    def to_dict(self):
        pieces = [{"type": str(p), "color": p.getColor(), "column": p.getPosition().column,
                   "row": p.getPosition().row, "has_moved": p.has_moved}
                  for p in self.__grid.values()]
        ep = self._en_passant_target
        return {"pieces": pieces, "en_passant": str(ep) if ep else None}

    def from_dict(self, data):
        self.__grid = {}
        mapping = {"K": King, "Q": Queen, "R": Rook, "B": Bishop, "N": Knight, "P": Pawn}
        pieces_data = data if isinstance(data, list) else data.get("pieces", [])
        ep_str = None if isinstance(data, list) else data.get("en_passant")
        for item in pieces_data:
            pos = Position(item["column"], item["row"])
            piece = mapping[item["type"]](pos, item["color"])
            piece.has_moved = item.get("has_moved", False)
            self.__grid[str(pos)] = piece
        self._en_passant_target = Position(ep_str[0], int(ep_str[1])) if ep_str else None


# =========================
# REGLES
# =========================
class ChessRules:
    @staticmethod
    def is_check(board, color):
        kp = board.getKingPosition(color)
        if kp is None: return True
        return any(p.isValidMove(kp, board) for p in board.getPiecesByColor(1 - color))

    @staticmethod
    def is_legal_move(board, start, end, color):
        piece = board.getPiece(start)
        if piece is None or piece.getColor() != color: return False
        if not piece.isValidMove(end, board): return False
        if str(piece) == "K":
            dc = FILES.index(end.column) - FILES.index(start.column)
            if abs(dc) == 2:
                if ChessRules.is_check(board, color): return False
                step = 1 if dc > 0 else -1
                for off in range(1, abs(dc) + 1):
                    inter = Position(FILES[FILES.index(start.column) + step * off], start.row)
                    tb = board.clone(); tb.movePiece(start, inter)
                    if ChessRules.is_check(tb, color): return False
                return True
        tb = board.clone(); tb.movePiece(start, end)
        return not ChessRules.is_check(tb, color)

    @staticmethod
    def get_legal_moves(board, position):
        piece = board.getPiece(position)
        if piece is None: return []
        color = piece.getColor()
        return [Position(col, row) for col in FILES for row in range(1, 9)
                if ChessRules.is_legal_move(board, position, Position(col, row), color)]

    @staticmethod
    def has_any_legal_move(board, color):
        return any(ChessRules.get_legal_moves(board, p.getPosition()) for p in board.getPiecesByColor(color))

    @staticmethod
    def is_checkmate(board, color):
        return ChessRules.is_check(board, color) and not ChessRules.has_any_legal_move(board, color)

    @staticmethod
    def is_stalemate(board, color):
        return not ChessRules.is_check(board, color) and not ChessRules.has_any_legal_move(board, color)


# =========================
# EVALUATION IA
# =========================
PIECE_VALUES = {"K": 20000, "Q": 900, "R": 500, "B": 330, "N": 320, "P": 100}

PAWN_TABLE   = [ 0, 0, 0, 0, 0, 0, 0, 0, 50,50,50,50,50,50,50,50, 10,10,20,30,30,20,10,10, 5, 5,10,25,25,10, 5, 5, 0, 0, 0,20,20, 0, 0, 0, 5,-5,-10, 0, 0,-10,-5, 5, 5,10,10,-20,-20,10,10, 5, 0, 0, 0, 0, 0, 0, 0, 0]
KNIGHT_TABLE = [-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50]
BISHOP_TABLE = [-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20]
ROOK_TABLE   = [0,0,0,0,0,0,0,0, 5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0]
QUEEN_TABLE  = [-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20]
KING_MID     = [-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20]
KING_END     = [-50,-40,-30,-20,-20,-30,-40,-50,-30,-20,-10,0,0,-10,-20,-30,-30,-10,20,30,30,20,-10,-30,-30,-10,30,40,40,30,-10,-30,-30,-10,30,40,40,30,-10,-30,-30,-10,20,30,30,20,-10,-30,-30,-30,0,0,0,0,-30,-30,-50,-30,-30,-30,-30,-30,-30,-50]
PIECE_TABLES = {"P": PAWN_TABLE, "N": KNIGHT_TABLE, "B": BISHOP_TABLE, "R": ROOK_TABLE, "Q": QUEEN_TABLE}

def is_endgame(board):
    queens = sum(1 for p in board.getAllPieces() if str(p) == "Q")
    minors = sum(1 for p in board.getAllPieces() if str(p) in ("R", "B", "N"))
    return queens == 0 or (queens <= 2 and minors <= 2)

def get_table_score(piece, pos, endgame=False):
    col_idx = FILES.index(pos.column); row_idx = 8 - pos.row
    idx = row_idx * 8 + col_idx
    if piece.getColor() == 1: idx = 63 - idx
    if str(piece) == "K":
        table = KING_END if endgame else KING_MID
    else:
        table = PIECE_TABLES.get(str(piece))
    return table[idx] if table else 0

def evaluate_board(board):
    endgame = is_endgame(board)
    score = 0
    pieces = board.getAllPieces()
    # Matériel + position
    for piece in pieces:
        val = PIECE_VALUES.get(str(piece), 0) + get_table_score(piece, piece.getPosition(), endgame)
        score += val if piece.getColor() == 0 else -val
    # Bonus mobilité
    white_mob = sum(len(ChessRules.get_legal_moves(board, p.getPosition())) for p in board.getPiecesByColor(0))
    black_mob = sum(len(ChessRules.get_legal_moves(board, p.getPosition())) for p in board.getPiecesByColor(1))
    score += (white_mob - black_mob) * 5
    # Bonus paire de fous
    white_bishops = sum(1 for p in pieces if str(p) == "B" and p.getColor() == 0)
    black_bishops = sum(1 for p in pieces if str(p) == "B" and p.getColor() == 1)
    if white_bishops >= 2: score += 30
    if black_bishops >= 2: score -= 30
    return score

def minimax(board, depth, alpha, beta, maximizing, time_limit=None, start_time=None):
    if time_limit and start_time and (time.time() - start_time) >= time_limit:
        return evaluate_board(board), None
    if depth == 0:
        return quiescence(board, alpha, beta, maximizing), None

    color = 0 if maximizing else 1
    all_moves = []
    for piece in board.getPiecesByColor(color):
        s = piece.getPosition()
        for e in ChessRules.get_legal_moves(board, s):
            all_moves.append((s, e))
    if not all_moves:
        if ChessRules.is_check(board, color):
            return (-99999 + (10 - depth) if maximizing else 99999 - (10 - depth)), None
        return 0, None

    # Tri MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
    def move_score(mv):
        victim = board.getPiece(mv[1])
        attacker = board.getPiece(mv[0])
        if victim:
            return -(PIECE_VALUES.get(str(victim), 0) * 10 - PIECE_VALUES.get(str(attacker), 100))
        return 0
    all_moves.sort(key=move_score)

    best_move = None
    if maximizing:
        best_val = float('-inf')
        for s, e in all_moves:
            if time_limit and start_time and (time.time() - start_time) >= time_limit:
                break
            nb = board.clone(); nb.movePiece(s, e)
            val, _ = minimax(nb, depth - 1, alpha, beta, False, time_limit, start_time)
            if val > best_val: best_val = val; best_move = (s, e)
            alpha = max(alpha, val)
            if beta <= alpha: break
        return best_val, best_move
    else:
        best_val = float('inf')
        for s, e in all_moves:
            if time_limit and start_time and (time.time() - start_time) >= time_limit:
                break
            nb = board.clone(); nb.movePiece(s, e)
            val, _ = minimax(nb, depth - 1, alpha, beta, True, time_limit, start_time)
            if val < best_val: best_val = val; best_move = (s, e)
            beta = min(beta, val)
            if beta <= alpha: break
        return best_val, best_move

def quiescence(board, alpha, beta, maximizing, depth=4):
    """Recherche de quiescence : continue uniquement sur les captures."""
    stand_pat = evaluate_board(board)
    if depth == 0: return stand_pat
    if maximizing:
        if stand_pat >= beta: return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha: return alpha
        beta = min(beta, stand_pat)

    color = 0 if maximizing else 1
    captures = []
    for piece in board.getPiecesByColor(color):
        s = piece.getPosition()
        for e in ChessRules.get_legal_moves(board, s):
            if board.getPiece(e) is not None:
                captures.append((s, e))
    captures.sort(key=lambda mv: -PIECE_VALUES.get(str(board.getPiece(mv[1])), 0))

    for s, e in captures:
        nb = board.clone(); nb.movePiece(s, e)
        val = quiescence(nb, alpha, beta, not maximizing, depth - 1)
        if maximizing:
            alpha = max(alpha, val)
            if alpha >= beta: return beta
        else:
            beta = min(beta, val)
            if beta <= alpha: return alpha
    return alpha if maximizing else beta

def iterative_deepening(board, time_limit_sec):
    """Approfondissement itératif : cherche le meilleur coup dans le temps imparti."""
    start = time.time()
    best_move = None
    for depth in range(1, 8):
        if time.time() - start >= time_limit_sec * 0.9:
            break
        _, move = minimax(board, depth, float('-inf'), float('inf'), False,
                          time_limit=time_limit_sec * 0.9, start_time=start)
        if move is not None:
            best_move = move
        if time.time() - start >= time_limit_sec * 0.9:
            break
    return best_move


# =========================
# PROMOTION POPUP
# =========================
def ask_promotion(root, color):
    result = {"piece": "Q"}
    popup = tk.Toplevel(root)
    popup.title("Promotion du pion")
    popup.configure(bg=BG_COLOR)
    popup.geometry("400x170")
    popup.resizable(False, False)
    popup.grab_set(); popup.focus_force()
    tk.Label(popup, text="Choisissez la pièce de promotion :",
             font=("Arial", 13, "bold"), fg=LIGHT, bg=BG_COLOR).pack(pady=14)
    btn_frame = tk.Frame(popup, bg=BG_COLOR); btn_frame.pack()
    def choose(p): result["piece"] = p; popup.destroy()
    for label, code in [("Dame","Q"),("Tour","R"),("Fou","B"),("Cavalier","N")]:
        sym = UNICODE_PIECES[(code, color)]
        tk.Button(btn_frame, text=f"{sym} {label}", font=("Arial", 15),
                  bg=BUTTON, fg=LIGHT, activebackground=ACCENT, activeforeground="white",
                  width=8, height=1, bd=0, cursor="hand2",
                  command=lambda c=code: choose(c)).pack(side="left", padx=8)
    root.wait_window(popup)
    return result["piece"]


# =========================
# MENU
# =========================
class Menu:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        self.root.geometry("780x1020")
        self.root.minsize(760, 950)
        self.root.resizable(True, True)
        self.root.configure(bg=BG_COLOR)
        self.create_ui()

    def clear_window(self):
        for w in self.root.winfo_children(): w.destroy()

    def create_ui(self):
        tk.Label(self.root, text="♔  CHESS  ♚", font=("Georgia", 34, "bold"), fg=LIGHT, bg=BG_COLOR).pack(pady=40)
        tk.Label(self.root, text="Choisissez votre mode de jeu", font=("Arial", 15), fg=ACCENT, bg=BG_COLOR).pack(pady=4)

        style = ttk.Style(); style.theme_use("clam")
        style.configure("Custom.TCombobox",
            fieldbackground=BUTTON, background=BUTTON, foreground=LIGHT,
            selectbackground=ACCENT, selectforeground=LIGHT,
            arrowcolor=ACCENT, bordercolor=ACCENT, font=("Arial", 13))

        # Mode de jeu
        f1 = tk.Frame(self.root, bg=BG_COLOR); f1.pack(pady=12)
        tk.Label(f1, text="Mode :", font=("Arial", 13, "bold"), fg=LIGHT, bg=BG_COLOR).pack(side="left", padx=(0,10))
        self.mode_var = tk.StringVar(value="2 Joueurs")
        modes = ["2 Joueurs", "IA — Facile", "IA — Intermédiaire", "IA — Expert", "Mode Puzzle"]
        ttk.Combobox(f1, textvariable=self.mode_var, values=modes,
            state="readonly", width=26, style="Custom.TCombobox", font=("Arial", 13)).pack(side="left")

        # Chrono
        f2 = tk.Frame(self.root, bg=BG_COLOR); f2.pack(pady=8)
        tk.Label(f2, text="Chrono :", font=("Arial", 13, "bold"), fg=LIGHT, bg=BG_COLOR).pack(side="left", padx=(0,10))
        self.clock_var = tk.StringVar(value="Pas de chrono")
        ttk.Combobox(f2, textvariable=self.clock_var, values=list(CLOCK_MODES.keys()),
            state="readonly", width=26, style="Custom.TCombobox", font=("Arial", 13)).pack(side="left")

        # Description
        self.desc_label = tk.Label(self.root, text="", font=("Arial", 11), fg=ACCENT,
                                   bg=BG_COLOR, wraplength=520, justify="center")
        self.desc_label.pack(pady=6)
        self.mode_var.trace("w", self.update_description)
        self.clock_var.trace("w", self.update_description)

        # Puzzle selector
        self.puzzle_frame = tk.Frame(self.root, bg=BG_COLOR)
        tk.Label(self.puzzle_frame, text="Puzzle :", font=("Arial", 12, "bold"), fg=LIGHT, bg=BG_COLOR).pack(side="left", padx=(0,10))
        self.puzzle_var = tk.StringVar(value=PUZZLES[0]["name"])
        ttk.Combobox(self.puzzle_frame, textvariable=self.puzzle_var,
            values=[p["name"] for p in PUZZLES], state="readonly",
            width=32, style="Custom.TCombobox", font=("Arial", 11)).pack(side="left")
        self.mode_var.trace("w", self.toggle_puzzle_selector)

        tk.Button(self.root, text="▶  JOUER", font=("Arial", 16, "bold"),
            bg=ACCENT, fg="white", activebackground=DEEP_WISTERIA, activeforeground="white",
            width=16, height=2, bd=0, cursor="hand2", command=self.start_game).pack(pady=30)

        self.update_description()

    def update_description(self, *args):
        mode = self.mode_var.get(); clock = self.clock_var.get()
        descs = {
            "2 Joueurs":          "Jouez en local à deux joueurs sur le même écran.",
            "IA — Facile":        "L'IA joue des coups entièrement aléatoires.",
            "IA — Intermédiaire": "Minimax profondeur 2 avec tables de position.",
            "IA — Expert":        "Approfondissement itératif + quiescence + évaluation avancée. L'IA respecte aussi le chrono !",
            "Mode Puzzle":        "Résolvez des positions tactiques précises.",
        }
        clock_desc = ""
        if clock != "Pas de chrono":
            cfg = CLOCK_MODES[clock]
            if cfg[0] == "total": clock_desc = f"\n⏱ Chaque joueur dispose de {cfg[1]//60}min au total."
            else: clock_desc = f"\n⏱ Vous avez {cfg[2]} secondes par coup."
        self.desc_label.config(text=descs.get(mode, "") + clock_desc)

    def toggle_puzzle_selector(self, *args):
        if self.mode_var.get() == "Mode Puzzle": self.puzzle_frame.pack(pady=8)
        else: self.puzzle_frame.pack_forget()

    def start_game(self):
        mode = self.mode_var.get(); clock = self.clock_var.get()
        puzzle_index = 0
        if mode == "Mode Puzzle":
            names = [p["name"] for p in PUZZLES]
            puzzle_index = names.index(self.puzzle_var.get())
        mode_map = {"2 Joueurs":"player","IA — Facile":"ai_easy",
                    "IA — Intermédiaire":"ai_medium","IA — Expert":"ai_hard","Mode Puzzle":"puzzle"}
        clock_cfg = CLOCK_MODES[clock]
        self.clear_window()
        ChessGUI(self.root, mode_map[mode], puzzle_index=puzzle_index, clock_cfg=clock_cfg)


# =========================
# INTERFACE JEU
# =========================
class ChessGUI:
    def __init__(self, root, mode="player", puzzle_index=0, clock_cfg=None):
        self.root = root
        self.mode = mode
        self.puzzle_index = puzzle_index
        self.clock_cfg = clock_cfg  # None | ("total", secs, None) | ("per_move", None, secs)

        self.root.title("Chess")
        self.root.geometry("700x820")
        self.root.configure(bg=MAGNOLIA)
        self.root.resizable(False, False)

        self.board = Board()
        self.currentColor = 0
        self.selectedPosition = None
        self.legalMoves = []
        self.game_over = False

        # Chrono state
        self.white_time = None  # secondes restantes (budget total) ou None
        self.black_time = None
        self.move_time = None   # secondes restantes pour le coup en cours (per_move)
        self._clock_running = False
        self._clock_thread = None
        self._move_start = None

        if clock_cfg:
            if clock_cfg[0] == "total":
                self.white_time = clock_cfg[1]
                self.black_time = clock_cfg[1]
            else:
                self.move_time = clock_cfg[2]

        if self.mode == "puzzle":
            self._load_puzzle(puzzle_index)

        self.build_ui()
        self.updateStatus()
        self.drawBoard()
        self._start_clock()

    def _load_puzzle(self, idx):
        p = PUZZLES[idx]
        self.board.from_dict(p["board"])
        self.currentColor = p["player_color"]

    # ========================
    # CHRONO
    # ========================
    def _start_clock(self):
        if self.clock_cfg is None: return
        self._clock_running = True
        self._move_start = time.time()
        self._clock_thread = threading.Thread(target=self._clock_loop, daemon=True)
        self._clock_thread.start()

    def _clock_loop(self):
        while self._clock_running and not self.game_over:
            time.sleep(0.2)
            if self.game_over: break
            elapsed = time.time() - self._move_start
            self.root.after(0, self._update_clock_display, elapsed)

    def _update_clock_display(self, elapsed):
        if self.game_over: return
        cfg = self.clock_cfg
        if cfg is None: return 

        if cfg[0] == "total":
            # Décrémenter le temps du joueur actif
            if self.currentColor == 0:
                remaining = max(0, self.white_time - elapsed)
                self._display_timers(remaining, self.black_time)
                if remaining <= 0:
                    self._time_up(0)
            else:
                remaining = max(0, self.black_time - elapsed)
                self._display_timers(self.white_time, remaining)
                if remaining <= 0:
                    self._time_up(1)

        elif cfg[0] == "per_move":
            remaining = max(0, cfg[2] - elapsed)
            self._display_move_timer(remaining)
            if remaining <= 0:
                self._time_up(self.currentColor)

    def _display_timers(self, white_rem, black_rem):
        def fmt(s): return f"{int(s)//60:02d}:{int(s)%60:02d}"
        w_color = TIMER_WARNING if white_rem < 10 else TIMER_OK
        b_color = TIMER_WARNING if black_rem < 10 else TIMER_OK
        self.white_timer_label.config(text=f"♔ Blancs : {fmt(white_rem)}", fg=w_color)
        self.black_timer_label.config(text=f"♚ Noirs : {fmt(black_rem)}", fg=b_color)

    def _display_move_timer(self, remaining):
        color = TIMER_WARNING if remaining < 4 else TIMER_NORMAL
        who = "Blancs" if self.currentColor == 0 else "Noirs"
        self.move_timer_label.config(
            text=f"⏱ {who} — {int(remaining)+1}s restante(s)",
            fg=color)

    def _time_up(self, color):
        if self.game_over: return
        self.game_over = True
        self._clock_running = False
        loser = "Blancs" if color == 0 else "Noirs"
        winner = "Noirs" if color == 0 else "Blancs"
        self.root.after(0, lambda: messagebox.showinfo(
            "Temps écoulé !", f"⏰ Les {loser} ont dépassé le temps !\n\nLes {winner} gagnent."))

    def _commit_move_time(self):
        """Appel après chaque coup pour sauvegarder le temps consommé dans le budget."""
        if self.clock_cfg is None: return
        elapsed = time.time() - self._move_start
        if self.clock_cfg[0] == "total":
            if self.currentColor == 0:
                self.white_time = max(0, self.white_time - elapsed)
            else:
                self.black_time = max(0, self.black_time - elapsed)
        self._move_start = time.time()

    def _remaining_time_for_ai(self):
        """Retourne le temps disponible pour que l'IA joue son coup (en secondes)."""
        if self.clock_cfg is None: return 5.0
        if self.clock_cfg[0] == "per_move":
            return float(self.clock_cfg[2]) * 0.85
        elif self.clock_cfg[0] == "total":
            remaining = self.black_time
            if remaining is None: return 5.0
            # Allouer environ 5% du budget restant par coup, min 0.5s, max 8s
            return min(8.0, max(0.5, remaining * 0.05))
        return 5.0

    # ========================
    # BUILD UI
    # ========================
    def build_ui(self):
        top = tk.Frame(self.root, bg=MAGNOLIA)
        top.pack(fill="x", padx=18, pady=(10, 4))
        tk.Label(top, text="Chess", font=("Georgia", 26, "bold"), bg=MAGNOLIA, fg=WISTERIA).pack()

        mode_labels = {
            "player":"Mode : 2 Joueurs","ai_easy":"Mode : IA Facile",
            "ai_medium":"Mode : IA Intermédiaire","ai_hard":"Mode : IA Expert",
            "puzzle":f"Mode : Puzzle — {PUZZLES[self.puzzle_index]['name']}",
        }
        tk.Label(top, text=mode_labels.get(self.mode,""), font=("Helvetica",12,"bold"),
                 bg=MAGNOLIA, fg=SOFT_TEXT).pack(pady=(2,0))

        if self.mode == "puzzle":
            tk.Label(top, text=PUZZLES[self.puzzle_index]["description"],
                     font=("Helvetica",11,"italic"), bg=MAGNOLIA, fg=DEEP_WISTERIA,
                     wraplength=650).pack(pady=(2,0))

        self.statusLabel = tk.Label(top, text="", font=("Helvetica",12), bg=MAGNOLIA, fg=SOFT_TEXT)
        self.statusLabel.pack(pady=(2,0))

        # ---- Panneau chrono ----
        self.timer_frame = tk.Frame(self.root, bg=MAGNOLIA)
        self.timer_frame.pack(fill="x", padx=18, pady=2)

        self.white_timer_label = tk.Label(self.timer_frame, text="", font=("Courier",13,"bold"),
                                          bg=MAGNOLIA, fg=TIMER_OK)
        self.black_timer_label = tk.Label(self.timer_frame, text="", font=("Courier",13,"bold"),
                                          bg=MAGNOLIA, fg=TIMER_OK)
        self.move_timer_label  = tk.Label(self.timer_frame, text="", font=("Courier",13,"bold"),
                                          bg=MAGNOLIA, fg=TIMER_NORMAL)

        if self.clock_cfg:
            if self.clock_cfg[0] == "total":
                self.white_timer_label.pack(side="left", expand=True)
                self.black_timer_label.pack(side="right", expand=True)
                self._display_timers(self.white_time, self.black_time)
            elif self.clock_cfg[0] == "per_move":
                self.move_timer_label.pack(expand=True)
                self._display_move_timer(self.clock_cfg[2])

        # ---- Plateau ----
        self.canvas = tk.Canvas(self.root, width=BOARD_PIXELS, height=BOARD_PIXELS,
                                bg=MAGNOLIA, highlightthickness=0)
        self.canvas.pack(padx=18, pady=6)
        self.canvas.bind("<Button-1>", self.onClick)

        # ---- Boutons ----
        bottom = tk.Frame(self.root, bg=MAGNOLIA)
        bottom.pack(fill="x", padx=18, pady=(0,12))
        btn_style = {"bg":WISTERIA,"fg":"white","activebackground":DEEP_WISTERIA,
                     "activeforeground":"white","relief":"flat","font":("Helvetica",10,"bold"),
                     "cursor":"hand2","padx":10,"pady":8,"bd":0}

        tk.Button(bottom, text="Nouvelle partie", command=self.resetGame, **btn_style).pack(side="left", padx=(0,6))
        if self.mode != "puzzle":
            tk.Button(bottom, text="Sauvegarder", command=self.saveGame, **btn_style).pack(side="left", padx=(0,6))
            tk.Button(bottom, text="Charger", command=self.loadGame, **btn_style).pack(side="left", padx=(0,6))
        # ---- BOUTON ABANDONNER ----
        tk.Button(bottom, text="🏳 Abandonner", command=self.resign,
                  bg="#7B3F3F", fg="white", activebackground="#5c2222",
                  activeforeground="white", relief="flat", font=("Helvetica",10,"bold"),
                  cursor="hand2", padx=10, pady=8, bd=0).pack(side="left", padx=(0,6))
        tk.Button(bottom, text="Menu", command=self.backToMenu, **btn_style).pack(side="left")

    def clear_window(self):
        self._clock_running = False
        for w in self.root.winfo_children(): w.destroy()

    def backToMenu(self):
        self._clock_running = False
        self.clear_window()
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("700x820")
        Menu(self.root)

    def resign(self):
        if self.game_over: return
        who = "Blancs" if self.currentColor == 0 else "Noirs"
        winner = "Noirs" if self.currentColor == 0 else "Blancs"
        if messagebox.askyesno("Abandonner", f"Les {who} veulent abandonner.\nConfirmer ?"):
            self.game_over = True
            self._clock_running = False
            messagebox.showinfo("Abandon", f"🏳 Les {who} abandonnent.\nLes {winner} gagnent !")

    def resetGame(self):
        self._clock_running = False
        if self.mode == "puzzle":
            self._load_puzzle(self.puzzle_index)
        else:
            self.board.reset()
            self.currentColor = 0
        self.game_over = False
        self.selectedPosition = None; self.legalMoves = []
        # Reset chrono
        if self.clock_cfg and self.clock_cfg[0] == "total":
            self.white_time = self.clock_cfg[1]
            self.black_time = self.clock_cfg[1]
        self.updateStatus(); self.drawBoard()
        self._start_clock()

    def saveGame(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")])
        if not filename: return
        with open(filename,"w",encoding="utf-8") as f:
            json.dump({"currentColor":self.currentColor,"mode":self.mode,
                       "board":self.board.to_dict()},f,indent=2)
        messagebox.showinfo("Sauvegarde","Partie sauvegardée avec succès.")

    def loadGame(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON","*.json")])
        if not filename: return
        with open(filename,"r",encoding="utf-8") as f: data=json.load(f)
        self.board.from_dict(data["board"])
        self.currentColor=data.get("currentColor",0)
        self.selectedPosition=None; self.legalMoves=[]
        self.updateStatus(); self.drawBoard()
        messagebox.showinfo("Chargement","Partie chargée avec succès.")
        if self.mode in ["ai_easy","ai_medium","ai_hard"] and self.currentColor==1:
            self.root.after(500,self.ai_move)

    def check_and_promote(self, position):
        piece = self.board.getPiece(position)
        if piece is None or str(piece) != "P": return
        color = piece.getColor()
        if position.row != (8 if color == 0 else 1): return
        chosen = ask_promotion(self.root, color)
        mapping = {"Q":Queen,"R":Rook,"B":Bishop,"N":Knight}
        np_ = mapping[chosen](position, color); np_.has_moved = True
        self.board.setPiece(position, np_)

    # ========================
    # DESSIN
    # ========================
    def drawBoard(self):
        self.canvas.delete("all")
        castle_hints = self._get_castle_hints()
        for ri in range(8):
            for ci in range(8):
                x1=ci*SQUARE_SIZE; y1=ri*SQUARE_SIZE; x2=x1+SQUARE_SIZE; y2=y1+SQUARE_SIZE
                fill = MAGNOLIA if (ri+ci)%2==0 else WISTERIA
                self.canvas.create_rectangle(x1,y1,x2,y2,fill=fill,outline=fill)
                pos = Position.from_xy(ci, ri)
                if pos == self.selectedPosition:
                    self.canvas.create_rectangle(x1+4,y1+4,x2-4,y2-4,outline=SELECT_BORDER,width=3)
                if pos in self.legalMoves:
                    if pos in castle_hints:
                        self.canvas.create_rectangle(x1+6,y1+6,x2-6,y2-6,outline="#E8C547",width=3,fill="")
                    else:
                        self.canvas.create_oval(x1+28,y1+28,x2-28,y2-28,fill=MOVE_DOT,outline="")
                piece = self.board.getPiece(pos)
                if piece:
                    if piece.getColor()==0:
                        self.canvas.create_text(x1+SQUARE_SIZE/2+1,y1+SQUARE_SIZE/2+1,text=piece.symbol(),font=("Segoe UI Symbol",34),fill=DEEP_WISTERIA)
                        self.canvas.create_text(x1+SQUARE_SIZE/2,y1+SQUARE_SIZE/2,text=piece.symbol(),font=("Segoe UI Symbol",34),fill=MAGNOLIA)
                    else:
                        self.canvas.create_text(x1+SQUARE_SIZE/2,y1+SQUARE_SIZE/2,text=piece.symbol(),font=("Segoe UI Symbol",34),fill=DEEP_WISTERIA)
        for i,l in enumerate(FILES):
            self.canvas.create_text(i*SQUARE_SIZE+SQUARE_SIZE/2,BOARD_PIXELS-8,text=l,fill=SOFT_TEXT,font=("Helvetica",10,"bold"))
        for i in range(8):
            self.canvas.create_text(10,i*SQUARE_SIZE+SQUARE_SIZE/2,text=str(8-i),fill=SOFT_TEXT,font=("Helvetica",10,"bold"))

    def _get_castle_hints(self):
        if self.selectedPosition is None: return set()
        piece = self.board.getPiece(self.selectedPosition)
        if piece is None or str(piece)!="K": return set()
        return {pos for pos in self.legalMoves
                if abs(FILES.index(pos.column)-FILES.index(self.selectedPosition.column))==2}

    def updateStatus(self, extra=""):
        turn = "Blancs" if self.currentColor==0 else "Noirs"
        text = f"Tour des {turn}"
        if self.mode in ["ai_easy","ai_medium","ai_hard"]:
            text += " (vous)" if self.currentColor==0 else " (IA)"
        if ChessRules.is_check(self.board,self.currentColor): text+=" — ⚠ Échec !"
        if extra: text+=f" — {extra}"
        self.statusLabel.config(text=text)

    def finishIfNeeded(self):
        if ChessRules.is_checkmate(self.board,self.currentColor):
            winner="Blancs" if self.currentColor==1 else "Noirs"
            self.game_over=True; self._clock_running=False
            self.updateStatus("Échec et mat !")
            messagebox.showinfo("Fin de partie",f"♛ Échec et mat ! Les {winner} gagnent.")
            return True
        if ChessRules.is_stalemate(self.board,self.currentColor):
            self.game_over=True; self._clock_running=False
            self.updateStatus("Pat !")
            messagebox.showinfo("Fin de partie","½ Pat — Match nul.")
            return True
        return False

    def get_all_legal_moves(self, color):
        moves=[]
        for p in self.board.getPiecesByColor(color):
            s=p.getPosition()
            for e in ChessRules.get_legal_moves(self.board,s): moves.append((s,e))
        return moves

    # ========================
    # IA
    # ========================
    def ai_move(self):
        if self.mode not in ["ai_easy","ai_medium","ai_hard"]: return
        if self.currentColor!=1: return
        if self.finishIfNeeded(): return

        if self.mode=="ai_easy":
            moves=self.get_all_legal_moves(1)
            if not moves: self.finishIfNeeded(); return
            start,end=random.choice(moves)

        elif self.mode=="ai_medium":
            _,move=minimax(self.board,3,float('-inf'),float('inf'),False)
            if move is None: self.finishIfNeeded(); return
            start,end=move

        else:  # ai_hard : approfondissement itératif avec limite de temps
            time_limit=self._remaining_time_for_ai()
            move=iterative_deepening(self.board, time_limit)
            if move is None:
                moves=self.get_all_legal_moves(1)
                if not moves: self.finishIfNeeded(); return
                start,end=random.choice(moves)
            else:
                start,end=move

        self._commit_move_time()
        self.board.movePiece(start,end)
        moved=self.board.getPiece(end)
        if moved and str(moved)=="P" and end.row==(8 if moved.getColor()==0 else 1):
            nq=Queen(end,moved.getColor()); nq.has_moved=True; self.board.setPiece(end,nq)
        self._move_start=time.time()
        self.currentColor=0
        self.selectedPosition=None; self.legalMoves=[]
        self.updateStatus("L'IA a joué")
        self.drawBoard()
        self.finishIfNeeded()
        self.updateStatus()
        self.drawBoard()

    # ========================
    # CLIC
    # ========================
    def onClick(self, event):
        if self.game_over: return
        if self.mode in ["ai_easy","ai_medium","ai_hard"] and self.currentColor==1: return

        col=event.x//SQUARE_SIZE; ri=event.y//SQUARE_SIZE
        if not(0<=col<8 and 0<=ri<8): return
        clicked=Position.from_xy(col,ri)
        clicked_piece=self.board.getPiece(clicked)

        if self.selectedPosition is None:
            if clicked_piece is None: return
            if clicked_piece.getColor()!=self.currentColor:
                messagebox.showinfo("Tour incorrect","Ce n'est pas le tour de cette pièce."); return
            self.selectedPosition=clicked
            self.legalMoves=ChessRules.get_legal_moves(self.board,clicked)
            self.drawBoard(); return

        if clicked==self.selectedPosition:
            self.selectedPosition=None; self.legalMoves=[]; self.drawBoard(); return

        if clicked in self.legalMoves:
            ms=self.selectedPosition; me=clicked

            if self.mode=="puzzle":
                p=PUZZLES[self.puzzle_index]; ss,se=p["solution"]
                if str(ms)==ss and str(me)==se:
                    self.board.movePiece(ms,me); self.check_and_promote(me)
                    self.selectedPosition=None; self.legalMoves=[]; self.drawBoard()
                    self.statusLabel.config(text="✅ Bravo ! Vous avez trouvé le bon coup !")
                    messagebox.showinfo("Puzzle résolu !","🎉 Excellent ! Coup gagnant trouvé !")
                else:
                    self.selectedPosition=None; self.legalMoves=[]
                    self.statusLabel.config(text="❌ Mauvais coup — Réessayez !")
                    messagebox.showwarning("Raté !","Ce n'est pas le bon coup. Réessayez !")
                    self._load_puzzle(self.puzzle_index); self.updateStatus(); self.drawBoard()
                return

            self._commit_move_time()
            self.board.movePiece(ms,me); self.check_and_promote(me)
            self.selectedPosition=None; self.legalMoves=[]
            self.currentColor=1-self.currentColor
            self._move_start=time.time()
            self.updateStatus(); self.drawBoard()
            if self.finishIfNeeded(): return
            if self.mode in ["ai_easy","ai_medium","ai_hard"] and self.currentColor==1:
                self.updateStatus("L'IA réfléchit...")
                self.drawBoard()
                delay=300 if self.mode=="ai_easy" else (500 if self.mode=="ai_medium" else 100)
                self.root.after(delay,self.ai_move)
            return

        if clicked_piece and clicked_piece.getColor()==self.currentColor:
            self.selectedPosition=clicked
            self.legalMoves=ChessRules.get_legal_moves(self.board,clicked)
            self.drawBoard(); return

        messagebox.showwarning("Coup invalide","Déplacement interdit.")


# =========================
# LANCEMENT
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    Menu(root)
    root.mainloop()
