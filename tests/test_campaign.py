"""Pure campaign economy and deployment tests, no Pygame required."""

import copy
import json
import random
import unittest
from pathlib import Path

from src.core.campaign import (
    ROUTES, campaign_balance_report, draft_shop_offers,
    prepare_encounter, validate_campaign, victory_reward, capture_progress,
)
from src.core.formation import make_board


CONTENT = json.loads(
    (Path(__file__).resolve().parents[1] / "content" / "shop_items.json").read_text("utf-8")
)
STAGES = CONTENT["stages"]


def roster_on_board(board, color):
    tally = {}
    for x in range(board.w):
        for y in range(board.h):
            p = board.get(x, y)
            if p is not None and p.color == color:
                tally[p.kind] = tally.get(p.kind, 0) + 1
    return tally


class CampaignBalanceTests(unittest.TestCase):
    def test_campaign_has_six_named_distinct_encounters_and_a_final_boss(self):
        validate_campaign(STAGES)
        self.assertEqual(len(STAGES), 6)
        self.assertEqual(len(set(s["name"] for s in STAGES)), 6)
        self.assertIn("Q", STAGES[-1]["enemy_start"])
        self.assertEqual(STAGES[0]["enemy_start"], {"K": 1, "P": 3})
        material = [r["enemy_material"] for r in campaign_balance_report(STAGES)]
        self.assertEqual([3, 6, 6, 10, 11, 20], material)

    def test_campaign_carries_an_explicit_progression_without_first_stage_100_tick_bug(self):
        report = campaign_balance_report(STAGES)
        self.assertEqual([r["player_ticks"] for r in report], [22, 23, 24, 25, 26, 28])
        self.assertEqual([r["enemy_ticks"] for r in report], [16, 18, 19, 21, 23, 25])
        self.assertTrue(all(r["player_ticks"] >= r["enemy_ticks"] for r in report))
        self.assertTrue(all(r["reward_gold"] >= 10 for r in report))

    def test_route_choices_are_meaningful_and_do_not_mutate_source(self):
        before = copy.deepcopy(STAGES)
        for stage in STAGES:
            steady, safe, risk = (
                prepare_encounter(stage, route) for route in ("steady", "safe", "risk")
            )
            self.assertGreater(safe["player_ticks"], steady["player_ticks"])
            self.assertLess(safe["reward_gold"], steady["reward_gold"])
            self.assertEqual(safe["enemy_army"], steady["enemy_army"])
            self.assertGreater(risk["enemy_ticks"], steady["enemy_ticks"])
            self.assertGreater(risk["reward_gold"], steady["reward_gold"])
            self.assertEqual(
                risk["enemy_army"].get("N", 0),
                steady["enemy_army"].get("N", 0) + 1,
            )
        self.assertEqual(STAGES, before)

    def test_rewards_are_exact_and_never_paid_automatically_on_a_loss(self):
        stage = STAGES[2]
        self.assertEqual(victory_reward(stage, "steady", 20, 0.06), 15)
        self.assertEqual(victory_reward(stage, "safe", 20, 0.06), 11)
        self.assertEqual(victory_reward(stage, "risk", 20, 0.06), 23)
        with self.assertRaises(ValueError):
            victory_reward(stage, "risk", -10, 0.06)

    def test_king_survives_and_every_paid_piece_is_on_the_actual_board(self):
        player = {"K": 1, "P": 6, "N": 2, "R": 2, "B": 1, "Q": 1}
        enemy = prepare_encounter(STAGES[-1], "risk")["enemy_army"]
        for color in ("w", "b"):
            board = make_board(8, 8, player, enemy, color)
            self.assertEqual(roster_on_board(board, color), player)
            self.assertEqual(
                roster_on_board(board, "b" if color == "w" else "w"), enemy)
            self.assertEqual(board.bottom_color, color)
            self.assertIsNotNone(board.locate_king(color))

    def test_overflow_is_rejected_instead_of_silently_dropping_shop_buys(self):
        with self.assertRaises(ValueError):
            make_board(8, 8, {"K": 1, "P": 16}, {"K": 1, "P": 3}, "w")
        with self.assertRaises(ValueError):
            make_board(8, 8, {"K": 0, "P": 3}, {"K": 1}, "w")

    def test_shop_never_draws_three_unaffordable_offers(self):
        pool = CONTENT["shop_pool"]
        for gold in [5, 6, 10, 12, 30]:
            for seed in range(150):
                offers = draft_shop_offers(pool, gold, rng=random.Random(seed))
                self.assertEqual(len(offers), 3)
                self.assertEqual(len(set(o["id"] for o in offers)), 3)
                affordable_count = sum(o["cost"] <= gold for o in pool)
                self.assertGreaterEqual(
                    sum(o["cost"] <= gold for o in offers),
                    min(2, affordable_count))
        with self.assertRaises(ValueError):
            draft_shop_offers(pool, 0, rng=random.Random(12))

    def test_timeout_capture_goal_requires_actual_enemy_losses(self):
        stage = STAGES[1]
        b = make_board(8, 8, {"K": 1, "R": 1, "P": 3},
                       stage["enemy_start"], "w")
        initial = capture_progress(b, "b", stage, "steady")
        self.assertEqual(initial, {"captured": 0, "required": 2, "met": False})
        pawns = [(x, y) for x in range(8) for y in range(8)
                 if (p := b.get(x, y)) and p.color == "b" and p.kind == "P"]
        for x, y in pawns[:2]:
            b.set(x, y, None)
        score = capture_progress(b, "b", stage, "steady")
        self.assertEqual(score, {"captured": 2, "required": 2, "met": True})
        self.assertEqual(capture_progress(b, "b", stage, "risk")["required"], 4)

    def test_first_stage_survival_is_not_the_same_as_risky_capture_goal(self):
        b = make_board(8, 8, {"K": 1, "R": 1, "P": 3},
                       STAGES[0]["enemy_start"], "w")
        self.assertTrue(capture_progress(b, "b", STAGES[0], "steady")["met"])
        risk_enemy = prepare_encounter(STAGES[0], "risk")["enemy_army"]
        risk_board = make_board(8, 8, {"K": 1, "R": 1, "P": 3},
                                risk_enemy, "w")
        self.assertFalse(capture_progress(
            risk_board, "b", STAGES[0], "risk")["met"])

    def test_invalid_campaign_variants_rejected_before_loading(self):
        a = copy.deepcopy(STAGES)
        a[0]["enemy_start"]["K"] = 0
        with self.assertRaises(ValueError):
            validate_campaign(a)
        b = copy.deepcopy(STAGES)
        b[1]["enemy_start"]["BAD"] = 3
        with self.assertRaises(ValueError):
            validate_campaign(b)
        c = copy.deepcopy(STAGES)
        c[1]["reward_gold"] = -3
        with self.assertRaises(ValueError):
            validate_campaign(c)
        with self.assertRaises(ValueError):
            prepare_encounter(STAGES[1], "magical")

    def test_campaign_report_is_deterministic_diagnostics_not_empirical_balance(self):
        first = campaign_balance_report(STAGES)
        second = campaign_balance_report(STAGES)
        self.assertEqual(first, second)
        self.assertIn("time_margin_ticks", first[0])
        self.assertNotIn("win_rate", first[0])
        self.assertIn("material_delta_vs_previous", first[-1])


if __name__ == "__main__":
    unittest.main()
