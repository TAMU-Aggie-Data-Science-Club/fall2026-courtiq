"""CourtIQ: one CSV-backed application, no fetching or training on navigation."""
import json
import streamlit as st
from src.pipeline import APP
from src import dashboard as ui

PAGE_LABELS = {
    "scouting-lab": "◎  Scouting Lab",
    "on-off-impact": "◉  On/Off Impact",
    "team-forecasts": "◈  Team Forecasts",
    "player-matchups": "⇄  Player Matchups",
    "breakout-watch": "↗  Breakout Watch",
}


def update_page_url():
    st.query_params["page"] = st.session_state["nav_page"]


def update_theme_url():
    # Dark is the default, so only a switch to light is kept in the URL (?dark=0).
    if st.session_state["dark_mode"]:
        st.query_params.pop("dark", None)
    else:
        st.query_params["dark"] = "0"


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
/* Sun / moon theme switch (sidebar). Off = light: white knob on the left with an orange sun.
   On = dark: knob slides right with a blue moon. The inactive icon shows faintly on the track. */
.st-key-dark_mode [data-testid="stCheckbox"]>label{gap:.7rem;align-items:center}
.st-key-dark_mode [data-testid="stCheckbox"]>label>div:first-child{position:relative;flex:0 0 76px;width:76px;height:36px;border-radius:999px;margin:0;
  background:#dfe4ea !important;box-shadow:inset 0 2px 5px #0000002e;transition:background .25s}
.st-key-dark_mode [data-testid="stCheckbox"]>label>div:first-child::before,.st-key-dark_mode [data-testid="stCheckbox"]>label>div:first-child::after{content:"";position:absolute;
  top:9px;width:18px;height:18px;background-size:contain;background-repeat:no-repeat;transition:opacity .25s}
.st-key-dark_mode [data-testid="stCheckbox"]>label>div:first-child::before{left:11px;background-image:url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='%23c9d0e2'%20stroke-width='2'%20stroke-linecap='round'%3E%3Ccircle%20cx='12'%20cy='12'%20r='4.2'/%3E%3Cpath%20d='M12%202.5v2.2M12%2019.3v2.2M2.5%2012h2.2M19.3%2012h2.2M5.3%205.3l1.6%201.6M17.1%2017.1l1.6%201.6M5.3%2018.7l1.6-1.6M17.1%206.9l1.6-1.6'/%3E%3C/svg%3E");opacity:0}
.st-key-dark_mode [data-testid="stCheckbox"]>label>div:first-child::after{right:11px;background-image:url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='%23a3abb8'%20stroke-width='2'%20stroke-linejoin='round'%3E%3Cpath%20d='M20%2014.6A8.2%208.2%200%200%201%209.4%204a8.2%208.2%200%201%200%2010.6%2010.6z'/%3E%3Cpath%20d='M17.2%202.8l.7%201.6%201.6.7-1.6.7-.7%201.6-.7-1.6-1.6-.7%201.6-.7z'%20fill='%23a3abb8'%20stroke='none'/%3E%3C/svg%3E");opacity:1}
.st-key-dark_mode [data-testid="stCheckbox"]>label>div:first-child>div{position:absolute;top:3px;left:3px;width:30px;height:30px;margin:0;
  border-radius:50%;background:#fff url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='%23f59e0b'%20stroke-width='2'%20stroke-linecap='round'%3E%3Ccircle%20cx='12'%20cy='12'%20r='4.2'/%3E%3Cpath%20d='M12%202.5v2.2M12%2019.3v2.2M2.5%2012h2.2M19.3%2012h2.2M5.3%205.3l1.6%201.6M17.1%2017.1l1.6%201.6M5.3%2018.7l1.6-1.6M17.1%206.9l1.6-1.6'/%3E%3C/svg%3E") center/19px no-repeat !important;
  box-shadow:0 2px 6px #00000040;transform:none !important;transition:left .25s,background .25s}
.st-key-dark_mode [data-testid="stWidgetLabel"] p{white-space:nowrap}
.st-key-dark_mode [data-testid="stCheckbox"]>label:has(input:checked)>div:first-child{background:#66729c !important}
.st-key-dark_mode [data-testid="stCheckbox"]>label:has(input:checked)>div:first-child::before{opacity:1}
.st-key-dark_mode [data-testid="stCheckbox"]>label:has(input:checked)>div:first-child::after{opacity:0}
.st-key-dark_mode [data-testid="stCheckbox"]>label:has(input:checked)>div:first-child>div{left:43px;
  background:#fff url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='%234257c8'%20stroke-width='2'%20stroke-linejoin='round'%3E%3Cpath%20d='M20%2014.6A8.2%208.2%200%200%201%209.4%204a8.2%208.2%200%201%200%2010.6%2010.6z'/%3E%3Cpath%20d='M17.2%202.8l.7%201.6%201.6.7-1.6.7-.7%201.6-.7-1.6-1.6-.7%201.6-.7z'%20fill='%234257c8'%20stroke='none'/%3E%3C/svg%3E") center/19px no-repeat !important}
.st-key-dark_mode [data-testid="stCheckbox"]>label:has(input:focus-visible)>div:first-child{outline:2px solid #ff9c60;outline-offset:2px}

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
dark_mode = st.query_params.get("dark") != "0"
if st.session_state.get("dark_mode") != dark_mode:
    st.session_state["dark_mode"] = dark_mode
theme_label = "Dark mode" if dark_mode else "Light mode"
st.sidebar.toggle(theme_label, key="dark_mode", on_change=update_theme_url,
                  help="Switch between dark and light colors for the page, cards and charts.")
if ui.dark():
    st.html(ui.DARK_STYLE)
else:
    st.html(ui.LIGHT_STYLE)
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
