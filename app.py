"""CourtIQ profile placeholders with independent Week 1 component previews."""

import pandas as pd
from plotly.graph_objects import Figure
import streamlit as st

from src import analytics, charts, data, views

st.set_page_config(page_title="CourtIQ", page_icon="🏀", layout="wide")
st.markdown("""
<style>
.stMainBlockContainer { max-width: 1200px; padding-top: 2.5rem; }
.court-eyebrow { color: #d58b20; font-size: .75rem; font-weight: 700;
                 letter-spacing: .16em; margin-bottom: .5rem; }
.court-empty { min-height: 250px; border-radius: 12px; display: flex;
               align-items: center; justify-content: center; flex-direction: column;
               background: linear-gradient(160deg, rgba(148,163,184,.07), rgba(148,163,184,.015));
               border: 1px dashed rgba(148,163,184,.22); text-align: center;
               padding: 1.5rem; margin: .5rem 0; }
.court-empty p { margin: .3rem 0; opacity: .55; font-size: .9rem; }
.court-bars { display: flex; align-items: end; gap: 8px; height: 64px; margin-bottom: 1rem; }
.court-bars span { width: 15px; border-radius: 4px 4px 0 0; background: rgba(213,139,32,.2); }
.court-bars span:nth-child(1) { height: 25%; }
.court-bars span:nth-child(2) { height: 55%; }
.court-bars span:nth-child(3) { height: 80%; }
.court-bars span:nth-child(4) { height: 65%; }
.court-bars span:nth-child(5) { height: 40%; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🏀 CourtIQ")
st.sidebar.caption("A clearer view of the game.")
section = st.sidebar.radio("Explore", ["Players", "Teams", "Compare", "Trends"])
mode = "Placeholders only"
if section in ("Players", "Teams"):
    with st.sidebar.expander("Development settings"):
        mode = st.radio("Week 1 inputs", ["Placeholders only", "Fictional practice", "Local NBA snapshots"])
        st.caption("Preview components here. Layout and visual choices are open for team discussion.")
st.sidebar.caption("Development preview · Fall 2026")
st.markdown('<div class="court-eyebrow">COURTIQ / EXPLORER</div>', unsafe_allow_html=True)
st.title(section)


def empty_visual(title, description):
    # Decorative skeleton only: no plotted values or fabricated statistics.
    st.markdown(f"""<div class="court-empty">
        <div class="court-bars" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span></div>
        <strong>{title}</strong><p>{description}</p><p>Visualization preview</p>
        </div>""", unsafe_allow_html=True)


def show_result(result, owner):
    if result is None:
        st.caption("No preview returned. The function may be unfinished or this selection has no result.")
    elif isinstance(result, pd.DataFrame):
        st.dataframe(result, hide_index=True, use_container_width=True)
    elif isinstance(result, Figure):
        st.plotly_chart(result, use_container_width=True)
    else:
        st.error(f"{owner}: return a DataFrame or Plotly Figure to match the component contract.")


def preview(function, *args):
    try:
        return function(*args)
    except Exception as exc:
        st.error(f"Component needs attention: {type(exc).__name__}: {exc}")
        return None


def inputs(kind, demo):
    try:
        raw, metadata = data.load_snapshot(kind, demo)
        return raw, data.component_table(raw, metadata), metadata
    except (ValueError, OSError) as exc:
        st.caption(str(exc))
        return None


if section in ("Players", "Teams"):
    player_page = section == "Players"
    st.caption("Season performance, league context, and the story behind the numbers.")
    active = mode != "Placeholders only"
    demo = mode == "Fictional practice"
    primary = inputs("players" if player_page else "teams", demo) if active else None
    ratings = inputs("ratings", demo) if active and not player_page else None
    if demo:
        st.warning("SYNTHETIC practice data — all names and values are invented.")
    elif primary or ratings:
        metadata = (primary or ratings)[2]
        st.caption(f"{metadata['source']} · {metadata['season']} · {metadata['season_type']} · "
                   f"Retrieved {metadata['retrieved_at']}")
    else:
        st.caption("2025–26 regular season · Layout preview · No statistics loaded")

    with st.container(border=True):
        if primary:
            preview(views.render_player_profile if player_page else views.render_team_profile,
                    primary[1].copy(), primary[2].copy())
        else:
            select, season = st.columns([3, 1])
            with select:
                st.selectbox("Player" if player_page else "Team",
                             ["Choose a player" if player_page else "Choose a team"], disabled=True)
            with season:
                st.selectbox("Season", ["2025–26"], disabled=True)
            labels = (["Games played", "Points / game", "Rebounds / game", "Assists / game"]
                      if player_page else ["Games played", "Record", "Win percentage", "Points / game"])
            for column, label in zip(st.columns(4), labels):
                column.metric(label, "—")

    main, context = st.columns([1.6, 1], gap="large")
    with main:
        st.subheader("Scoring profile" if player_page else "League efficiency")
        st.caption("The selected player's scoring among league peers." if player_page
                   else "A team's offensive and defensive performance in league context.")
        chart_data = primary if player_page else ratings
        if chart_data:
            if not player_page and not demo and primary:
                st.caption(f"Ratings source: {chart_data[2]['source']} · "
                           f"Retrieved {chart_data[2]['retrieved_at']}")
            frame = chart_data[1]
            id_column = "PLAYER_ID" if player_page else "TEAM_ID"
            name_column = "PLAYER_NAME" if player_page else "TEAM_NAME"
            choices = frame.loc[frame["GP"] >= 20] if player_page else frame
            if choices.empty:
                st.caption("No eligible records for this period.")
            else:
                labels = dict(zip(choices[id_column], choices[name_column]))
                chosen = st.selectbox("Highlight", list(labels), format_func=labels.get,
                                      key="player_highlight" if player_page else "team_highlight")
                function = charts.player_scoring_distribution if player_page else charts.team_efficiency
                show_result(preview(function, frame.copy(), chosen), "Jason" if player_page else "Jack")
        else:
            empty_visual("Player vs. league" if player_page else "Offense vs. defense",
                         "Scoring distribution and a highlighted player." if player_page
                         else "League teams, with your selection highlighted.")
    with context:
        st.subheader("League percentiles" if player_page else "Team ratings")
        st.caption("Relative standing in points, rebounds, and assists." if player_page
                   else "Points per 100 possessions. Lower defensive rating is better.")
        if chart_data:
            function = analytics.calculate_percentiles if player_page else analytics.prepare_ratings
            show_result(preview(function, chart_data[1].copy()), "Sri" if player_page else "Michael")
        else:
            empty_visual("Performance snapshot" if player_page else "ORTG · DRTG · NETRTG",
                         "A shared scale for each statistical category." if player_page
                         else "Offensive, defensive, and net rating.")

    with st.expander("Recent performance · planned"):
        st.caption("Space for recent games, season comparisons, and shooting context in a later increment.")
    with st.expander("Development notes & component checks"):
        st.caption("Wednesday, October 21: discuss size, order, and visual choices. "
                   "Edit only your named TODO function in src/; keep shared helpers and app.py unchanged.")
        if player_page:
            st.markdown("**P1** June · `views.render_player_profile()` — selection/summary  \n"
                        "**P2** Jason · `charts.player_scoring_distribution()` — scoring visual  \n"
                        "**P3** Sri · `analytics.calculate_percentiles()` — comparison inputs  \n"
                        "**P4** Recent performance — reserved for later")
            if primary:
                st.write("Aiden · source/field audit")
                show_result(preview(data.audit_source, primary[0].copy()), "Aiden")
                st.write("Ignacio · player cleanup")
                show_result(preview(data.clean_players, primary[0].copy(), primary[2]["season"]),
                            "Ignacio")
        else:
            st.markdown("**T1** Casey · `views.render_team_profile()` — selection/record  \n"
                        "**T2** Michael · `analytics.prepare_ratings()` — rating checks  \n"
                        "**T3** Jack · `charts.team_efficiency()` — efficiency visual  \n"
                        "**T4** Recent performance — reserved for later")
            if primary:
                st.write("Andrew · team cleanup")
                show_result(preview(data.clean_teams, primary[0].copy(), primary[2]["season"]), "Andrew")
        st.code('with st.container(border=True):\n    st.metric("Example statistic", "12.3")\n'
                '    # st.plotly_chart(my_figure, use_container_width=True)', language="python")
else:
    st.caption("Compare performance on a common scale." if section == "Compare"
               else "Follow performance over time.")
    empty_visual("Player & team comparisons" if section == "Compare" else "Form & performance",
                 "Consistent periods, units, and useful context." if section == "Compare"
                 else "Game histories, rolling averages, and recent-versus-season views.")
    st.caption("Planned section · Available in a later increment")
