"""Presentation UI consuming only compact app-ready files and trusted models."""
from datetime import datetime, timedelta
from html import escape
from zoneinfo import ZoneInfo
import json
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from src.pipeline import APP
from src.features import scouting,impact

SOURCE_NBA="https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores"
SOURCE_ODDS="https://www.kaggle.com/datasets/cviaxmiwnptr/nba-betting-data-october-2007-to-june-2024"


@st.cache_resource(show_spinner=False)
def table(name,version):
    path=APP/f"{name}.csv.gz"
    columns = ["game_id","player_id","team_id","opponent_id","date","season","season_start","player_name","minutes","played","home","points","rebounds","assists","pra"] if name == "player_games" else None
    frame=pd.read_csv(path,low_memory=False,usecols=columns)
    if "date" in frame: frame["date"]=pd.to_datetime(frame.date)
    return frame


COLORS = dict(zip("ATL BOS BKN CHA CHI CLE DAL DEN DET GSW HOU IND LAC LAL MEM MIA MIL MIN NOP NYK OKC ORL PHI PHX POR SAC SAN TOR UTA WAS".split(),
    "#cc3448 #168458 #667788 #008994 #d23753 #a33954 #1675af #bd902d #d33753 #317aca #d43a50 #bf942c #c34455 #8055ad #6382b4 #b93955 #23855d #3675a2 #aa8049 #e37935 #168cb6 #247eb1 #3978bd #8959ac #c94745 #8153a5 #808890 #c33b51 #795daa #c94355".split()))


def team_color(teams, tid):
    code = teams.loc[teams.team_id.eq(tid), "team_code"]
    return COLORS.get(code.iloc[0], "#db7335") if len(code) else "#db7335"


def dark():
    """True when the viewer turned on the sidebar dark-mode switch (per session)."""
    return bool(st.session_state.get("dark_mode", False))


SHARED_STYLE = """
<style>
.ciq-table-wrap {overflow-x:auto; border:1px solid #8794a455; border-radius:.65rem; margin:.35rem 0 1rem;}
.ciq-table {width:100%; border-collapse:collapse; font-size:.9rem;}
.ciq-table th {text-align:left; font-weight:650; padding:.55rem .75rem; white-space:nowrap;
    background:color-mix(in srgb,currentColor 7%,transparent); border-bottom:1px solid #8794a455;}
.ciq-table td {padding:.5rem .75rem; border-bottom:1px solid #8794a430;}
.ciq-table tr:last-child td {border-bottom:0;}
.ciq-table .num {text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap;}
.ciq-table th.num {text-align:right;}
.ciq-table tr.is-selected td {background:color-mix(in srgb,#b54b1c 15%,transparent); font-weight:650;}
.ciq-table tr.is-gap td {text-align:center; padding:.15rem; opacity:.6;}
.ciq-table th.group {text-align:center; border-bottom:0;}
.ciq-intro {font-size:1.02rem; margin:-.25rem 0 .9rem;}
.ciq-steps {display:flex; flex-wrap:wrap; gap:.4rem .9rem; margin:0 0 .9rem; font-size:.9rem;}
.ciq-steps span {display:inline-flex; align-items:center; gap:.4rem;}
.ciq-steps b {display:inline-flex; align-items:center; justify-content:center; width:1.4rem; height:1.4rem;
    border-radius:50%; background:#b54b1c; color:#fff; font-size:.8rem;}
.ciq-cards {display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.7rem;}
.ciq-card {min-width:0; padding:.8rem 1rem; border:1px solid color-mix(in srgb,var(--accent) 35%,transparent);
    border-top:4px solid var(--accent); border-radius:.7rem; background:color-mix(in srgb,var(--accent) 9%,transparent);}
.ciq-card h4 {margin:.15rem 0 .5rem; padding:0; font-size:clamp(1rem,3vw,1.35rem);}
.ciq-card small {font-size:.82rem;}
.ciq-stat-row {display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.5rem;}
.ciq-stat {padding:.45rem .55rem; border-radius:.5rem; background:color-mix(in srgb,var(--accent) 10%,transparent);}
.ciq-stat b {display:block; font-size:.78rem; letter-spacing:.02em;}
.ciq-stat strong {display:block; font-size:1.45rem; line-height:1.2;}
.ciq-stat span {display:block; font-size:.78rem;}
@media(max-width:640px) {.ciq-cards {grid-template-columns:1fr;}}
</style>
"""

DARK_STYLE = """
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"],
[data-testid="stBottomBlockContainer"] {background:#121b22 !important; color:#ece6da;}
.stApp [data-testid="stMain"] :is(h1,h2,h3,h4,h5,h6,p,li,label,strong,b,td,th,summary) {color:#ece6da;}
.stApp [data-testid="stMain"] [data-testid="stMarkdownContainer"] {color:#ece6da;}
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] p,
.stApp [data-testid="stWidgetLabel"] p {color:#b9c2c8 !important;}
[data-testid="stHeader"] button, [data-testid="stToolbar"] * {color:#ece6da;}
.stApp [data-baseweb="select"] > div, .stApp [data-baseweb="input"], .stApp [data-baseweb="input"] > div,
.stApp [data-baseweb="base-input"], .stApp input, .stApp textarea {
    background:#1b2731 !important; color:#ece6da !important; border-color:#3a4a56 !important;}
.stApp [data-baseweb="select"] svg, .stApp [data-testid="stNumberInput"] button svg {fill:#ece6da; color:#ece6da;}
.stApp [data-testid="stNumberInput"] button {background:#22313c; color:#ece6da; border-color:#3a4a56;}
.stApp .st-key-team_spread :is([data-baseweb="input"], [data-baseweb="base-input"]):has(input:disabled),
.stApp .st-key-team_spread input:disabled,
.stApp .st-key-team_spread button:disabled {
    background:#29333b !important; color:#b9c2c8 !important; border-color:#4a555e !important;
    opacity:1;
}
.stApp .st-key-team_spread input:disabled {-webkit-text-fill-color:#b9c2c8 !important;}
.stApp .st-key-team_spread button:disabled svg {fill:#8e9aa3; color:#8e9aa3;}
[data-baseweb="popover"] > div, [data-baseweb="menu"], [data-baseweb="popover"] ul, [role="listbox"],
[data-baseweb="calendar"], [data-baseweb="calendar"] > div, [data-testid="stPopoverBody"] {
    background:#1b2731 !important; color:#ece6da !important;}
[role="option"], [role="option"] *, [data-baseweb="calendar"] * {color:#ece6da !important;}
[role="option"]:hover, [role="option"][aria-selected="true"] {background:#2a3b47 !important;}
[data-baseweb="calendar"] [aria-selected="true"] div {background:#b54b1c !important;}
.stApp [data-testid="stExpander"] details {background:#16222b; border-color:#34444f;}
.stApp [data-testid="stExpander"] summary {background:#16222b !important; color:#ece6da !important;}
.stApp [data-testid="stExpander"] summary:hover {background:#1d2b35 !important;}
.stApp [data-testid="stExpander"] summary * {color:#ece6da !important;}
.stApp [data-testid="stTooltipIcon"] svg, .stApp [data-testid="stTooltipHoverTarget"] svg {color:#b9c2c8; stroke:#b9c2c8;}
.stApp [data-testid="stExpander"] summary svg {fill:#ece6da; color:#ece6da;}
.stApp [data-baseweb="tab-list"] button p {color:#ece6da;}
.stApp [data-baseweb="tab-border"] {background:#34444f;}
.stApp [data-testid="stMain"] button[kind="secondary"], .stApp [data-testid="stMain"] [data-testid="stBaseButton-secondary"],
.stApp [data-testid="stMain"] [data-testid="stBaseButton-segmented_control"],
.stApp [data-testid="stMain"] [data-testid="stBaseButton-pills"], .stApp [data-testid="stPopover"] button,
.stApp [data-testid="stDownloadButton"] button {
    background:#1b2731 !important; color:#ece6da !important; border-color:#3a4a56 !important;}
[data-testid="stPopoverBody"] [data-testid="stDownloadButton"] button {
    background:#22313c !important; color:#ece6da !important; border-color:#52636f !important;}
[data-testid="stPopoverBody"] [data-testid="stDownloadButton"] button :is(p, span, svg) {
    color:inherit !important;}
[data-testid="stPopoverBody"] [data-testid="stDownloadButton"] button:is(:hover,:focus-visible) {
    background:#2a3b47 !important; border-color:#e08b4f !important;}
.stApp [data-testid="stMain"] [data-testid="stBaseButton-segmented_controlActive"],
.stApp [data-testid="stMain"] [data-testid="stBaseButton-pillsActive"] {
    background:color-mix(in srgb,#e08b4f 22%,#1b2731) !important; color:#ffd8bd !important; border-color:#e08b4f !important;}
.stApp [data-testid="stMain"] [data-testid="stBaseButton-segmented_controlActive"] p {color:#ffd8bd !important;}
.stApp [data-testid="stAlert"] > div {background:#1d2b35 !important; color:#ece6da;}
.stApp [data-testid="stAlert"] * {color:#ece6da;}
.stApp [data-testid="stMain"] label[data-baseweb="radio"]:not(:has(input:checked)) > div:first-child {
    background-color:#1b2731 !important; border:2px solid #7d8a93 !important;}
.stApp [data-testid="stMain"] label[data-baseweb="radio"]:not(:has(input:checked)) > div:first-child > div {
    background-color:#1b2731 !important;}
.stApp [data-testid="stMain"] label[data-baseweb="radio"]:has(input:checked) > div:first-child > div {
    background-color:#121b22 !important;}
.stApp [data-testid="stSlider"] [data-testid="stSliderTickBarMin"], .stApp [data-testid="stSlider"] [data-testid="stSliderTickBarMax"] {color:#b9c2c8;}
.stApp [data-testid="stMain"] [data-testid="stCheckbox"] label span:first-child {border-color:#a7b1b8;}
.stApp [data-testid="stMain"] [data-testid="stProgress"] p {color:#ece6da;}
.stApp hr {border-color:#34444f;}
.stApp a {color:#f2a46f;}
.forecast-win-bar {background:#26343e !important;}
.forecast-win-bar span+span, .ciq-table tr.is-selected td {border-color:#121b22;}
.scout-crown {background:#4a3a10 !important; color:#ffe7a3 !important;}
.stApp .impact-stint-key b {color:#202c36 !important;}
</style>
"""

DARK_CHART = dict(paper="#121b22", plot="#16222b", text="#ece6da", muted="#b9c2c8", grid="#2c3b46")


def show_chart(fig, **kwargs):
    """Render a Plotly figure; in dark mode recolor its canvas, text and grid for the dark page."""
    kwargs.setdefault("use_container_width", True)
    if dark():
        c = DARK_CHART
        fig.update_layout(paper_bgcolor=c["paper"], plot_bgcolor=c["plot"], font_color=c["text"],
                          legend_font_color=c["text"], hoverlabel=dict(bgcolor="#1b2731", font_color=c["text"]))
        fig.update_xaxes(automargin=True, gridcolor=c["grid"], zerolinecolor=c["grid"], linecolor=c["grid"],
                         tickfont_color=c["muted"], title_font_color=c["text"])
        fig.update_yaxes(automargin=True, gridcolor=c["grid"], zerolinecolor=c["grid"], linecolor=c["grid"],
                         tickfont_color=c["muted"], title_font_color=c["text"])
        if "polar" in fig.layout and fig.layout.polar is not None:
            fig.update_polars(bgcolor=c["plot"], angularaxis=dict(gridcolor=c["grid"], linecolor=c["grid"],
                              tickfont_color=c["text"]),
                              radialaxis=dict(gridcolor=c["grid"], linecolor=c["grid"], tickfont_color=c["muted"]))
        kwargs["theme"] = None
    st.plotly_chart(fig, **kwargs)


