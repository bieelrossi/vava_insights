from __future__ import annotations

from typing import Any, Iterable


JsonObject = dict[str, Any]


def normalize_player_matches(
    matches: Iterable[JsonObject],
    *,
    player_puuid: str,
) -> list[JsonObject]:
    """Extract the target player's match-level facts from Henrik match payloads."""
    normalized: list[JsonObject] = []
    for match in matches:
        metadata = match.get("metadata") or {}
        players = (match.get("players") or {}).get("all_players") or []
        player = next(
            (candidate for candidate in players if candidate.get("puuid") == player_puuid),
            None,
        )
        if player is None:
            continue

        team = str(player.get("team") or "")
        team_result = (match.get("teams") or {}).get(team.lower()) or {}
        stats = player.get("stats") or {}
        rounds = sum(
            int(((match.get("teams") or {}).get(color) or {}).get("rounds_won") or 0)
            for color in ("red", "blue")
        )
        normalized.append(
            {
                "match_id": metadata.get("matchid"),
                "started_at": metadata.get("game_start_patched"),
                "map": metadata.get("map"),
                "mode": metadata.get("mode"),
                "season": metadata.get("season_id"),
                "agent": player.get("character"),
                "team": team,
                "rounds_played": rounds or metadata.get("rounds_played") or 0,
                "team_rounds_won": team_result.get("rounds_won") or 0,
                "opponent_rounds_won": team_result.get("rounds_lost") or 0,
                "match_won": bool(team_result.get("has_won")),
                "kills": stats.get("kills") or 0,
                "deaths": stats.get("deaths") or 0,
                "assists": stats.get("assists") or 0,
                "score": stats.get("score") or 0,
                "damage_made": player.get("damage_made") or 0,
                "damage_received": player.get("damage_received") or 0,
            }
        )
    return normalized