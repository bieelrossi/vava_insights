from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Iterable

from ..features.round_events import infer_initial_sides, side_for_round
from .economy import classify_economy


JsonObject = dict[str, Any]

# Henrik exposes map coordinates in an arbitrary map coordinate system.  The
# threshold is intentionally a configuration constant and is reported in the
# output so conclusions remain reproducible when it is changed.
POSITION_SUPPORT_DISTANCE = 2_000.0
POSITION_CLOSE_DISTANCE = 1_000.0
REFRAG_WINDOW_MS = 5_000
ABILITY_SLOTS = ("c", "q", "e")
ABILITY_EVENT_CONTAINER_KEYS = ("ability_events", "ability_cast_events", "cast_events")
ABILITY_TIMESTAMP_KEYS = ("cast_time_in_round", "time_in_round", "timestamp", "time")
ABILITY_TARGET_KEYS = ("target_puuid", "receiver_puuid", "target", "targets")
ABILITY_EFFECT_KEYS = ("effect", "effect_result", "hit", "hits", "affected_players")


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number >= 0 else None


def _cast_value(casts: JsonObject | None, slot: str) -> float | None:
    if not casts:
        return None
    # Match-level Henrik payloads use x_cast; round-level payloads use x_casts.
    for key in (f"{slot}_cast", f"{slot}_casts"):
        if key in casts:
            return _number(casts.get(key))
    return None


def _event_value(event: JsonObject, keys: tuple[str, ...]) -> Any:
    """Return the first populated schema alias from a cast-level event."""
    for key in keys:
        value = event.get(key)
        if value is not None:
            return value
    return None


def _event_records(value: Any) -> list[JsonObject]:
    """Normalize a possible event container without assuming an API schema."""
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def extract_ability_events(matches: Iterable[JsonObject], *, player_puuid: str) -> list[JsonObject]:
    """Extract cast-level facts only when the source actually exposes them.

    Henrik v2 payloads currently expose aggregate counters and null round
    counters, not cast events. The aliases make the collector forward-compatible
    with cached or future payloads that add documented event records, while an
    empty result remains an explicit absence of evidence.
    """
    events: list[JsonObject] = []
    for match in matches:
        metadata = match.get("metadata") or {}
        for round_index, round_data in enumerate(match.get("rounds") or [], start=1):
            if round_data.get("end_type") == "Surrendered":
                continue
            target_stat = next(
                (item for item in round_data.get("player_stats", []) if item.get("player_puuid") == player_puuid),
                None,
            )
            containers: list[tuple[str, Any, bool]] = [
                (key, round_data.get(key), False) for key in ABILITY_EVENT_CONTAINER_KEYS
            ]
            if target_stat:
                containers.extend(
                    (f"player_stats.{key}", target_stat.get(key), True)
                    for key in ABILITY_EVENT_CONTAINER_KEYS
                )
            for source, container, implicit_target_actor in containers:
                for event in _event_records(container):
                    actor = _event_value(event, ("caster_puuid", "player_puuid", "actor_puuid"))
                    if not implicit_target_actor and actor != player_puuid:
                        continue
                    timestamp = _number(_event_value(event, ABILITY_TIMESTAMP_KEYS))
                    target = _event_value(event, ABILITY_TARGET_KEYS)
                    effect = _event_value(event, ABILITY_EFFECT_KEYS)
                    events.append(
                        {
                            "match_id": metadata.get("matchid"),
                            "round": round_index,
                            "source": source,
                            "ability": _event_value(event, ("ability", "ability_name", "ability_slot", "slot")),
                            "cast_time_in_round_ms": int(timestamp) if timestamp is not None else None,
                            "target": target,
                            "effect": effect,
                        }
                    )
    return events


