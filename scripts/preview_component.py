"""Run one application component independently on local NBA or practice inputs."""

import argparse
import json

import pandas as pd
from plotly.graph_objects import Figure

from src import analytics, charts, data
from src.data import ROOT


def save_result(result, name, metadata, stage="processed"):
    if result is None:
        print("NO OUTPUT: the function is unfinished or no chart is available for this selection. "
              "Check your TODOs and selected ID if you expected a result. "
              "Any earlier preview file is unchanged.")
        return
    if not isinstance(result, (pd.DataFrame, Figure)):
        raise TypeError("Return a pandas DataFrame or Plotly Figure, or None when no chart is available.")
    output = ROOT / "data" / stage / "week1"
    output.mkdir(parents=True, exist_ok=True)
    if isinstance(result, pd.DataFrame):
        path = output / f"{name}.csv"
        result.to_csv(path, index=False)
        print(result.to_string(index=False))
    else:
        path = output / f"{name}.html"
        result.add_annotation(
            text=(f"{metadata['source']} | {metadata['season']} | {metadata['season_type']}"
                  f" | Retrieved: {metadata.get('retrieved_at') or 'not applicable (practice)'}"),
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
    parser.add_argument("--id", type=int, help="Player/team ID to highlight; otherwise use the first eligible record")
    args = parser.parse_args()
    kind = ("ratings" if args.component in ("team-ratings", "team-chart") else
            "teams" if args.component == "clean-teams" else "players")
    try:
        raw, metadata = data.load_snapshot(kind, args.demo)
    except (ValueError, OSError) as exc:
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
        eligible = (frame.loc[frame["GP"] >= 20].dropna(subset=["PTS_PER_GAME"])
                    if kind == "players" else frame.dropna(subset=["OFF_RATING", "DEF_RATING"]))
        selected = (args.id if args.id is not None else
                    eligible.iloc[0][id_column] if not eligible.empty else frame.iloc[0][id_column])
        function = charts.player_scoring_distribution if kind == "players" else charts.team_efficiency
        result = function(frame.copy(), selected)
    stage = "interim" if args.component.startswith("clean-") else "processed"
    save_result(result, args.component, metadata, stage)


if __name__ == "__main__":
    main()
