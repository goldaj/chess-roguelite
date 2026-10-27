"""Adversaire tactique du Chess Roguelite, sans dépendance à Pygame.

Niveaux: facile = capture gloutonne, normal = anticipation d'une réponse,
difficile = anticipation de deux réponses avec élagage alpha-bêta.
Les règles particulières du plateau (Amazone, dimensions, promotion,
orientation, prise en passant) restent celles de Board.

Une pièce gelée ne peut pas être choisie *pour ce tour de l'IA*.
La recherche est plafonnée en noeuds pour ne pas monopoliser l'interface.
"""

from __future__ import annotations

from dataclasses import dataclass

from .board import Board

VALUES = {"P": 100, "N": 320, "B": 330, "R": 500,
          "Q": 900, "A": 1400, "K": 20000}
LEVELS = ("easy", "normal", "hard")
SEARCH_LIMITS = {"normal": 450, "hard": 1400}
MATE = 100000
INFINITY = 10**9

# (from_x, from_y), (to_x, to_y)
Move = tuple[tuple[int, int], tuple[int, int]]


def opponent(color: str) -> str:
    return "b" if color == "w" else "w"


def find_all_moves(board: Board, color: str, frozen=()) -> list[Move]:
    """Déplacements légaux avec exclusion explicite des pièces gelées."""
    blocked = set(frozen)
    moves = []
    for y in range(board.h):
        for x in range(board.w):
            piece = board.get(x, y)
            if piece and piece.color == color and (x, y) not in blocked:
                for dst in board.legal_moves_for(x, y):
                    moves.append(((x, y), dst))
    return moves


def _capture_value(board: Board, move: Move) -> int:
    (x, y), (xx, yy) = move
    piece = board.get(x, y)
    victim = board.get(xx, yy)
    if victim:
        return VALUES.get(victim.kind, 0)
    # En passant: the target square is empty, but there is an adjacent pawn.
    if piece and piece.kind == "P" and x != xx and board.en_passant == (xx, yy):
        side = board.get(xx, y)
        if side and side.kind == "P" and side.color != piece.color:
            return VALUES["P"]
    return 0


def _priority(board: Board, move: Move) -> tuple[int, int, int, int, int]:
    """Capture King/Queen first, then favorable exchanges, then stable coords."""
    (x, y), (xx, yy) = move
    piece = board.get(x, y)
    taken = _capture_value(board, move)
    promotion = 0
    if piece and piece.kind == "P":
        target_row = 0 if piece.color == board.bottom_color else board.h - 1
        if yy == target_row:
            promotion = VALUES["Q"] - VALUES["P"]
    return (-taken - promotion, VALUES.get(piece.kind, 0), y, x, yy * board.w + xx)


def _ordered_moves(board: Board, color: str, frozen=()) -> list[Move]:
    return sorted(find_all_moves(board, color, frozen), key=lambda m: _priority(board, m))


def _evaluate(board: Board, color: str) -> int:
    """Approximate board value in centipawns relative to 'color'.

    Not an exact chess evaluation. Threats and the board centre supplement
    material. No future board state or stochastic information is consulted.
    """
    our_king = board.locate_king(color)
    their_king = board.locate_king(opponent(color))
    if our_king is None:
        return -MATE
    if their_king is None:
        return MATE
    score = 0
    cx = (board.w - 1) / 2
    cy = (board.h - 1) / 2
    for x in range(board.w):
        for y in range(board.h):
            piece = board.get(x, y)
            if not piece:
                continue
            sign = 1 if piece.color == color else -1
            base = VALUES.get(piece.kind, 0)
            # Modest positional shaping, independent of color.
            if piece.kind != "K":
                centre = round(10 * (min(board.w, board.h) - abs(x - cx) - abs(y - cy)))
                base += centre
                # Hanging pieces and tactical threats matter more than mobility.
                if board.is_attacked(x, y, opponent(piece.color)):
                    base -= max(18, VALUES.get(piece.kind, 0) // 12)
            score += sign * base

    for side, king in ((color, our_king), (opponent(color), their_king)):
        if board.is_attacked(king[0], king[1], opponent(side)):
            score += -70 if side == color else 70
    return score


@dataclass
class SearchStats:
    nodes: int = 0
    capped: bool = False


def _search(board: Board, color: str, depth: int, alpha: int, beta: int,
            stats: SearchStats, node_limit: int) -> int:
    """Depth-first negamax; hard cap stops expensive Pygame-frame searches."""
    stats.nodes += 1
    if stats.nodes >= node_limit:
        stats.capped = True
        return _evaluate(board, color)

    if depth <= 0 or board.locate_king(color) is None or board.locate_king(opponent(color)) is None:
        return _evaluate(board, color)

    moves = _ordered_moves(board, color)
    if not moves:
        king = board.locate_king(color)
        if king and board.is_attacked(*king, opponent(color)):
            return -MATE + (3 - depth)  # no legal move with king attacked
        return 0  # stalemate (the game's turn/skipping rules remain in App)

    best = -INFINITY
    for move in moves:
        child = board.clone()
        child.move_and_promote(*move[0], *move[1])
        candidate = -_search(child, opponent(color), depth - 1,
                             -beta, -alpha, stats, node_limit)
        if candidate > best:
            best = candidate
        alpha = max(alpha, candidate)
        if alpha >= beta or stats.capped:
            break
    return best


def choose_move_with_stats(board: Board, color: str, *,
                           difficulty: str = "normal", frozen=(),
                           node_limit: int | None = None) -> tuple[Move | None, SearchStats]:
    """Choose a legal move, even when the budget is exhausted.

    Frozen is a *root-level* effect for the current enemy turn, never applied
    to hypothetical future turns. Equal scores use stable move ordering.
    """
    if difficulty not in LEVELS:
        raise ValueError("unknown AI difficulty")
    if color not in ("w", "b"):
        raise ValueError("unknown piece color")
    if node_limit is not None and (type(node_limit) is not int or node_limit < 1):
        raise ValueError("node_limit must be a positive integer")

    moves = _ordered_moves(board, color, frozen)
    stats = SearchStats()
    if not moves:
        return None, stats
    if difficulty == "easy":
        # Preserve the original greedy style, now correctly obeying frozen.
        return moves[0], stats

    depth = 2 if difficulty == "normal" else 3
    budget = node_limit if node_limit is not None else SEARCH_LIMITS[difficulty]
    best_move, best_score = moves[0], -INFINITY
    alpha = -INFINITY
    for move in moves:
        child = board.clone()
        child.move_and_promote(*move[0], *move[1])
        score = -_search(child, opponent(color), depth - 1,
                         -INFINITY, -alpha, stats, budget)
        # Stable, deterministic tie-breaking.
        if score > best_score:
            best_score, best_move = score, move
        alpha = max(alpha, score)
        if stats.capped:
            break
    return best_move, stats


def choose_move(board: Board, color: str, *,
                difficulty: str = "normal", frozen=()) -> Move | None:
    """Backward-compatible entry point used by the Pygame loop."""
    move, _ = choose_move_with_stats(board, color,
                                     difficulty=difficulty, frozen=frozen)
    return move