def summarize_ability_event_detail(matches: Iterable[JsonObject], *, player_puuid: str) -> JsonObject:
    events = extract_ability_events(matches, player_puuid=player_puuid)
    timestamped = [event for event in events if event["cast_time_in_round_ms"] is not None]
    targeted = [event for event in events if event["target"] not in (None, [], {})]
    effects = [event for event in events if event["effect"] not in (None, [], {})]
    return {
        "availability": "available" if events else "unavailable",
        "events": len(events),
        "timestamped_events": len(timestamped),
        "targeted_events": len(targeted),
        "effect_result_events": len(effects),
        "timestamp_coverage": len(timestamped) / len(events) if events else None,
        "target_coverage": len(targeted) / len(events) if events else None,
        "effect_result_coverage": len(effects) / len(events) if events else None,
        "event_sources": sorted({str(event["source"]) for event in events}),
        "events_preview": events[:20],
        "limitations": [
            "Event-level effectiveness is emitted only when cast event records are supplied by the source.",
            "A timestamp and target alone do not prove that a cast caused a later kill, damage event, or round win.",
        ],
    }


def _player_stats(match: JsonObject, player_puuid: str) -> JsonObject | None:
    return next(
        (
            player
            for player in (match.get("players") or {}).get("all_players", [])
            if player.get("puuid") == player_puuid
        ),
        None,
    )


def _rounds_played(match: JsonObject, player_puuid: str) -> int:
    return sum(
        1
        for round_data in match.get("rounds", [])
        if round_data.get("end_type") != "Surrendered"
        and any(stat.get("player_puuid") == player_puuid for stat in round_data.get("player_stats", []))
    )


def _round_outcomes(match: JsonObject, target_team: str | None) -> dict[int, bool]:
    return {
        number: round_data.get("winning_team") == target_team
        for number, round_data in enumerate(match.get("rounds", []), start=1)
        if round_data.get("end_type") != "Surrendered"
    }


def _match_ability_row(match: JsonObject, player_puuid: str) -> JsonObject | None:
    player = _player_stats(match, player_puuid)
    if not player:
        return None
    target_team = player.get("team")
    target_stats = player.get("stats") or {}
    team_result = (match.get("teams") or {}).get(str(target_team).lower()) or {}
    rounds_played = _rounds_played(match, player_puuid)
    if not rounds_played:
        rounds_played = int(team_result.get("rounds_won") or 0) + int(team_result.get("rounds_lost") or 0)

    match_casts = player.get("ability_casts") or {}
    round_casts = {slot: 0.0 for slot in (*ABILITY_SLOTS, "x")}
    round_cast_available = {slot: False for slot in (*ABILITY_SLOTS, "x")}
    for round_data in match.get("rounds", []):
        if round_data.get("end_type") == "Surrendered":
            continue
        stat = next(
            (item for item in round_data.get("player_stats", []) if item.get("player_puuid") == player_puuid),
            None,
        )
        casts = (stat or {}).get("ability_casts") or {}
        for slot in (*ABILITY_SLOTS, "x"):
            value = _cast_value(casts, slot)
            if value is not None:
                round_cast_available[slot] = True
                round_casts[slot] += value

    # Prefer round detail when present; older Henrik payloads only have the
    # match aggregate, which is still useful for usage normalized by rounds.
    casts: dict[str, float | None] = {}
    cast_source: dict[str, str] = {}
    for slot in (*ABILITY_SLOTS, "x"):
        if round_cast_available[slot]:
            casts[slot] = round_casts[slot]
            cast_source[slot] = "round_player_stats"
        else:
            casts[slot] = _cast_value(match_casts, slot)
            cast_source[slot] = "match_player_ability_casts" if casts[slot] is not None else "unavailable"

    non_ultimate = sum(casts[slot] or 0 for slot in ABILITY_SLOTS)
    ultimate = casts["x"]
    total = non_ultimate + (ultimate or 0)
    return {
        "match_id": (match.get("metadata") or {}).get("matchid"),
        "map": (match.get("metadata") or {}).get("map"),
        "agent": player.get("character"),
        "team": target_team,
        "rounds_played": rounds_played,
        "match_won": bool(team_result.get("has_won")),
        "rounds_won": int(team_result.get("rounds_won") or 0),
        "kills": int(target_stats.get("kills") or 0),
        "deaths": int(target_stats.get("deaths") or 0),
        "assists": int(target_stats.get("assists") or 0),
        "damage": int(player.get("damage_made") or 0),
        "casts": casts,
        "cast_source": cast_source,
        "non_ultimate_casts": non_ultimate,
        "ultimate_casts": ultimate,
        "total_casts": total,
        "cast_data_available": any(value is not None for value in casts.values()),
    }


