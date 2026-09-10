from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from .composition import ROLE_BY_AGENT
from .economy import classify_economy


JsonObject = dict[str, Any]


def _target(match: JsonObject, player_puuid: str) -> JsonObject | None:
    return next(
        (
            player
            for player in (match.get("players") or {}).get("all_players", [])
            if player.get("puuid") == player_puuid
        ),
        None,
    )


def _label(player: JsonObject) -> str:
    name = str(player.get("name") or "Unknown")
    tag = str(player.get("tag") or "")
    return f"{name}#{tag}" if tag else name


def _valid_rounds(match: JsonObject) -> list[JsonObject]:
    return [round_data for round_data in match.get("rounds", []) if round_data.get("end_type") != "Surrendered"]


def _rounds_played(match: JsonObject) -> int:
    return len(_valid_rounds(match))


def _party_context(target: JsonObject, own: list[JsonObject]) -> tuple[int | None, str]:
    party_id = target.get("party_id")
    party = [player for player in own if party_id and player.get("party_id") == party_id]
    size = len(party) if party_id else None
    party_type = {1: "solo", 2: "duo", 3: "trio", 4: "four_stack", 5: "five_stack"}.get(size, "unknown")
    return size, party_type


def _match_row(match: JsonObject, player_puuid: str) -> JsonObject | None:
    target = _target(match, player_puuid)
    if not target:
        return None
    players = (match.get("players") or {}).get("all_players", [])
    own = [player for player in players if player.get("team") == target.get("team")]
    stats = target.get("stats") or {}
    team_result = (match.get("teams") or {}).get(str(target.get("team")).lower()) or {}
    party_size, party_type = _party_context(target, own)
    rounds = _rounds_played(match)
    return {
        "match_id": (match.get("metadata") or {}).get("matchid"),
        "map": (match.get("metadata") or {}).get("map") or "Unknown",
        "agent": target.get("character") or "Unknown",
        "role": ROLE_BY_AGENT.get(target.get("character"), "Unknown"),
        "party_size": party_size,
        "party_type": party_type,
        "match_won": bool(team_result.get("has_won")),
        "rounds": rounds,
        "kills": int(stats.get("kills") or 0),
        "deaths": int(stats.get("deaths") or 0),
        "assists": int(stats.get("assists") or 0),
        "damage": int(target.get("damage_made") or 0),
        "score": int(stats.get("score") or 0),
        "own": own,
        "target_puuid": player_puuid,
    }


def _performance_summary(rows: list[JsonObject]) -> JsonObject:
    matches = len(rows)
    rounds = sum(int(row.get("rounds") or 0) for row in rows)
    kills = sum(int(row.get("kills") or 0) for row in rows)
    deaths = sum(int(row.get("deaths") or 0) for row in rows)
    return {
        "matches": matches,
        "rounds": rounds,
        "evidence": "supported" if matches >= 5 else "weak_evidence",
        "win_rate": sum(bool(row.get("match_won")) for row in rows) / matches if matches else None,
        "kd": kills / deaths if deaths else None,
        "kills_per_match": kills / matches if matches else None,
        "deaths_per_match": deaths / matches if matches else None,
        "assists_per_match": sum(int(row.get("assists") or 0) for row in rows) / matches if matches else None,
        "adr": sum(int(row.get("damage") or 0) for row in rows) / rounds if rounds else None,
        "acs": sum(int(row.get("score") or 0) for row in rows) / rounds if rounds else None,
    }


def _group_summary(rows: list[JsonObject], keys: tuple[str, ...]) -> JsonObject:
    values = {key: rows[0].get(key) for key in keys}
    return {**values, **_performance_summary(rows)}


