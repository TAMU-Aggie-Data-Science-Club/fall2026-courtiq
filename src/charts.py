"""Plotly figures from supplied tables; no requests or Streamlit calls."""

import plotly.express as px


# Owner: Jason Q. Koffi — edit only this function body.
def player_scoring_distribution(frame, player_id):
    """Return a Plotly scoring distribution highlighting one selected player."""
    # TODO(Jason) 1: Keep GP >= 20 and nonmissing PTS_PER_GAME in a copy.
    # Return None for empty eligible input or an ineligible/unknown selected ID.
    # TODO 2: Build px.histogram(..., x="PTS_PER_GAME") and label both axes.
    # Example on unrelated data:
    # px.histogram({"minutes": [10, 20, 20, 30]}, x="minutes", nbins=4)
    # TODO 3: fig.add_vline(x=selected_value, annotation_text=player_name).
    # Label the cohort and period. This shows a distribution, not causality.
    # Always use plot values in points/game; do not divide by games again.
    return None


# Owner: Jack Dunlap — edit only this function body.
def team_efficiency(frame, team_id):
    """Return OFF_RATING vs DEF_RATING scatterplot highlighting the chosen team."""
    # TODO(Jack) 1: Exclude missing OFF_RATING/DEF_RATING from a copy; handle empty/unknown ID.
    # TODO 2: px.scatter(..., x="OFF_RATING", y="DEF_RATING", hover_name="TEAM_NAME").
    # Example: px.scatter({"x": [1, 2], "y": [3, 4]}, x="x", y="y")
    # TODO 3: Give the selected team a distinct marker; label units and period.
    # Explain that lower defensive rating is better. If you reverse y, label that choice.
    # A highlighted point gives league context without claiming causality.
    return None
