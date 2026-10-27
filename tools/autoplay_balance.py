"""Synthetic chess-vs-chess *feasibility probe*, not a human balance estimator.

Plays genuine Board + choose_move for fixed default player deck, WITHOUT shop,
meta upgrades, frozen skills or carryover. It is deliberately labelled limited:
two deterministic orientation cases per stage/route are NOT win-rate evidence.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.core.ai import choose_move
from src.core.campaign import prepare_encounter, capture_progress
from src.core.formation import make_board

ROOT = Path(__file__).resolve().parents[1]
CONTENTS = json.loads((ROOT / "content" / "shop_items.json").read_text("utf-8"))
DEFAULT_DECK = {"K": 1, "R": 1, "B": 1, "P": 3}


def play_reference_game(stage: dict, route: str, player_color: str) -> dict:
    """One deterministic game with both agents on EASY and the same rules.

    Checks turn budgets in the *same order as App*: time exhaustion is resolved
    before the king-capture victory check. No coins, relics or metaprogression.
    """
    scenario = prepare_encounter(stage, route)
    b = make_board(*scenario["board"], DEFAULT_DECK, scenario["enemy_army"], player_color)
    enemy_color = "b" if player_color == "w" else "w"
    player_ticks = scenario["player_ticks"]
    enemy_ticks = scenario["enemy_ticks"]
    turn = "w"
    passes = 0
    outcome = "incomplete"
    number_of_moves = 0
    for _ in range(140):
        move = choose_move(b, turn, difficulty="easy")
        if move is None:
            passes += 1
            if passes >= 2:
                outcome = "no_legal_moves"
                break
        else:
            passes = 0
            b.move_and_promote(*move[0], *move[1])
            number_of_moves += 1
            if turn == player_color:
                player_ticks -= 1
                if b.locate_king(enemy_color) is None:
                    outcome = "player_captured_king"
                    break
                if player_ticks <= 0:
                    outcome = "player_out_of_ticks"
                    break
            else:
                enemy_ticks -= 1
                if b.locate_king(player_color) is None:
                    outcome = "enemy_captured_king"
                    break
                if enemy_ticks <= 0:
                    if capture_progress(b, enemy_color, stage, route)["met"]:
                        outcome = "mission_completed_on_timeout"
                    else:
                        outcome = "mission_failed_on_timeout"
                    break
        turn = "b" if turn == "w" else "w"
    return {
        "name": stage["name"], "route": route, "player_color": player_color,
        "opponents": "easy_vs_easy_FIXED_DECK_NO_SHOP",
        "outcome": outcome, "moves_played": number_of_moves,
        "player_ticks_left": player_ticks, "enemy_ticks_left": enemy_ticks,
        "player_won": outcome in ("player_captured_king",
                                  "mission_completed_on_timeout"),
        "capture_goal": capture_progress(b, enemy_color, stage, route),
    }


def main() -> None:
    matrix = [
        play_reference_game(stage, route, color)
        for stage in CONTENTS["stages"]
        for route in ("steady", "safe", "risk")
        for color in ("w", "b")
    ]
    print(json.dumps({
        "kind": "synthetic_deterministic_sparring_NOT_human_balance_evidence",
        "games": len(matrix),
        "results": matrix,
        "disclaimer": ("These are NOT statistically independent games;"
                       " no shop, upgrades, skills or carryover."
                       " Never use as an estimated human win rate."),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
