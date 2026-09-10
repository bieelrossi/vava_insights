from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


def player_slug(player: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", player.lower()).strip("-") or "player"


def default_app_data_root() -> Path:
    app_data = os.environ.get("APPDATA")
    if app_data:
        return Path(app_data) / "vava_insights"
    return Path.home() / "AppData" / "Roaming" / "vava_insights"


@dataclass(frozen=True)
class PlayerStorage:
    """Filesystem locations for one player's private cache and derived outputs."""

    project_root: Path
    player_slug: str
    app_data_root: Path | None = None

    @property
    def private_root(self) -> Path:
        root = self.app_data_root or default_app_data_root()
        return root / "players" / self.player_slug

    @property
    def raw_dir(self) -> Path:
        return self.private_root / "raw"

    @property
    def processed_dir(self) -> Path:
        return self.project_root / "data" / "processed" / self.player_slug

    @property
    def curated_dir(self) -> Path:
        return self.project_root / "data" / "curated" / self.player_slug

    @property
    def reports_dir(self) -> Path:
        return self.project_root / "reports" / self.player_slug

    @property
    def stats_path(self) -> Path:
        return self.processed_dir / "stats.json"

    @property
    def manifest_path(self) -> Path:
        return self.processed_dir / "analysis_manifest.json"

    @property
    def prompt_path(self) -> Path:
        return self.reports_dir / "prompt.md"

    def ensure_directories(self) -> None:
        for directory in (self.raw_dir, self.processed_dir, self.curated_dir, self.reports_dir):
            directory.mkdir(parents=True, exist_ok=True)