def html_table(frame, *, numeric=(), highlight=None, groups=None, gap_before=None, headers=None):
    """Readable, theme-aware table. `highlight` marks rows (e.g. the selected player);
    `groups` is an optional list of (label, span) header groups; `gap_before` inserts a
    '…' row before that row position to show the list skips ahead."""
    numeric = set(numeric)
    head = ""
    if groups:
        head += "<tr>" + "".join(
            f'<th class="group" colspan="{span}">{escape(str(label))}</th>' for label, span in groups) + "</tr>"
    labels = headers or list(frame.columns)
    head += "<tr>" + "".join(
        f'<th class="{"num" if col in numeric else ""}">{escape(str(label))}</th>'
        for col, label in zip(frame.columns, labels)) + "</tr>"
    rows = []
    for position, (_, record) in enumerate(frame.iterrows()):
        if gap_before is not None and position == gap_before:
            rows.append(f'<tr class="is-gap"><td colspan="{len(frame.columns)}">⋯</td></tr>')
        selected = highlight is not None and bool(highlight[position])
        cells = "".join(
            f'<td class="{"num" if col in numeric else ""}">{escape("—" if pd.isna(value) else str(value))}</td>'
            for col, value in record.items())
        row_class = ' class="is-selected"' if selected else ""
        rows.append(f"<tr{row_class}>{cells}</tr>")
    st.html(f'<div class="ciq-table-wrap"><table class="ciq-table"><thead>{head}</thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def page_intro(text, steps=()):
    """Plain-language one-liner plus numbered 'how to use' steps, shared by every tool."""
    step_html = "".join(f"<span><b>{i}</b>{escape(step)}</span>" for i, step in enumerate(steps, 1))
    st.html(f'<p class="ciq-intro">{escape(text)}</p>' + (f'<div class="ciq-steps">{step_html}</div>' if steps else ""))


def _oklab(hex_color, cvd=None):
    rgb = np.array([int(hex_color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)])
    lin = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
    if cvd == "protan":
        lin = np.array([[.152286, 1.052583, -.204868], [.114503, .786281, .099216], [-.003882, -.048116, 1.051998]]) @ lin
    elif cvd == "deutan":
        lin = np.array([[.367322, .860646, -.227968], [.280085, .672501, .047413], [-.011820, .042940, .968881]]) @ lin
    lin = np.clip(lin, 0, 1)
    lms = np.array([[.4122214708, .5363325363, .0514459929], [.2119034982, .6806995451, .1073969566],
                    [.0883024619, .2817188376, .6299787005]]) @ lin
    lms = np.cbrt(lms)
    return np.array([[.2104542553, .7936177850, -.0040720468], [1.9779984951, -2.4285922050, .4505937099],
                     [.0259040371, .7827717662, -.8086757660]]) @ lms


def color_distance(first, second):
    """Smallest OKLab distance (x100) across normal, protan and deutan vision."""
    return min(100 * np.linalg.norm(_oklab(first, cvd) - _oklab(second, cvd)) for cvd in (None, "protan", "deutan"))


PAIR_FALLBACKS = ("#1f5bab", "#a8441a", "#4b5b66")


def pair_colors(teams, home_id, away_id):
    """Team colors for a two-team view, swapping the away color for a contrasting one when the
    two would be hard to tell apart (similar team colors or red-green color vision)."""
    home, away = team_color(teams, home_id), team_color(teams, away_id)
    if color_distance(home, away) < 12:
        away = max(PAIR_FALLBACKS, key=lambda candidate: color_distance(home, candidate))
    return home, away


@st.cache_resource(show_spinner=False)
def model(name, version, modified):
    from src.models.common import load
    return load(name)


def bundle(name, version):
    path = APP.parent / "artifacts" / f"{name}.pkl"
    return model(name, version, path.stat().st_mtime_ns)


@st.cache_data(show_spinner=False)
def ranks(version, season, lens, min_games, ratings_modified, _league):
    return scouting.rankings(_league, season, lens, min_games=min_games)


def custom_matchup(lookup, key, latest, *, compact=False, earliest=None):
    if compact:
        c1, swap_picker, c2, date_picker = st.columns([1.25, .24, 1.25, 1], gap="small")
    else:
        c1, c2 = st.columns(2)
        date_picker = st
    home = c1.selectbox("Home team", list(lookup), format_func=lookup.get, key=key+"_home")
    away = c2.selectbox("Away team", [tid for tid in lookup if tid != home], format_func=lookup.get, key=key+"_away")
    if compact:
        def swap_sides():
            home_key, away_key = key+"_home", key+"_away"
            st.session_state[home_key], st.session_state[away_key] = (
                st.session_state[away_key], st.session_state[home_key],
            )

        swap_picker.button(
            "Swap home and away", icon=":material/swap_horiz:", help="Swap home and away",
            on_click=swap_sides, key=key+"_swap_sides",
        )
    default = (latest + timedelta(days=1)).date()
    if earliest is not None:
        default = max(default, earliest)
    when = date_picker.date_input("Game date", default, min_value=earliest, key=key+"_date")
    if earliest is not None:
        date_picker.caption(f"Earliest forecast date: {earliest:%b} {earliest.day}, {earliest.year}.")
    return home, away, when


def schedule_fixtures(team_ids, version):
    games=table("games",version)
    fixtures=games[["game_id","date","home_team_id","away_team_id"]]
    if (APP/"schedule.csv.gz").exists():
        fixtures=pd.concat([fixtures,table("schedule",version)]).drop_duplicates("game_id")
    return fixtures[fixtures.date.gt(pd.Timestamp("2025-04-13")) &
                    fixtures.home_team_id.isin(team_ids) & fixtures.away_team_id.isin(team_ids)]


def choose(frame,key,label="Player"):
    order = next((c for c in ("probability","pra_pg","minutes_on","recent_minutes","minutes") if c in frame), None)
    if order:
        frame = frame.sort_values([order,"player_name"],ascending=[False,True])
    names=frame.drop_duplicates("player_id").set_index("player_id").player_name.to_dict()
    if not names: return None
    return st.selectbox(label,list(names),format_func=names.get,key=key)


def methodology(manifest):
    with st.expander("Sources, definitions & limitations"):
        st.markdown(f"[NBA box scores]({SOURCE_NBA}) · [Historical betting data]({SOURCE_ODDS}) · [The Odds API](https://the-odds-api.com/)")
        st.write(f"Dataset version {manifest['version']}; built {manifest['built_at']}. Source coverage is the supplied download, not a live NBA feed.")
        st.write("CourtIQ qualification: 20 played games & 15 minutes/game. Shooting percentiles need 50 attempts. Rankings use all eligible players in that season, not just the Top 50. Missing is not zero.")
        st.write("Box scores do not identify guarding assignments, injuries or confirmed active rosters. On/off is observational and reflects teammates and opponents.")
        st.write("2024-25 has source coverage omissions. Four current-season games lack duration/player-minute coverage; those values remain unavailable. DNP comparisons use only explicit rows.")
        st.write("Historical line timing is unknown. Market comparisons are retrospective, not a demonstrated trading strategy. Predictions are educational statistical estimates; actual outcomes may differ.")


@st.cache_data
def scouting_game_dates(version):
    path = APP / "player_games.csv.gz"
    if not path.exists():
        return {}
    games = pd.read_csv(path, usecols=["season", "date", "played"], parse_dates=["date"])
    return games.loc[games.played].groupby("season").date.max().to_dict()


@st.cache_data
def scouting_team_game_counts(version):
    path = APP / "team_games.csv.gz"
    if not path.exists():
        return {}
    games = pd.read_csv(path, usecols=["season", "team_id", "game_id"])
    counts = games.groupby(["season", "team_id"]).game_id.nunique()
    return {season: rows.droplevel("season").to_dict() for season, rows in counts.groupby(level="season")}


def scouting_freshness(season, manifest):
    latest = scouting_game_dates(manifest["version"]).get(season)
    built = pd.to_datetime(manifest.get("built_at"), utc=True, errors="coerce")
    labels = []
    if pd.notna(latest):
        labels.append(f"Games included through {latest:%b} {latest.day}, {latest.year}")
    if pd.notna(built):
        built = built.tz_convert("America/Chicago")
        labels.append(f"Box-score snapshot prepared {built:%b} {built.day}, {built.year}")
    if labels:
        st.caption(" · ".join(labels))


SCOUT_BADGES = {
    "Elite Scorer": "🔥",
    "Sharpshooter": "🎯",
    "Playmaker": "🤝",
    "Rebounding Specialist": "🏀",
    "All-Around Contributor": "⭐",
}

SCOUT_STYLE = """
<style>
.stMainBlockContainer {padding-top:3.75rem;}
.scout-header {margin:.9rem 0; text-align:center;}
.scout-badges {display:flex; align-items:center; justify-content:center; flex-wrap:wrap; gap:.45rem;}
.scout-identity h3 {margin:0; padding:0; font-size:clamp(1.55rem,4vw,2.25rem); font-weight:750;}
.scout-identity p {margin:.25rem 0 0;}
.scout-team-position {font-size:.95rem;}
.scout-team-name {white-space:nowrap;}
.scout-team-dot {display:inline-block; width:.6em; height:.6em; border-radius:50%;
    margin-inline-end:.38em; background:var(--team-accent);
    border:1px solid color-mix(in srgb,var(--team-accent),currentColor 25%);
    vertical-align:.04em;}
.scout-badges:not(:empty) {margin-top:.5rem;}
.scout-chip {border:1px solid var(--accent); border-radius:999px; padding:.22rem .6rem;
    background:color-mix(in srgb,var(--accent) 12%,transparent); font-size:.82rem;}
.scout-grid {display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.65rem;}
.scout-cards {grid-template-columns:repeat(4,minmax(0,1fr)); margin-bottom:1rem;}
.scout-tile {border:1px solid color-mix(in srgb,var(--accent) 35%,transparent);
    border-inline-start:4px solid var(--accent); border-radius:.65rem; padding:.65rem .8rem;
    background:color-mix(in srgb,var(--accent) 8%,transparent);}
.scout-tile strong {display:block; font-size:1.35rem;}
.scout-metric-heading {display:flex; flex-wrap:wrap; justify-content:space-between; gap:.3rem;}
.scout-detail {font-size:.82rem; margin:.25rem 0 0;}
.scout-crown {display:inline-block; background:#fff1c7; color:#664900;
    border-radius:999px; padding:0 .25rem;}
.st-key-scout_lens [data-testid="stButtonGroup"] button {flex:1;}
.scout-track {height:.45rem; border-radius:999px; overflow:hidden;
    background:color-mix(in srgb,var(--accent) 18%,transparent); margin-top:.4rem;}
.scout-track span {display:block; height:100%; background:var(--accent); border-radius:inherit;}
.scout-legend {display:flex; flex-wrap:wrap; gap:.4rem; margin:.25rem 0 .75rem;}
@media(max-width:640px) {
    .scout-grid {grid-template-columns:1fr;}
    .scout-cards {grid-template-columns:repeat(2,minmax(0,1fr));}
}
</style>
"""


def scouting_metric_cards(breakdown, player_row, min_games=20, show_crowns=True):
    cards = []
    for _, metric in breakdown.iterrows():
        title, definition, _ = scouting.METRIC_DETAILS[metric.metric]
        raw_value = scouting.display_value(metric.metric, metric.value)
        percentile = metric.percentile
        color = scouting.percentile_color(percentile)
        crown = ""
        if metric.qualified:
            placement = f"{scouting.percentile_label(percentile)} percentile"
            rank = metric["rank"]
            detail = f"Rank {rank:g} of {metric.population:,}"
            if show_crowns and rank == 1:
                crown = ' <span class="scout-crown" title="Ranked first in the league" aria-label="Ranked first in the league">👑</span>'
            track = (
                f'<div class="scout-track" aria-hidden="true">'
                f'<span style="width:{percentile:g}%"></span></div>'
            )
        else:
            placement = "Unranked"
            detail = scouting.ranking_status(metric.metric, player_row, min_games)
            track = ""
        if metric.metric in ("drtg", "netrtg"):
            coverage = player_row.get("ratings_coverage", np.nan)
            if pd.notna(coverage):
                detail += f" · {coverage:.1%} of minutes covered"
        cards.append(f"""
            <div class="scout-tile" style="--accent:{color}">
                <div class="scout-metric-heading"><b>{title}{crown}</b><b>{placement}</b></div>
                <div class="scout-detail">{raw_value} · {detail}</div>
                {track}
                <div class="scout-detail">{definition}</div>
            </div>
        """)
    st.html('<div class="scout-grid">' + "".join(cards) + "</div>")


def scouting_advanced_stats(row):
    cards = []
    for metric, (label, precision, definition) in scouting.ADVANCED.items():
        value = row.get(metric, np.nan)
        if pd.notna(value) and np.isfinite(value):
            cards.append(f"""
                <div class="scout-tile" style="--accent:#b54b1c">
                    <b>{label}</b><strong>{value:{precision}}</strong>
                    <div class="scout-detail">{definition}</div>
                </div>
            """)
    if cards:
        st.subheader("Advanced season stats")
        st.html('<div class="scout-grid">' + "".join(cards) + "</div>")


def scouting_sources():
    with st.expander("Sources and how to read the rankings"):
        comparison, production, shooting, defense, advanced, badges = st.tabs(
            ["Rankings & sources", "Game stats", "Shooting", "Defense & rebounding", "Advanced stats", "Badges"]
        )
        with comparison:
            st.markdown(
                f"""
- **Season, teams, and position** — The page combines regular-season appearances across the teams listed under the player's name. The position on that line shows where the player started most often that season. An additional position appears if it accounts for at least two starts and 25% of recorded starts. The team filter helps find players.
- **Who qualifies** — Players normally need 20 games and 15 minutes per game. The latest season, if still in progress, uses a 5-game minimum until the snapshot includes at least 20 games for every team. Early rankings can swing sharply and badges and crowns start once standard qualification resumes. Three-point percentage requires 50 three-point attempts, and free-throw percentage requires 50 free-throw attempts in every season.
- **Rank** — Rank 1 is the highest value for most stats. Defensive Rating and Foul Avoidance rank lower raw values first. “Rank 12 of 230” means 230 players qualified for that stat. Ties share the average of their positions. 👑 marks rank 1 when standard rankings apply.
- **Percentile** — Places a player's value on a 0–100 scale within that stat's eligible group. A 90th percentile is near the top tenth. The page rounds percentile labels to whole numbers.
- **Unranked** — The player missed a qualification cutoff or the stat was unavailable. Look under the stat for the reason.
- **Coverage** — The date near the filters shows the latest player game in the selected season. The snapshot preparation date is recorded in CourtIQ. The original download date is unavailable. Some games are missing, including in 2024–25. The latest season may be in progress. [Historical NBA box scores]({SOURCE_NBA})
                """
            )
        with production:
            st.markdown(
                """
- **GP · Games played** — Counts regular-season appearances with more than zero recorded minutes.
- **MPG · Minutes per game** — Total minutes divided by games played. Helps explain how much time a player had to produce.
- **PPG · Points per game** — Total points divided by games played. Measures scoring volume.
- **APG · Assists per game** — Credited assists divided by games played. An assist credits a pass that directly leads to a made basket.
- **Rebounds per game** — Offensive plus defensive rebounds divided by games played.
- **Steals per game** — Credited steals divided by games played. A steal credits a defender for taking possession from the opponent.
- **Blocks per game** — Credited blocked shots divided by games played. Steals and blocks capture specific defensive plays.
                """
            )
        with shooting:
            st.markdown(
                """
- **Field-goal %** — Made field goals divided by field-goal attempts. Includes twos and threes.
- **Two-point %** — Made twos divided by attempted twos.
- **Three-point %** — Made threes divided by attempted threes.
- **Free-throw %** — Made free throws divided by attempted free throws.
- **True shooting (TS%)** — Points divided by twice the sum of field-goal attempts and 44% of free-throw attempts. The free-throw adjustment estimates how many scoring attempts those trips used.
- **Effective FG% (eFG%)** — Adds half a make for every made three, then divides by field-goal attempts. The extra weight reflects that threes are worth more than twos.
- **3PA per game** — Three-point attempts divided by games played. A higher rank means more attempts per game.
- **Free-throw rate** — Free-throw attempts per 100 field-goal attempts. Shows how often a player gets to the line relative to their shot volume.
                """
            )
        with defense:
            st.markdown("**Per 36 minutes** divides each season count by minutes played and multiplies by 36.")
            st.markdown("\n".join(f"- **{label}** — {definition}"
                                  for label, definition, _ in scouting.DEFENSE.values()))
            st.markdown(
                "**Ratings coverage.** Defensive and Net Rating use on-court points and possessions "
                "reconstructed from the Kaggle game box scores. We sum the counts across games that "
                "have a unique result. A player needs at least 95% of their season minutes covered. "
                "The rating cards show the actual share covered."
            )
            st.markdown(
                "**Team DREB share.** Divide the player's total defensive rebounds by their teams' "
                "total defensive rebounds in games they played. We use the player's team in each game "
                "and require complete rebound records. A 15% share means the player grabbed 15 of every "
                "100 team defensive rebounds in those games. Playing time affects this share because "
                "the team total covers the whole game."
            )
            st.markdown(
                "**Limits.** Ratings reflect teammates and lineups. Steals and blocks capture specific "
                "plays, and the lens describes a statistical profile."
            )
        with advanced:
            st.markdown(
                """
- **True shooting and effective FG%** — The same season-total efficiency measures described in the **Shooting** tab.
- **Assist-to-turnover ratio** — Season assists divided by season turnovers. A ratio of 3.00 means three assists per turnover. It is unavailable when there are zero recorded turnovers.
- **Points per 36 minutes** — Season points divided by minutes played, multiplied by 36.
- **Rebounds per 36 minutes** — Season rebounds divided by minutes played, multiplied by 36.
- **Assists per 36 minutes** — Season assists divided by minutes played, multiplied by 36.
- **How to read per-36 stats** — They put players on the same playing-time scale. Rates from a small number of minutes can swing more, and a player's rate may change with a different role.
                """
            )
        with badges:
            badge_rules = {
                "Elite Scorer": "90th percentile or higher in points per game.",
                "Sharpshooter": "85th percentile or higher in three-point percentage. The player must qualify for the three-point ranking.",
                "Playmaker": "85th percentile or higher in assists per game.",
                "Rebounding Specialist": "90th percentile or higher in rebounds per game.",
                "All-Around Contributor": "75th percentile or higher in at least four All-Around stats.",
            }
            st.markdown("**All-Around badges**")
            st.write("The player header shows up to three All-Around badges.")
            for badge, rule in badge_rules.items():
                st.markdown(f"- {SCOUT_BADGES[badge]} **{badge}** — {rule}")
            st.markdown("**Defense & Rebounding badges**")
            for badge, (icon, requirements) in scouting.DEFENSIVE_BADGES.items():
                rule = " and ".join(
                    f"{cutoff}th percentile or higher in {scouting.DEFENSE[metric][0]}"
                    for metric, cutoff in requirements.items()
                )
                st.markdown(f"- {icon} **{badge}** — {rule}.")
            st.caption("Defensive Playmaker takes the place of Shot Blocker and Ball Hawk when earned.")


def scouting_defense_cohort(league, ratings_modified):
    if ratings_modified is None:
        return league
    ratings = table("scouting_ratings", ratings_modified)
    comparison = league.merge(
        ratings, on=["player_id", "season_start", "games", "minutes"], how="left",
        validate="one_to_one", suffixes=("", "_reconstructed"),
    )
    for metric in ("drtg", "netrtg"):
        if metric in league:
            comparison[metric] = comparison.pop(f"{metric}_reconstructed")
    return comparison


def scouting_page(seasons, teams, manifest):
    st.html(SCOUT_STYLE)
    st.header("Player Scouting Lab")
    available = sorted(seasons.loc[seasons.season_start >= 2023, "season"].unique(), reverse=True)
    if not available:
        st.info("No player seasons are available.")
        return

    season_col, team_col, player_col = st.columns([1, 1.25, 1.75])
    season = season_col.selectbox("Season", available, index=min(1, len(available) - 1), key="scout_season")
    season_rows = seasons[seasons.season.eq(season)]
    league = scouting.canonical(season_rows)
    provisional = False
    completed_start = manifest.get("latest_completed_start")
    if season == available[0] and completed_start is not None and int(season[:4]) > completed_start:
        counts = scouting_team_game_counts(manifest["version"]).get(season, {})
        provisional = any(counts.get(tid, 0) < 20 for tid in teams.team_id)
    min_games = 5 if provisional else 20
    team_lookup = teams.set_index("team_id")
    team_names = team_lookup.team_name.to_dict()
    stints = season_rows[season_rows.team_id.ne(0)]
    team_ids = sorted(stints.team_id.unique(), key=lambda tid: team_names.get(tid, str(tid)))
    team_id = team_col.selectbox(
        "Find by team", [0, *team_ids],
        format_func=lambda tid: "All teams" if tid == 0 else team_names.get(tid, f"Team {tid}"),
        key="scout_team",
    )
    roster = league
    if team_id:
        roster = league[league.player_id.isin(stints.loc[stints.team_id.eq(team_id), "player_id"])]
    roster = roster.sort_values("player_name").reset_index(drop=True)
    qualified = roster[roster.games.ge(min_games) & roster.mpg.ge(15)]
    leaders = qualified.points_pg.dropna()
    default_player = int(leaders.idxmax()) if not leaders.empty else 0
    with player_col:
        players = roster.set_index("player_id").player_name.to_dict()
        pid = st.selectbox("Search player", list(players), index=default_player,
                           format_func=players.get, key="scout_player") if players else None
    scouting_freshness(season, manifest)
    st.caption("The team filter finds players who appeared for that team. Stats combine all teams played for, and ranks compare across the league in the selected season.")
    if pid is None:
        st.info("No players match this selection.")
        return

    row = league[league.player_id.eq(pid)].iloc[0]
    version = manifest["version"]
    ratings_path = APP / "scouting_ratings.csv.gz"
    ratings_modified = ratings_path.stat().st_mtime_ns if ratings_path.exists() else None
    all_around = ranks(version, season, "All-Around", min_games, None, league).query("player_id == @pid")
    defense_league = scouting_defense_cohort(league, ratings_modified)
    defense_row = defense_league[defense_league.player_id.eq(pid)].iloc[0]
    defense = ranks(version, season, scouting.DEFENSE_LENS, min_games, ratings_modified, defense_league).query("player_id == @pid")
    if provisional:
        badges, defensive_badges = [], []
        all_around_summary = scouting.scouting_summary(all_around, row.player_name)
    else:
        badges, all_around_summary = scouting.report(all_around, row.player_name)
        defensive_badges = scouting.defensive_badges(defense)
    player_team_ids = set(stints.loc[stints.player_id.eq(pid), "team_id"])
    season_teams = []
    for tid in team_ids:
        if tid not in player_team_ids:
            continue
        name = escape(str(team_names.get(tid, f"Team {tid}")))
        accent = team_color(teams, tid)
        season_teams.append(
            f'<span class="scout-team-name"><span class="scout-team-dot" aria-hidden="true" '
            f'style="--team-accent:{accent}"></span>{name}</span>'
        )
    chips = []
    position, position_detail = scouting.starting_position(defense_row)
    identity = " · ".join(part for part in (" / ".join(season_teams), escape(position)) if part)
    identity_line = f'<p class="scout-team-position">{identity}</p>' if identity else ""
    for badge in badges:
        icon = SCOUT_BADGES[badge]
        chips.append(f'<span class="scout-chip" style="--accent:#526e7e">{icon} {badge}</span>')
    for badge in defensive_badges:
        icon, _ = scouting.DEFENSIVE_BADGES[badge]
        chips.append(f'<span class="scout-chip" style="--accent:#8b542f">{icon} {badge}</span>')
    st.html(
        f'<div class="scout-header"><div class="scout-identity">'
        f'<h3>{escape(row.player_name)}</h3>{identity_line}</div>'
        f'<div class="scout-badges">{"".join(chips)}</div></div>'
    )
    metrics = [
        ("GP", "Games played", row.games, ".0f"),
        ("MPG", "Minutes per game", row.mpg, ".1f"),
        ("PPG", "Points per game", row.points_pg, ".1f"),
        ("APG", "Assists per game", row.assists_pg, ".1f"),
    ]
    cards = []
    for label, definition, value, precision in metrics:
        number = format(value, precision) if pd.notna(value) else "—"
        cards.append(
            '<div class="scout-tile" style="--accent:#b54b1c">'
            f'<b>{label}</b><strong>{number}</strong><span>{definition}</span></div>'
        )
    st.html('<div class="scout-grid scout-cards">' + "".join(cards) + "</div>")
    st.subheader(f"{row.player_name} · League comparison")
    st.write(
        "Each percentile compares this player with eligible players in the same season. Most "
        "stats rank higher values first. Defensive Rating and Foul Avoidance rank lower raw values "
        "first, and volume stats show how often something happens."
    )
    if provisional:
        st.warning(
            "**Early-season rankings.** The minimum to qualify drops from 20 games played to 5, "
            "with at least 15 minutes per game played. With so few games, percentiles can be "
            "misleading and change sharply after a single game."
        )
    lens = st.segmented_control(
        "Scouting lens", list(scouting.LENSES), default="All-Around",
        selection_mode="single", key="scout_lens", width="stretch",
    ) or "All-Around"
    breakdown = all_around
    report_title = "All-around scouting report"
    summary = all_around_summary
    if lens == scouting.DEFENSE_LENS:
        breakdown = defense
        row = defense_row
        report_title = "Defensive scouting report"
        summary = scouting.defense_report(breakdown, row.player_name)
    elif lens != "All-Around":
        breakdown = ranks(version, season, lens, min_games, None, league).query("player_id == @pid")
        report_title = f"{lens} scouting report"
        summary = scouting.scouting_summary(breakdown, row.player_name)
    player_stints = stints[stints.player_id.eq(pid)]
    primary_stint = player_stints.nlargest(1, "minutes")
    color = team_color(teams, primary_stint.team_id.iloc[0]) if not primary_stint.empty else "#b54b1c"
    show_chart(
        scouting.radar(breakdown, color=color, show_crowns=not provisional, player_name=row.player_name),
        use_container_width=True, theme=None,
    )
    st.markdown(f"**{report_title}**")
    st.write(summary)
    if lens == scouting.DEFENSE_LENS:
        st.caption("Steals and blocks capture specific plays. On-court ratings also reflect teammates and lineups.")
    st.markdown("**Stat by stat**")
    legend = [(85, "85 and above"), (50, "50 to below 85"), (30, "30 to below 50"),
              (0, "Below 30"), (np.nan, "Unranked")]
    legend_labels = [
        f'<span class="scout-chip" style="--accent:{scouting.percentile_color(value)}">{label}</span>'
        for value, label in legend
    ]
    st.html('<div class="scout-legend">' + "".join(legend_labels) + "</div>")
    scouting_metric_cards(breakdown, row, min_games=min_games, show_crowns=not provisional)
    scouting_advanced_stats(row)
    if position_detail:
        with st.expander("Position details"):
            st.write(position_detail)
    scouting_sources()


IMPACT_STYLE = """
<style>
.stMainBlockContainer {padding-top:3.75rem;}
.impact-identity {text-align:center; margin:1rem 0;}
.impact-identity h3 {margin:0; padding:0; font-size:clamp(1.55rem,4vw,2.25rem);}
.impact-identity p {margin:.25rem 0 0;}
.impact-team-dot {display:inline-block; width:.62em; height:.62em; border-radius:50%;
    background:var(--accent); margin-inline-end:.4em; vertical-align:.04em;}
.impact-grid {display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.65rem;}
.impact-tile {border:1px solid color-mix(in srgb,var(--accent) 35%,transparent);
    border-inline-start:4px solid var(--accent); border-radius:.65rem; padding:.75rem .9rem;
    background:color-mix(in srgb,var(--accent) 8%,transparent);}
.impact-tile strong {display:block; font-size:1.5rem;}
.impact-tile p {margin:.25rem 0 0; font-size:.86rem;}
.impact-stint-key {display:flex; flex-wrap:wrap; gap:.45rem 1rem; font-size:.9rem;}
.impact-stint-key span {display:inline-flex; align-items:center; gap:.35rem;}
.impact-stint-key b {display:inline-flex; align-items:center; justify-content:center;
    box-sizing:border-box; flex:0 0 1.35rem; width:1.35rem; height:1.35rem;
    padding:0; line-height:1; border:2px solid var(--accent); border-radius:50%;
    background:#fffdf8; color:#202c36;}
.impact-stint-key small {font-size:.85em;}
@media(max-width:640px) {
    .impact-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
    .impact-grid .impact-tile:last-child {grid-column:1/-1;}
}
</style>
"""


def impact_cards(cards):
    tiles = []
    for label, value, unit, context, color in cards:
        tiles.append(
            f'<div class="impact-tile" style="--accent:{color}">'
            f'<b>{label}</b><strong>{value}</strong><span>{unit}</span><p>{context}</p></div>'
        )
    st.html(f'<div class="impact-grid">{"".join(tiles)}</div>')


@st.cache_data(show_spinner=False)
def impact_player_games(version):
    columns = ["game_id", "player_id", "team_id", "season", "date", "played", "minutes", "plus_minus"]
    return pd.read_csv(APP / "player_games.csv.gz", usecols=columns, parse_dates=["date"])


def impact_trend(season, pid, tid, team_games, version, color):
    st.subheader("On/Off over time")
    st.write(
        "See how the team's on-court and bench margins changed as the season progressed. "
        "Each point uses the last 10 appearances with usable box scores, starting after five."
    )
    player_games = impact_player_games(version)
    stint = player_games.loc[
        player_games.season.eq(season) & player_games.player_id.eq(pid) & player_games.team_id.eq(tid)
    ]
    trend = impact.rolling_margins(stint, team_games)
    if trend.empty:
        st.info("This team stint needs at least five appearances with usable box scores to show a trend.")
        return
    show_chart(impact.trend_chart(trend, color), use_container_width=True)
    st.caption("Each line uses the total point margin and minutes in that stretch. Games with more minutes carry more weight.")


def impact_league_comparison(season_rows, teams, pid, tid, min_games=20):
    from html import escape

    st.subheader("Compare with other players")
    st.caption("Each ranking is for one player and team stint. The filter applies to the league comparison below.")
    minimum = st.slider("Minimum on-court minutes", 0, 2500, 500, 100, key="impact_peer_minutes")
    st.caption(
        f"To appear in the scatterplot and table, a player needs {min_games} games played for that team, "
        f"at least {minimum:,} on-court minutes, and scoring margins for both on-court and bench minutes."
    )
    if min_games == 5:
        st.warning(
            "**Early-season comparisons.** The game minimum drops from 20 to 5 until the snapshot "
            "includes 20 games for every team. A few games can swing on/off margins and ranks sharply."
        )
    peers = impact.scout_peers(season_rows, minimum, pid, tid, min_games=min_games)
    if peers.empty:
        enough_games = season_rows.games.ge(min_games)
        enough_minutes = season_rows.minutes_on.ge(minimum)
        if not enough_games.any():
            reason = f"No player has played {min_games} games for one team in this snapshot."
        elif not (enough_games & enough_minutes).any():
            reason = "No stint that meets the game minimum reaches this minutes cutoff. Try lowering the slider."
        else:
            reason = "The stints that meet the game and minutes minimums lack a usable on-court or bench margin."
        st.info(f"No scatterplot or table to show. {reason}")
        return
    team_lookup = teams.set_index("team_id")
    peers["team_name"] = peers.team_id.map(team_lookup.team_name).fillna("Team unavailable")
    peers["team_accent"] = peers.team_id.map(team_lookup.team_code).map(COLORS).fillna("#db7335")
    peers["stint_label"] = peers.player_name + " · " + peers.team_name
    player_stints = peers.loc[peers.player_id.eq(pid)].sort_values(["team_name", "team_id"])
    numbers = dict(zip(player_stints.team_id, range(1, len(player_stints) + 1)))
    peers["stint_number"] = peers.team_id.map(numbers).where(peers.player_id.eq(pid)).astype("Int64")
    selected = peers.loc[peers.selected]
    st.caption(f"{len(peers):,} qualifying team stints across the league")
    if selected.empty:
        st.caption("The selected team stint is outside this comparison group.")
    else:
        rank = selected.iloc[0]["rank"]
        st.write(f"**Selected team stint: #{rank} of {len(peers):,}**")
    st.write(
        "**Read the scatterplot:** Each dot is one player's team stint. Farther right means a higher "
        "bench margin. Farther up means a higher on-court margin. "
        "Above the dotted line, the on-court margin was higher. Below it, the bench margin was higher."
    )
    if numbers:
        entries = []
        for stint in player_stints.itertuples():
            context = "<small>· Shown above</small>" if stint.team_id == tid else ""
            entries.append(
                f'<span><b style="--accent:{stint.team_accent}">{numbers[stint.team_id]}</b>'
                f'{escape(stint.team_name)}{context}</span>'
            )
        st.html(f'<div class="impact-stint-key" aria-label="Numbered team stints">{"".join(entries)}</div>')
    show_chart(impact.scatter(peers, pid, tid), use_container_width=True)
    st.markdown("**Top 8 on/off differences, plus the selected player**")
    st.caption("Ranked by **On/off per 48**: the team's point margin with the player on the court minus "
               "its margin with the player on the bench. The highlighted row is the player you picked.")
    top = peers.head(8)
    leaders = pd.concat([top, selected]).drop_duplicates(["player_id", "team_id"]).reset_index(drop=True)
    display = pd.DataFrame({
        "Rank": leaders["rank"].map(lambda value: f"#{value}"),
        "Player · team": leaders.stint_label.where(~leaders.selected, "★ " + leaders.stint_label),
        "On/off per 48 ▼": leaders.on_off_diff.map(impact.signed_margin),
        "On court per 48": leaders.on_per48.map(impact.signed_margin),
        "On bench per 48": leaders.off_per48.map(impact.signed_margin),
        "Minutes on / bench": [f"{on:,.0f} / {off:,.0f}" for on, off in zip(leaders.minutes_on, leaders.minutes_off)],
    })
    outside_top = not selected.empty and not top.selected.any()
    html_table(display, numeric={"On/off per 48 ▼", "On court per 48", "On bench per 48", "Minutes on / bench"},
               highlight=leaders.selected.tolist(), gap_before=len(top) if outside_top else None)


def impact_page(impacts, teams, manifest):
    from html import escape

    st.html(IMPACT_STYLE)
    st.header("On/Off Impact")
    st.write(
        "See how a team scored relative to its opponents with a player on the court and on the bench. "
        "Pick a season and player to see how those margins changed over time and how they compare across the league."
    )
    available = sorted(impacts.loc[impacts.season_start.ge(2023), "season"].unique(), reverse=True)
    if not available:
        st.info("No on/off seasons are available.")
        return

    season_col, team_col, player_col = st.columns([1, 1.25, 1.75])
    season = season_col.selectbox("Season", available, index=min(1, len(available) - 1), key="impact_season")
    season_rows = impacts.loc[impacts.season.eq(season)]
    lookup = teams.set_index("team_id").team_name.to_dict()

    def team_name(tid):
        return lookup.get(tid, f"Team {tid}")

    team_ids = sorted(season_rows.team_id.unique(), key=team_name)
    team_filter = team_col.selectbox(
        "Find by team", [0, *team_ids], key="impact_team_filter",
        format_func=lambda tid: team_name(tid) if tid else "All teams",
    )
    roster = season_rows if team_filter == 0 else season_rows.loc[season_rows.team_id.eq(team_filter)]
    with player_col:
        pid = choose(roster, "impact_player", "Search player")
    if pid is None:
        st.info("No players match the selected season and team.")
        return

    player_rows = season_rows.loc[season_rows.player_id.eq(pid)].sort_values("minutes_on", ascending=False)
    stints = player_rows.team_id.tolist()
    tid = stints[0]
    if len(stints) > 1:
        default = stints.index(team_filter) if team_filter in stints else 0
        tid = st.selectbox(
            "Team stint", stints, index=default, format_func=team_name,
            key=f"impact_stint_{season}_{pid}_{team_filter}",
            help="Switch teams to see results for that team only.",
        )
    row = player_rows.loc[player_rows.team_id.eq(tid)].iloc[0]
    color = team_color(teams, tid)
    version = manifest["version"]
    team_games = table("team_games", version)
    min_games = 20
    completed_start = manifest.get("latest_completed_start")
    if season == available[0] and completed_start is not None and int(season[:4]) > completed_start:
        counts = team_games.loc[team_games.season.eq(season)].groupby("team_id").game_id.nunique()
        if counts.reindex(teams.team_id, fill_value=0).lt(20).any():
            min_games = 5
    latest = team_games.loc[team_games.season.eq(season) & team_games.team_id.eq(tid), "date"].max()
    if pd.notna(latest):
        st.caption(f"{team_name(tid)} team games included through {latest:%b} {latest.day}, {latest.year}.")
    st.html(
        f'<div class="impact-identity"><h3>{escape(row.player_name)}</h3>'
        f'<p><span class="impact-team-dot" style="--accent:{color}" aria-hidden="true"></span>'
        f'{escape(team_name(tid))} · {escape(season)}</p></div>'
    )

    st.subheader("On court vs. on bench")
    st.write("Team point margin per 48 minutes, using games the player appeared in.")
    on_minutes = f"{row.minutes_on:,.0f} minutes on court" if pd.notna(row.minutes_on) else "Minutes unavailable"
    off_minutes = f"{row.minutes_off:,.0f} minutes on bench" if pd.notna(row.minutes_off) else "Minutes unavailable"
    games_used = f"{row.valid_on_games:,.0f} of {row.games:,.0f} played games used"
    impact_cards([
        ("On court", impact.signed_margin(row.on_per48), "Points per 48", on_minutes, color),
        ("On bench", impact.signed_margin(row.off_per48), "Points per 48", off_minutes, "#637783"),
        ("On/Off difference", impact.signed_margin(row.on_off_diff), "Points per 48", games_used, "#b54b1c"),
    ])
    if pd.notna(row.on_per48) or pd.notna(row.off_per48):
        show_chart(impact.margin_bars(row, color), use_container_width=True)
    st.write(impact.court_summary(row))
    if row.reliability == "Low":
        st.info("Sample size: Limited. A short stretch on either side can make this comparison swing.")
    elif pd.notna(row.reliability):
        sample = "Large" if row.reliability == "High" else "Moderate"
        st.caption(f"Sample size: {sample} · {games_used}")
    st.caption("Teammates, opponents, and game situations also affect these margins.")

    impact_trend(season, pid, tid, team_games, version, color)
    impact_league_comparison(season_rows, teams, pid, tid, min_games=min_games)
    with st.expander("How to read On/Off Impact"):
        st.markdown(
            f"""
- **Team point margin** — Points scored minus points allowed. A positive margin means the team outscored opponents.
- **Per 48 minutes** — Divide the total point margin by the minutes in each group and multiply by 48. Both groups use the same scale.
- **On/Off difference** — The on-court margin minus the bench margin. Both groups use games the player appeared in with usable minutes and scoring data.
- **Sample size** — Limited means under 500 minutes on court or under 250 on the bench, or minutes are unavailable. Large means at least 1,500 on court and 500 on the bench. Everything in between is Moderate.
- **Trend** — Each point uses up to 10 recent appearances for the selected team. It starts after five usable games. A missing line means there were no usable minutes for that side of the comparison.
- **What to take away** — These comparisons describe team results in the minutes and games covered. Rotations, teammates, and opponents all influence them. [Historical NBA box scores]({SOURCE_NBA})
            """
        )


TEAM_FORECAST_STYLE = """
<style>
.stMainBlockContainer {padding-top:3.75rem;}
.forecast-scoreboard,.forecast-form-cards {display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.7rem;}
.forecast-side {min-width:0; padding:.8rem 1rem; border:1px solid color-mix(in srgb,var(--accent) 35%,transparent);
    border-top:4px solid var(--accent); border-radius:.7rem;
    background:color-mix(in srgb,var(--accent) 9%,transparent);}
.forecast-side h4 {margin:.2rem 0; padding:0; font-size:clamp(1rem,3vw,1.45rem);}
.forecast-side small {font-size:.85rem;}
.forecast-score {display:block; font-size:clamp(1.7rem,5vw,2.7rem); line-height:1.15;}
.forecast-chance {display:block; margin-top:.4rem;}
.forecast-team-heading {display:flex;flex-wrap:wrap;align-items:center;gap:.2rem .45rem;}
.forecast-favorite {display:inline-block;padding:.12rem .45rem;border-radius:999px;
    border:1px solid color-mix(in srgb,var(--accent) 60%,transparent);
    background:color-mix(in srgb,var(--accent) 15%,transparent);font-size:.78rem;font-weight:600;}
.forecast-scoreboard .forecast-side {border-top-width:1px;border-inline-start:4px solid var(--accent);}
.forecast-result {background:color-mix(in srgb,currentColor 5%,transparent);
    border:1px solid #8794a455;border-radius:.65rem;padding:.65rem .85rem;}
.forecast-result-scores {display:flex;flex-wrap:wrap;align-items:center;gap:.25rem .65rem;font-size:.95rem;}
.forecast-winner {font-weight:700;}
.forecast-winner-label {margin-inline-start:.3rem;font-size:.78rem;color:var(--result-win);}
.forecast-final-heading {display:flex;flex-wrap:wrap;align-items:center;gap:.35rem .65rem;margin-bottom:.35rem;}
.forecast-final-heading h4 {margin:0;padding:0;}
.forecast-verdict {border:1px solid #8794a466;border-radius:999px;padding:.15rem .5rem;font-size:.8rem;font-weight:600;}
.forecast-verdict[data-result="correct"] {--badge-color:var(--result-win);}
.forecast-verdict[data-result="missed"] {--badge-color:var(--result-miss);}
.forecast-verdict[data-result] {color:var(--badge-color,currentColor);
    background:color-mix(in srgb,var(--badge-color,currentColor) 12%,transparent);
    border-color:color-mix(in srgb,var(--badge-color,currentColor) 55%,transparent);}
.forecast-total {display:block;margin-top:.4rem;}
.forecast-margin-key {display:flex;flex-wrap:wrap;gap:.45rem .65rem;margin:.2rem 0 .45rem;}
.forecast-margin-key > span {display:inline-flex;align-items:center;gap:.45rem;
    border:1px solid #8794a466;border-radius:.5rem;padding:.2rem .4rem;font-size:.82rem;}
.forecast-margin-symbol {color:var(--cue);font-weight:700;min-width:1em;text-align:center;}
.forecast-form-record {display:block; font-size:1.4rem;}
.forecast-form-coverage {display:block; margin-top:.35rem;}
.forecast-win-bar {display:flex; height:.65rem; margin:.7rem 0 0; border-radius:999px; overflow:hidden;
    background:#f3eee4;}
.forecast-win-bar span {display:block; flex:none; height:100%;}
.forecast-win-bar span+span {border-inline-start:2px solid #fffdf8; box-sizing:border-box;}
:is(.st-key-team_swap_sides,.st-key-player_swap_sides) {width:100%; display:flex; justify-content:center; margin-top:1.75rem;}
:is(.st-key-team_swap_sides,.st-key-player_swap_sides) [data-testid="stTooltipHoverTarget"] {justify-content:center !important;}
:is(.st-key-team_swap_sides,.st-key-player_swap_sides) button {position:relative; width:2.4rem; height:2.5rem; min-width:0; padding:.35rem;}
:is(.st-key-team_swap_sides,.st-key-player_swap_sides) button > span {
    position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); margin:0;
}
:is(.st-key-team_swap_sides,.st-key-player_swap_sides) button [data-testid="stMarkdownContainer"] {
    position:absolute; width:1px; height:1px; overflow:hidden; clip-path:inset(50%); white-space:nowrap;
}
@media(max-width:640px) {
    .forecast-side {padding:.65rem;}
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] :is(.st-key-team_swap_sides,.st-key-player_swap_sides)) {
        flex-wrap:wrap; gap:.45rem;
    }
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] :is(.st-key-team_swap_sides,.st-key-player_swap_sides))
        > [data-testid="stColumn"] {width:auto; min-width:0; flex:1 1 0;}
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] :is(.st-key-team_swap_sides,.st-key-player_swap_sides))
        > [data-testid="stColumn"]:nth-child(2) {flex:0 0 2.4rem;}
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] :is(.st-key-team_swap_sides,.st-key-player_swap_sides))
        > [data-testid="stColumn"]:last-child {flex:1 0 100%;}
}
</style>
"""


def forecast_margin_label(margin, home, away, digits=1):
    points = round(abs(margin), digits)
    if not points:
        return "Tie"
    team = home if margin > 0 else away
    return f"{team} by {points:.{digits}f}"


def forecast_scoreboard(result, home, away, colors):
    from html import escape

    cards = []
    for side, name in (("away", away), ("home", home)):
        score = result[f"{side}_score"]
        probability = result[f"{side}_win"]
        other_side = "home" if side == "away" else "away"
        favorite = (
            '<span class="forecast-favorite"><span aria-hidden="true">🎯</span> Predicted winner</span>'
            if probability > result[f"{other_side}_win"] else ""
        )
        cards.append(
            f'<article class="forecast-side" style="--accent:{colors[name]}">'
            f'<small>{side.title()}</small><div class="forecast-team-heading"><h4>{escape(name)}</h4>{favorite}</div>'
            f'<strong class="forecast-score">{score:.1f}</strong><small>Projected points</small>'
            f'<b class="forecast-chance">{probability:.1%} win chance</b></article>'
        )
    st.html(
        '<div class="forecast-scoreboard">' + "".join(cards) + '</div>'
        '<div class="forecast-win-bar" aria-hidden="true">'
        f'<span style="width:{result["away_win"]:.6%};background:{colors[away]}"></span>'
        f'<span style="width:{result["home_win"]:.6%};background:{colors[home]}"></span></div>'
        f'<small class="forecast-total">Projected total · <b>{result["total"]:.1f} points</b></small>'
    )


def forecast_margin_chart(result, home, away, colors, actual_margin=None, spread=None):
    import plotly.graph_objects as go

    margin = result["margin"]
    low = result["distribution"]["low"]
    high = result["distribution"]["high"]
    market_margin = -spread if spread is not None else None
    positions = [low, high, margin, actual_margin, market_margin]
    extent = max(4, *(abs(value) for value in positions if value is not None)) * 1.15
    neutral = DARK_CHART["text"] if dark() else "#526570"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[low, high], y=[0, 0], mode="lines+markers",
        line=dict(color=neutral, width=4), marker=dict(size=8),
        text=[forecast_margin_label(value, home, away, 0) for value in (low, high)],
        hovertemplate="%{text}<extra>80% range endpoint</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[margin], y=[0], mode="markers",
        marker=dict(symbol="diamond", size=13, color=colors[home if margin >= 0 else away]),
        hovertemplate=f"{forecast_margin_label(margin, home, away)}<extra>Projected margin</extra>",
    ))
    rows = ["Forecast"]
    if actual_margin is not None:
        rows.append("Actual")
        fig.add_trace(go.Scatter(
            x=[actual_margin], y=[-1], mode="markers",
            marker=dict(symbol="circle", size=15, color=forecast_result_colors()[0]),
            name="Actual",
            hovertemplate=f"{forecast_margin_label(actual_margin, home, away, 0)}<extra>Actual margin</extra>",
        ))
    if market_margin is not None:
        near_marker = min(abs(market_margin - value) for value in (margin, low, high)) < extent * .07
        fig.add_trace(go.Scatter(
            x=[market_margin], y=[.25 if near_marker else 0], mode="markers",
            marker=dict(symbol="square-open", size=12, color=neutral),
            name="Spread", hovertemplate=f"{home} {spread:+g}<extra>Home spread</extra>",
        ))
    fig.update_yaxes(
        tickvals=list(range(0, -len(rows), -1)), ticktext=rows,
        range=[.45 - len(rows), .55], fixedrange=True, showgrid=False, zeroline=False,
    )
    fig.add_vline(x=0, line_color="#697681", line_dash="dot")
    fig.update_xaxes(range=[-extent, extent], title_text="Away advantage  ←  Point margin  →  Home advantage",
                     tickformat=".0f")
    fig.update_layout(height=155 + 36 * (len(rows) - 1), margin=dict(l=68, r=16, t=12, b=48), showlegend=False)
    return fig


