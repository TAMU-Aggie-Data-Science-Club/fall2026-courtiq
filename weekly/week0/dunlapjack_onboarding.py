"""Deliverable 0: copy this file to weekly/week0/<github-handle>_onboarding.py."""

from pathlib import Path

import pandas as pd
import plotly.express as px
from nba_api.stats.endpoints import leaguedashplayerstats

ROOT = Path(__file__).resolve().parents[2]
USE_API = False  # Set True to try the prepared NBA request; False uses the backup.
SEASON = "2025-26"


def load_players(use_api):
    """Provided: load per-game stats, falling back if the API is unavailable."""
    if use_api:
        try:
            # PerGame means PTS, REB and AST are already averages.
            response = leaguedashplayerstats.LeagueDashPlayerStats(
                season=SEASON, per_mode_detailed="PerGame", timeout=15
            )
            raw = response.get_data_frames()[0]
            players = raw[
                ["PLAYER_ID", "PLAYER_NAME", "TEAM_ABBREVIATION", "GP", "PTS", "REB", "AST"]
            ].rename(columns={
                "PTS": "PTS_PER_GAME", "REB": "REB_PER_GAME", "AST": "AST_PER_GAME"
            })
            if players.empty or players["PLAYER_ID"].duplicated().any():
                raise ValueError("Expected a nonempty table with one row per player.")
            return players, f"NBA.com — {SEASON} (PerGame)"
        except Exception as exc:
            print(f"API unavailable ({type(exc).__name__}: {exc}). Using the backup.")

    players = pd.read_csv(ROOT / "weekly/week0/player_stats_backup.csv")
    return players, "SYNTHETIC backup — fictional players and statistics"


def main():
    players, source = load_players(USE_API)
    print(f"Source: {source}")
    print(players.head())
    print("Columns:", players.columns.tolist())

    # TODO 1: Print the table's shape and inspect its data types.
    print("Shape:", players.shape)
    print(players.dtypes)

    # TODO 2: Keep players with at least 20 games. Hint: pandas boolean indexing.
    eligible_players = players[players["GP"] >= 20]
    if eligible_players is None:
        print("Next: complete TODO 2 to filter by games played.")
        return

    # TODO 3: Sort PTS_PER_GAME descending and keep five rows.
    # Hints: sort_values(..., ascending=False), head(5).
    top_five = eligible_players.sort_values("PTS_PER_GAME", ascending=False).head(5)
    if top_five is None:
        print("Next: complete TODO 3 to find the top five scorers.")
        return
    print(top_five[["PLAYER_NAME", "GP", "PTS_PER_GAME"]])

    # TODO 4: Create a px.bar figure using top_five.
    # Use PLAYER_NAME for x and PTS_PER_GAME for y.
    fig = px.bar(top_five, x="PLAYER_NAME", y="PTS_PER_GAME")
    if fig is None:
        print("Next: complete TODO 4 to create the chart.")
        return

    # Provided: label the source, preserve ranking order, and save the chart.
    fig.update_layout(
        title=f"{source}: top five scorers with at least 20 games",
        xaxis_title="Player", yaxis_title="Points per game",
        xaxis={"categoryorder": "array", "categoryarray": top_five["PLAYER_NAME"].tolist()},
    )
    output = ROOT / "data/processed/onboarding_chart.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(output, include_plotlyjs=True)
    print(f"Open this file in a browser: {output}")


if __name__ == "__main__":
    main()
