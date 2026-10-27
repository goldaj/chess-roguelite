"""A six-encounter campaign with an explicit risk/reward route each round.

Pure gameplay logic, no Pygame and no access to saves. The user chooses an
approach *before* the next fight. Numeric values are a first playable balance
candidate, not evidence of a fair win-rate (requires human playtesting).
"""

from __future__ import annotations

ROUTES = {
    "steady": {"label": "Équilibré", "player_ticks": 0, "enemy_ticks": 0,
               "gold": 0, "reinforcement": None},
    "safe": {"label": "Prudent", "player_ticks": 5, "enemy_ticks": 0,
             "gold": -4, "reinforcement": None},
    "risk": {"label": "Audacieux", "player_ticks": 0, "enemy_ticks": 3,
             "gold": 8, "reinforcement": "N"},
}
PIECE_MATERIAL = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "A": 12}
PIECE_KINDS = frozenset((*PIECE_MATERIAL, "K"))


def _require_int(value, name: str, minimum: int) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be integer >= {minimum}")
    return value


def validate_campaign(stages: list[dict]) -> None:
    """Fail before game initialization for malformed/impossible encounter sets."""
    if not isinstance(stages, list) or len(stages) < 2:
        raise ValueError("campaign needs multiple encounters")
    seen = set()
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            raise ValueError("stage must be a dictionary")
        if not isinstance(stage.get("name"), str) or not stage["name"].strip():
            raise ValueError("stage needs a non-empty name")
        if stage["name"] in seen:
            raise ValueError("duplicate stage name")
        seen.add(stage["name"])
        board = stage.get("board")
        if not isinstance(board, list) or len(board) != 2:
            raise ValueError("board dimensions must be [width, height]")
        w = _require_int(board[0], "width", 6)
        h = _require_int(board[1], "height", 6)
        if w > 16 or h > 16:
            raise ValueError("board too large for this prototype")
        army = stage.get("enemy_start")
        if not isinstance(army, dict) or army.get("K") != 1:
            raise ValueError("exactly one enemy King required")
        if set(army) - PIECE_KINDS:
            raise ValueError("unknown piece type")
        if not all(type(v) is int and v >= 0 for v in army.values()):
            raise ValueError("invalid enemy roster")
        if sum(army.values()) + 1 > 2 * w:
            raise ValueError("enemy reinforcements exceed two home rows")
        _require_int(stage.get("player_ticks"), "player_ticks", 1)
        _require_int(stage.get("enemy_ticks"), "enemy_ticks", 1)
        _require_int(stage.get("reward_gold"), "reward_gold", 5)
        if stage["reward_gold"] < 4:
            raise ValueError("reward must pay for safe route")


def prepare_encounter(stage: dict, route: str = "steady") -> dict:
    """Isolated encounter parameters: choices cost gold *earned on victory*."""
    if route not in ROUTES:
        raise ValueError("invalid campaign route")
    p = ROUTES[route]
    army = dict(stage["enemy_start"])
    if p["reinforcement"]:
        piece = p["reinforcement"]
        army[piece] = army.get(piece, 0) + 1
    width = stage["board"][0]
    if sum(army.values()) > 2 * width:
        raise ValueError("roster would overflow home rows")
    return {
        "name": stage["name"],
        "board": list(stage["board"]),
        "enemy_army": army,
        "player_ticks": stage["player_ticks"] + p["player_ticks"],
        "enemy_ticks": stage["enemy_ticks"] + p["enemy_ticks"],
        "reward_gold": stage["reward_gold"] + p["gold"],
        "route": route,
        "route_name": p["label"],
    }


def victory_reward(stage: dict, route: str, remaining_player_ticks: float,
                   tick_reward_factor: float) -> int:
    """No reward for a loss; caller must only invoke this for a real win."""
    encounter = prepare_encounter(stage, route)
    if type(remaining_player_ticks) not in (float, int):
        raise ValueError("invalid remaining ticks")
    if not 0 <= remaining_player_ticks < 1_000_000:
        raise ValueError("invalid remaining ticks")
    if type(tick_reward_factor) not in (float, int) or not 0 <= tick_reward_factor <= 1:
        raise ValueError("invalid tick reward factor")
    return encounter["reward_gold"] + int(remaining_player_ticks * tick_reward_factor)