def _aggregate_ability_rows(rows: list[JsonObject]) -> JsonObject:
    matches = len(rows)
    rounds = sum(int(row.get("rounds_played") or 0) for row in rows)
    casts = sum(float(row.get("total_casts") or 0) for row in rows)
    ultimates = sum(float(row.get("ultimate_casts") or 0) for row in rows)
    kills = sum(int(row.get("kills") or 0) for row in rows)
    deaths = sum(int(row.get("deaths") or 0) for row in rows)
    damage = sum(int(row.get("damage") or 0) for row in rows)
    rounds_won = sum(int(row.get("rounds_won") or 0) for row in rows)
    return {
        "matches": matches,
        "rounds": rounds,
        "match_win_rate": sum(bool(row.get("match_won")) for row in rows) / matches if matches else None,
        "round_win_rate": rounds_won / rounds if rounds else None,
        "total_casts": casts,
        "casts_per_round": casts / rounds if rounds else None,
        "total_ultimates": ultimates,
        "ultimates_per_round": ultimates / rounds if rounds else None,
        "kills_per_match": kills / matches if matches else None,
        "deaths_per_match": deaths / matches if matches else None,
        "damage_per_round": damage / rounds if rounds else None,
        "kills_per_100_casts": kills * 100 / casts if casts else None,
        "damage_per_100_casts": damage * 100 / casts if casts else None,
    }


def _lift(with_cast: JsonObject, without_cast: JsonObject, field: str) -> float | None:
    first = with_cast.get(field)
    second = without_cast.get(field)
    return first - second if first is not None and second is not None else None


def summarize_ability_usage(matches: Iterable[JsonObject], *, player_puuid: str) -> JsonObject:
    materialized = list(matches)
    event_detail = summarize_ability_event_detail(materialized, player_puuid=player_puuid)
    rows = [
        row
        for match in materialized
        for row in [_match_ability_row(match, player_puuid)]
        if row and row["cast_data_available"]
    ]
    by_slot: dict[str, JsonObject] = {}
    for slot in (*ABILITY_SLOTS, "x"):
        with_cast = _aggregate_ability_rows(
            [row for row in rows if (row["casts"].get(slot) or 0) > 0]
        )
        without_cast = _aggregate_ability_rows(
            [row for row in rows if (row["casts"].get(slot) or 0) == 0]
        )
        by_slot[slot] = {
            "with_cast": with_cast,
            "without_cast": without_cast,
            "match_win_rate_lift": _lift(with_cast, without_cast, "match_win_rate"),
            "round_win_rate_lift": _lift(with_cast, without_cast, "round_win_rate"),
        }

    any_cast = [row for row in rows if row["total_casts"] > 0]
    no_cast = [row for row in rows if row["total_casts"] == 0]
    utility = [row for row in rows if row["non_ultimate_casts"] > 0]
    no_utility = [row for row in rows if row["non_ultimate_casts"] == 0]
    ultimate = [row for row in rows if (row["ultimate_casts"] or 0) > 0]
    no_ultimate = [row for row in rows if (row["ultimate_casts"] or 0) == 0]
    return {
        "definitions": {
            "ability_slots": "C/Q/E are regular abilities; X is ultimate.",
            "effectiveness": "Cast-level efficacy requires source-provided cast events with timestamp and target/effect fields; otherwise only aggregate usage is reported.",
            "casts_per_round": "Total casts divided by valid non-surrender rounds.",
            "round_ability_source": "Uses round player_stats when populated, otherwise match player ability_casts.",
        },
        "coverage": {
            "matches_with_cast_data": len(rows),
            "matches_without_cast_data": sum(
                1
                for match in materialized
                if _match_ability_row(match, player_puuid)
                and not _match_ability_row(match, player_puuid)["cast_data_available"]
            ),
        },
        "overall": _aggregate_ability_rows(rows),
        "by_slot": by_slot,
        "usage_context": {
            "any_ability": _aggregate_ability_rows(any_cast),
            "no_ability": _aggregate_ability_rows(no_cast),
            "regular_ability": _aggregate_ability_rows(utility),
            "no_regular_ability": _aggregate_ability_rows(no_utility),
            "ultimate": _aggregate_ability_rows(ultimate),
            "no_ultimate": _aggregate_ability_rows(no_ultimate),
            "ultimate_match_win_rate_lift": _lift(
                _aggregate_ability_rows(ultimate), _aggregate_ability_rows(no_ultimate), "match_win_rate"
            ),
            "ultimate_round_win_rate_lift": _lift(
                _aggregate_ability_rows(ultimate), _aggregate_ability_rows(no_ultimate), "round_win_rate"
            ),
        },
        "match_rows": rows,
        "event_detail": event_detail,
        "limitations": [
            "When event_detail.availability is unavailable, the payload did not expose cast-level timestamps or target/effect results, so a cast cannot be linked deterministically to a specific kill.",
            "Usage groups are descriptive and confounded by agent, map, economy, opponent and match length.",
            "A zero ultimate count means no recorded cast, not necessarily that the player had no ultimate available.",
        ],
    }


