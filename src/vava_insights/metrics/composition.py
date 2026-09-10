from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable


ROLE_BY_AGENT = {
    "Jett": "Duelist", "Phoenix": "Duelist", "Reyna": "Duelist", "Yoru": "Duelist",
    "Waylay": "Duelist", "Raze": "Duelist", "Neon": "Duelist", "Iso": "Duelist",
    "Omen": "Controller", "Astra": "Controller", "Brimstone": "Controller",
    "Viper": "Controller", "Harbor": "Controller", "Clove": "Controller",
    "Sova": "Initiator", "Skye": "Initiator", "Fade": "Initiator", "Breach": "Initiator",
    "Gekko": "Initiator", "Tejo": "Initiator", "Cypher": "Sentinel",
    "Chamber": "Sentinel", "Killjoy": "Sentinel", "Vyse": "Sentinel",
}


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    matches = len(rows)
    return {
        "matches": matches,
        "win_rate": sum(bool(row["team_won"]) for row in rows) / matches if matches else None,
    }


def summarize_composition(
    matches: Iterable[dict[str, Any]],
    *,
    player_puuid: str,
    minimum_composition_matches: int = 2,
    minimum_teammate_matches: int = 5,
) -> dict[str, Any]:
    composition_rows: list[dict[str, Any]] = []
    role_rows: list[dict[str, Any]] = []
    teammate_rows: list[dict[str, Any]] = []

    for match in matches:
        metadata = match.get("metadata") or {}
        players = (match.get("players") or {}).get("all_players") or []
        target = next((player for player in players if player.get("puuid") == player_puuid), None)
        if not target:
            continue
        target_team = target.get("team")
        own_players = [player for player in players if player.get("team") == target_team]
        enemy_players = [player for player in players if player.get("team") != target_team]
        team_won = bool((match.get("teams") or {}).get(str(target_team).lower(), {}).get("has_won"))
        target_agent = target.get("character") or "Unknown"
        composition_rows.append({
            "match_id": metadata.get("matchid"),
            "map": metadata.get("map"),
            "season": metadata.get("season_id"),
            "target_agent": target_agent,
            "target_role": ROLE_BY_AGENT.get(target_agent, "Unknown"),
            "own_composition": " | ".join(sorted(player.get("character") or "Unknown" for player in own_players)),
            "enemy_composition": " | ".join(sorted(player.get("character") or "Unknown" for player in enemy_players)),
            "team_won": team_won,
        })
        stats = target.get("stats") or {}
        role_rows.append({
            "match_id": metadata.get("matchid"),
            "agent": target_agent,
            "role": ROLE_BY_AGENT.get(target_agent, "Unknown"),
            "team_won": team_won,
            "kills": stats.get("kills", 0) or 0,
            "deaths": stats.get("deaths", 0) or 0,
            "assists": stats.get("assists", 0) or 0,
            "damage_made": target.get("damage_made", 0) or 0,
        })
        for teammate in own_players:
            if teammate.get("puuid") != player_puuid:
                teammate_rows.append({
                    "match_id": metadata.get("matchid"),
                    "teammate": teammate.get("name"),
                    "teammate_agent": teammate.get("character"),
                    "team_won": team_won,
                    "target_agent": target_agent,
                    "map": metadata.get("map"),
                })

    composition_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    teammate_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    role_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in composition_rows:
        composition_groups[row["own_composition"]].append(row)
    for row in teammate_rows:
        teammate_groups[(row["teammate"], row["teammate_agent"])].append(row)
    for row in role_rows:
        role_groups[row["role"]].append(row)

    role_summary = []
    for role, group in sorted(role_groups.items(), key=lambda item: (-len(item[1]), item[0])):
        summary = _aggregate(group)
        summary.update({
            "role": role,
            "avg_kills": sum(float(row["kills"]) for row in group) / len(group),
            "avg_deaths": sum(float(row["deaths"]) for row in group) / len(group),
            "avg_assists": sum(float(row["assists"]) for row in group) / len(group),
            "avg_damage": sum(float(row["damage_made"]) for row in group) / len(group),
        })
        role_summary.append(summary)

    return {
        "role_catalog": ROLE_BY_AGENT,
        "role_summary": role_summary,
        "composition_summary": [
            {"own_composition": key, **_aggregate(group)}
            for key, group in sorted(composition_groups.items(), key=lambda item: (-len(item[1]), item[0]))
            if len(group) >= minimum_composition_matches
        ],
        "teammate_summary": [
            {"teammate": key[0], "teammate_agent": key[1], **_aggregate(group)}
            for key, group in sorted(teammate_groups.items(), key=lambda item: (-len(item[1]), item[0]))
            if len(group) >= minimum_teammate_matches
        ],
        "thresholds": {
            "minimum_composition_matches": minimum_composition_matches,
            "minimum_teammate_matches": minimum_teammate_matches,
        },
        "limitations": [
            "Role is nominal agent classification, not observed tactical role.",
            "Teammate and composition win rates are descriptive associations and do not establish synergy or causality.",
            "Rare compositions remain available in raw match data but are omitted from the summary below the threshold.",
        ],
    }