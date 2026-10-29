"""Two-ply tactical enemy AI with deterministic tie-breaking.

Preserves choose_move(board, color) and find_all_moves() used by the UI.
No pygame dependency. Costs are modest on the small roguelite boards.
"""
from __future__ import annotations

from .board import Board

VALUES = {'P': 1, 'N': 3, 'B': 3.1, 'R': 5, 'Q': 9, 'A': 12, 'K': 100}


def find_all_moves(board: Board, color: str):
    moves = []
    for x in range(board.w):
        for y in range(board.h):
            piece = board.get(x, y)
            if piece and piece.color == color:
                for xx, yy in board.legal_moves_for(x, y):
                    target = board.get(xx, yy)
                    gain = VALUES.get(target.kind, 0) if target else 0
                    if piece.kind == 'P' and xx != x and board.en_passant == (xx, yy):
                        gain = VALUES['P']
                    moves.append(((x, y), (xx, yy), gain))
    return moves


def evaluate(board: Board, color: str) -> float:
    """Material + light advancement, relative to the perspective color."""
    total = 0.0
    for x in range(board.w):
        for y in range(board.h):
            piece = board.get(x, y)
            if not piece:
                continue
            value = VALUES.get(piece.kind, 0)
            if piece.kind == 'P':
                advancement = (board.h - 1 - y) if piece.color == board.bottom_color else y
                value += advancement * 0.06
            if piece.kind in ('N', 'B', 'A'):
                value += 0.045 * min(x, board.w - 1 - x, y, board.h - 1 - y)
            total += value if piece.color == color else -value
    return total


def choose_move(board: Board, color: str):
    """Look one opponent reply ahead so free material traps are less attractive.

    The opposing side minimizes our material score; we choose the maximum.
    A capture of a king remains a winning condition for the original game.
    """
    moves = find_all_moves(board, color)
    if not moves:
        return None
    enemy = 'b' if color == 'w' else 'w'
    best = None
    best_score = float('-inf')
    for start, end, gain in moves:
        future = board.clone()
        future.move_and_promote(*start, *end)
        if future.locate_king(enemy) is None:
            score = 10000
        else:
            replies = find_all_moves(future, enemy)
            if not replies:
                score = evaluate(future, color)
            else:
                score = min(_reply_value(future, start2, end2, color)
                            for start2, end2, _ in replies)
        # A slight capture preference avoids unproductive tactical shuffling.
        score += 0.015 * gain
        # Deterministic traversal: reproducible battles and tests.
        if score > best_score:
            best_score = score
            best = (start, end)
    return best


def _reply_value(board: Board, start, end, color: str) -> float:
    future = board.clone()
    future.move_and_promote(*start, *end)
    if future.locate_king(color) is None:
        return -10000
    return evaluate(future, color)