def _location_map(kill: JsonObject) -> dict[str, JsonObject]:
    return {
        str(item.get("player_puuid")): item
        for item in kill.get("player_locations_on_kill", [])
        if item.get("player_puuid") and item.get("location")
    }


def _distance(first: JsonObject | None, second: JsonObject | None) -> float | None:
    if not first or not second or first.get("x") is None or first.get("y") is None:
        return None
    if second.get("x") is None or second.get("y") is None:
        return None
    return math.hypot(float(first["x"]) - float(second["x"]), float(first["y"]) - float(second["y"]))


def _position_facts(
    kill: JsonObject,
    *,
    player_puuid: str,
    player_team: str | None,
    event_type: str,
) -> JsonObject:
    locations = _location_map(kill)
    own = locations.get(player_puuid)
    if not own and event_type == "death" and kill.get("victim_death_location"):
        own = {"location": kill["victim_death_location"]}
    own_location = (own or {}).get("location")
    teammate_distances = sorted(
        (distance, puuid)
        for puuid, item in locations.items()
        if puuid != player_puuid and item.get("player_team") == player_team
        for distance in [_distance(own_location, item.get("location"))]
        if distance is not None
    )
    nearest = teammate_distances[0][0] if teammate_distances else None
    nearest_puuid = teammate_distances[0][1] if teammate_distances else None
    support_puuids = [puuid for distance, puuid in teammate_distances if distance <= POSITION_SUPPORT_DISTANCE]
    close_puuids = [puuid for distance, puuid in teammate_distances if distance <= POSITION_CLOSE_DISTANCE]
    if nearest is None:
        context = "unavailable"
    elif nearest <= POSITION_SUPPORT_DISTANCE:
        context = "supported"
    else:
        context = "isolated"
    return {
        "position_available": nearest is not None,
        "position": own_location,
        "nearest_teammate_distance": nearest,
        "nearest_teammate_puuid": nearest_puuid,
        "supporting_teammate_puuids": support_puuids,
        "close_teammate_puuids": close_puuids,
        "teammates_within_close_distance": sum(distance <= POSITION_CLOSE_DISTANCE for distance, _ in teammate_distances),
        "teammates_within_support_distance": sum(distance <= POSITION_SUPPORT_DISTANCE for distance, _ in teammate_distances),
        "position_context": context,
    }


