from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping


JsonObject = dict[str, Any]


def summarize_source_coverage(
    rows: Iterable[JsonObject], *, season_labels: Mapping[str, str] | None = None
) -> JsonObject:
    """Expose the exact match coverage used by the aggregation pipeline.

    This is deliberately a source-coverage audit, not a claim about a
    player's complete Riot or Tracker history.  It makes map totals auditable
    against the acts returned by the configured source.
    """
    materialized = list(rows)
    labels = season_labels or {}
    by_season: dict[str, list[JsonObject]] = defaultdict(list)
    by_map: dict[str, list[JsonObject]] = defaultdict(list)
    by_map_season: dict[tuple[str, str], list[JsonObject]] = defaultdict(list)
    for row in materialized:
        map_name = str(row.get("map") or "Unknown")
        season = str(row.get("season") or "Unknown")
        by_season[season].append(row)
        by_map[map_name].append(row)
        by_map_season[(map_name, season)].append(row)

    return {
        "definitions": {
            "coverage_scope": (
                "Only match details loaded into this run from the Henrik cache or API; "
                "this is not an assertion of external Tracker or complete Riot-history coverage."
            ),
            "map_by_season": "Number of analyzed match IDs for each observed map and season_id.",
        },
        "matches": len(materialized),
        "by_season": [
            {"season_id": season, "season": labels.get(season, season), "matches": len(group)}
            for season, group in sorted(by_season.items())
        ],
        "by_map": [
            {"map": map_name, "matches": len(group)}
            for map_name, group in sorted(by_map.items())
        ],
        "by_map_season": [
            {
                "map": map_name,
                "season_id": season,
                "season": labels.get(season, season),
                "matches": len(group),
            }
            for (map_name, season), group in sorted(by_map_season.items())
        ],
        "limitations": [
            "A mismatch with Tracker, the Riot client, or another export indicates a source-coverage difference until the missing match IDs are supplied.",
            "The pipeline does not invent or interpolate missing matches.",
        ],
    }
