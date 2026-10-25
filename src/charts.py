"""Plotly figures from supplied tables; no requests or Streamlit calls."""

from re import match

import plotly.express as px
import pandas as pd

# Owner: Jason Q. Koffi — edit only this function body.
def player_scoring_distribution(frame, player_id):
    """Return a Plotly scoring distribution highlighting one selected player."""
    # TODO(Jason) 1: Keep GP >= 20 and nonmissing PTS_PER_GAME in a copy.
    # Return None for empty eligible input or an ineligible/unknown selected ID
    qualified = frame[(frame["GP"] >= 20) & (frame["PTS_PER_GAME"].notna())].copy() 
    if qualified.empty or player_id not in qualified["PLAYER_ID"].values: #Checks if the filtered dataframe is empty or if the selected player ID is not in the filtered dataframe.
        return None #Returns None if the filtered dataframe is empty or if the selected player ID is not in the filtered dataframe.
    
    identified = qualified[qualified["PLAYER_ID"] == player_id] #Filters the qualified players dataframe to get the row corresponding to the selected player ID.
    selected_value = identified["PTS_PER_GAME"].iloc[0]  #Gets the PTS_PER_GAME value of the selected player from the filtered dataframe.
    player_name = identified["PLAYER_NAME"].iloc[0]  #Gets the name of the selected player from the filtered dataframe.
    season = identified["SEASON"].iloc[0] #Gets the season values from the qualified dataframe.

    # TODO 2: Build px.histogram(..., x="PTS_PER_GAME") and label both axes.
    # Example on unrelated data:
    # px.histogram({"minutes": [10, 20, 20, 30]}, x="minutes", nbins=4)
    fig = px.histogram(
        qualified, x="PTS_PER_GAME", nbins=20,
        color_discrete_sequence=["#AEB4BF"],
    )

    fig.update_traces(
        marker_line_color="#9AA0A6", marker_line_width=1.5, opacity=1, #Bar Color & Opacity
        hovertemplate="%{x} points per game<br>%{y} players<extra></extra>", #Bar Descriptions
    )
    fig.update_layout(
        font_color = "#E8EAED", #Chart Font Color
        xaxis_title="Points per Game", 
        yaxis_title="Number of Players",
        plot_bgcolor= "#0B0D12", #Chart Background Color
        paper_bgcolor="#0B0D12", #Paper Background Color
        bargap=0.05,
    )

    # TODO 3: fig.add_vline(x=selected_value, annotation_text=player_name).
    # Label the cohort and period. This shows a distribution, not causality.
    # Always use plot values in points/game; do not divide by games again.
    
    #League Avg Vertical Dotted line
    league_avg = qualified["PTS_PER_GAME"].mean() 
    fig.add_vline(
        x=league_avg, line_dash="dot", line_color="#1879DA", line_width=2, #Size and Color of the line
        name=f"League Avg.: {league_avg:.1f}", showlegend=True, #Legend Text
        
    )
    #Player Avg Vertical Dotted line
    fig.add_vline(
        x=selected_value, line_dash="dash", line_color="#E03C31", line_width=3, #Size and Color of the line
        showlegend=True, name=f"{player_name}: {selected_value:.1f}", #Legend Text
        
        
    )
    
    fig.update_layout(
        title=(
            f"<b>Scoring distribution — {season} ({len(qualified)} players)</b>" #Title
            "<br><sup>Players with 20+ games · dashed line = selected player</sup>" #Subtitle

        ),
        margin={"t": 90},
    )
    return fig


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