def forecast_margin_key(result, home, away, projection_color, actual_margin, spread):
    margin = result["margin"]
    dist = result["distribution"]
    low, high = (forecast_margin_label(dist[edge], home, away, 0) for edge in ("low", "high"))
    neutral = DARK_CHART["text"] if dark() else "#526570"
    entries = [
        ("◆", "Projected", forecast_margin_label(margin, home, away), projection_color),
        ("━", "80% range", f"{low} to {high}", neutral),
    ]
    if actual_margin is not None:
        entries.append(("●", "Actual", forecast_margin_label(actual_margin, home, away, 0), forecast_result_colors()[0]))
    if spread is not None:
        entries.append(("□", "Spread", f"{home} {spread:+g}", neutral))
    entries.append(("⋮", "Even score", "0 points", "#8b969e"))
    items = "".join(
        f'<span><span class="forecast-margin-symbol" style="--cue:{color}" aria-hidden="true">{symbol}</span>'
        f'<span><b>{escape(label)}</b> · {escape(value)}</span></span>'
        for symbol, label, value, color in entries
    )
    st.html(f'<div class="forecast-margin-key" aria-label="Point margin chart key">{items}</div>')


def team_recent_form(team_games, home_id, away_id, when, names, colors):
    from html import escape

    st.subheader("Recent form")
    st.caption("Each team’s games against any opponent before the matchup date. Above zero means the team outscored its opponent.")
    window = st.radio(
        "Recent games per team", [5, 10, 20], format_func=lambda count: f"Last {count}",
        key="team_recent_window", horizontal=True,
    )
    history = team_games.loc[
        team_games.date.lt(pd.Timestamp(when)) & team_games.team_id.isin([away_id, home_id])
    ]
    recent = history.sort_values("date").groupby("team_id").tail(window).copy()
    if recent.empty:
        st.info("No earlier box scores are available for these teams in this snapshot.")
        return
    recent["team_name"] = recent.team_id.map(names)
    opponents = recent.opponent_id.map(names).fillna("Unknown opponent")
    recent["opponent"] = recent.home.map({1: "vs. ", 0: "at "}).fillna("") + opponents
    recent["game_result"] = [
        f"{'W' if game.points > game.opp_points else 'L'} {game.points:.0f}–{game.opp_points:.0f}"
        if pd.notna(game.points) and pd.notna(game.opp_points) else "Final score unavailable"
        for game in recent.itertuples()
    ]
    cards = []
    for team_id in (away_id, home_id):
        team = recent.loc[recent.team_id.eq(team_id)]
        name = names[team_id]
        count = len(team)
        wins = int(team.win.sum())
        record = f"{wins}–{count - wins}" if count else "Unavailable"
        margin = team.margin.mean()
        average = f"Average margin: {impact.signed_margin(margin)} pts" if pd.notna(margin) else "Average margin unavailable"
        coverage = f"{count} of {window} games available" if count < window else f"{count} games"
        cards.append(
            f'<article class="forecast-side" style="--accent:{colors[name]}">'
            f'<h4>{escape(name)}</h4><strong class="forecast-form-record">{record}</strong>'
            f'<span>{average}</span><small class="forecast-form-coverage">{coverage}</small></article>'
        )
    st.html('<div class="forecast-form-cards">' + "".join(cards) + "</div>")
    fig = px.line(
        recent, x="date", y="margin", color="team_name", markers=True, color_discrete_map=colors,
        line_dash="team_name", line_dash_map={names[away_id]: "dash", names[home_id]: "solid"},
        custom_data=["team_name", "opponent", "game_result"],
        labels={"date": "Game date", "team_name": "Team", "margin": "Scoring margin (points)"},
    )
    fig.update_traces(
        hovertemplate="<b>%{customdata[0]} %{customdata[1]}</b><br>"
                      "%{x|%b %d, %Y}<br>"
                      "%{customdata[2]} · Margin %{y:+.0f} pts<extra></extra>"
    )
    fig.add_hline(y=0, line_color="#697681", line_dash="dot")
    fig.update_layout(height=350, margin=dict(l=45, r=15, t=40, b=52),
                      legend=dict(orientation="h", y=1.14, x=0))
    fig.update_yaxes(tickformat=".0f")
    show_chart(fig, use_container_width=True)


