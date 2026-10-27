"""Headless, behavioral tests of the actual Chess Roguelite tactical opponent."""
import unittest

from src.core.ai import (
    LEVELS, choose_move, choose_move_with_stats, find_all_moves
)
from src.core.board import Board, Piece


def position():
    board = Board(8, 8)
    board.set(7, 0, Piece("K", "b"))
    board.set(0, 7, Piece("K", "w"))
    return board


def snapshot(board):
    return tuple(
        (x, y, p.kind, p.color, p.moved)
        for y in range(board.h) for x in range(board.w)
        if (p := board.get(x, y)) is not None
    ), board.en_passant, board.bottom_color


class TacticalOpponentTests(unittest.TestCase):
    def test_levels_offered_for_actual_gameplay(self):
        self.assertEqual(LEVELS, ("easy", "normal", "hard"))

    def test_greedy_easy_takes_bait_but_normal_sees_recapture(self):
        b = position()
        b.set(3, 3, Piece("Q", "b"))
        b.set(3, 5, Piece("P", "w", True))  # bait
        b.set(3, 7, Piece("R", "w"))        # defended by white rook
        bait = ((3, 3), (3, 5))
        self.assertIn(bait, find_all_moves(b, "b"))
        self.assertEqual(bait, choose_move(b, "b", difficulty="easy"))
        self.assertNotEqual(bait, choose_move(b, "b", difficulty="normal"))

    def test_captured_king_is_terminal_priority(self):
        b = position()
        b.set(0, 7, None)
        b.set(1, 7, Piece("K", "w"))
        b.set(0, 7, Piece("Q", "b"))
        expected = ((0, 7), (1, 7))
        self.assertIn(expected, find_all_moves(b, "b"))
        for mode in LEVELS:
            self.assertEqual(expected, choose_move(b, "b", difficulty=mode))

    def test_freeze_excludes_piece_and_must_choose_alternative(self):
        b = position()
        b.set(3, 3, Piece("Q", "b"))
        b.set(3, 5, Piece("P", "w", True))
        b.set(1, 1, Piece("P", "b"))
        normal = choose_move(b, "b", difficulty="easy")
        self.assertEqual(normal[0], (3, 3))
        for mode in LEVELS:
            moved = choose_move(b, "b", difficulty=mode, frozen={(3, 3)})
            self.assertIsNotNone(moved)
            self.assertNotEqual(moved[0], (3, 3))
            self.assertIn(moved, find_all_moves(b, "b"))

    def test_all_pieces_frozen_returns_none_but_board_unchanged(self):
        b = position()
        frozen = {(7, 0)}
        original = snapshot(b)
        self.assertIsNone(choose_move(b, "b", frozen=frozen))
        self.assertEqual(snapshot(b), original)

    def test_normal_and_hard_never_lose_legality(self):
        b = position()
        b.set(3, 3, Piece("Q", "b"))
        b.set(3, 5, Piece("P", "w", True))
        b.set(3, 7, Piece("R", "w"))
        b.set(1, 1, Piece("P", "b"))
        for mode in LEVELS:
            original = snapshot(b)
            move = choose_move(b, "b", difficulty=mode)
            self.assertIn(move, find_all_moves(b, "b"))
            self.assertEqual(original, snapshot(b), mode)

    def test_hard_is_deterministic_and_respects_node_budget(self):
        b = position()
        b.set(3, 3, Piece("Q", "b"))
        b.set(3, 5, Piece("P", "w"))
        b.set(3, 7, Piece("R", "w"))
        results = [choose_move_with_stats(b, "b", difficulty="hard", node_limit=70)
                   for _ in range(3)]
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[1], results[2])
        self.assertLessEqual(results[0][1].nodes, 70)
        self.assertIn(results[0][0], find_all_moves(b, "b"))

    def test_other_board_orientations_and_amazon_are_supported(self):
        b = position()
        b.bottom_color = "b"
        b.set(3, 4, Piece("A", "b"))
        b.set(2, 5, Piece("P", "w"))
        for mode in LEVELS:
            m = choose_move(b, "b", difficulty=mode)
            self.assertIn(m, find_all_moves(b, "b"))

    def test_en_passant_appears_to_opponent_and_search_without_mutation(self):
        b = position()
        b.set(4, 4, Piece("P", "b", True))
        b.set(3, 6, Piece("P", "w"))
        b.move_and_promote(3, 6, 3, 4)
        target = ((4, 4), (3, 5))
        # Black pawns move downward (+1), white pawns upward (-1).
        self.assertIn(target, find_all_moves(b, "b"))
        old = snapshot(b)
        self.assertIn(choose_move(b, "b", difficulty="normal"), find_all_moves(b, "b"))
        self.assertEqual(old, snapshot(b))

    def test_empty_or_missing_king_returns_no_unjustified_move(self):
        b = Board(4, 4)
        self.assertIsNone(choose_move(b, "b"))
        self.assertEqual([], find_all_moves(b, "b"))

    def test_validation_of_difficulty_and_budget(self):
        b = position()
        with self.assertRaises(ValueError):
            choose_move(b, "b", difficulty="turbo")
        with self.assertRaises(ValueError):
            choose_move_with_stats(b, "b", node_limit=-1)
        with self.assertRaises(ValueError):
            choose_move_with_stats(b, "r")


if __name__ == "__main__":
    unittest.main()
