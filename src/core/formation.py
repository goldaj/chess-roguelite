"""Shared deployment for the real game and balance simulations.

Every paid/surviving piece MUST be on the board; no truncation. This replaces
the duplicated player/enemy placement loops that silently dropped excess pawns.
"""

from __future__ import annotations

from .board import Board, Piece

KINDS = ("K", "R", "N", "B", "Q", "A", "P")


def make_board(width: int, height: int, player_army: dict,
               enemy_army: dict, player_color: str) -> Board:
    if (type(width) is not int or type(height) is not int or
            width < 6 or height < 6 or width > 16 or height > 16):
        raise ValueError("unsupported chess board dimensions")
    if player_color not in ("w", "b"):
        raise ValueError("invalid color")
    for label, army in (("player", player_army), ("enemy", enemy_army)):
        if not isinstance(army, dict) or army.get("K") != 1:
            raise ValueError(f"{label} must have exactly one king")
        if (set(army) - set(KINDS) or
            any(type(v) is not int or v < 0 for v in army.values()) or
            sum(army.values()) > 2 * width):
            raise ValueError(f"{label} army is invalid or does not fit")
    board = Board(width, height)
    board.bottom_color = player_color
    center = width // 2
    ordered_columns = sorted(range(width), key=lambda x: (abs(x - center), x))

    def deploy(army: dict, color: str, *, bottom: bool) -> None:
        back = height - 1 if bottom else 0
        front = height - 2 if bottom else 1
        board.set(center, back, Piece("K", color))
        # Place pawns first across the front rank.
        pawns = army.get("P", 0)
        for col in ordered_columns[:min(pawns, width)]:
            board.set(col, front, Piece("P", color))
        # Other named pieces occupy the back rank first, then front.
        pieces = [kind for kind in ("R", "N", "B", "Q", "A", "P")
                  for _ in range(army.get(kind, 0) - (min(pawns, width) if kind == "P" else 0))]
        # For a large army, place reserves on any remaining home-row squares.
        slots = [(col, back) for col in ordered_columns if board.get(col, back) is None]
        slots += [(col, front) for col in ordered_columns if board.get(col, front) is None]
        if len(pieces) > len(slots):
            raise ValueError("army does not fit the deployment area")
        for (x, y), kind in zip(slots, pieces):
            board.set(x, y, Piece(kind, color))

    deploy(player_army, player_color, bottom=True)
    deploy(enemy_army, "b" if player_color == "w" else "w", bottom=False)
    return board
