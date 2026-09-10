from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable


JsonObject = dict[str, Any]


def classify_economy(loadout_value: Any, round_number: int) -> str:
    if round_number in (1, 13):
        return "pistol"
    if loadout_value is None:
        return "unknown"
    if float(loadout_value) < 2000:
        return "eco_or_force"
    if float(loadout_value) < 3900:
        return "bonus_or_light_buy"
    return "full_buy"


def _target_player(match: JsonObject, player_puuid: str) -> JsonObject | None:
    return next(
        (
            player
            for player in (match.get("players") or {}).get("all_players", [])
            if player.get("puuid") == player_puuid
        ),
        None,
    )


def _round_stat(round_data: JsonObject, player_puuid: str) -> JsonObject | None:
    return next(
        (
            stat
            for stat in round_data.get("player_stats", [])
            if stat.get("player_puuid") == player_puuid
        ),
        None,
    )


def _clutch_row(
    *,
    match: JsonObject,
    round_data: JsonObject,
    round_number: int,
    stat: JsonObject,
    target_team: str,
    player_puuid: str,
) -> JsonObject | None:
    # Kill events use zero-based round indexes in the Henrik payload.
    round_kills = sorted(
        [
            kill
            for kill in match.get("kills", [])
            if kill.get("round") == round_number - 1
        ],
        key=lambda kill: kill.get("kill_time_in_round", 0),
    )
    own_kills = [kill for kill in round_kills if kill.get("killer_puuid") == player_puuid]
    if not own_kills:
        return None

    allied_players = {
        item.get("player_puuid")
        for item in round_data.get("player_stats", [])
        if item.get("player_team") == target_team
    }
    first_kill_time = own_kills[0].get("kill_time_in_round", 0)
    killed_allies_before_first_kill = {
        kill.get("victim_puuid")
        for kill in round_kills
        if kill.get("victim_team") == target_team
        and kill.get("kill_time_in_round", 0) <= first_kill_time
    }
    enemies_alive_before_kill = {
        item.get("player_puuid")
        for item in round_data.get("player_stats", [])
        if item.get("player_team") != target_team
    } - {
        kill.get("victim_puuid")
        for kill in round_kills
        if kill.get("victim_team") != target_team
        and kill.get("kill_time_in_round", 0) < first_kill_time
    }
    if allied_players - killed_allies_before_first_kill != {player_puuid} or not enemies_alive_before_kill:
        return None
    return {
        "match_id": (match.get("metadata") or {}).get("matchid"),
        "round": round_number,
        "enemies_alive_before_kill": len(enemies_alive_before_kill),
        "kills_in_round": len(own_kills),
        "round_won": round_data.get("winning_team") == target_team,
    }


def extract_economy_rows(
    matches: Iterable[JsonObject],
    *,
    player_puuid: str,
) -> tuple[list[JsonObject], list[JsonObject], dict[str, int]]:
    economy_rows: list[JsonObject] = []
    clutch_rows: list[JsonObject] = []
    weapon_counts: Counter[str] = Counter()
    end_type_counts: Counter[str] = Counter()

    for match in matches:
        metadata = match.get("metadata") or {}
        target = _target_player(match, player_puuid)
        if not target:
            continue
        target_team = target.get("team")
        for round_number, round_data in enumerate(match.get("rounds", []), start=1):
            if round_data.get("end_type") == "Surrendered":
                continue
            stat = _round_stat(round_data, player_puuid)
            if not stat:
                continue
            economy = stat.get("economy") or {}
            weapon = economy.get("weapon") or {}
            armor = economy.get("armor") or {}
            loadout_value = economy.get("loadout_value")
            round_kills = [
                kill for kill in match.get("kills", []) if kill.get("round") == round_number - 1
            ]
            row = {
                "match_id": metadata.get("matchid"),
                "round": round_number,
                "map": metadata.get("map"),
                "agent": target.get("character"),
                "round_won": round_data.get("winning_team") == target_team,
                "economy_class": classify_economy(loadout_value, round_number),
                "loadout_value": loadout_value,
                "spent": economy.get("spent"),
                "credits_remaining": economy.get("remaining"),
                "weapon": weapon.get("name"),
                "armor": armor.get("name"),
                "kills": stat.get("kills", 0) or 0,
                "deaths": int(any(kill.get("victim_puuid") == player_puuid for kill in round_kills)),
                "damage": stat.get("damage", 0) or 0,
            }
            economy_rows.append(row)
            if row["weapon"]:
                weapon_counts[str(row["weapon"])] += 1
            end_type_counts[str(round_data.get("end_type", "unknown"))] += 1
            clutch = _clutch_row(
                match=match,
                round_data=round_data,
                round_number=round_number,
                stat=stat,
                target_team=str(target_team),
                player_puuid=player_puuid,
            )
            if clutch:
                clutch_rows.append(clutch)
    return economy_rows, clutch_rows, dict(end_type_counts)


def _round_summary(rows: list[JsonObject]) -> dict[str, Any]:
    rounds = len(rows)
    return {
        "rounds": rounds,
        "round_win_rate": sum(bool(row["round_won"]) for row in rows) / rounds if rounds else None,
        "avg_kills": sum(float(row["kills"]) for row in rows) / rounds if rounds else None,
        "avg_damage": sum(float(row["damage"]) for row in rows) / rounds if rounds else None,
    }


def summarize_economy(
    rows: Iterable[JsonObject],
    clutch_rows: Iterable[JsonObject],
    end_type_counts: dict[str, int],
) -> dict[str, Any]:
    materialized = list(rows)
    grouped: dict[str, list[JsonObject]] = defaultdict(list)
    for row in materialized:
        grouped[str(row.get("economy_class") or "unknown")].append(row)
    pistols = [row for row in materialized if row.get("economy_class") == "pistol"]
    clutches = list(clutch_rows)
    return {
        "sample": {
            "matches": len({row.get("match_id") for row in materialized if row.get("match_id")}),
            "rounds": len(materialized),
        },
        "weapons": Counter(
            str(row["weapon"]) for row in materialized if row.get("weapon")
        ).most_common(),
        "economy": [
            {"economy_class": economy_class, **_round_summary(group)}
            for economy_class, group in sorted(grouped.items())
        ],
        "pistols": _round_summary(pistols),
        "clutch_proxy": {
            "situations": len(clutches),
            "wins": sum(bool(row["round_won"]) for row in clutches),
            "win_rate": (
                sum(bool(row["round_won"]) for row in clutches) / len(clutches)
                if clutches
                else None
            ),
            "definition": "last allied player alive before one or more own kills",
        },
        "round_end_types": end_type_counts,
    }