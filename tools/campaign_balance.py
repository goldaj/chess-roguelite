"""Offline campaign diagnostics; NEVER called by the running game.

Default: static game-data report (not a predicted win rate).
--save explicitly supplied: aggregate local player results from that save file,
grouped by encounter, route and user-selected enemy AI level. No network, no
automatic discovery of private files and no outputs written to disk.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

from src.core.campaign import campaign_balance_report

ROOT = Path(__file__).resolve().parents[1]
CONTENT_PATH = ROOT / "content" / "shop_items.json"


def summarise_played_sessions(meta: dict) -> list[dict]:
    history = meta.get("campaign_balance_history", [])
    if not isinstance(history, list):
        raise ValueError("invalid balance history")
    groups = defaultdict(lambda: [0, 0])
    for record in history:
        if not isinstance(record, dict):
            continue
        try:
            stage = record["stage"]
            route = record["route"]
            level = record["ai_difficulty"]
            result = record["result"]
        except KeyError:
            continue
        if (type(stage) is not int or not 1 <= stage <= 6 or
                route not in ("steady", "safe", "risk") or
                level not in ("easy", "normal", "hard") or
                result not in ("victory", "defeat")):
            continue
        row = groups[stage, route, level]
        row[0] += 1
        row[1] += result == "victory"
    out = []
    for (stage, route, level), (runs, wins) in sorted(groups.items()):
        rate = wins / runs
        z = 1.96
        norm = 1 + z*z/runs
        centre = (rate + z*z/(2*runs)) / norm
        half = z*math.sqrt(rate*(1-rate)/runs + z*z/(4*runs*runs))/norm
        out.append({
            "stage": stage, "route": route, "ai_difficulty": level,
            "observed_encounters": runs, "victories": wins,
            "observed_win_rate": round(rate, 4),
            "wilson95_low": round(max(0, centre-half), 4),
            "wilson95_high": round(min(1, centre+half), 4),
            "note": "One player's local encounters only; selection bias and abandonments not counted",
        })
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Chess roguelite campaign diagnostics")
    parser.add_argument("--save", type=Path, help="Explicit path to a local save with encounter results")
    args = parser.parse_args()
    content = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    report = {
        "kind": "static_campaign_parameters_NOT_a_win_rate",
        "stages": campaign_balance_report(content["stages"]),
        "routes": ("steady", "safe", "risk"),
        "limitations": "Material/turn margins do not predict challenge; tuning requires real player data.",
    }
    if args.save:
        meta = json.loads(args.save.read_text(encoding="utf-8"))
        report["local_play_observations"] = summarise_played_sessions(meta)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
