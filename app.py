"""CourtIQ navigation shell. All analytics described here are planned."""

import streamlit as st

st.set_page_config(page_title="CourtIQ", page_icon="🏀", layout="wide")
st.title("CourtIQ")
st.caption("NBA analytics for curious fans · Development preview")
section = st.sidebar.radio("Explore", ["Players", "Teams", "Compare", "Trends"])
st.sidebar.info("Navigation is ready. Data collection and analytics are planned.")
st.header(section)
st.info("Placeholder page — no NBA statistics are loaded.")

if section == "Players":
    st.markdown("""
    Search for a player and explore season statistics and recent performance.

    Planned features:
    - League percentiles and context for strengths and weaknesses.
    - Interactive shot charts.
    - Season filters and recent 5, 10, or 20-game views.
    """)
elif section == "Teams":
    st.markdown("""
    Search for a team and explore its record and recent form.

    Planned features:
    - League rankings and offensive/defensive efficiency.
    - Interactive team statistics and shot-distribution visualizations.
    - Season and recent-period filters.
    """)
elif section == "Compare":
    st.markdown("""
    Compare two players or two teams using consistent definitions and periods.

    Planned features:
    - Normalized metrics and interactive comparison charts.
    - Context for playing time, pace, sample size, and missing statistics.
    """)
else:
    st.markdown("""
    Explore how player and team performance changes over time.

    Planned features:
    - Rolling averages and recent-versus-season comparisons.
    - Supporting charts with clear dates and sample sizes.
    - Explanations that distinguish ordinary variation from evidence of change.
    """)
