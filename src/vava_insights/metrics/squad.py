from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any, Iterable


def party_label(size: int | None) -> str:
    return {1: "solo", 2: "duo", 3: "trio", 4: "four_stack", 5: "five_stack"}.get(size, "unknown")


def player_label(player: dict[str, Any]) -> str:
    name = player.get("name") or "Unknown"
    tag = player.get("tag") or ""
    return f"{name}#{tag}" if tag else str(name)


def wilson_interval(wins: int, matches: int, z: float = 1.96) -> tuple[float | None, float | None]:
    if not matches:
        return None, None
    proportion = wins / matches
    denominator = 1 + z**2 / matches
    center = (proportion + z**2 / (2 * matches)) / denominator
    margin = z * math.sqrt(proportion * (1 - proportion) / matches + z**2 / (4 * matches**2)) / denominator
    return center - margin, center + margin


def _group_summary(rows: list[dict[str, Any]], total_matches: int) -> dict[str, Any]:
    matches = len(rows)
    wins = sum(bool(row["match_won"]) for row in rows)
    low, high = wilson_interval(wins, matches)
    rounds = sum(int(row["rounds_played"]) for row in rows)
    deaths = sum(int(row["deaths"]) for row in rows)
    return {
        "matches": matches,
        "sample_share": matches / total_matches if total_matches else None,
        "win_rate": wins / matches if matches else None,
        "win_rate_ci95_low": low,
        "win_rate_ci95_high": high,
        "kd": sum(float(row["kills"]) for row in rows) / deaths if deaths else None,
        "adr": sum(float(row["damage_made"]) for row in rows) / rounds if rounds else None,
        "acs": sum(float(row["score"]) for row in rows) / rounds if rounds else None,
    }


def summarize_squad(matches: Iterable[dict[str, Any]], *, player_puuid: str) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for match in matches:
        metadata = match.get("metadata") or {}
        players = (match.get("players") or {}).get("all_players") or []
        target = next((player for player in players if player.get("puuid") == player_puuid), None)
        if not target:
            continue
        target_team = target.get("team")
        own = [player for player in players if player.get("team") == target_team]
        enemies = [player for player in players if player.get("team") != target_team]
        party_id = target.get("party_id")
        party = [player for player in own if party_id and player.get("party_id") == party_id]
        enemy_party_counts = Counter(player.get("party_id") for player in enemies if player.get("party_id"))
        target_stats = target.get("stats") or {}
        team_result = (match.get("teams") or {}).get(str(target_team).lower()) or {}
        rounds_played = sum(int(((match.get("teams") or {}).get(color) or {}).get("rounds_won") or 0) for color in ("red", "blue"))
        rows.append({
            "match_id": metadata.get("matchid"),
            "season": metadata.get("season_id"),
            "map": metadata.get("map"),
            "party_id_available": bool(party_id),
            "party_size": len(party) if party_id else None,
            "party_type": party_label(len(party) if party_id else None),
            "is_premade": bool(party_id) and len(party) >= 2,
            "is_five_stack": bool(party_id) and len(party) == 5,
            "party_roster": " | ".join(sorted(player_label(player) for player in party)),
            "premade_teammates": sorted(player_label(player) for player in party if player.get("puuid") != player_puuid),
            "opponent_largest_party_size": max(enemy_party_counts.values(), default=None),
            "opponent_is_five_stack": max(enemy_party_counts.values(), default=None) == 5,
            "match_won": bool(team_result.get("has_won")),
            "rounds_played": rounds_played,
            "kills": target_stats.get("kills", 0) or 0,
            "deaths": target_stats.get("deaths", 0) or 0,
            "damage_made": target.get("damage_made", 0) or 0,
            "score": target_stats.get("score", 0) or 0,
        })

    total = len(rows)
    by_party: dict[tuple[Any, str], list[dict[str, Any]]] = defaultdict(list)
    by_context: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_five_stack: dict[str, list[dict[str, Any]]] = defaultdict(list)
    exact_squads: dict[str, list[dict[str, Any]]] = defaultdict(list)
    teammate_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_party[(row["party_size"], row["party_type"])].append(row)
        by_context["premade_2_to_5" if row["is_premade"] else "solo"].append(row)
        by_five_stack["five_stack" if row["is_five_stack"] else "not_five_stack"].append(row)
        if row["is_five_stack"]:
            exact_squads[row["party_roster"]].append(row)
        for teammate in row["premade_teammates"]:
            teammate_rows[teammate].append(row)

    return {
        "definitions": {
            "party_size": "players on the target team sharing the target player's party_id",
            "five_stack": "target party_size equals 5",
            "exact_squad": "same set of five account name#tag values",
        },
        "coverage": {
            "matches": total,
            "party_id_available_matches": sum(bool(row["party_id_available"]) for row in rows),
            "party_id_coverage": sum(bool(row["party_id_available"]) for row in rows) / total if total else None,
        },
        "by_party_size": [
            {"party_size": key[0], "party_type": key[1], **_group_summary(group, total)}
            for key, group in sorted(by_party.items(), key=lambda item: (-len(item[1]), str(item[0])))
        ],
        "premade_vs_solo": [{"group_context": key, **_group_summary(group, total)} for key, group in by_context.items()],
        "five_stack_vs_other": [{"five_stack_context": key, **_group_summary(group, total)} for key, group in by_five_stack.items()],
        "five_stack_validation": {
            "target_five_stack_matches": len(by_five_stack.get("five_stack", [])),
            "opponent_five_stack_matches": sum(row["opponent_is_five_stack"] for row in rows if row["is_five_stack"]),
        },
        "exact_five_stack_squads": [
            {"party_roster": key, "matches": len(group), "wins": sum(row["match_won"] for row in group), "win_rate": sum(row["match_won"] for row in group) / len(group)}
            for key, group in sorted(exact_squads.items(), key=lambda item: (-len(item[1]), item[0]))
        ],
        "premade_teammates": [
            {"teammate": key, "matches": len(group), "win_rate": sum(row["match_won"] for row in group) / len(group)}
            for key, group in sorted(teammate_rows.items(), key=lambda item: (-len(item[1]), item[0]))
        ],
        "limitations": [
            "Party membership is observable per match, but friendship or communication quality is not observable.",
            "Win-rate differences are descriptive and confounded by opponent strength, map, agent and composition.",
        ],
    }