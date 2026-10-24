"""Functional chess rules, using the headless board engine."""
import ast
import unittest
from pathlib import Path

from src.core.board import Board, Piece


class ChessRulesTests(unittest.TestCase):
    def test_en_passant_captures_adjacent_pawn_and_expires(self):
        board = Board(8, 8)
        board.set(0, 7, Piece("K", "w"))
        board.set(7, 0, Piece("K", "b"))
        board.set(4, 3, Piece("P", "w", True))
        board.set(5, 1, Piece("P", "b"))
        board.move_and_promote(5, 1, 5, 3)
        self.assertEqual(board.en_passant, (5, 2))
        self.assertIn((5, 2), board.legal_moves_for(4, 3))
        board.move_and_promote(4, 3, 5, 2)
        self.assertIsNone(board.get(5, 3))
        self.assertEqual(board.get(5, 2).color, "w")
        self.assertIsNone(board.en_passant)

    def test_en_passant_expires_after_another_move(self):
        board = Board(8, 8)
        board.set(0, 7, Piece("K", "w"))
        board.set(7, 0, Piece("K", "b"))
        board.set(4, 3, Piece("P", "w", True))
        board.set(5, 1, Piece("P", "b"))
        board.move_and_promote(5, 1, 5, 3)
        board.move_and_promote(0, 7, 0, 6)
        self.assertNotIn((5, 2), board.legal_moves_for(4, 3))

    def test_promotion_uses_board_orientation(self):
        board = Board(8, 8)
        board.bottom_color = "b"
        board.set(4, 1, Piece("P", "b", True))
        board.move_and_promote(4, 1, 4, 0)
        self.assertEqual(board.get(4, 0).kind, "Q")
        board.set(3, 6, Piece("P", "w", True))
        board.move_and_promote(3, 6, 3, 7)
        self.assertEqual(board.get(3, 7).kind, "Q")

    def test_transform_handlers_are_class_methods(self):
        source = Path(__file__).resolve().parents[1] / "src" / "main.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        app = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "App")
        methods = {node.name for node in app.body if isinstance(node, ast.FunctionDef)}
        self.assertTrue({"try_transform_to", "handle_click_transform", "draw_transform_select"} <= methods)


if __name__ == "__main__":
    unittest.main()
