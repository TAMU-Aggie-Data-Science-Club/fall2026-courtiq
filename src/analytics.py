"""Deterministic calculations on supplied tables; no collection or UI rendering."""

import numpy as np
import pandas as pd

from src.data import METRICS


# Owner: Sri Abhinav Thatavarthi — edit only this function body.
def calculate_percentiles(frame):
    """Return PLAYER_ID, SEASON, PTS_PCTL, REB_PCTL, AST_PCTL for GP >= 20."""
    # prototype cohort != official NBA qualification rule.
    eligible = frame.loc[frame["GP"] >= 20].copy()
    # Ties share average ranks; missing values stay missing & are excluded per metric.
    for metric, percentile in zip(METRICS, ["PTS_PCTL", "REB_PCTL", "AST_PCTL"]):
        eligible[percentile] = eligible[metric].rank(method="average", pct=True) * 100
    return eligible[["PLAYER_ID", "SEASON", "PTS_PCTL", "REB_PCTL", "AST_PCTL"]]


# Owner: Michael Du — edit only this function body.
def prepare_ratings(frame):
    """Return ratings plus CALCULATED_NET_RATING, without changing source fields."""
    # TODO(Michael) 1: Validate unique SEASON/TEAM_ID, numeric finite ratings when present,
    # and required identifiers. Missing ratings remain missing and are reported.
    # TODO 2: CALCULATED_NET_RATING = OFF_RATING - DEF_RATING.
    # Compare with source NET_RATING using absolute tolerance 0.2 (rounded values).
    # Unexpected discrepancies should raise ValueError, not overwrite source data.
    # Example: np.isclose(115.2 - 110.1, 5.1, atol=0.2, rtol=0)
    # TODO 3: Explain units and missing counts in your PR evidence.
    # ORTG/DRTG: points scored/allowed per 100 possessions. Lower DRTG is better.
    # Do not invent a possession estimate or derive ratings from points/game.
    return None
