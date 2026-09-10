from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def slugify(player: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", player.lower()).strip("-") or "player"


def write_agent_package(
    *,
    player: str,
    statistics: dict[str, Any],
    reports_dir: Path,
    stats_dir: Path,
) -> tuple[Path, Path]:
    """Write the structured input and prompt consumed by the Copilot agent."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    stats_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(player)
    stats_path = stats_dir / "stats.json"
    prompt_path = reports_dir / "prompt.md"
    stats_path.write_text(
        json.dumps(statistics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    prompt_path.write_text(
        "\n".join(
            [
                f"# Relatório de performance: {player}",
                "",
                "Use o agente `.github/agents/valorant-performance-analyst.agent.md`.",
                "Procure automaticamente o `stats.json` correspondente em `data/processed/*/stats.json` e interprete exclusivamente esse pacote.",
                "Gere o relatório final em Markdown em `reports/<jogador>/`, respeitando as limitações e a estrutura definidas pelo agente.",
                "",
                f"Fonte dos dados: `{stats_path.name}`",
            ]
        ),
        encoding="utf-8",
    )
    return stats_path, prompt_path