def _time(kill: JsonObject) -> int | None:
    value = _number(kill.get("kill_time_in_round"))
    return int(value) if value is not None else None


def _same_round_kills(match: JsonObject) -> dict[int, list[JsonObject]]:
    grouped: dict[int, list[JsonObject]] = defaultdict(list)
    for index, kill in enumerate(match.get("kills") or []):
        row = dict(kill)
        row["_event_index"] = index
        grouped[int(kill.get("round") or 0)].append(row)
    for kills in grouped.values():
        kills.sort(key=lambda item: (_time(item) is None, _time(item) or 0, item["_event_index"]))
    return grouped


def _round_won(outcomes: dict[int, bool], kill: JsonObject) -> bool | None:
    return outcomes.get(int(kill.get("round") or 0) + 1)


def _event_row(
    *,
    kill: JsonObject,
    event_type: str,
    player_puuid: str,
    player_team: str,
    outcomes: dict[int, bool],
    position: JsonObject,
    map_name: str,
    agent: str,
    side: str | None,
    economy_class: str | None,
) -> JsonObject:
    return {
        "event_type": event_type,
        "round": int(kill.get("round") or 0) + 1,
        "event_time_in_round_ms": _time(kill),
        "map": map_name,
        "agent": agent,
        "side": side,
        "economy_class": economy_class,
        "position_context": position["position_context"],
        "position_available": position["position_available"],
        "position": position["position"],
        "nearest_teammate_distance": position["nearest_teammate_distance"],
        "nearest_teammate_puuid": position["nearest_teammate_puuid"],
        "_supporting_teammate_puuids": position["supporting_teammate_puuids"],
        "_close_teammate_puuids": position["close_teammate_puuids"],
        "teammates_within_close_distance": position["teammates_within_close_distance"],
        "teammates_within_support_distance": position["teammates_within_support_distance"],
        "round_won": _round_won(outcomes, kill),
        "weapon": kill.get("damage_weapon_name"),
        "opponent_puuid": kill.get("victim_puuid") if event_type == "kill" else kill.get("killer_puuid"),
        "opponent_team": kill.get("victim_team") if event_type == "kill" else kill.get("killer_team"),
    }


def _find_refrag(
    *,
    events: list[JsonObject],
    index: int,
    event_type: str,
    player_puuid: str,
    player_team: str,
) -> tuple[bool, bool, int | None]:
    """Return (opportunity, exact_refrag, delta_ms) for one target event."""
    current = events[index]
    current_time = _time(current)
    if current_time is None:
        return False, False, None
    if event_type == "kill":
        prior = [
            event
            for event in events[:index]
            if event.get("victim_team") == player_team
            and event.get("victim_puuid") != player_puuid
            and event.get("killer_team") != player_team
            and _time(event) is not None
            and 0 < current_time - _time(event) <= REFRAG_WINDOW_MS
        ]
        if not prior:
            return False, False, None
        candidate = prior[-1]
        delta = current_time - _time(candidate)
        return True, candidate.get("killer_puuid") == current.get("victim_puuid"), delta

    following = [
        event
        for event in events[index + 1 :]
        if event.get("killer_team") == player_team
        and event.get("victim_team") != player_team
        and _time(event) is not None
        and 0 < _time(event) - current_time <= REFRAG_WINDOW_MS
    ]
    if not following:
        return False, False, None
    candidate = following[0]
    delta = _time(candidate) - current_time
    return True, candidate.get("victim_puuid") == current.get("killer_puuid"), delta


def _round_group_rate(events: list[JsonObject], *, field: str, loss: bool = False) -> float | None:
    round_outcomes: dict[tuple[int, int], bool] = {}
    for event in events:
        if event.get(field) and event.get("round_won") is not None:
            round_outcomes[(int(event["match_round"][0]), int(event["match_round"][1]))] = bool(event["round_won"])
    if not round_outcomes:
        return None
    values = [not value if loss else value for value in round_outcomes.values()]
    return sum(values) / len(values)


