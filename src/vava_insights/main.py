from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if __package__:
    from .pipeline import PlayerIdentifier, run_player_analysis
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from vava_insights.pipeline import PlayerIdentifier, run_player_analysis


BRAZIL_TIMEZONE = timezone(timedelta(hours=-3), name="BRT")


def log_stage(message: str) -> None:
    timestamp = datetime.now(BRAZIL_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp} BRT] {message}", flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compile Valorant player statistics for the performance analyst agent.")
    parser.add_argument("player", nargs="?", help="Player name or identifier in the format name#tag")
    parser.add_argument("--affinity", default="br", help="Henrik API affinity, default: br")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--max-matches", type=int, default=100)
    group.add_argument(
        "--all-history",
        action="store_true",
        help="Analyze every cached match or every match available through pagination.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Ignore an existing stats.json and regenerate the analysis.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    log_stage("[1/4] Lendo parametros da analise...")
    player_value = args.player or input("Jogador (nome#codigo): ").strip()
    player = PlayerIdentifier.parse(player_value)
    project_root = Path(__file__).resolve().parents[2]
    scope = "todo o historico" if args.all_history else f"ate {args.max_matches} partidas"
    log_stage(f"[2/4] Jogador: {player.label}")
    log_stage(f"[3/4] Iniciando analise ({scope})...")
    stats_path, prompt_path = run_player_analysis(
        player,
        project_root=project_root,
        affinity=args.affinity,
        max_matches=None if args.all_history else args.max_matches,
        refresh=args.refresh,
    )
    log_stage("[4/4] Analise concluida.")
    print(f"Estatisticas: {stats_path}")
    print(f"Prompt para o agente: {prompt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())