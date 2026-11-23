"""CourtIQ: one CSV-backed application, no fetching or training on navigation."""
import json
import streamlit as st
from src.pipeline import APP
from src import dashboard as ui

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
</style>""", unsafe_allow_html=True)
st.html(ui.SHARED_STYLE)
st.sidebar.markdown('<div class="court-brand"><strong>CourtIQ</strong><small>NBA scouting &amp; forecasts</small></div>',unsafe_allow_html=True)
page = st.sidebar.radio("Explore", ["Players","Teams","Compare","Trends"],
    format_func={"Players":"◎  Player Scouting & Impact","Teams":"◈  Team Forecasts",
                 "Compare":"⇄  Player Matchups","Trends":"↗  Breakout Watch"}.get)
st.sidebar.toggle("Dark mode", key="dark_mode", help="Switch the page, cards and charts to dark colors.")
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
if page=="Players":
    mode=st.radio("Player tools",["Scouting Lab","On/Off Impact"],horizontal=True)
    if mode=="Scouting Lab": ui.scouting_page(ui.table("player_season",version),teams,manifest)
    else: ui.impact_page(ui.table("on_off",version),teams,manifest)
elif page=="Teams": ui.team_page(ui.table("team_games",version),teams,version)
elif page=="Compare": ui.player_page(ui.table("player_games",version),ui.table("team_games",version),teams,version)
else: ui.breakout_page(ui.table("player_season",version),version)
if page in ("Compare","Trends"):
    ui.methodology(manifest)
