"""Deterministic calculations on supplied tables; no collection or UI rendering."""

import numpy as np
import pandas as pd

from src.data import METRICS


# Owner: Sri Abhinav Thatavarthi — edit only this function body.
def calculate_percentiles(frame):
    """Return PLAYER_ID, SEASON, PTS_PCTL, REB_PCTL, AST_PCTL for GP >= 20."""
    # TODO(Sri) 1: Filter GP >= 20 into a copy. This classroom cohort is not an official rule.
    # TODO 2: For each metric, use rank(method="average", pct=True) * 100.
    # Missing values stay missing; pandas excludes them from that metric's denominator.
    # Example: pd.Series([10, 10, 30]).rank(method="average", pct=True) * 100
    # gives [50, 50, 100]. It is a relative rank, not "50% as good".
    # TODO 3: Return the five named columns; check GP=19/20, ties and missing values.
    # Use the one supplied practice table: ID 103 is excluded, PTS_PCTL for ID 102
    # is about 83.33, and AST_PCTL for ID 104 stays missing. No extra fixture needed.
    # Empty input returns an empty DataFrame with those same columns.
    return None


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
