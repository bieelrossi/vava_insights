from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    matches = len(rows)
    rounds = sum(float(row["rounds_played"]) for row in rows)
    kills = sum(float(row["kills"]) for row in rows)
    deaths = sum(float(row["deaths"]) for row in rows)
    assists = sum(float(row["assists"]) for row in rows)
    damage = sum(float(row["damage_made"]) for row in rows)
    score = sum(float(row["score"]) for row in rows)
    return {
        "matches": matches,
        "win_rate": sum(bool(row["match_won"]) for row in rows) / matches if matches else None,
        "rounds": int(rounds),
        "kd": kills / deaths if deaths else None,
        "adr": damage / rounds if rounds else None,
        "acs": score / rounds if rounds else None,
        "kills_per_match": kills / matches if matches else None,
        "deaths_per_match": deaths / matches if matches else None,
        "assists_per_match": assists / matches if matches else None,
    }


def summarize_baseline(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Build deterministic match, agent and map summaries from normalized rows."""
    materialized = list(rows)
    dimensions: dict[str, dict[str, list[dict[str, Any]]]] = {
        "by_agent": defaultdict(list),
        "by_map": defaultdict(list),
        "by_season": defaultdict(list),
    }
    for row in materialized:
        for dimension, key in (("by_agent", "agent"), ("by_map", "map"), ("by_season", "season")):
            dimensions[dimension][str(row.get(key) or "unknown")].append(row)

    return {
        "overall": _aggregate(materialized),
        **{
            dimension: [
                {key: value, **_aggregate(group)}
                for value, group in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))
            ]
            for dimension, groups in dimensions.items()
            for key in [dimension.removeprefix("by_")]
        },
        "limitations": [
            "This baseline uses match-level facts only; round, economy, clutch and trade metrics are not inferred here.",
            "Win rates are descriptive associations and should be interpreted with sample size and context.",
        ],
    }