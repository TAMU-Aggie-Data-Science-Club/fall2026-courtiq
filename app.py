"""CourtIQ: one CSV-backed application, no fetching or training on navigation."""
import json
import streamlit as st
from src.pipeline import APP
from src import dashboard as ui

st.set_page_config(page_title="CourtIQ",page_icon="🏀",layout="wide")
st.markdown("<style>.stMainBlockContainer{max-width:1250px;padding-top:2rem} h1{letter-spacing:-.03em}</style>",unsafe_allow_html=True)
st.sidebar.title("🏀 CourtIQ")
st.sidebar.caption("A clearer view of the game.")
page=st.sidebar.radio("Explore",["Players","Teams","Compare","Trends"])
st.title("CourtIQ")
st.caption("NBA scouting, matchup forecasts & player impact")
manifest_path=APP/"manifest.json"
if not manifest_path.exists():
    st.info("Data is not prepared yet. Run python scripts/build_dataset.py, then python scripts/train_models.py.")
    st.stop()
manifest=json.loads(manifest_path.read_text())
version=manifest["version"]
seasons=ui.table("player_season",version)
teams=ui.table("teams",version)
if page=="Players":
    mode=st.radio("Player tools",["Scouting Lab","On/Off Impact"],horizontal=True)
    if mode=="Scouting Lab": ui.scouting_page(seasons,teams,manifest)
    else: ui.impact_page(ui.table("on_off",version),teams)
elif page=="Teams": ui.team_page(ui.table("team_games",version),teams,version)
elif page=="Compare": ui.player_page(ui.table("player_games",version),ui.table("team_games",version),teams)
else: ui.breakout_page(seasons,version)
if page != "Players" or mode != "Scouting Lab":
    ui.methodology(manifest)