def campaign_balance_report(stages: list[dict]) -> list[dict]:
    """Deterministic balance *diagnostics*, not empirical player win rates.

    Track material, time and rewards, and make sudden difficulty jumps visible.
    AI skill, king safety, usable move counts and synergy must be measured by
    real matches. Never call this estimate an ELO, win-rate or fair campaign.
    """
    validate_campaign(stages)
    result = []
    previous = None
    for i, stage in enumerate(stages):
        ro = prepare_encounter(stage)
        material = sum(PIECE_MATERIAL.get(k, 0) * n
                       for k, n in ro["enemy_army"].items())
        result.append({
            "stage": i + 1,
            "name": ro["name"],
            "enemy_material": material,
            "enemy_piece_count": sum(ro["enemy_army"].values()),
            "player_ticks": ro["player_ticks"],
            "enemy_ticks": ro["enemy_ticks"],
            "time_margin_ticks": ro["player_ticks"] - ro["enemy_ticks"],
            "reward_gold": ro["reward_gold"],
            "material_delta_vs_previous": None if previous is None else material - previous,
        })
        previous = material
    return result


def draft_shop_offers(pool: list[dict], gold: int, *, rng=None) -> list[dict]:
    """Draft three distinct offers, guaranteeing an affordable option.

    This fixes a common shop dead-end in the previous random three-offer draw.
    Affordability is not *usability*: an option needing a free square must still
    validate it at purchase, and gold can be spent before another purchase.
    """
    import random

    rng = rng or random
    _require_int(gold, "gold", 0)
    if not isinstance(pool, list) or len(pool) < 3:
        raise ValueError("shop requires at least three choices")
    ids = [item.get("id") for item in pool]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate shop offer IDs")
    for item in pool:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("invalid shop offer")
        _require_int(item.get("cost"), "shop cost", 0)
    affordable = [item for item in pool if item["cost"] <= gold]
    if not affordable:
        raise ValueError("campaign shop must contain an affordable option")
    valuable = [item for item in affordable
                if item.get("type") in ("tick", "buy_piece", "convert", "start_power")]
    first = rng.choice(valuable or affordable)
    remaining = [item for item in pool if item["id"] != first["id"]]
    return [first, *rng.sample(remaining, 2)]


def record_stage_result(meta: dict, *, stage: int, route: str,
                        ai_difficulty: str, won: bool,
                        remaining_player_ticks: float, remaining_enemy_ticks: float,
                        player_material: int) -> None:
    """Bounded LOCAL anonymous play record, enabling actual balance analysis.

    Counts *completed* fights only. Quits, user skill and changed AI settings
    must be accounted for separately before inferring difficulty.
    """
    if not isinstance(meta, dict) or type(stage) is not int or stage < 1:
        raise ValueError("invalid balance record")
    if route not in ROUTES or ai_difficulty not in ("easy", "normal", "hard"):
        raise ValueError("invalid route/difficulty")
    if type(won) is not bool:
        raise ValueError("invalid result")
    for value in (remaining_player_ticks, remaining_enemy_ticks):
        if type(value) not in (float, int) or not -1000 <= value < 100000:
            raise ValueError("invalid remaining ticks")
    if type(player_material) is not int or player_material < 0:
        raise ValueError("invalid remaining material")
    records = meta.setdefault("campaign_balance_history", [])
    if not isinstance(records, list):
        raise ValueError("invalid existing history")
    records.append({
        "stage": stage, "route": route, "ai_difficulty": ai_difficulty,
        "result": "victory" if won else "defeat",
        "player_ticks_left": float(remaining_player_ticks),
        "enemy_ticks_left": float(remaining_enemy_ticks),
        "player_material_left": player_material,
    })
    del records[:-200]  # capped save, not an endless telemetry stream
