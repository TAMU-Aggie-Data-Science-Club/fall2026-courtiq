"""Source tables, local snapshots and validation. No requests on import or UI reads.

Shared helpers are PM-owned; member-owned TODOs are marked beside each function.
"""

from datetime import datetime
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SEASON = "2025-26"
RAW = ROOT / "data/raw/week1"
METRICS = ["PTS_PER_GAME", "REB_PER_GAME", "AST_PER_GAME"]
FIELDS = {
    "players": ["PLAYER_ID", "PLAYER_NAME", "GP", "PTS", "REB", "AST"],
    "teams": ["TEAM_ID", "TEAM_NAME", "GP", "W", "L", "W_PCT", "PTS", "REB", "AST"],
    "ratings": ["TEAM_ID", "TEAM_NAME", "OFF_RATING", "DEF_RATING", "NET_RATING"],
}


def practice_data(kind):
    """Small invented inputs for development, never evidence of NBA completion."""
    if kind == "players":
        frame = pd.DataFrame([
            [101, "Example Player A", 40, 10.0, 3.0, 2.0],
            [102, "Example Player B", 20, 20.0, 5.0, 4.0],
            [103, "Example Player C", 19, 30.0, 7.0, 6.0],
            [104, "Example Player D", 50, 20.0, 9.0, None],
        ], columns=FIELDS[kind])
    elif kind == "teams":
        frame = pd.DataFrame([
            [201, "Example Team A", 40, 10, 30, .25, 100.0, 40.0, 20.0],
            [202, "Example Team B", 40, 20, 20, .50, 110.0, 42.0, 24.0],
            [203, "Example Team C", 40, 30, 10, .75, 120.0, 44.0, 28.0],
        ], columns=FIELDS[kind])
    else:
        frame = pd.DataFrame([
            [201, "Example Team A", 108.0, 115.0, -7.0],
            [202, "Example Team B", 112.0, 112.0, 0.0],
            [203, "Example Team C", 118.0, 109.0, 9.0],
        ], columns=FIELDS[kind])
    return frame, {"source": "SYNTHETIC — all names and values invented",
                   "season": "SYNTHETIC-01", "season_type": "Practice only",
                   "retrieved_at": None, "kind": kind}


def load_snapshot(kind, demo=False):
    """Read an explicit local snapshot; missing data never triggers a request."""
    if kind not in FIELDS:
        raise ValueError("Choose players, teams, or ratings.")
    if demo:
        return practice_data(kind)
    path = RAW / f"{kind}_{SEASON}.json"
    try:
        raw_text = path.read_text(encoding="utf-8")
        payload = json.loads(raw_text)
        metadata = json.loads(path.with_suffix(".meta.json").read_text(encoding="utf-8"))
        expected_parameters = {
            "season": SEASON, "season_type_all_star": "Regular Season",
            "per_mode_detailed": "PerGame",
            "measure_type_detailed_defense": "Advanced" if kind == "ratings" else "Base",
        }
        if (metadata["season"] != SEASON or metadata["kind"] != kind
                or metadata["season_type"] != "Regular Season"
                or metadata["source"] != "NBA.com via nba_api"
                or datetime.fromisoformat(metadata["retrieved_at"]).tzinfo is None
                or metadata.get("sha256") != hashlib.sha256(raw_text.encode()).hexdigest()):
            raise ValueError("Snapshot metadata does not match the Week 1 request.")
        if any(metadata["parameters"].get(key) != value for key, value in expected_parameters.items()):
            raise ValueError("Snapshot parameters mix periods, units or statistic types.")
        results = payload["resultSets"]
        result = results[0] if isinstance(results, list) else results
        frame = pd.DataFrame(result["rowSet"], columns=result["headers"])
        missing = set(FIELDS[kind]) - set(frame.columns)
        if missing or frame.empty:
            raise ValueError(f"Empty response or missing fields: {sorted(missing)}")
        return frame, metadata
    except FileNotFoundError:
        raise ValueError(
            f"No {kind} snapshot. After PM source guidance, run: "
            f"python -m scripts.fetch_data {kind}. "
            "Use the labeled practice option to develop offline."
        ) from None
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Malformed {kind} snapshot; ask Cemal before replacing it.") from exc


def component_table(raw, metadata):
    """Provided selection/renaming, not a substitute for the cleaning tasks."""
    frame = raw[FIELDS[metadata["kind"]]].copy()
    frame = frame.rename(columns={"PTS": "PTS_PER_GAME", "REB": "REB_PER_GAME",
                                  "AST": "AST_PER_GAME"})
    frame["SEASON"] = metadata["season"]
    return frame


# Owner: Aiden Jackson — edit only this function body.
def audit_source(frame):
    """Return columns FIELD, DTYPE, MISSING; inspect the raw input without changing it."""
    # TODO(Aiden) 1: Inspect shape, dtypes, and missing counts (frame.isna().sum()).
    # TODO 2: Build one summary row per input column. Example for a DIFFERENT table:
    # toy = pd.DataFrame({"value": [1, None]})
    # print(toy.isna().sum())  # value: 1
    # Hint: pd.DataFrame({"FIELD": frame.columns, "DTYPE": ..., "MISSING": ...})
    # TODO 3: Report whether PLAYER_ID repeats in this audit. Do not silently drop rows.
    return None


# Owner: Ignacio Wijatno — edit only this function body.
def clean_players(raw, season):
    """Return one row per SEASON/PLAYER_ID with the canonical player fields."""
    # TODO(Ignacio) 1: Check required fields, then work on raw[FIELDS["players"]].copy().
    # TODO 2: Convert IDs/GP/PTS/REB/AST with pd.to_numeric(..., errors="raise").
    # Reject missing/duplicate PLAYER_ID. Preserve missing metrics as missing.
    # Hint: frame["PLAYER_ID"].isna().any(); frame.duplicated(["PLAYER_ID"]).any().
    # Deferred before production/database use: name, integer/range and infinity checks.
    # TODO 3: Add SEASON, rename PTS/REB/AST to *_PER_GAME, print before/after counts.
    # PerGame fields are ALREADY averages. No division by GP and no fillna(0).
    # Example: pd.to_numeric(pd.Series(["2", "3"]), errors="raise")
    return None


# Owner: Andrew Mok — edit only this function body.
def clean_teams(raw, season):
    """Return canonical team fields keyed by SEASON/TEAM_ID; leave raw unchanged."""
    # TODO(Andrew) 1: Select required fields into a copy; reject missing/duplicate TEAM_ID.
    # TODO 2: Convert numeric columns with pd.to_numeric(..., errors="raise").
    # GP/W/L must be present nonnegative integers; require W + L == GP.
    # Preserve source W_PCT and missing basic metrics; do not recalculate percentages.
    # Deferred before production/database use: W_PCT tolerance/zero-GP, name and metric-range checks.
    # TODO 3: Add SEASON and rename PTS/REB/AST to *_PER_GAME. Print row counts.
    # Do not drop teams because they have a missing metric or fill that value with 0.
    return None