def forecast_matchup(names, version, latest, key="team", model_name="team"):
    mode = st.radio(
        "Find a matchup", ["Upcoming Games", "Past Games", "Custom Matchup"],
        key=f"{key}_matchup_mode", horizontal=True,
    )
    if mode != "Upcoming Games":
        try:
            tasks = bundle(model_name, version)["tasks"]
            cutoff = max(pd.Timestamp(task["inference_available_after"]) for task in tasks.values())
        except (ValueError, FileNotFoundError) as exc:
            st.warning(str(exc))
            return None
        earliest = cutoff.date() + timedelta(days=1)
        if mode == "Custom Matchup":
            return custom_matchup(names, key, latest, compact=True, earliest=earliest)

    today = pd.Timestamp(datetime.now(ZoneInfo("America/Chicago")).date())
    is_upcoming = mode == "Upcoming Games"
    if is_upcoming:
        fixtures = schedule_fixtures(names, version).sort_values(["date", "home_team_id"])
        games = fixtures.loc[fixtures.date.ge(today)]
        if games.empty:
            st.info("The schedule snapshot has no upcoming games. Choose Past Games or Custom Matchup above.")
            return None
        team_picker, dates_picker, game_picker = st.columns([1.15, 1, 2])
    else:
        recorded = table("games", version)
        games = recorded.loc[
            recorded.date.lt(today) & recorded.date.ge(pd.Timestamp(earliest))
            & recorded.home_team_id.isin(names) & recorded.away_team_id.isin(names)
            & recorded.home_points.notna() & recorded.away_points.notna()
        ].sort_values(["date", "home_team_id"])
        if games.empty:
            st.info("No recorded games in this snapshot fall within the model’s supported dates. Try Custom Matchup.")
            return None
        team_picker, opponent_picker = st.columns(2)
        game_picker = st

    if f"{key}_fixture_filter" not in st.session_state:
        st.session_state[f"{key}_fixture_filter"] = st.session_state.get(f"{key}_fixture_selection", 0)
    team_id = team_picker.selectbox(
        "Find by team", [0, *names], key=f"{key}_fixture_filter",
        format_func=lambda tid: names[tid] if tid else "All teams",
    )
    st.session_state[f"{key}_fixture_selection"] = team_id
    if team_id:
        games = games.loc[games.home_team_id.eq(team_id) | games.away_team_id.eq(team_id)]
    if games.empty:
        kind = "upcoming" if is_upcoming else "recorded past"
        game_picker.info(f"No {kind} games for this team are in the snapshot. Try All teams or Custom Matchup.")
        return None

    if is_upcoming:
        limit = dates_picker.selectbox(
            "Dates to show", [3, 7, 14, 30, "all"], key=f"{key}_upcoming_limit",
            format_func=lambda count: "All scheduled dates" if count == "all" else f"Next {count} game days",
        )
        days = games.date.drop_duplicates()
        if limit != "all":
            days = days.head(limit)
        slate = games.loc[games.date.isin(days)].set_index("game_id")
        labels = {
            gid: f"{row.date:%b} {row.date.day} · {names[row.away_team_id]} at {names[row.home_team_id]}"
            for gid, row in slate.iterrows()
        }
        game_id = game_picker.selectbox("Upcoming matchup", list(labels), format_func=labels.get, key=f"{key}_upcoming_game")
        st.caption(f"Showing {len(days)} game {'date' if len(days) == 1 else 'dates'} in the schedule snapshot.")
    else:
        opponent = 0
        if team_id:
            opponents = set(games.loc[games.home_team_id.eq(team_id), "away_team_id"])
            opponents.update(games.loc[games.away_team_id.eq(team_id), "home_team_id"])
            opponent = opponent_picker.selectbox(
                "Opponent", [0, *sorted(opponents, key=names.get)], key=f"{key}_past_opponent_{team_id}",
                format_func=lambda tid: names[tid] if tid else "Any opponent",
                help="Includes meetings at either team's home court.",
            )
            if opponent:
                games = games.loc[games.home_team_id.eq(opponent) | games.away_team_id.eq(opponent)]
        month_picker, day_picker = st.columns(2)
        game_picker = st.container()
        months = games.date.dt.strftime("%Y-%m")
        month_options = sorted(months.unique(), reverse=True)
        previous_month = st.session_state.get(f"{key}_past_month")
        previous_day = st.session_state.get(f"{key}_past_date")
        filters = (team_id, opponent)
        changed_filter = st.session_state.get(f"{key}_past_last_filter") != filters
        if previous_month not in month_options or (
            changed_filter and previous_day is not None and not games.date.eq(pd.Timestamp(previous_day)).any()
        ):
            previous_month = month_options[0]
        st.session_state[f"{key}_past_last_filter"] = filters
        st.session_state[f"{key}_past_month"] = previous_month
        month = month_picker.selectbox(
            "Month", month_options,
            format_func=lambda value: pd.Period(value, freq="M").strftime("%B %Y"), key=f"{key}_past_month",
        )
        month_games = games.loc[months.eq(month)]
        game_counts = month_games.groupby(month_games.date.dt.date).game_id.nunique().sort_index(ascending=False)
        days = {
            day: f"{day:%b} {day.day} · {count} {'game' if count == 1 else 'games'}"
            for day, count in game_counts.items()
        }
        st.session_state[f"{key}_past_date"] = previous_day if previous_day in days else next(iter(days))
        day = day_picker.selectbox("Game day", list(days), format_func=days.get, key=f"{key}_past_date")
        slate = month_games.loc[month_games.date.eq(pd.Timestamp(day))].set_index("game_id")
        labels = {gid: f"{names[row.away_team_id]} at {names[row.home_team_id]}" for gid, row in slate.iterrows()}
        game_id = game_picker.selectbox("Matchup", list(labels), format_func=labels.get, key=f"{key}_past_game")
    selected = slate.loc[game_id]
    return selected.home_team_id, selected.away_team_id, selected.date.date()