def _relative_map_summary(rows: list[JsonObject]) -> JsonObject:
    matches = len(rows)
    rounds = sum(int(row.get("rounds") or 0) for row in rows)
    target_kills = sum(int(row.get("kills") or 0) for row in rows)
    target_deaths = sum(int(row.get("deaths") or 0) for row in rows)
    target_damage = sum(int(row.get("damage") or 0) for row in rows)
    target_score = sum(int(row.get("score") or 0) for row in rows)
    ally_kills = ally_deaths = ally_damage = ally_score = ally_rounds = 0
    ally_players = 0
    teammate_presence: dict[str, int] = defaultdict(int)
    for row in rows:
        allies = [player for player in row["own"] if player.get("puuid") != row["target_puuid"]]
        ally_players += len(allies)
        ally_rounds += int(row.get("rounds") or 0) * len(allies)
        for ally in allies:
            stats = ally.get("stats") or {}
            ally_kills += int(stats.get("kills") or 0)
            ally_deaths += int(stats.get("deaths") or 0)
            ally_damage += int(ally.get("damage_made") or 0)
            ally_score += int(stats.get("score") or 0)
            teammate_presence[_label(ally)] += 1
    target = {
        "matches": matches,
        "rounds": rounds,
        "kd": target_kills / target_deaths if target_deaths else None,
        "adr": target_damage / rounds if rounds else None,
        "acs": target_score / rounds if rounds else None,
        "kills_per_match": target_kills / matches if matches else None,
        "deaths_per_match": target_deaths / matches if matches else None,
    }
    allies = {
        "players_per_match": ally_players / matches if matches else None,
        "rounds": ally_rounds,
        "kd": ally_kills / ally_deaths if ally_deaths else None,
        "adr": ally_damage / ally_rounds if ally_rounds else None,
        "acs": ally_score / ally_rounds if ally_rounds else None,
        "kills_per_player_match": ally_kills / ally_players if ally_players else None,
        "deaths_per_player_match": ally_deaths / ally_players if ally_players else None,
    }
    return {
        "matches": matches,
        "evidence": "supported" if matches >= 5 else "weak_evidence",
        "win_rate": sum(bool(row.get("match_won")) for row in rows) / matches if matches else None,
        "target": target,
        "teammate_average": allies,
        "target_minus_teammate_average": {
            metric: target.get(metric) - allies.get(metric)
            if target.get(metric) is not None and allies.get(metric) is not None
            else None
            for metric in ("kd", "adr", "acs")
        },
        "teammate_presence": [
            {"teammate": teammate, "matches": count}
            for teammate, count in sorted(teammate_presence.items(), key=lambda item: (-item[1], item[0]))
        ],
    }


def _economy_rows(matches: Iterable[JsonObject], player_puuid: str) -> list[JsonObject]:
    rows: list[JsonObject] = []
    for match in matches:
        target = _target(match, player_puuid)
        if not target:
            continue
        team = target.get("team")
        metadata = match.get("metadata") or {}
        for round_number, round_data in enumerate(_valid_rounds(match), start=1):
            stats = round_data.get("player_stats", [])
            target_stat = next((stat for stat in stats if stat.get("player_puuid") == player_puuid), None)
            if not target_stat:
                continue
            target_economy = (target_stat.get("economy") or {}).get("loadout_value")
            own_stats = [stat for stat in stats if stat.get("player_team") == team]
            classes = [
                classify_economy((stat.get("economy") or {}).get("loadout_value"), round_number)
                for stat in own_stats
            ]
            class_counts: dict[str, int] = defaultdict(int)
            for economy_class in classes:
                class_counts[economy_class] += 1
            team_class = max(class_counts, key=class_counts.get) if class_counts else "unknown"
            round_won = round_data.get("winning_team") == team
            rows.append({
                "match_id": (match.get("metadata") or {}).get("matchid"),
                "map": metadata.get("map") or "Unknown",
                "economy_class": classify_economy(target_economy, round_number),
                "team_economy_class": team_class,
                "round_won": round_won,
                "kills": int(target_stat.get("kills") or 0),
                "damage": int(target_stat.get("damage") or 0),
            })
    return rows


def _economy_summary(rows: list[JsonObject]) -> JsonObject:
    rounds = len(rows)
    matches = len({row.get("match_id") for row in rows if row.get("match_id")})
    return {
        "matches": matches,
        "rounds": rounds,
        "evidence": "supported" if rounds >= 50 else "weak_evidence",
        "round_win_rate": sum(bool(row.get("round_won")) for row in rows) / rounds if rounds else None,
        "avg_kills": sum(int(row.get("kills") or 0) for row in rows) / rounds if rounds else None,
        "avg_damage": sum(int(row.get("damage") or 0) for row in rows) / rounds if rounds else None,
    }


