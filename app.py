"""CourtIQ: one CSV-backed application, no fetching or training on navigation."""
import json
import streamlit as st
from src.pipeline import APP
from src import dashboard as ui


PAGE_ROUTES = {
    "scouting-lab": ("Players", "Scouting Lab"),
    "on-off-impact": ("Players", "On/Off Impact"),
    "team-forecasts": ("Teams", None),
    "player-matchups": ("Compare", None),
    "breakout-watch": ("Trends", None),
}
ROUTE_BY_SELECTION = {selection: slug for slug, selection in PAGE_ROUTES.items()}


def update_page_url():
    section = st.session_state["nav_section"]
    tool = st.session_state.get("nav_player_tool", "Scouting Lab") if section == "Players" else None
    slug = ROUTE_BY_SELECTION[section, tool]
    if st.query_params.get("page") != slug:
        st.query_params["page"] = slug


st.set_page_config(page_title="CourtIQ",page_icon="🏀",layout="wide")
slug = st.query_params.get("page")
if slug not in PAGE_ROUTES:
    slug = "scouting-lab"
    st.query_params["page"] = slug
section, tool = PAGE_ROUTES[slug]
if st.session_state.get("nav_section") != section:
    st.session_state["nav_section"] = section
if tool is not None and st.session_state.get("nav_player_tool") != tool:
    st.session_state["nav_player_tool"] = tool

st.markdown("""<style>
.stMainBlockContainer{max-width:1180px;padding-top:2rem}
h1,h2,h3{letter-spacing:-.035em}
[data-testid="stSidebar"]{border-right:4px solid #ed8446}
.court-brand{position:relative;overflow:hidden;background:#223541;border:1px solid #52606b;border-radius:14px;padding:22px 18px;color:#fff7ed}
.court-brand strong{position:relative;font-size:2.2rem;letter-spacing:-.055em;z-index:1}
.court-brand small{display:block;position:relative;z-index:1;color:#ffbb90;font-size:.85rem}
.court-brand:before,.court-brand:after{content:"";position:absolute;border:2px solid #bd774c;border-radius:50%;width:155px;height:155px;right:-74px;top:-38px}
.court-brand:after{width:75px;height:75px;right:-35px;top:3px}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:.5rem .7rem;border-radius:8px}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:#324653;box-shadow:inset 3px 0 #ff9c60}

[data-testid="stMetric"]{border:1px solid #8794a455;border-radius:12px;padding:12px 16px}
</style>""", unsafe_allow_html=True)
st.sidebar.markdown('<div class="court-brand"><strong>CourtIQ</strong><small>NBA scouting &amp; forecasts</small></div>',unsafe_allow_html=True)
page = st.sidebar.radio("Explore", ["Players","Teams","Compare","Trends"],
    format_func={"Players":"◎  Player scouting & impact","Teams":"◈  Team forecasts",
                 "Compare":"⇄  Player matchups","Trends":"↗  Breakout watch"}.get,
    key="nav_section", on_change=update_page_url)
manifest_path=APP/"manifest.json"
if not manifest_path.exists():
    st.info("Data is not prepared yet. Run python scripts/build_dataset.py, then python scripts/train_models.py.")
    st.stop()
manifest=json.loads(manifest_path.read_text())
version=manifest["version"]

teams=ui.table("teams",version).sort_values("team_name")
st.sidebar.divider()
st.sidebar.caption("Historical box scores · Offline forecasts")
if page=="Players":
    mode=st.radio("Player tools",["Scouting Lab","On/Off Impact"],horizontal=True,
                  key="nav_player_tool",on_change=update_page_url)
    if mode=="Scouting Lab": ui.scouting_page(ui.table("player_season",version),version,teams)
    else: ui.impact_page(ui.table("on_off",version),teams,manifest)
elif page=="Teams": ui.team_page(ui.table("team_games",version),teams,version)
elif page=="Compare": ui.player_page(ui.table("player_games",version),ui.table("team_games",version),teams,version)
else: ui.breakout_page(ui.table("player_season",version),version)
ui.sources_and_limitations(ROUTE_BY_SELECTION[page, mode if page == "Players" else None])