def team_forecast_matchup(names, version, latest):
    return forecast_matchup(names, version, latest, "team", "team")


def team_actual_result(version, home_id, away_id, when):
    today = datetime.now(ZoneInfo("America/Chicago")).date()
    if when >= today:
        return None
    games = table("games", version)
    matches = games.loc[
        games.date.eq(pd.Timestamp(when)) & games.home_team_id.eq(home_id) & games.away_team_id.eq(away_id)
        & games.home_points.notna() & games.away_points.notna() & games.home_points.ne(games.away_points)
    ]
    return matches.iloc[0] if len(matches) == 1 else None


def forecast_result_colors():
    return ("#7fdfbe", "#ffb68b") if dark() else ("#12694f", "#9a3c14")


def forecast_actual_score(actual, home, away, forecast):
    winner = home if actual.home_points > actual.away_points else away
    scores = []
    for name, points in ((away, actual.away_points), (home, actual.home_points)):
        score = f"{escape(name)} {points:.0f}"
        if name == winner:
            score = f'<strong class="forecast-winner">{score}<small class="forecast-winner-label">Winner</small></strong>'
        scores.append(f"<span>{score}</span>")
    score_line = '<span aria-hidden="true">·</span>'.join(scores)
    verdict = ""
    outcome = "even"
    if forecast is not None:
        home_chance, away_chance = forecast["home_win"], forecast["away_win"]
        if home_chance == away_chance:
            verdict = "Equal win chances"
        else:
            favorite = home if home_chance > away_chance else away
            correct = favorite == winner
            outcome = "correct" if correct else "missed"
            verdict = "✓ Model correctly picked the winner" if correct else "✕ Model picked the wrong winner"
    badge = f'<span class="forecast-verdict" data-result="{outcome}">{verdict}</span>' if verdict else ""
    win_color, miss_color = forecast_result_colors()
    st.html(
        f'<div class="forecast-result" style="--result-win:{win_color};--result-miss:{miss_color}">'
        f'<div class="forecast-final-heading"><h4>Final score</h4>{badge}</div>'
        f'<div class="forecast-result-scores">{score_line}</div></div>'
    )


