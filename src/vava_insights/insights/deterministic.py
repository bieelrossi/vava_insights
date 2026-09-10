from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InsightRules:
    """Configurable rules for descriptive, deterministic findings."""

    minimum_overall_matches: int = 5
    minimum_group_matches: int = 5
    positive_kd: float = 1.0
    positive_win_rate: float = 0.5


def _sample_status(matches: int, minimum: int) -> str:
    if matches <= 0:
        return "insufficient_data"
    if matches < minimum:
        return "weak_evidence"
    return "supported"


def _group_signals(
    groups: list[dict[str, Any]],
    *,
    dimension: str,
    rules: InsightRules,
) -> dict[str, Any]:
    signals: list[dict[str, Any]] = []
    for group in groups:
        matches = int(group.get("matches") or 0)
        signals.append(
            {
                dimension: group.get(dimension),
                "status": _sample_status(matches, rules.minimum_group_matches),
                "evidence": {
                    "matches": matches,
                    "win_rate": group.get("win_rate"),
                    "kd": group.get("kd"),
                    "adr": group.get("adr"),
                    "acs": group.get("acs"),
                },
                "limitation": (
                    f"A associação por {dimension} não controla mapa, adversários, composição, teammates ou período."
                ),
            }
        )
    return {
        "dimension": dimension,
        "minimum_matches": rules.minimum_group_matches,
        "signals": signals,
    }


def build_deterministic_insights(
    baseline: dict[str, Any],
    *,
    rules: InsightRules | None = None,
) -> dict[str, Any]:
    """Create evidence-backed findings without generating causal conclusions."""
    rules = rules or InsightRules()
    overall = baseline.get("overall") or {}
    matches = int(overall.get("matches") or 0)
    win_rate = overall.get("win_rate")
    kd = overall.get("kd")
    mechanical_output = (
        kd is not None
        and float(kd) >= rules.positive_kd
        and win_rate is not None
        and float(win_rate) < rules.positive_win_rate
    )

    findings: list[dict[str, Any]] = [
        {
            "id": "mechanical_output_vs_results",
            "status": (
                "descriptive_only"
                if matches >= rules.minimum_overall_matches and mechanical_output
                else _sample_status(matches, rules.minimum_overall_matches)
            ),
            "triggered": mechanical_output,
            "observation": (
                "A produção mecânica agregada está acima do limiar de K/D, enquanto o win rate permanece abaixo de 50%."
                if mechanical_output
                else "A regra de divergência entre produção mecânica e resultado não foi acionada."
            ),
            "evidence": {
                "matches": matches,
                "win_rate": win_rate,
                "kd": kd,
                "adr": overall.get("adr"),
                "acs": overall.get("acs"),
                "thresholds": {
                    "minimum_matches": rules.minimum_overall_matches,
                    "positive_kd": rules.positive_kd,
                    "positive_win_rate": rules.positive_win_rate,
                },
            },
            "limitation": (
                "Este achado não mede trade, utilidade, FK/FD, economia, contexto de round ou causalidade."
            ),
        }
    ]

    return {
        "method": "deterministic_rules_v1",
        "rules": {
            "minimum_overall_matches": rules.minimum_overall_matches,
            "minimum_group_matches": rules.minimum_group_matches,
            "positive_kd": rules.positive_kd,
            "positive_win_rate": rules.positive_win_rate,
        },
        "findings": findings,
        "by_agent": _group_signals(
            baseline.get("by_agent") or [],
            dimension="agent",
            rules=rules,
        ),
        "by_map": _group_signals(
            baseline.get("by_map") or [],
            dimension="map",
            rules=rules,
        ),
    }