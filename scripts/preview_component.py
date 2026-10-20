"""Run one application component independently on local NBA or practice inputs."""

import argparse
import json

import pandas as pd

from src import analytics, charts, data
from src.data import ROOT


def save_result(result, name, metadata, stage="processed"):
    if result is None:
        print("UNFINISHED: replace the TODO return value in your assigned function.")
        return
    output = ROOT / "data" / stage / "week1"
    output.mkdir(parents=True, exist_ok=True)
    if isinstance(result, pd.DataFrame):
        path = output / f"{name}.csv"
        result.to_csv(path, index=False)
        print(result.to_string(index=False))
    else:
        path = output / f"{name}.html"
        result.add_annotation(
            text=f"{metadata['source']} | {metadata['season']} | {metadata['season_type']}",
            x=0, y=-0.2, xref="paper", yref="paper", showarrow=False, xanchor="left",
        )
        result.update_layout(margin={"b": 100})
        result.write_html(path, include_plotlyjs=True)
    path.with_suffix(".meta.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Local preview: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("component", choices=["source-audit", "clean-players", "clean-teams",
                                            "player-percentiles", "team-ratings", "player-chart", "team-chart"])
    parser.add_argument("--demo", action="store_true", help="Use explicitly fictional practice inputs")
    parser.add_argument("--id", type=int, help="Player/team ID to highlight; otherwise use the first record")
    args = parser.parse_args()
    kind = ("ratings" if args.component in ("team-ratings", "team-chart") else
            "teams" if args.component == "clean-teams" else "players")
    try:
        raw, metadata = data.load_snapshot(kind, args.demo)
    except ValueError as exc:
        parser.exit(1, f"{exc}\n")
    frame = data.component_table(raw, metadata)
    print(f"{metadata['source']} | {metadata['season']} | {metadata['season_type']}")
    if args.component == "source-audit":
        print("Request provenance:", metadata)
        result = data.audit_source(raw.copy())
    elif args.component == "clean-players":
        result = data.clean_players(raw.copy(), metadata["season"])
    elif args.component == "clean-teams":
        result = data.clean_teams(raw.copy(), metadata["season"])
    elif args.component == "player-percentiles":
        result = analytics.calculate_percentiles(frame.copy())
    elif args.component == "team-ratings":
        result = analytics.prepare_ratings(frame.copy())
    else:
        id_column = "PLAYER_ID" if kind == "players" else "TEAM_ID"
        selected = args.id if args.id is not None else frame.iloc[0][id_column]
        function = charts.player_scoring_distribution if kind == "players" else charts.team_efficiency
        result = function(frame.copy(), selected)
    stage = "interim" if args.component.startswith("clean-") else "processed"
    save_result(result, args.component, metadata, stage)


if __name__ == "__main__":
    main()