@st.cache_data(show_spinner=False)
def team_market_record(version):
    """Held-out 2025-26 forecasts scored against historical betting lines for the same games."""
    def backtest(name, prefix):
        frame = table(f"backtest_team_{name}", version).query("period == 'test'")
        return frame[["game_id", "actual", "prediction"]].rename(
            columns={"actual": f"{prefix}_actual", "prediction": f"{prefix}_pred"})

    games = backtest("margin", "margin").merge(backtest("total", "total"), on="game_id").merge(
        backtest("home_win", "win"), on="game_id")
    odds = table("odds_history", version)[["game_id", "spread_home", "total_line"]]
    games = games.merge(odds, on="game_id", how="left", validate="one_to_one")
    record = {"n": len(games), "season": str(table("backtest_team_margin", version).query("period == 'test'").season.iloc[0]),
              "winner": float(((games.win_pred >= .5) == games.win_actual.eq(1)).mean())}
    lined = games.loc[games.spread_home.notna()]
    favorite = lined.spread_home.ne(0)
    record["market_winner"] = float((np.sign(-lined.spread_home[favorite]) == np.sign(lined.margin_actual[favorite])).mean())
    record["margin_mae"] = float((games.margin_actual - games.margin_pred).abs().mean())
    record["market_margin_mae"] = float((lined.margin_actual + lined.spread_home).abs().mean())
    record["total_mae"] = float((games.total_actual - games.total_pred).abs().mean())
    totals = games.loc[games.total_line.notna()]
    record["market_total_mae"] = float((totals.total_actual - totals.total_line).abs().mean())
    covered = lined.margin_actual + lined.spread_home
    pick = lined.margin_pred + lined.spread_home
    ats = covered.ne(0) & pick.ne(0)
    record["ats"] = float(((covered > 0) == (pick > 0))[ats].mean())
    record["ats_n"] = int(ats.sum())
    over = totals.total_actual - totals.total_line
    lean = totals.total_pred - totals.total_line
    ou = over.ne(0) & lean.ne(0)
    record["ou"] = float(((over > 0) == (lean > 0))[ou].mean())
    record["ou_n"] = int(ou.sum())
    return record


