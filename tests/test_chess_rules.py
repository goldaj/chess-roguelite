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



from src.core.ai import choose_move

class TacticalBranchRegressionTests(unittest.TestCase):
    def board(self, bottom='w'):
        b=Board(8,8);b.bottom_color=bottom
        b.set(0,7 if bottom=='w' else 0,Piece('K',bottom))
        enemy='b' if bottom=='w' else 'w'
        b.set(7,0 if bottom=='w' else 7,Piece('K',enemy))
        return b

    def test_double_push_sets_en_passant_target(self):
        b=self.board();b.set(4,6,Piece('P','w'))
        self.assertIn((4,4),b.legal_moves_for(4,6))
        b.move_and_promote(4,6,4,4)
        self.assertEqual(b.en_passant,(4,5))

    def test_en_passant_removes_exact_opponent_pawn(self):
        b=self.board();b.set(4,3,Piece('P','w',True))
        b.set(5,1,Piece('P','b'))
        b.move_and_promote(5,1,5,3)
        self.assertIn((5,2),b.legal_moves_for(4,3))
        b.move_and_promote(4,3,5,2)
        self.assertIsNone(b.get(5,3))
        self.assertEqual((b.get(5,2).kind,b.get(5,2).color),('P','w'))
        self.assertIsNone(b.en_passant)

    def test_en_passant_expires_after_other_move(self):
        b=self.board();b.set(4,3,Piece('P','w',True));b.set(5,1,Piece('P','b'))
        b.move_and_promote(5,1,5,3)
        b.move_and_promote(0,7,0,6)
        self.assertIsNone(b.en_passant)
        self.assertNotIn((5,2),b.legal_moves_for(4,3))

    def test_illegal_en_passant_missing_victim(self):
        b=self.board();b.set(4,3,Piece('P','w',True));b.en_passant=(5,2)
        self.assertNotIn((5,2),b.legal_moves_for(4,3))

    def test_promotion_respects_bottom_color_black(self):
        b=self.board(bottom='b')
        b.set(3,1,Piece('P','b',True))
        b.move_and_promote(3,1,3,0)
        self.assertEqual(b.get(3,0).kind,'Q')
        b.set(4,6,Piece('P','w',True))
        b.move_and_promote(4,6,4,7)
        self.assertEqual(b.get(4,7).kind,'Q')

    def test_clone_does_not_share_mutated_pieces(self):
        b=self.board();b.set(3,6,Piece('P','w'))
        copy=b.clone();copy.move_and_promote(3,6,3,4)
        self.assertFalse(b.get(3,6).moved)
        self.assertIsNone(b.en_passant)
        self.assertEqual(copy.en_passant,(3,5))

    def test_ai_finds_king_capture(self):
        b=self.board();b.set(7,2,Piece('R','w'))
        # Black king at 7,0; vertical rook capture is immediate winning option.
        move=choose_move(b,'w')
        self.assertEqual(move,((7,2),(7,0)))

    def test_ai_avoids_obvious_queen_hanging(self):
        b=self.board()
        b.set(3,4,Piece('Q','w'))
        b.set(4,3,Piece('P','b',True))
        b.set(5,2,Piece('R','b',True))
        # Queen may capture pawn at (4,3) but enemy rook can recapture (4,3) only
        # if rook aligns; use a rook on (4,1) instead.
        b.set(5,2,None);b.set(4,1,Piece('R','b',True))
        chosen=choose_move(b,'w')
        self.assertNotEqual(chosen,((3,4),(4,3)))

    def test_ai_is_deterministic(self):
        b=self.board();b.set(3,5,Piece('N','w'))
        self.assertEqual(choose_move(b,'w'),choose_move(b,'w'))

    def test_ai_no_moves(self):
        b=Board(1,1)
        self.assertIsNone(choose_move(b,'b'))


