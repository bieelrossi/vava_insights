from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ingestion.history import HenrikHistoryClient
from .ingestion.storage import PlayerStorage, player_slug
from .config import load_dotenv
from .insights.deterministic import build_deterministic_insights
from .features.round_events import extract_round_events
from .metrics.baseline import summarize_baseline
from .metrics.economy import extract_economy_rows, summarize_economy
from .metrics.impact import summarize_impact
from .metrics.advanced_impact import summarize_advanced_impact
from .metrics.composition import summarize_composition
from .metrics.contextual import summarize_contextual_splits
from .metrics.squad import summarize_squad
from .metrics.source_coverage import summarize_source_coverage
from .normalization.matches import normalize_player_matches
from .reporting.agent_bridge import write_agent_package


@dataclass(frozen=True)
class PlayerIdentifier:
    name: str
    tag: str | None = None

    @classmethod
    def parse(cls, value: str) -> "PlayerIdentifier":
        name, separator, tag = value.partition("#")
        if not name.strip():
            raise ValueError("player name cannot be empty")
        if separator and not tag.strip():
            raise ValueError("player tag cannot be empty")
        return cls(name=name.strip(), tag=tag.strip() if separator else None)

    @property
    def label(self) -> str:
        return f"{self.name}#{self.tag}" if self.tag else self.name


def _resolve_existing_player(
    player: PlayerIdentifier,
    *,
    project_root: Path,
) -> tuple[PlayerIdentifier, PlayerStorage | None]:
    if player.tag:
        return player, None
    candidates: list[tuple[PlayerIdentifier, PlayerStorage]] = []
    processed_root = project_root / "data" / "processed"
    for manifest_path in processed_root.glob("*/analysis_manifest.json"):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            candidate = PlayerIdentifier.parse(str(manifest.get("player", "")))
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if candidate.name.casefold() == player.name.casefold() and candidate.tag:
            candidates.append(
                (
                    candidate,
                    PlayerStorage(project_root=project_root, player_slug=manifest_path.parent.name),
                )
            )
    if not candidates:
        return player, None
    if len(candidates) > 1:
        raise ValueError(f"more than one analyzed player matches '{player.name}'; use name#tag")
    return candidates[0]


def _load_cached_matches(raw_matches_dir: Path, *, name: str, tag: str) -> tuple[str | None, list[dict[str, Any]]]:
    matches: list[dict[str, Any]] = []
    player_puuid: str | None = None
    for path in sorted(raw_matches_dir.glob("*.json")):
        match = json.loads(path.read_text(encoding="utf-8"))
        players = (match.get("players") or {}).get("all_players") or []
        player = next(
            (
                candidate
                for candidate in players
                if str(candidate.get("name") or "").casefold() == name.casefold()
                and str(candidate.get("tag") or "").casefold() == tag.casefold()
            ),
            None,
        )
        if player:
            player_puuid = str(player["puuid"])
            matches.append(match)
    return player_puuid, matches


def _match_id(match: dict[str, Any]) -> str | None:
    metadata = match.get("metadata") or {}
    meta = match.get("meta") or {}
    match_id = metadata.get("matchid") or meta.get("id")
    return str(match_id) if match_id else None


def _season_labels_from_inventory(raw_dir: Path) -> dict[str, str]:
    """Use stored-list act labels when present; detail payloads only carry IDs."""
    inventory_path = raw_dir / "history" / "inventory.json"
    if not inventory_path.exists():
        return {}
    try:
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    labels: dict[str, str] = {}
    for item in inventory:
        season = (item.get("meta") or {}).get("season") or {}
        season_id = season.get("id")
        label = season.get("short") or season_id
        if season_id and label:
            labels[str(season_id)] = str(label)
    return labels