def evaluation_downloads(prefix):
    path = APP / "evaluation.json"
    with st.popover("Download the full evaluation"):
        baseline = APP / "baselines.json"
        if baseline.exists():
            st.download_button("Baseline comparison", json.dumps(json.loads(baseline.read_text()).get(prefix), indent=2),
                               file_name=f"{prefix}_baselines.json")
        if path.exists():
            st.download_button("Model evaluation", json.dumps(
                {k: v for k, v in json.loads(path.read_text()).items() if k.startswith(prefix)}, indent=2),
                file_name=f"{prefix}_evaluation.json")
        market = APP / "market_evaluation.json"
        if prefix == "team" and market.exists():
            st.download_button("Historical market comparison", market.read_text(), file_name=market.name)


def team_accuracy(version):
    needed = [APP / f"backtest_team_{name}.csv.gz" for name in ("margin", "total", "home_win")] + [APP / "odds_history.csv.gz"]
    if not all(path.exists() for path in needed):
        return
    with st.expander("How accurate are these forecasts?"):
        r = team_market_record(version)
        st.write(f"We tested the model on all {r['n']:,} games of the {r['season']} season. "
                 "It never saw these games while it was being built, so this is a fair test.")
        html_table(pd.DataFrame({
            "Check": ["Picked the winner", "Average miss on the final margin", "Average miss on total points",
                      "Against the spread (ATS) win rate", "Over/under win rate"],
            "CourtIQ model": [f"{r['winner']:.1%}", f"{r['margin_mae']:.1f} pts", f"{r['total_mae']:.1f} pts",
                              f"{r['ats']:.1%} of {r['ats_n']:,}", f"{r['ou']:.1%} of {r['ou_n']:,}"],
            "Betting lines": [f"{r['market_winner']:.1%} (favorite)", f"{r['market_margin_mae']:.1f} pts (spread)",
                              f"{r['market_total_mae']:.1f} pts (total)", "—", "—"],
        }), numeric={"CourtIQ model", "Betting lines"})
        st.caption("ATS and over/under compare the model's projected margin and total with each game's betting line; "
                   "pushes are left out. At typical −110 odds a bettor needs about 52.4% to break even, so these "
                   "forecasts are not a betting edge. The historical betting file doesn't say whether its lines are "
                   "opening or closing (kickoff) lines.")
        evaluation_downloads("team")


@st.cache_data(show_spinner=False, max_entries=256)
def cached_team_forecast(version, model_modified, home, away, when, spread):
    from src.models import team

    return team.predict(table("team_games", version), home, away, when, spread,
                        model("team", version, model_modified))


def team_page(t, teams, version):
    st.html(TEAM_FORECAST_STYLE)
    st.header("Team Forecasts")
    page_intro("Pick any game to see each team's chance of winning and the projected final score.",
               ["Find a game", "Read the win chances and score", "Optional: add the home spread"])
    names = teams.set_index("team_id").team_name.to_dict()
    matchup_choice = team_forecast_matchup(names, version, t.date.max())
    if matchup_choice is None:
        return
    h, a, when = matchup_choice
    if st.session_state.get("team_matchup_mode") == "Past Games":
        st.caption(f"This forecast uses only box scores from games played before {when:%b} {when.day}, {when.year}.")
    else:
        st.caption(f"Forecast uses box scores before game day, available through {t.date.max():%b %d, %Y}.")
    home, away = names[h], names[a]
    home_color, away_color = pair_colors(teams, h, a)
    colors = {away: away_color, home: home_color}
    actual = team_actual_result(version, h, a, when)

    forecast_summary = st.container()
    spread_toggle, spread_input = st.columns([1, 1.3], vertical_alignment="bottom")
    margin_heading = spread_toggle.empty()
    use_spread = spread_toggle.toggle("Include home spread", key="team_use_spread",
                                      help="Adds a spread marker and each side’s chance to cover.")
    spread_value = spread_input.number_input(
        "Home spread", min_value=-60.0, max_value=60.0, value=-4.5, step=.5,
        key="team_spread", disabled=not use_spread,
        help="Enter a spread from −60 to +60. At −4.5, the home team must win by 5 or more to cover.",
    )
    spread = spread_value if use_spread else None

    result = None
    progress = forecast_summary.progress(0, text="Loading the forecast model…")
    try:
        model_path = APP.parent / "artifacts" / "team.pkl"
        modified = model_path.stat().st_mtime_ns
        model("team", version, modified)
        progress.progress(45, text="Building each team's recent form and ratings…")
        result = cached_team_forecast(version, modified, h, a, when, spread)
        progress.progress(100, text="Forecast ready")
    except (ValueError, FileNotFoundError) as exc:
        forecast_summary.warning(str(exc))
    finally:
        progress.empty()

    if result is not None:
        with forecast_summary:
            st.subheader("Historical forecast" if actual is not None else "Matchup at a glance")
            forecast_scoreboard(result, home, away, colors)
            if actual is not None:
                forecast_actual_score(actual, home, away, result)
            if result["disagreement"]:
                st.info("The projected score and the win chances favor different teams. Each comes from a separate model.")
        margin_heading.subheader("Point margin")
        dist = result["distribution"]
        actual_margin = actual.home_points - actual.away_points if actual is not None else None
        codes = teams.set_index("team_id").team_code.to_dict()
        projection_color = colors[home if result["margin"] >= 0 else away]
        forecast_margin_key(result, codes[h], codes[a], projection_color, actual_margin, spread)
        show_chart(forecast_margin_chart(result, home, away, colors, actual_margin, spread))
        if spread is not None:
            st.write(f"**Spread outcomes** · Home covers {dist['home_cover']:.0%} · "
                     f"Away covers {dist['away_cover']:.0%} · Push {dist['push']:.0%}")
    elif actual is not None:
        with forecast_summary:
            forecast_actual_score(actual, home, away, None)

    odds = APP / "odds_today.csv"
    with st.expander("Today's market lines"):
        if odds.exists():
            html_table(pd.read_csv(odds))
            st.caption("Check the retrieval time. Choose a matchup above and type its spread in manually.")
        else:
            st.caption("Market lines are unavailable in this snapshot. You can still type a spread in manually.")

    team_recent_form(t, h, a, when, names, colors)
    team_accuracy(version)
    with st.expander("How to read Team Forecasts"):
        st.markdown(
            f"""
- **Win chance** — How often the model expects each team to win a game like this one.
- **Projected score** — Expected points for each team. The win chance comes from a separate model, so the two can occasionally disagree.
- **Home spread** — Home covers when its final margin plus the spread is above zero. A push means exactly zero.
- **Likely range** — Based on how far past forecasts missed. 8 in 10 games like this one finished inside it.
- **Recent form** — Each dot is one game. Point margin is points scored minus points allowed.
- **Coverage** — Forecasts only use games played before the selected date. [Historical NBA box scores]({SOURCE_NBA})
            """
        )
        if result is not None:
            st.caption(f"This model supports dates after {result['cutoff']}. Dataset version {result['version']}.")


@st.cache_data(show_spinner=False, max_entries=256)
def cached_player_forecast(version, model_modified, player_id, opponent_id, when, home):
    from src.models import player
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1, user_api="openmp"):
        frame, _ = player.predict(table("player_games", version), table("team_games", version), player_id,
                                  opponent_id, when, home, model("player", version, model_modified))
    return frame


def player_meetings(players, first, second, when):
    """Every earlier game where both players appeared on opposite teams, one row per game."""
    played = players.loc[players.played & players.date.lt(pd.Timestamp(when))]
    columns = ["game_id", "date", "season", "team_id", "points", "rebounds", "assists", "minutes"]
    joint = played.loc[played.player_id.eq(first), columns].merge(
        played.loc[played.player_id.eq(second), columns].drop(columns=["date", "season"]),
        on="game_id", suffixes=("_a", "_b"))
    return joint.loc[joint.team_id_a.ne(joint.team_id_b)].sort_values("date", ascending=False)


def stand_in_lines(games, stat):
    """Average of each player's previous (up to) 10 games in the same season, needing at least 5.
    Only earlier games count, so the line is known before tipoff. `games` must be sorted by
    player, season and date."""
    keys = [games.player_id, games.season_start]
    previous = games.groupby(keys)[stat].shift(1)
    return previous.groupby(keys).rolling(10, min_periods=5).mean().reset_index(level=[0, 1], drop=True)


@st.cache_data(show_spinner=False)
def player_prop_record(version):
    """Held-out over/under record against a stand-in line: the player's average over his previous
    (up to) 10 games that season, requiring at least 5. Not a sportsbook prop line."""
    games = table("player_games", version)
    results = {}
    for stat in ("points", "rebounds", "assists"):
        path = APP / f"backtest_player_{stat}.csv.gz"
        if not path.exists():
            continue
        test = table(f"backtest_player_{stat}", version).query("period == 'test'")
        season = games.loc[games.played & games.season_start.isin(test.season_start.unique())]
        season = season.sort_values(["player_id", "season_start", "date", "game_id"])
        scored = test.merge(season.assign(line=stand_in_lines(season, stat))[["game_id", "player_id", "line"]],
                            on=["game_id", "player_id"], how="inner", validate="one_to_one").dropna(subset=["line"])
        result = scored.actual - scored.line
        lean = scored.prediction - scored.line
        valid = result.ne(0) & lean.ne(0)
        results[stat] = {"rate": float(((result > 0) == (lean > 0))[valid].mean()), "n": int(valid.sum()),
                         "season": str(test.season.iloc[0]),
                         "mae": float((test.actual - test.prediction).abs().mean())}
    return results