def _position_summary(events: list[JsonObject], context: str) -> JsonObject:
    group = [event for event in events if event.get("position_context") == context]
    rounds: dict[tuple[str, int], bool] = {}
    for event in group:
        if event.get("round_won") is not None:
            rounds[(str(event.get("match_id")), int(event["round"]))] = bool(event["round_won"])
    return {
        "events": len(group),
        "event_share": len(group) / len(events) if events else None,
        "rounds": len(rounds),
        "round_win_rate": sum(rounds.values()) / len(rounds) if rounds else None,
        "round_loss_rate": sum(not value for value in rounds.values()) / len(rounds) if rounds else None,
        "avg_nearest_teammate_distance": (
            sum(float(event["nearest_teammate_distance"]) for event in group if event.get("nearest_teammate_distance") is not None)
            / sum(event.get("nearest_teammate_distance") is not None for event in group)
            if any(event.get("nearest_teammate_distance") is not None for event in group)
            else None
        ),
    }


def _refrag_summary(events: list[JsonObject], event_type: str) -> JsonObject:
    group = [event for event in events if event.get("event_type") == event_type]
    opportunities = sum(bool(event.get("refrag_opportunity")) for event in group)
    exact = sum(bool(event.get("exact_refrag")) for event in group)
    return {
        "events": len(group),
        "opportunities": opportunities,
        "exact_refrags": exact,
        "rate": exact / opportunities if opportunities else None,
    }


def _context_summary(events: list[JsonObject]) -> JsonObject:
    available = [event for event in events if event.get("position_available")]
    kills = [event for event in available if event.get("event_type") == "kill"]
    deaths = [event for event in available if event.get("event_type") == "death"]
    matches = len({event.get("match_id") for event in events if event.get("match_id")})
    return {
        "events": len(events),
        "matches": matches,
        "evidence": "supported" if matches >= 5 else "weak_evidence",
        "position_available_events": len(available),
        "position_coverage": len(available) / len(events) if events else None,
        "kills": {context: _position_summary(kills, context) for context in ("isolated", "supported")},
        "deaths": {context: _position_summary(deaths, context) for context in ("isolated", "supported")},
        "refrag_given": _refrag_summary(events, "kill"),
        "refrag_received": _refrag_summary(events, "death"),
    }


def _split_context(events: list[JsonObject], field: str) -> list[JsonObject]:
    groups: dict[str, list[JsonObject]] = defaultdict(list)
    for event in events:
        groups[str(event.get(field) or "unknown")].append(event)
    return [
        {field: value, **_context_summary(group)}
        for value, group in sorted(groups.items())
    ]


