from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable


def _safe_rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def summarize_event_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    rounds = len(rows)
    first_kills = sum(bool(row.get("first_kill")) for row in rows)
    first_deaths = sum(bool(row.get("first_death")) for row in rows)
    deaths = sum(int(row.get("deaths") or 0) for row in rows)
    return {
        "rounds": rounds,
        "round_win_rate": sum(bool(row.get("round_won")) for row in rows) / rounds if rounds else None,
        "kast_rate": sum(bool(row.get("kast")) for row in rows) / rounds if rounds else None,
        "damage_participation_rate": (
            sum(bool(row.get("damage_participation")) for row in rows) / rounds if rounds else None
        ),
        "fk_rate": _safe_rate(first_kills, rounds),
        "fd_rate": _safe_rate(first_deaths, rounds),
        "fk_fd_net": first_kills - first_deaths,
        "trade_rate": _safe_rate(sum(bool(row.get("traded")) for row in rows), deaths),
        "round_win_after_fk": _safe_rate(
            sum(bool(row.get("round_won")) for row in rows if row.get("first_kill")),
            first_kills,
        ),
        "round_win_after_fd": _safe_rate(
            sum(bool(row.get("round_won")) for row in rows if row.get("first_death")),
            first_deaths,
        ),
        "avg_damage": sum(float(row.get("damage") or 0) for row in rows) / rounds if rounds else None,
    }


def summarize_impact(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    materialized = list(rows)
    by_side: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_match: dict[str, int] = defaultdict(int)
    for row in materialized:
        if row.get("side"):
            by_side[str(row["side"])].append(row)
        if row.get("match_id"):
            by_match[str(row["match_id"])] += 1

    return {
        "definition": {
            "kast": "kill + assist + survive + trade",
            "trade_window_ms": 5000,
            "first_blood": "first kill event in the round",
            "round_indexing": "Henrik kill events are zero-based; output rounds are one-based.",
        },
        "overall": summarize_event_group(materialized),
        "by_side": {side: summarize_event_group(group) for side, group in by_side.items()},
        "sample": {
            "matches": len(by_match),
            "rounds": len(materialized),
            "side_inference_coverage": (
                sum(bool(row.get("side")) for row in materialized) / len(materialized)
                if materialized
                else 0.0
            ),
            "excluded_surrender_events": 0,
            "per_match_round_reconciliation": "not_available",
        },
    }