def player_accuracy(version):
    record = player_prop_record(version)
    if not record:
        return
    baselines = {}
    path = APP / "baselines.json"
    if path.exists():
        baselines = {row["target"]: row["mae"] for row in json.loads(path.read_text()).get("player", [])}
    with st.expander("How accurate are these projections?"):
        season = next(iter(record.values()))["season"]
        st.write(f"We tested the model on every player game of the {season} season, which it never saw while "
                 "being built.")
        html_table(pd.DataFrame({
            "Stat": [stat.title() for stat in record],
            "Average miss": [f"{r['mae']:.1f}" for r in record.values()],
            "Miss using last-10 average only": [f"{baselines[s]:.1f}" if s in baselines else "—" for s in record],
            "Over/under win rate*": [f"{r['rate']:.1%} of {r['n']:,}" for r in record.values()],
        }), numeric={"Average miss", "Miss using last-10 average only", "Over/under win rate*"})
        st.caption("*Our data has no historical sportsbook prop lines, so the over/under check uses a stand-in line: "
                   "the player's average over his previous 10 games that season (at least 5 games needed). A pick "
                   "wins when the projection lands on the same side of that line as the real result; exact ties are "
                   "left out. A coin flip would score about 50%. Real prop lines are sharper, so expect a lower "
                   "rate against them.")
        evaluation_downloads("player")


STAT_ABBR = {"points": "PTS", "rebounds": "REB", "assists": "AST"}


def player_card(name, team, side, color, frame):
    stats = []
    for row in frame.itertuples():
        stats.append(
            f'<div class="ciq-stat"><b>{STAT_ABBR.get(row.stat, escape(row.stat.upper()))}</b><strong>{row.prediction:.1f}</strong>'
            f'<span>Range {row.low:.0f}–{row.high:.0f}</span><span>Last-10 avg {row.baseline:.1f}</span></div>')
    return (f'<article class="ciq-card" style="--accent:{color}"><small>{side} · {escape(team)}</small>'
            f'<h4>{escape(name)}</h4><div class="ciq-stat-row">{"".join(stats)}</div></article>')


def player_page(p, t, teams, version):
    st.html(TEAM_FORECAST_STYLE)
    st.header("Player Matchups")
    page_intro("Pick a game, then one player from each team, to compare their projected points, rebounds and assists.",
               ["Find a game", "Pick a player on each team", "Compare projections and past meetings"])
    names = teams.set_index("team_id").team_name.to_dict()
    codes = teams.set_index("team_id").team_code.to_dict()
    choice = forecast_matchup(names, version, p.date.max(), key="player", model_name="player")
    if choice is None:
        return
    home, away, when = choice
    st.caption(f"Projections use box scores before game day, available through {p.date.max():%b %d, %Y}.")
    prior = p[p.date.lt(pd.Timestamp(when)) & p.played]
    ordered = prior.sort_values(["date", "game_id"])
    roster = ordered.drop_duplicates("player_id", keep="last").copy()
    recent = ordered.groupby("player_id").tail(10)
    roster["recent_minutes"] = roster.player_id.map(recent.groupby("player_id").minutes.mean())
    roster = roster[roster.season_start.eq(roster.season_start.max())]
    away_col, home_col = st.columns(2)
    with away_col:
        b = choose(roster[roster.team_id.eq(away)], "p_b", f"Away player · {names[away]}")
    with home_col:
        a = choose(roster[roster.team_id.eq(home)], "p_a", f"Home player · {names[home]}")
    st.caption("Players are listed by recent minutes with their last recorded team. "
               "Injuries, availability and who guards whom aren't in the box scores.")
    if a is None or b is None:
        st.info("No supported historical roster for this date.")
        return
    player_names = roster.set_index("player_id").player_name
    home_color, away_color = pair_colors(teams, home, away)

    left = right = None
    progress = st.progress(0, text="Loading the projection model…")
    try:
        modified = (APP.parent / "artifacts" / "player.pkl").stat().st_mtime_ns
        model("player", version, modified)
        progress.progress(35, text=f"Projecting {player_names[a]}…")
        left = cached_player_forecast(version, modified, a, away, when, True)
        progress.progress(70, text=f"Projecting {player_names[b]}…")
        right = cached_player_forecast(version, modified, b, home, when, False)
        progress.progress(100, text="Projections ready")
    except (ValueError, FileNotFoundError) as exc:
        st.warning(str(exc))
    finally:
        progress.empty()

    if left is not None and right is not None:
        st.subheader("Projected stat line")
        st.html('<div class="ciq-cards">'
                + player_card(player_names[b], names[away], "Away", away_color, right)
                + player_card(player_names[a], names[home], "Home", home_color, left) + "</div>")
        result = pd.concat([right.assign(player=player_names[b]), left.assign(player=player_names[a])])
        result["stat"] = result.stat.str.title()
        result["upper"] = result.high - result.prediction
        result["lower"] = result.prediction - result.low
        chart = px.bar(result, x="stat", y="prediction", color="player", barmode="group",
                       error_y="upper", error_y_minus="lower",
                       color_discrete_map={player_names[a]: home_color, player_names[b]: away_color},
                       hover_data={"baseline": ":.1f", "upper": False, "lower": False},
                       labels={"stat": "Stat", "prediction": "Projected", "player": "Player",
                               "baseline": "Last-10 average"})
        chart.update_traces(marker_line_width=0, error_y_color="#5b6a74", error_y_thickness=1.6, error_y_width=7)
        chart.update_layout(height=340, bargap=.3, bargroupgap=.08, legend=dict(orientation="h", y=1.12),
                            margin=dict(l=40, r=15, t=30, b=40))
        show_chart(chart)
        st.caption("Bars show the projection; whiskers show the likely range (8 in 10 past games landed inside it). "
                   "Last-10 average is each player's average over his previous 10 games this season.")

    meetings = player_meetings(p, b, a, when)
    st.subheader("Past meetings")
    if meetings.empty:
        st.info(f"{player_names[a]} and {player_names[b]} haven't played against each other in this snapshot. "
                "The projections rely on each player's recent games and the opposing team's defense.")
    else:
        st.write(f"**{len(meetings)}** earlier {'game' if len(meetings) == 1 else 'games'} with both players "
                 "on opposite teams, newest first.")
        display = pd.DataFrame({
            "date": meetings.date.map(lambda d: f"{d:%b} {d.day}, {d.year}"),
            "game": [f"{codes.get(x, '?')} vs {codes.get(y, '?')}" for x, y in zip(meetings.team_id_a, meetings.team_id_b)],
            **{f"{stat}_{side}": meetings[f"{stat}_{side}"].map(lambda v: "—" if pd.isna(v) else f"{v:.0f}")
               for side in ("a", "b") for stat in ("points", "rebounds", "assists", "minutes")},
        })
        html_table(display, headers=["Date", "Teams", *(["PTS", "REB", "AST", "MIN"] * 2)],
                   groups=[("", 2), (player_names[b], 4), (player_names[a], 4)],
                   numeric=[c for c in display.columns if c[-2:] in ("_a", "_b")])
        if len(meetings) < 3:
            st.caption("Only a few meetings, so treat these as anecdotes rather than a trend.")
    player_accuracy(version)
    with st.expander("How to read Player Matchups"):
        st.markdown(
            f"""
- **Projection** — The model's expected points, rebounds and assists, using each player's recent games, rest, home court and the opponent's defense and pace.
- **Range** — Based on how far past projections missed. 8 in 10 past games landed inside it.
- **Last-10 average** — The player's average over his previous 10 games this season. It's a simple yardstick to compare the projection with.
- **Past meetings** — Games where both players appeared for opposing teams. Box scores don't show who guarded whom.
- **Coverage** — Projections only use games before the selected date. [Historical NBA box scores]({SOURCE_NBA})
            """
        )


def breakout_accuracy(version):
    path = APP / "backtest_breakout_breakout.csv.gz"
    if not path.exists():
        return
    test = table("backtest_breakout_breakout", version).query("period == 'test'")
    top = test.nlargest(15, "prediction")
    hits = int(top.actual.sum())
    rate = test.actual.mean()
    with st.expander("How accurate is Breakout Watch?"):
        season = str(test.season.iloc[0])
        outcome = f"{int(season[:4]) + 1}-{str(int(season[:4]) + 2)[-2:]}"
        st.write(f"We tested the model on {len(test):,} players heading into the {outcome} season. "
                 "It never saw that season while it was being built.")
        st.markdown(
            f"- **{hits} of its top 15 picks** actually broke out.\n"
            f"- Breakouts are rare: only **{rate:.0%}** of all players broke out, so 15 random picks would "
            f"average about **{15 * rate:.1f}**.\n"
            "- Treat the list as \"players worth watching\", not a guarantee. Most players on it won't break out."
        )
        evaluation_downloads("breakout")


def breakout_page(seasons, version):
    st.header("Breakout Watch")
    path = APP / "breakout_candidates.csv.gz"
    if not path.exists():
        st.info("Breakout model not prepared. Run the offline training command.")
        return
    f = table("breakout_candidates", version)
    upcoming = f"{int(f.season_start.max()) + 1}-{str(int(f.season_start.max()) + 2)[-2:]}"
    page_intro(f"See which players the model thinks are most likely to take a big leap in {upcoming}.",
               ["Scan the top 10", "Pick a player to see his track record", "Check how past picks did"])
    st.html(
        '<div class="ciq-card" style="--accent:#a8441a"><b>What counts as a breakout?</b>'
        '<div class="ciq-stat-row" style="margin-top:.5rem">'
        '<div class="ciq-stat"><b>MINUTES</b><strong>20+</strong><span>per game next season</span></div>'
        '<div class="ciq-stat"><b>MORE PLAYING TIME</b><strong>+5</strong><span>minutes per game or more</span></div>'
        '<div class="ciq-stat"><b>PRODUCTION</b><strong>+15</strong><span>percentile points in points + rebounds + assists per 36 min</span></div>'
        '</div></div>')
    st.caption(f"Estimates use stats through the {f.season.iloc[0]} season. Rookies are excluded. "
               "Chances are model estimates, not guarantees.")
    st.subheader("Top 10 breakout chances")
    leaders = f.nlargest(10, "probability").sort_values("probability")
    chart = px.bar(leaders, x="probability", y="player_name", orientation="h", text="probability",
                   labels={"probability": "Estimated breakout chance", "player_name": "Player"},
                   color_discrete_sequence=["#a8441a"])
    chart.update_traces(texttemplate="%{x:.0%}", textposition="outside", cliponaxis=False,
                        hovertemplate="%{y}: %{x:.0%}<extra></extra>")
    chart.update_xaxes(tickformat=".0%", range=[0, min(1, leaders.probability.max() * 1.18)])
    chart.update_yaxes(title_text=None, automargin=True)
    chart.update_layout(height=400, margin=dict(l=10, r=40, t=40, b=40), bargap=.35)
    show_chart(chart)
    st.subheader("Player track record")
    pid = choose(f, "breakout_player", "Search player")
    if pid is not None:
        selected = f[f.player_id.eq(pid)].iloc[0]
        rank = int(f.probability.rank(ascending=False, method="min")[f.player_id.eq(pid)].iloc[0])
        hist = scouting.canonical(seasons)
        hist = hist[hist.player_id.eq(pid)].sort_values("season_start")
        st.html(
            f'<div class="ciq-card" style="--accent:#a8441a"><small>Rank #{rank} of {len(f)}</small>'
            f'<h4>{escape(selected.player_name)}</h4><div class="ciq-stat-row">'
            f'<div class="ciq-stat"><b>BREAKOUT CHANCE</b><strong>{selected.probability:.0%}</strong></div>'
            f'<div class="ciq-stat"><b>MINUTES / GAME</b><strong>{selected.mpg:.1f}</strong><span>{selected.season}</span></div>'
            f'<div class="ciq-stat"><b>PTS+REB+AST / 36</b><strong>{selected.pra_per36:.1f}</strong><span>{selected.season}</span></div>'
            '</div></div>')
        trend = hist.rename(columns={"mpg": "Minutes per game", "pra_per36": "Points + rebounds + assists per 36"})
        line = px.line(trend, x="season", y=["Minutes per game", "Points + rebounds + assists per 36"], markers=True,
                       labels={"variable": "Measure", "value": "Season average", "season": "Season"},
                       color_discrete_sequence=["#1f5bab", "#a8441a"])
        line.for_each_trace(lambda trace: trace.update(line_dash="dash") if trace.name.startswith("Points") else None)
        line.update_layout(height=320, legend=dict(orientation="h", y=1.15), margin=dict(l=40, r=15, t=30, b=40))
        show_chart(line)
        st.caption("Season averages for every season in the data. The current season isn't part of the estimate.")
    breakout_accuracy(version)
