"""Exercise real chess shop methods without initializing the graphical Pygame app."""
import ast
import json
import types
import unittest
from pathlib import Path

from src.core.board import Board, Piece

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "main.py"
CONTENT = json.loads((ROOT / "content" / "shop_items.json").read_text(encoding="utf-8"))


def shop_class():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    app = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "App")
    names = {"purchase", "convert_piece_dialog", "buy_piece_dialog",
             "count_army", "try_transform_to", "handle_click_transform"}
    methods = [node for node in app.body
               if isinstance(node, ast.FunctionDef) and node.name in names]
    assert len(methods) == len(names)
    namespace = {"CONTENT": CONTENT, "Piece": Piece,
                 "PIECE_NAMES_FR": {"N":"Cavalier","Q":"Dame","K":"Roi"}}
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(SOURCE), "exec"), namespace)
    mock = type("ShopHost", (), {})
    for name in names:
        setattr(mock, name, namespace[name])
    return mock


def make_shop():
    host = shop_class()()
    host.board = Board(6, 6)
    host.board.bottom_color = "w"
    host.board_w = host.board_h = 6
    host.board.set(2, 5, Piece("K", "w"))
    host.board.set(2, 4, Piece("P", "w"))
    host.board.set(2, 0, Piece("K", "b"))
    host.player_color = "w"
    host.player_army = host.count_army("w")
    host.meta = {"amazon_unlocked": False}
    host.gold = 100
    host.purchased_offers = set()
    host.message = ""
    host.state = "shop"
    host.world_layout = lambda: (0, 0, 0)
    host.to_cell = lambda mx, my, ox, oy: (2, 4)
    return host


class ShopGameplayTests(unittest.TestCase):
    def test_buy_piece_places_on_real_board_once(self):
        host = make_shop()
        item = next(x for x in CONTENT["shop_pool"] if x["id"] == "buy_N")
        host.purchase(item)
        self.assertEqual(host.gold, 88)
        self.assertEqual(host.player_army["N"], 1)
        self.assertIn("buy_N", host.purchased_offers)
        host.purchase(item)
        self.assertEqual(host.gold, 88)
        self.assertEqual(host.player_army["N"], 1)

    def test_conversion_replaces_a_pawn_and_is_only_charged_once(self):
        host = make_shop()
        item = next(x for x in CONTENT["shop_pool"] if x["id"] == "convert_piece")
        host.purchase(item)
        self.assertEqual(host.gold, 92)
        self.assertIsNone(host.player_army.get("P"))
        self.assertEqual(host.player_army.get("N"), 1)
        self.assertEqual(host.board.get(2, 4).kind, "N")
        host.purchase(item)
        self.assertEqual(host.gold, 92)

    def test_transform_is_paid_only_after_legal_target(self):
        host = make_shop()
        item = {"id":"transform_to_Q","type":"transform_to","piece":"Q","cost":18}
        host.purchase(item)
        self.assertEqual(host.gold, 100)
        self.assertEqual(host.state, "transform_select")
        host.to_cell = lambda mx, my, ox, oy: (2, 5)
        host.handle_click_transform(5, 5)
        self.assertEqual(host.gold, 100)
        self.assertEqual(host.state, "transform_select")
        host.to_cell = lambda mx, my, ox, oy: (2, 4)
        host.handle_click_transform(5, 5)
        self.assertEqual(host.board.get(2, 4).kind, "Q")
        self.assertEqual(host.gold, 82)
        self.assertEqual(host.state, "shop")
        self.assertEqual(host.player_army.get("Q"), 1)

    def test_cannot_buy_amazon_before_unlock(self):
        host = make_shop()
        item = next(x for x in CONTENT["shop_pool"] if x["id"] == "buy_A")
        host.purchase(item)
        self.assertEqual(host.gold, 100)
        self.assertEqual(host.count_army("w"), {"K":1, "P":1})


if __name__ == "__main__":
    unittest.main()
