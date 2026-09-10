from __future__ import annotations

from typing import Any, Iterable


JsonObject = dict[str, Any]


def infer_initial_sides(rounds: list[JsonObject]) -> dict[str, str]:
    for round_data in rounds[:12]:
        if round_data.get("end_type") == "Surrendered":
            continue
        planted_by = (round_data.get("plant_events") or {}).get("planted_by") or {}
        attacking_team = planted_by.get("team")
        if attacking_team:
            defending_team = "Blue" if attacking_team == "Red" else "Red"
            return {attacking_team: "Attack", defending_team: "Defense"}
    return {}


def side_for_round(
    initial_sides: dict[str, str],
    team: str | None,
    round_number: int,
) -> str | None:
    if not initial_sides or team not in initial_sides:
        return None
    if round_number <= 12:
        return initial_sides[team]
    if round_number <= 24:
        return "Defense" if initial_sides[team] == "Attack" else "Attack"
    overtime_pair = (round_number - 25) // 2
    overtime_start = "Attack" if overtime_pair % 2 == 0 else "Defense"
    first_half_side = initial_sides[team]
    overtime_side = (
        first_half_side
        if overtime_start == "Attack"
        else ("Defense" if first_half_side == "Attack" else "Attack")
    )
    return (
        overtime_side
        if (round_number - 25) % 2 == 0
        else ("Defense" if overtime_side == "Attack" else "Attack")
    )


def event_metrics(match: JsonObject, target_puuid: str) -> list[JsonObject]:
    metadata = match.get("metadata") or {}
    rounds = match.get("rounds") or []
    all_kills = match.get("kills") or []
    initial_sides = infer_initial_sides(rounds)
    rows: list[JsonObject] = []

    for round_number, round_data in enumerate(rounds, start=1):
        if round_data.get("end_type") == "Surrendered":
            continue
        player_stat = next(
            (
                stat
                for stat in round_data.get("player_stats", [])
                if stat.get("player_puuid") == target_puuid
            ),
            None,
        )
        if not player_stat:
            continue

        target_team = player_stat.get("player_team")
        # Henrik uses zero-based round numbers in kills; rounds are one-based here.
        round_kills = [
            kill for kill in all_kills if kill.get("round") == round_number - 1
        ]
        round_kills.sort(key=lambda kill: kill.get("kill_time_in_round", 0))
        own_kills = [kill for kill in round_kills if kill.get("killer_puuid") == target_puuid]
        own_deaths = [kill for kill in round_kills if kill.get("victim_puuid") == target_puuid]
        own_assists = [
            assistant
            for kill in round_kills
            for assistant in kill.get("assistants", [])
            if assistant.get("assistant_puuid") == target_puuid
        ]
        own_death = own_deaths[0] if own_deaths else None
        traded = False
        if own_death:
            death_time = own_death.get("kill_time_in_round", 0)
            traded = any(
                0 < kill.get("kill_time_in_round", 0) - death_time <= 5000
                and kill.get("killer_team") == target_team
                and kill.get("victim_team") != target_team
                for kill in round_kills
            )
        survived = not own_deaths
        rows.append(
            {
                "match_id": metadata.get("matchid"),
                "round": round_number,
                "team": target_team,
                "side": side_for_round(initial_sides, target_team, round_number),
                "round_won": round_data.get("winning_team") == target_team,
                "kills": len(own_kills),
                "deaths": len(own_deaths),
                "assists": len(own_assists),
                "damage": player_stat.get("damage", 0) or 0,
                "damage_participation": (player_stat.get("damage") or 0) > 0,
                "survived": survived,
                "kast": bool(own_kills or own_assists or survived or traded),
                "first_kill": bool(round_kills and round_kills[0].get("killer_puuid") == target_puuid),
                "first_death": bool(round_kills and round_kills[0].get("victim_puuid") == target_puuid),
                "traded": traded,
                "end_type": round_data.get("end_type"),
            }
        )
    return rows


def extract_round_events(
    matches: Iterable[JsonObject],
    *,
    player_puuid: str,
) -> list[JsonObject]:
    """Extract valid round events, excluding terminal surrender placeholders."""
    rows = [
        row
        for match in matches
        for row in event_metrics(match, player_puuid)
    ]
    return rows