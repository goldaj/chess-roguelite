"""Functional integration of real App round/shop/economy methods without Pygame."""

import ast
import copy
import json
import math
import unittest
from pathlib import Path

from src.core.campaign import (
    ROUTES, draft_shop_offers, prepare_encounter,
    record_stage_result, victory_reward,
)
from src.core.formation import make_board
from src.core.board import Piece

ROOT = Path(__file__).resolve().parents[1]
CONTENT = json.loads((ROOT / "content/shop_items.json").read_text(encoding="utf-8"))
MAIN = ROOT / "src/main.py"


def real_app_methods():
    parsed = ast.parse(MAIN.read_text(encoding="utf-8"))
    klass = next(node for node in parsed.body
                 if isinstance(node, ast.ClassDef) and node.name == "App")
    names = {
        "end_stage", "shop_continue_next", "place_armies_initial_layout",
        "count_army", "start_stage", "select_route", "purchase",
        "buy_piece_dialog",
    }
    selected = [m for m in klass.body
                if isinstance(m, ast.FunctionDef) and m.name in names]
    if len(selected) != len(names):
        raise AssertionError("actual campaign App methods missing")
    saved = []
    env = {
        "CONTENT": CONTENT, "Piece": Piece, "make_board": make_board,
        "ROUTES": ROUTES, "draft_shop_offers": draft_shop_offers,
        "prepare_encounter": prepare_encounter, "victory_reward": victory_reward,
        "record_stage_result": record_stage_result, "math": math,
        "save_meta": lambda meta: saved.append(copy.deepcopy(meta)),
    }
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(MAIN), "exec"), env)
    Host = type("ActualCampaignMethods", (), {name: env[name] for name in names})
    return Host, saved


def host():
    Klass, saves = real_app_methods()
    game = Klass()
    game.stage_index = 0
    game.manches_won = 0
    game.player_color, game.enemy_color = "w", "b"
    game.player_army = {"K": 1, "R": 1, "B": 1, "P": 3}
    game.enemy_army = {"K": 1, "P": 3}
    game.board_w, game.board_h = 8, 8
    game.place_armies_initial_layout()
    game.player_ticks = 20
    game.enemy_ticks = 16
    game.gold = 0
    game.ai_difficulty = "normal"
    game.route_choice = game.active_route = "steady"
    game.shop_ticks_bonus = 0
    game.shop_enemy_tick_reduction = 0.0
    game.meta = {"amazon_unlocked": False, "stats": {"runs": 0, "wins": 0}}
    game.frozen_coords = set()
    game.shop_stage_index = None
    game.purchased_offers = set()
    game.selection = None
    game.legal_moves = []
    game.double_start = False
    game.double_start_always = False
    game.freeze_random_next = False
    game.pre_moves_left = 0
    game.enemy_tick_factor = 1.0
    game.message = ""
    game.turn = "w"
    game.state = "play"
    game.phase = "manche"
    game.recompute_tile = lambda: None
    game.build_shop_buttons = lambda: None
    game.build_ingame_buttons = lambda: None
    return game, saves


class CampaignAppTests(unittest.TestCase):
    def test_actual_end_stage_has_real_rewards_and_persistent_observations(self):
        app, saved = host()
        app.end_stage(True)
        self.assertEqual(app.stage_index, 1)
        self.assertEqual(app.state, "shop")
        self.assertEqual(app.phase, "inter")
        self.assertEqual(app.gold, 11)  # base 10 + 1 tick-reward from 20 ticks
        self.assertEqual(app.enemy_army, {"K": 1, "P": 3, "N": 1})
        self.assertEqual(app.player_ticks, 23)
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0]["campaign_balance_history"][0]["result"], "victory")
        self.assertEqual(saved[0]["campaign_balance_history"][0]["stage"], 1)
        self.assertEqual(app.player_army, {"K": 1, "R": 1, "B": 1, "P": 3})

    def test_route_and_multiple_actual_shop_purchases_survive_rebuild(self):
        app, _ = host()
        app.end_stage(True)
        app.gold = 90  # isolated setup, not a campaign income claim
        app.purchase({"id": "extra_knight", "name": "Cavalier",
                      "type": "buy_piece", "piece": "N", "cost": 12})
        app.purchase({"id": "time_refill", "name": "Temps",
                      "type": "tick", "amount": 10, "cost": 6})
        app.purchase({"id": "enemy_refill", "name": "Pression",
                      "type": "tick_enemy", "amount": -0.10, "cost": 8})
        app.purchase({"id": "double_once", "name": "Initiative",
                      "type": "start_power", "effect": "double_once", "cost": 14})
        self.assertEqual(app.count_army("w")["N"], 1)
        self.assertEqual(app.shop_ticks_bonus, 10)
        self.assertAlmostEqual(app.shop_enemy_tick_reduction, 0.10)
        app.select_route("risk")
        app.shop_continue_next()
        self.assertEqual(app.active_route, "risk")
        self.assertEqual(app.turn, "w")
        self.assertEqual(app.enemy_ticks, 19)  # ceil((18+3) * 0.9)
        self.assertEqual(app.player_ticks, 33)  # 23 stage + 10 from shop
        self.assertEqual(app.enemy_army, {"K": 1, "P": 3, "N": 2})
        self.assertEqual(app.count_army("w")["N"], 1)
        self.assertEqual(app.count_army("b")["N"], 2)
        self.assertEqual(app.pre_moves_left, 2)
        self.assertFalse(app.double_start)
        self.assertEqual(app.shop_ticks_bonus, 0)
        self.assertEqual(app.shop_enemy_tick_reduction, 0)

    def test_one_use_initiative_ends_after_its_encounter(self):
        app, _ = host()
        app.end_stage(True)
        app.double_start = True
        app.shop_continue_next()
        self.assertEqual(app.pre_moves_left, 2)
        self.assertFalse(app.double_start)
        app.end_stage(True)
        app.shop_continue_next()
        self.assertEqual(app.pre_moves_left, 0)

    def test_defeat_is_not_rewarded_and_is_locally_counted(self):
        app, saves = host()
        app.end_stage(False)
        self.assertEqual(app.gold, 0)
        self.assertEqual(app.state, "meta")
        self.assertEqual(app.meta["stats"]["runs"], 1)
        self.assertEqual(app.meta["stats"]["wins"], 0)
        self.assertEqual(len(saves), 2)  # encounter result, then final save
        self.assertEqual(saves[-1]["campaign_balance_history"][-1]["result"], "defeat")

    def test_campaign_victory_unlocks_amazon_and_counts_actual_run(self):
        app, _ = host()
        app.stage_index = 5
        app.active_route = "safe"
        app.end_stage(True)
        self.assertEqual(app.state, "meta")
        self.assertTrue(app.meta["amazon_unlocked"])
        self.assertEqual(app.meta["stats"]["wins"], 1)
        self.assertEqual(app.meta["stats"]["runs"], 1)

    def test_play_history_is_bounded_and_keeps_only_local_metrics(self):
        meta = {}
        for i in range(215):
            record_stage_result(
                meta, stage=i % 6 + 1, route="steady", ai_difficulty="normal",
                won=i % 2 == 0, remaining_player_ticks=3,
                remaining_enemy_ticks=1, player_material=11)
        self.assertEqual(len(meta["campaign_balance_history"]), 200)
        self.assertNotIn("prompt", meta["campaign_balance_history"][0])
        self.assertNotIn("username", meta["campaign_balance_history"][0])


if __name__ == "__main__":
    unittest.main()