def _cache_matches_scope(storage: PlayerStorage, max_matches: int | None) -> bool:
    if not storage.stats_path.exists() or not storage.prompt_path.exists():
        return False
    if not storage.manifest_path.exists():
        return False
    try:
        manifest = json.loads(storage.manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    expected_scope = "all_history" if max_matches is None else f"max_matches:{max_matches}"
    return manifest.get("scope") == expected_scope


def run_player_analysis(
    player: PlayerIdentifier,
    *,
    project_root: Path,
    affinity: str = "br",
    max_matches: int | None = 100,
    refresh: bool = False,
) -> tuple[Path, Path]:
    load_dotenv(project_root)
    player, existing_storage = _resolve_existing_player(player, project_root=project_root)
    storage = existing_storage or PlayerStorage(project_root=project_root, player_slug=player_slug(player.label))
    storage.ensure_directories()
    raw_matches_dir = storage.raw_dir / "matches"
    puuid, matches = _load_cached_matches(raw_matches_dir, name=player.name, tag=player.tag)
    history_checked = False
    downloaded_matches = 0

    if max_matches is None and player.tag:
        api_key = os.environ.get("HENRIK_API_KEY")
        if api_key:
            client = HenrikHistoryClient(api_key, raw_dir=storage.raw_dir)
            puuid = client.resolve_puuid(name=player.name, tag=player.tag)
            inventory = client.discover_stored_matches(
                affinity=affinity,
                puuid=puuid,
                max_pages=None,
            )
            cached_match_ids = {
                str(match_id)
                for match_id in (_match_id(match) for match in matches)
                if match_id
            }
            for item in inventory:
                match_id = item.get("meta", {}).get("id")
                if not match_id or str(match_id) in cached_match_ids:
                    continue
                matches.append(client.fetch_match_details(str(match_id)))
                cached_match_ids.add(str(match_id))
                downloaded_matches += 1
            history_checked = True

    if _cache_matches_scope(storage, max_matches) and not refresh and downloaded_matches == 0:
        return storage.stats_path, storage.prompt_path

    if not matches and not history_checked:
        if not player.tag:
            raise RuntimeError(
                f"Player '{player.name}' has not been analyzed yet. Use name#tag for the first API collection."
            )
        api_key = os.environ.get("HENRIK_API_KEY")
        if not api_key:
            raise RuntimeError(
                f"No cached matches found for {player.label}. Set HENRIK_API_KEY to collect new data."
            )
        client = HenrikHistoryClient(api_key, raw_dir=storage.raw_dir)
        puuid = client.resolve_puuid(name=player.name, tag=player.tag)
        inventory = client.discover_stored_matches(
            affinity=affinity,
            puuid=puuid,
            max_pages=None if max_matches is None else max(1, (max_matches + 19) // 20),
        )
        for item in inventory[:max_matches]:
            match_id = item.get("meta", {}).get("id")
            if match_id:
                matches.append(client.fetch_match_details(str(match_id)))

    if not puuid:
        raise RuntimeError(f"Could not resolve PUUID for {player.label}")
    selected_matches = matches if max_matches is None else matches[:max_matches]
    rows = normalize_player_matches(selected_matches, player_puuid=puuid)
    if not rows:
        raise RuntimeError(f"No usable match data found for {player.label}")
    baseline = summarize_baseline(rows)
    round_events = extract_round_events(selected_matches, player_puuid=puuid)
    economy_rows, clutch_rows, end_type_counts = extract_economy_rows(
        selected_matches, player_puuid=puuid
    )
    statistics = {
        "player": {"name": player.name, "tag": player.tag, "label": player.label, "puuid": puuid},
        "sample": {"matches": len(rows), "source": "cached_matches_or_henrik_api"},
        "baseline": baseline,
        "source_coverage": summarize_source_coverage(
            rows, season_labels=_season_labels_from_inventory(storage.raw_dir)
        ),
        "deterministic_insights": build_deterministic_insights(baseline),
        "impact": summarize_impact(round_events),
        "round_events": round_events,
        "advanced_impact": summarize_advanced_impact(selected_matches, player_puuid=puuid),
        "economy": summarize_economy(economy_rows, clutch_rows, end_type_counts),
        "economy_rounds": economy_rows,
        "composition": summarize_composition(selected_matches, player_puuid=puuid),
        "squad": summarize_squad(selected_matches, player_puuid=puuid),
        "contextual_splits": summarize_contextual_splits(selected_matches, player_puuid=puuid),
        "match_rows": rows,
        "not_yet_supported": [
            "Ability effectiveness is unavailable unless the source supplies cast-level timestamps and targets/effect results; the ability event-detail audit records the observed coverage.",
            "Position metrics use event snapshots; continuous movement, line of sight and communication quality are not observable.",
        ],
    }
    output_paths = write_agent_package(
        player=player.label,
        statistics=statistics,
        reports_dir=storage.reports_dir,
        stats_dir=storage.processed_dir,
    )
    storage.manifest_path.write_text(
        json.dumps(
            {
                "player": player.label,
                "puuid": puuid,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "matches_analyzed": len(rows),
                "scope": "all_history" if max_matches is None else f"max_matches:{max_matches}",
                "source": "cached_matches_or_henrik_api",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return output_paths
