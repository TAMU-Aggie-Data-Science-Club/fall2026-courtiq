"""CourtIQ: one CSV-backed application, no fetching or training on navigation."""
import json
import streamlit as st
from src.pipeline import APP
from src import dashboard as ui

PAGE_LABELS = {
    "scouting-lab": "◎  Player Scouting Lab",
    "on-off-impact": "◉  On/Off Impact",
    "team-forecasts": "◈  Team Forecasts",
    "player-matchups": "⇄  Player Matchups",
    "breakout-watch": "↗  Breakout Watch",
}


def update_page_url():
    st.query_params["page"] = st.session_state["nav_page"]


def update_theme_url():
    if st.session_state["dark_mode"]:
        st.query_params["dark"] = "1"
    else:
        st.query_params.pop("dark", None)


st.set_page_config(page_title="CourtIQ",page_icon="🏀",layout="wide")
st.markdown("""<style>
.stMainBlockContainer{max-width:1180px;padding-top:3.75rem}
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
@media(max-width:640px){
.stMainBlockContainer{padding:3.25rem 1rem 2.5rem}
h1{font-size:2rem !important}
[data-testid="stMetric"]{padding:10px 12px}
}
</style>""", unsafe_allow_html=True)
st.html(ui.SHARED_STYLE)
st.sidebar.markdown('<div class="court-brand"><strong>CourtIQ</strong><small>NBA scouting &amp; forecasts</small></div>',unsafe_allow_html=True)
route = st.query_params.get("page")
if route not in PAGE_LABELS:
    route = "scouting-lab"
    st.query_params["page"] = route
if st.session_state.get("nav_page") != route:
    st.session_state["nav_page"] = route
page = st.sidebar.radio("Explore", list(PAGE_LABELS), format_func=PAGE_LABELS.get,
                        key="nav_page", on_change=update_page_url)
dark_mode = st.query_params.get("dark") == "1"
if st.session_state.get("dark_mode") != dark_mode:
    st.session_state["dark_mode"] = dark_mode
st.sidebar.toggle("Dark mode", key="dark_mode", on_change=update_theme_url,
                  help="Switch the page, cards and charts to dark colors.")
if ui.dark():
    st.html(ui.DARK_STYLE)
manifest_path=APP/"manifest.json"
if not manifest_path.exists():
    st.info("Data is not prepared yet. Run python scripts/build_dataset.py, then python scripts/train_models.py.")
    st.stop()
manifest=json.loads(manifest_path.read_text())
version=manifest["version"]

teams=ui.table("teams",version).sort_values("team_name")
st.sidebar.divider()
st.sidebar.caption("Historical box scores · Offline forecasts")
if page == "scouting-lab":
    ui.scouting_page(ui.table("player_season", version), teams, manifest)
elif page == "on-off-impact":
    ui.impact_page(ui.table("on_off", version), teams, manifest)
elif page == "team-forecasts":
    ui.team_page(ui.table("team_games", version), teams, version)
elif page == "player-matchups":
    ui.player_page(ui.table("player_games", version), ui.table("team_games", version), teams, version)
else:
    ui.breakout_page(ui.table("player_season", version), version)
ui.sources_and_limitations(page)
