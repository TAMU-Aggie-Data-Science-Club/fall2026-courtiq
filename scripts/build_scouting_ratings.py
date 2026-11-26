"""Build Scouting Lab's defensive ratings, rebound share, and starting-position counts.

Run from the repository root with:
    python -m scripts.build_scouting_ratings --raw-dir data/raw/kaggle
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.pipeline import APP, PROCESSED, RAW

KEYS = ["gameId", "home"]
TOLERANCE = 0.05000001  # Include both edges of the rounding interval.
MIN_COVERAGE = 0.95


def team_bounds(path):
    fields = KEYS + ["teamScore", "opponentScore", "possessions", "offensiveRating",
                     "defensiveRating", "reboundsDefensive"]
    teams = pd.read_csv(path, usecols=fields)
    teams = teams[teams.gameId.floordiv(10_000_000).eq(2)]
    opponent = (
        teams[KEYS + ["possessions"]]
        .assign(home=lambda rows: 1 - rows.home)
        .rename(columns={"possessions": "def_poss_max"})
    )
    teams = teams.merge(opponent, on=KEYS, how="left", validate="one_to_one")
    valid = (
        teams.possessions.gt(0) & teams.def_poss_max.gt(0)
        & teams.possessions.mod(1).eq(0) & teams.def_poss_max.mod(1).eq(0)
        & (100 * teams.teamScore / teams.possessions - teams.offensiveRating).abs().le(TOLERANCE)
        & (100 * teams.opponentScore / teams.def_poss_max - teams.defensiveRating).abs().le(TOLERANCE)
    )
    teams["off_poss_max"] = teams.possessions.where(valid)
    teams["def_poss_max"] = teams.def_poss_max.where(valid)
    teams["team_dreb"] = pd.to_numeric(teams.reboundsDefensive, errors="coerce")
    return teams[KEYS + ["teamScore", "opponentScore", "off_poss_max", "def_poss_max", "team_dreb"]]


def reconstruct(rows):
    off_poss = rows.possessions.where(rows.possessions.gt(0))
    off_points = (off_poss * rows.offensiveRating / 100).round()
    allowed = off_points - rows.plusMinusPoints
    off_rate = 100 * off_points / off_poss
    valid = (
        off_poss.mod(1).eq(0) & off_poss.le(rows.off_poss_max)
        & (off_rate - rows.offensiveRating).abs().le(TOLERANCE)
        & off_points.ge(rows.points) & off_points.le(rows.teamScore)
        & allowed.ge(0) & allowed.le(rows.opponentScore) & allowed.mod(1).eq(0)
    )

    # The two displayed ratings constrain the same underlying defensive rate.
    implied_def = off_rate - rows.netRating
    lower = np.maximum(rows.defensiveRating, implied_def) - TOLERANCE
    upper = np.minimum(rows.defensiveRating, implied_def) + TOLERANCE
    least = np.ceil(100 * allowed / upper.where(upper.gt(0))).clip(lower=1)
    most = np.minimum(
        np.floor(100 * allowed / lower.where(lower.gt(0), 1e-12)),
        rows.def_poss_max,
    )
    zero_rate = allowed.eq(0) & lower.le(0) & upper.ge(0)
    least = least.mask(zero_rate, 1)
    most = most.mask(zero_rate, rows.def_poss_max)
    unique = valid & lower.le(upper) & least.eq(most)
    return pd.DataFrame({
        "off_poss": off_poss, "off_points": off_points,
        "def_poss": least, "def_points": allowed,
    }).where(unique)


def build(raw_dir):
    bounds = team_bounds(raw_dir / "TeamStatisticsExtended.csv")
    games_path = PROCESSED / "player_games.csv.gz"
    if not games_path.exists():
        games_path = APP / "player_games.csv.gz"
        print("Full cleaned player logs are unavailable. Using bundled game logs only.")
    games = pd.read_csv(games_path, usecols=[
        "game_id", "player_id", "home", "played", "season_start", "minutes",
    ]).query("played")
    keys = ["game_id", "player_id", "home"]
    source_fields = ["numMinutes", "points", "reboundsDefensive", "possessions", "plusMinusPoints",
                     "offensiveRating", "defensiveRating", "netRating"]
    parts = []
    player_path = raw_dir / "PlayerStatisticsExtended.csv"
    for chunk in pd.read_csv(player_path, usecols=KEYS + ["personId", "startingPosition"] + source_fields,
                             chunksize=150_000, low_memory=False):
        chunk = chunk[chunk.gameId.isin(games.game_id)]
        if chunk.empty:
            continue
        chunk[source_fields] = chunk[source_fields].apply(pd.to_numeric, errors="coerce")
        chunk = chunk.merge(bounds, on=KEYS, how="left", validate="many_to_one")
        parts.append(chunk[KEYS + ["personId", "numMinutes", "reboundsDefensive", "team_dreb", "startingPosition"]]
                     .join(reconstruct(chunk)))
    if not parts:
        raise ValueError("The raw file has no matching Scouting Lab games.")
    counts = pd.concat(parts, ignore_index=True).rename(columns={"gameId": "game_id", "personId": "player_id"})
    counts = counts.drop_duplicates(keys, keep=False)
    games = games.merge(counts, on=keys, how="left", validate="one_to_one")
    matched = np.isclose(games.minutes, games.numMinutes, rtol=0, atol=1e-6)
    totals = ["off_poss", "off_points", "def_poss", "def_points"]
    games.loc[~matched, totals] = np.nan
    games["ratings_minutes"] = games.minutes.where(games.def_poss.notna(), 0)
    player_dreb = games.reboundsDefensive
    team_dreb = games.team_dreb
    rebound_match = (
        matched & player_dreb.ge(0) & player_dreb.mod(1).eq(0)
        & team_dreb.ge(player_dreb) & team_dreb.mod(1).eq(0)
    )
    games["player_dreb"] = player_dreb.where(rebound_match)
    games["team_dreb"] = team_dreb.where(rebound_match)
    position_columns = ["guard_starts", "forward_starts", "center_starts"]
    for code, column in zip(("G", "F", "C"), position_columns):
        games[column] = matched & games.startingPosition.eq(code)
    group = games.groupby(["player_id", "season_start"])
    ratings = group[totals + ["minutes", "ratings_minutes", "player_dreb", "team_dreb"] + position_columns].sum(min_count=1)
    ratings["games"] = group.size()
    ratings["rebound_games"] = group.team_dreb.count()
    ratings = ratings.reset_index()

    seasons = pd.read_csv(APP / "player_season.csv.gz", usecols=[
        "player_id", "season_start", "team_id", "games", "minutes", "mpg", "dreb",
    ]).query("team_id == 0")
    check = seasons.merge(ratings, on=["player_id", "season_start", "games"], suffixes=("", "_games"),
                          validate="one_to_one")
    check = check.loc[np.isclose(check.minutes, check.minutes_games, rtol=0, atol=1e-6)].copy()
    check["ratings_coverage"] = check.ratings_minutes / check.minutes
    ready = check.ratings_coverage.ge(MIN_COVERAGE)
    check["drtg"] = (100 * check.def_points / check.def_poss).where(ready)
    check["netrtg"] = (100 * check.off_points / check.off_poss - check.drtg).where(ready)
    rebound_ready = check.rebound_games.eq(check.games) & check.player_dreb.eq(check.dreb) & check.team_dreb.gt(0)
    check["team_dreb_share"] = check.player_dreb / check.team_dreb.where(rebound_ready)
    output = ["player_id", "season_start", "games", "minutes", "ratings_coverage", "drtg", "netrtg",
              "team_dreb_share", *position_columns]
    check[output].to_csv(APP / "scouting_ratings.csv.gz", index=False,
                         compression={"method": "gzip", "mtime": 0})
    eligible = check.games.ge(20) & check.mpg.ge(15)
    print(check.loc[eligible].groupby("season_start").agg(
        eligible=("games", "size"), ratings=("drtg", "count"), rebound_share=("team_dreb_share", "count"),
    ))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=RAW / "kaggle")
    build(parser.parse_args().raw_dir)