def summarize_position_and_refrags(
    matches: Iterable[JsonObject], *, player_puuid: str
) -> JsonObject:
    events: list[JsonObject] = []
    for match in matches:
        player = _player_stats(match, player_puuid)
        if not player:
            continue
        team = player.get("team")
        metadata = match.get("metadata") or {}
        map_name = metadata.get("map") or "Unknown"
        agent = player.get("character") or "Unknown"
        outcomes = _round_outcomes(match, team)
        initial_sides = infer_initial_sides(match.get("rounds") or [])
        round_data_by_number = {
            number: round_data
            for number, round_data in enumerate(match.get("rounds") or [], start=1)
            if round_data.get("end_type") != "Surrendered"
        }
        teammate_labels = {
            str(item.get("puuid")): f"{item.get('name') or 'Unknown'}#{item.get('tag')}"
            if item.get("tag")
            else str(item.get("name") or "Unknown")
            for item in (match.get("players") or {}).get("all_players", [])
            if item.get("puuid") and item.get("puuid") != player_puuid
        }
        for round_kills in _same_round_kills(match).values():
            for index, kill in enumerate(round_kills):
                event_type: str | None = None
                # A self-elimination can contain the target in both fields.
                # It is a death, not a kill credited to the target.
                if kill.get("victim_puuid") == player_puuid:
                    event_type = "death"
                elif kill.get("killer_puuid") == player_puuid:
                    event_type = "kill"
                if not event_type:
                    continue
                round_number = int(kill.get("round") or 0) + 1
                round_data = round_data_by_number.get(round_number) or {}
                target_stat = next(
                    (item for item in round_data.get("player_stats", []) if item.get("player_puuid") == player_puuid),
                    None,
                )
                target_economy = (target_stat or {}).get("economy") or {}
                position = _position_facts(
                    kill,
                    player_puuid=player_puuid,
                    player_team=team,
                    event_type=event_type,
                )
                event = _event_row(
                    kill=kill,
                    event_type=event_type,
                    player_puuid=player_puuid,
                    player_team=team,
                    outcomes=outcomes,
                    position=position,
                    map_name=map_name,
                    agent=agent,
                    side=side_for_round(initial_sides, team, round_number),
                    economy_class=classify_economy(target_economy.get("loadout_value"), round_number),
                )
                opportunity, exact, delta = _find_refrag(
                    events=round_kills,
                    index=index,
                    event_type=event_type,
                    player_puuid=player_puuid,
                    player_team=team,
                )
                event.update(
                    {
                        "match_id": (match.get("metadata") or {}).get("matchid"),
                        "match_round": ((match.get("metadata") or {}).get("matchid"), event["round"]),
                        "refrag_opportunity": opportunity,
                        "exact_refrag": exact,
                        "refrag_delta_ms": delta,
                        "assisted_kill": bool(kill.get("assistants")) if event_type == "kill" else None,
                        "_teammate_labels": teammate_labels,
                    }
                )
                events.append(event)

    kills = [event for event in events if event["event_type"] == "kill"]
    deaths = [event for event in events if event["event_type"] == "death"]
    position_events = [event for event in events if event["position_available"]]
    kill_position = {context: _position_summary([event for event in kills if event["position_available"]], context) for context in ("isolated", "supported")}
    death_position = {context: _position_summary([event for event in deaths if event["position_available"]], context) for context in ("isolated", "supported")}
    given_opportunities = sum(event["refrag_opportunity"] for event in kills)
    received_opportunities = sum(event["refrag_opportunity"] for event in deaths)
    given_exact = sum(event["exact_refrag"] for event in kills)
    received_exact = sum(event["exact_refrag"] for event in deaths)
    position_available = [event for event in events if event["position_available"]]
    teammate_groups: dict[str, list[JsonObject]] = defaultdict(list)
    map_teammate_groups: dict[tuple[str, str], list[JsonObject]] = defaultdict(list)
    for event in position_available:
        labels = event.get("_teammate_labels") or {}
        for teammate_puuid in event.get("_supporting_teammate_puuids") or []:
            teammate_groups[teammate_puuid].append(event)
            map_teammate_groups[(str(event.get("map") or "Unknown"), teammate_puuid)].append(event)
    teammate_proximity = []
    for teammate_puuid, group in sorted(teammate_groups.items(), key=lambda item: (-len(item[1]), item[0])):
        labels = group[0].get("_teammate_labels") or {}
        nearest = [event for event in group if event.get("nearest_teammate_puuid") == teammate_puuid]
        rounds = {
            (str(event.get("match_id")), int(event.get("round"))): bool(event.get("round_won"))
            for event in group
            if event.get("round_won") is not None
        }
        teammate_proximity.append({
            "teammate_puuid": teammate_puuid,
            "teammate": labels.get(teammate_puuid, "Unknown"),
            "support_events": len(group),
            "nearest_events": len(nearest),
            "kills": sum(event.get("event_type") == "kill" for event in group),
            "deaths": sum(event.get("event_type") == "death" for event in group),
            "rounds": len(rounds),
            "round_win_rate": sum(rounds.values()) / len(rounds) if rounds else None,
            "avg_nearest_distance": (
                sum(float(event["nearest_teammate_distance"]) for event in nearest if event.get("nearest_teammate_distance") is not None)
                / sum(event.get("nearest_teammate_distance") is not None for event in nearest)
                if any(event.get("nearest_teammate_distance") is not None for event in nearest)
                else None
            ),
            "evidence": "supported" if len(rounds) >= 5 else "weak_evidence",
            "evidence_basis": "supported_position_snapshot",
        })
    map_teammate_proximity = []
    for (map_name, teammate_puuid), group in sorted(map_teammate_groups.items()):
        labels = group[0].get("_teammate_labels") or {}
        map_teammate_proximity.append({
            "map": map_name,
            "teammate_puuid": teammate_puuid,
            "teammate": labels.get(teammate_puuid, "Unknown"),
            **_context_summary(group),
            "evidence_basis": "supported_position_snapshot",
        })

    return {
        "definitions": {
            "refrag_window_ms": REFRAG_WINDOW_MS,
            "refrag_given": "A teammate dies and the target kills that same enemy within the window.",
            "refrag_received": "The target dies and a teammate kills that same enemy within the window.",
            "position_supported": f"At least one teammate is within {POSITION_SUPPORT_DISTANCE:.0f} map-coordinate units at the event.",
            "position_isolated": f"No teammate is within {POSITION_SUPPORT_DISTANCE:.0f} map-coordinate units at the event.",
            "position_close": f"At least one teammate is within {POSITION_CLOSE_DISTANCE:.0f} map-coordinate units; exposed as a secondary count.",
            "position_distance": "Euclidean distance from the target to the nearest teammate in player_locations_on_kill.",
        },
        "coverage": {
            "target_kills": len(kills),
            "target_deaths": len(deaths),
            "position_available_events": len(position_events),
            "position_coverage": len(position_events) / len(events) if events else None,
        },
        "refrag": {
            "given": {
                "target_kills": len(kills),
                "opportunities": given_opportunities,
                "exact_refrags": given_exact,
                "rate": given_exact / given_opportunities if given_opportunities else None,
            },
            "received": {
                "target_deaths": len(deaths),
                "opportunities": received_opportunities,
                "exact_refrags": received_exact,
                "rate": received_exact / received_opportunities if received_opportunities else None,
            },
        },
        "position": {
            "kills": kill_position,
            "deaths": death_position,
            "solo_vs_supported_kill_round_win_rate_delta": (
                kill_position["isolated"]["round_win_rate"] - kill_position["supported"]["round_win_rate"]
                if kill_position["isolated"]["round_win_rate"] is not None and kill_position["supported"]["round_win_rate"] is not None
                else None
            ),
            "isolated_vs_supported_death_round_loss_rate_delta": (
                death_position["isolated"]["round_loss_rate"] - death_position["supported"]["round_loss_rate"]
                if death_position["isolated"]["round_loss_rate"] is not None and death_position["supported"]["round_loss_rate"] is not None
                else None
            ),
        },
        "by_map": _split_context(events, "map"),
        "by_agent": _split_context(events, "agent"),
        "by_side": _split_context(events, "side"),
        "by_economy": _split_context(events, "economy_class"),
        "by_teammate": teammate_proximity,
        "by_map_teammate": map_teammate_proximity,
        "events": [
            {key: value for key, value in event.items() if not key.startswith("_")}
            for event in events
        ],
        "limitations": [
            "Position is a snapshot at the kill event, not a full movement trajectory or line-of-sight model.",
            "A supported kill means a teammate was geographically near; it does not prove visual contact, tradeability or assistance.",
            "The comparison between isolated/supported and teammate-specific proximity is descriptive; round result is not causal evidence.",
            "Map, agent, side and economy splits use the same event snapshot and require their own sample-size checks.",
        ],
    }


def summarize_advanced_impact(matches: Iterable[JsonObject], *, player_puuid: str) -> JsonObject:
    materialized = list(matches)
    ability = summarize_ability_usage(materialized, player_puuid=player_puuid)
    interaction = summarize_position_and_refrags(materialized, player_puuid=player_puuid)
    return {
        "ability_usage": ability,
        "position_and_refrags": interaction,
    }
