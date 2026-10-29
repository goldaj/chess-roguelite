"""Execute actual App methods headlessly to verify UI wiring and enemy turns.

Uses the same AST-method extraction approach as test_shop_gameplay.py.
No fake AI: the enemy plays with src.core.ai.choose_move and a real Board.
"""
import ast
import unittest
from pathlib import Path

from src.core.ai import choose_move
from src.core.board import Board, Piece

SOURCE = Path(__file__).resolve().parents[1] / "src" / "main.py"


def make_game_class():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    app = next(node for node in tree.body
               if isinstance(node, ast.ClassDef) and node.name == "App")
    required = {"do_enemy_turn", "cycle_ai_difficulty", "build_options_buttons"}
    methods = [node for node in app.body
               if isinstance(node, ast.FunctionDef) and node.name in required]
    if len(methods) != len(required):
        raise AssertionError("UI or turn handler missing")
    writes = []
    class Button:
        def __init__(self, rect, text, callback):
            self.rect, self.text, self.callback = rect, text, callback
    class Pygame:
        @staticmethod
        def Rect(*args):
            return args

    env = {"choose_move": choose_move,
           "save_meta": lambda p: writes.append(dict(p)),
           "pygame": Pygame, "Button": Button}
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(SOURCE), "exec"), env)
    cls = type("HeadlessGame", (), {name: env[name] for name in required})
    return cls, writes


def create_game():
    Game, writes = make_game_class()
    game = Game()
    game.board = Board(8, 8)
    game.board.set(7, 0, Piece("K", "b"))
    game.board.set(0, 7, Piece("K", "w"))
    game.board.set(3, 3, Piece("Q", "b"))
    game.board.set(3, 5, Piece("P", "w"))
    game.board.set(1, 1, Piece("P", "b"))
    game.board_w = game.board_h = 8
    game.player_color = "w"
    game.enemy_color = "b"
    game.ai_difficulty = "easy"
    game.enemy_ticks = 15
    game.enemy_tick_factor = 1
    game.turn = "b"
    game.gold = 0
    game.frozen_coords = set()
    game.message = ""
    game.animate_move = lambda *args: None
    game.end_stage = lambda result: (_ for _ in ()).throw(AssertionError("unexpected stage end"))
    game.piece_value = lambda kind: {"P": 1, "Q": 9}.get(kind, 0)
    game.meta = {"stats": {"runs": 0}}
    game.screen = type("Screen", (), {"get_size": lambda s: (900, 750)})()
    game.toggle_fullscreen = lambda: None
    game.back_to_prev_from_options = lambda: None
    return game, writes


class TacticalAppTests(unittest.TestCase):
    def test_difficulty_selector_cycles_and_persists_without_resetting_a_run(self):
        app, writes = create_game()
        app.build_options_buttons()
        self.assertTrue(any("Facile" in b.text for b in app.opt_btns))
        app.cycle_ai_difficulty()
        self.assertEqual("normal", app.ai_difficulty)
        self.assertEqual("normal", writes[-1]["ai_difficulty"])
        self.assertTrue(any("Normal" in b.text for b in app.opt_btns))
        app.cycle_ai_difficulty()
        self.assertEqual("hard", app.ai_difficulty)
        app.cycle_ai_difficulty()
        self.assertEqual("easy", app.ai_difficulty)
        self.assertEqual(3, len(writes))

    def test_frozen_queen_does_not_cost_enemy_turn_when_pawn_can_move(self):
        app, _ = create_game()
        app.frozen_coords = {(3, 3)}
        app.do_enemy_turn()
        self.assertEqual("w", app.turn)
        self.assertIsNotNone(app.board.get(3, 3))  # Frozen queen stays
        self.assertIsNone(app.board.get(1, 1))  # Another piece moves instead
        self.assertEqual(14, app.enemy_ticks)
        self.assertEqual(set(), app.frozen_coords)

    def test_freeze_expires_after_one_turn_not_indefinitely(self):
        app, _ = create_game()
        app.frozen_coords = {(3, 3)}
        app.do_enemy_turn()
        self.assertEqual(set(), app.frozen_coords)
        app.turn = "b"
        next_move = choose_move(app.board, "b", difficulty="easy", frozen=app.frozen_coords)
        self.assertEqual((3, 3), next_move[0])

    def test_every_enemy_piece_frozen_means_one_pass_not_a_crash(self):
        app, _ = create_game()
        app.frozen_coords = {(7, 0), (3, 3), (1, 1)}
        app.do_enemy_turn()
        self.assertEqual("w", app.turn)
        self.assertEqual(15, app.enemy_ticks)
        self.assertEqual(set(), app.frozen_coords)


if __name__ == "__main__":
    unittest.main()