def summarize_contextual_splits(matches: Iterable[JsonObject], *, player_puuid: str) -> JsonObject:
    materialized = list(matches)
    match_rows = [row for match in materialized for row in [_match_row(match, player_puuid)] if row]
    by_map: dict[str, list[JsonObject]] = defaultdict(list)
    by_map_party: dict[tuple[str, str], list[JsonObject]] = defaultdict(list)
    by_map_agent: dict[tuple[str, str], list[JsonObject]] = defaultdict(list)
    for row in match_rows:
        by_map[str(row["map"])].append(row)
        by_map_party[(str(row["map"]), str(row["party_type"]))].append(row)
        by_map_agent[(str(row["map"]), str(row["agent"]))].append(row)
    economy_rows = _economy_rows(materialized, player_puuid)
    by_map_economy: dict[tuple[str, str, str], list[JsonObject]] = defaultdict(list)
    by_economy_alignment: dict[str, list[JsonObject]] = defaultdict(list)
    for row in economy_rows:
        by_map_economy[(str(row["map"]), str(row["economy_class"]), str(row["team_economy_class"]))].append(row)
        alignment = "aligned" if row["economy_class"] == row["team_economy_class"] else "different_from_team_mode"
        by_economy_alignment[alignment].append(row)
    teammate_by_map: dict[tuple[str, str], list[JsonObject]] = defaultdict(list)
    for row in match_rows:
        for ally in row["own"]:
            if ally.get("puuid") != player_puuid:
                teammate_by_map[(str(row["map"]), _label(ally))].append(row)
    return {
        "definitions": {
            "teammate_average": "allied players in the same match, excluding the target; this is a descriptive within-match comparison",
            "team_economy_class": "most frequent economy class among target-team round player_stats; ties use input order",
            "map_party_and_agent": "match-level target performance grouped by map and the observed target party/agent",
        },
        "thresholds": {
            "minimum_group_matches": 5,
            "minimum_economy_rounds": 50,
            "evidence_rule": "groups below the threshold are retained and marked weak_evidence",
        },
        "by_map": [
            {"map": map_name, **_relative_map_summary(rows)}
            for map_name, rows in sorted(by_map.items())
        ],
        "by_map_party": [
            _group_summary(rows, ("map", "party_type", "party_size"))
            for _, rows in sorted(by_map_party.items())
        ],
        "by_map_agent": [
            _group_summary(rows, ("map", "agent", "role"))
            for _, rows in sorted(by_map_agent.items())
        ],
        "by_map_economy": [
            {"map": map_name, "economy_class": economy_class, "team_economy_class": team_class, **_economy_summary(rows)}
            for (map_name, economy_class, team_class), rows in sorted(by_map_economy.items())
        ],
        "by_economy_alignment": [
            {"alignment": alignment, **_economy_summary(rows)}
            for alignment, rows in sorted(by_economy_alignment.items())
        ],
        "by_map_teammate": [
            {"map": map_name, "teammate": teammate, **_performance_summary(rows)}
            for (map_name, teammate), rows in sorted(teammate_by_map.items())
        ],
        "coverage": {
            "matches": len(match_rows),
            "economy_rounds": len(economy_rows),
            "maps": len(by_map),
            "teammates_with_match_rows": len({_label(ally) for row in match_rows for ally in row["own"] if ally.get("puuid") != player_puuid}),
        },
        "limitations": [
            "Teammate comparisons share the same match and map but are descriptive; they do not establish synergy or causality.",
            "Target and teammate averages are aggregate player-stat comparisons, not role-adjusted or opponent-adjusted ratings.",
            "Map × economy uses the target-team modal class per round and does not measure purchase intent or communication.",
            "Small map, party, agent, teammate and economy groups require weak_evidence treatment.",
        ],
    }
