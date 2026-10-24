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
    # 1. Plot only teams with both ratings; work on a copy so the caller's table is unchanged.
    teams = frame.dropna(subset=["OFF_RATING", "DEF_RATING"]).copy()
    if teams.empty or team_id not in set(teams["TEAM_ID"]):
        return None
    is_selected = teams["TEAM_ID"] == team_id
    teams["Group"] = is_selected.map({True: "Selected team", False: "Other teams"})
    teams = teams.sort_values("Group")  # "Other" sorts before "Selected", so the selection draws on top.
    selected = teams[teams["Group"] == "Selected team"].iloc[0]
    season = ", ".join(sorted(teams["SEASON"].astype(str).unique()))

    # 2. One point per team; hover shows the name and exact ratings.
    fig = px.scatter(
        teams, x="OFF_RATING", y="DEF_RATING", hover_name="TEAM_NAME",
        color="Group", symbol="Group",
        color_discrete_map={"Selected team": "#d62728", "Other teams": "#9e9e9e"},
        symbol_map={"Selected team": "star", "Other teams": "circle"},
        hover_data={"Group": False,"OFF_RATING": ":.1f",
                    "DEF_RATING": ":.1f", "NET_RATING": ":+.1f"},
        labels={"OFF_RATING": "Offensive rating (points scored per 100 possessions)",
                "DEF_RATING": "Defensive rating (points allowed per 100 possessions)",
                "NET_RATING": "Net rating", "Group": ""},
        title=f"Offense vs. defense — {season} ({len(teams)} teams)"
              "<br><sup>Top right = better offense and better defense</sup>",
    )

    # 3. Make the selected team stand out by shape, size and color, and name it on the chart.
    fig.update_traces(marker_size=9, opacity=0.7, selector={"name": "Other teams"})
    fig.update_traces(marker_size=18, marker_line_width=1, marker_line_color="black",
                      selector={"name": "Selected team"})
    fig.add_annotation(x=selected["OFF_RATING"], y=selected["DEF_RATING"],
                       text=selected["TEAM_NAME"], showarrow=True, arrowhead=0, ay=-30)

    # League-average lines split the chart into four groups for context.
    fig.add_vline(x=teams["OFF_RATING"].mean(), line_dash="dot", line_color="gray",
                  annotation_text="League avg. offense", annotation_position="bottom right")
    fig.add_hline(y=teams["DEF_RATING"].mean(), line_dash="dot", line_color="gray",
                  annotation_text="League avg. defense", annotation_position="bottom left")

    # Lower defensive rating is better, so reverse y: better teams appear toward the top right.
    fig.update_yaxes(autorange="reversed",
                     title="Defensive rating (points allowed per 100 possessions)<br>"
                           "<sup>Lower is better — axis reversed so better defense is higher</sup>")
    # Horizontal legend below the plot leaves the full width for the teams.
    fig.update_layout(legend={"orientation": "h", "yanchor": "top", "y": -0.2, "x": 0})
    # Shows league position only; it does not explain why a team rates this way.
    return fig
