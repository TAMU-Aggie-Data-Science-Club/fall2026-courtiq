"""Presentation UI consuming only compact app-ready files and trusted models."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
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


def heading(title, color):
    import html
    st.markdown(f'<h3 style="border-left:6px solid {color};padding-left:12px">{html.escape(title)}</h3>', unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def model(name, version, modified):
    from src.models.common import load
    return load(name)


def bundle(name, version):
    path = APP.parent / "artifacts" / f"{name}.pkl"
    return model(name, version, path.stat().st_mtime_ns)


@st.cache_data(show_spinner=False)
def ranks(version, season, lens):
    return scouting.rankings(table("player_season",version),season,lens)


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


def matchup(teams, version, key, latest):
    lookup = teams.set_index("team_id").team_name.to_dict()
    if st.toggle("Build a custom matchup", key=key+"_manual"):
        return custom_matchup(lookup, key, latest)
    fixtures = schedule_fixtures(lookup, version)
    if fixtures.empty:
        st.info("No supported fixtures in this snapshot. Switch to a custom matchup above.")
        st.stop()
    days=sorted(fixtures.date.dt.date.unique())
    today=pd.Timestamp.today().date()
    default=next((i for i,d in enumerate(days) if d>=today),len(days)-1)
    when=st.selectbox("Game day",days,index=default,key=key+"_day",format_func=lambda d:d.strftime("%a, %b %d, %Y"))
    slate=fixtures[fixtures.date.dt.date.eq(when)].sort_values("home_team_id").set_index("game_id")
    labels={gid:f"{lookup[r.away_team_id]} at {lookup[r.home_team_id]}" for gid,r in slate.iterrows()}
    gid=st.selectbox("Game",sorted(labels,key=labels.get),format_func=labels.get,key=key+"_game")
    row=slate.loc[gid]
    st.caption(f"League schedule snapshot · Forecast uses box scores before game day, available through {latest:%b %d, %Y}.")
    return row.home_team_id,row.away_team_id,when


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


def scouting_page(seasons,version,teams):
    st.header("Player Scouting Lab")
    st.caption("Pick a season and a player, then choose a skill to explore. Farther from the center means a higher league standing.")
    available=sorted(seasons.loc[seasons.season_start>=2023,"season"].unique(),reverse=True)
    season=st.selectbox("Season",available,index=min(1,len(available)-1),key="scout_season")
    f=scouting.canonical(seasons)
    f=f[f.season.eq(season)]
    pid=choose(f,"scout_player")
    if pid is None: st.info("No player seasons available."); return
    lens=st.selectbox("Scouting lens",list(scouting.LENSES))
    row=f[f.player_id.eq(pid)].iloc[0]
    stints=seasons[seasons.player_id.eq(pid)&seasons.season.eq(season)&seasons.team_id.ne(0)]
    color=team_color(teams,stints.nlargest(1,"minutes").team_id.iloc[0]) if len(stints) else "#db7335"
    heading(row.player_name,color)
    for col,label,value in zip(st.columns(4),["Games","Minutes / game","Points / game","Assists / game"],[row.games,row.mpg,row.points_pg,row.assists_pg]):
        col.metric(label,f"{value:.1f}" if pd.notna(value) else "N/A")
    ranked=ranks(version,season,lens)
    b=ranked[ranked.player_id.eq(pid)]
    if not b.qualified.all(): st.info("Some axes are not qualified. N/A axes are not replaced with zero or a league-average value.")
    st.plotly_chart(scouting.radar(b,color),use_container_width=True)
    with st.expander("Read the exact rankings"):
        detail=b[["label","percentile","rank","population"]].copy()
        detail.columns=["Skill","Percentile","League rank","Eligible players"]
        st.dataframe(detail.round(1),hide_index=True,width="stretch")
    badges,text=scouting.report(ranks(version,season,"All-Around").query("player_id == @pid"))
    st.write(" · ".join(badges) if badges else "No qualifying badges")
    st.write(text)
    st.caption("Badges and summary use the All-Around lens consistently, even when the shooting chart is selected.")
    with st.expander("Shooting efficiency explained"):
        for key, label in [("ts_pct","True shooting includes free throws"),("efg_pct","Effective field goal percentage gives extra credit for threes")]:
            value=row[key]
            st.write(f"{label} · {value:.1%}" if pd.notna(value) else f"{label} · Unavailable")


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
    st.plotly_chart(impact.trend_chart(trend, color), use_container_width=True)
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
    st.plotly_chart(impact.scatter(peers, pid, tid), use_container_width=True)
    leaders = pd.concat([peers.head(8), selected]).drop_duplicates(["player_id", "team_id"])
    display = pd.DataFrame({
        "Rank": leaders["rank"],
        "Player and team": leaders.stint_label.where(~leaders.selected, "★ " + leaders.stint_label),
        "On/off per 48": leaders.on_off_diff.map(impact.signed_margin),
        "On-court min": leaders.minutes_on.round().astype(int),
        "Bench min": leaders.minutes_off.round().astype(int),
    })
    st.dataframe(display, hide_index=True, width="stretch")


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
        st.plotly_chart(impact.margin_bars(row, color), use_container_width=True)
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


def performance(prefix):
    path=APP/"evaluation.json"
    if not path.exists(): return
    with st.expander("How accurate were these forecasts?"):
        for name,task in json.loads(path.read_text()).items():
            if not name.startswith(prefix): continue
            result=next((r for r in task["results"] if r["period"]=="test" and r["model"]==task["selected"]),None)
            if result is None: continue
            label=name.removeprefix(prefix+"_").replace("_"," ").capitalize()
            if "mae" in result:
                st.write(f"{label} · Average absolute error of {result['mae']:.1f} across {result['n']:,} held-out examples.")
            elif prefix=="team":
                st.write(f"Game winner · Correct in {result['accuracy']:.1%} of {result['n']:,} held-out games.")
            else:
                st.write(f"Breakout ranking · ROC AUC {result['roc_auc']:.2f} across {result['n']:,} held-out players. A value of 0.5 indicates chance ordering.")
        with st.popover("Evaluation details"):
            baseline=APP/"baselines.json"
            if baseline.exists():
                st.download_button("Download baseline comparison",json.dumps(json.loads(baseline.read_text()).get(prefix),indent=2),file_name=f"{prefix}_baselines.json")
            st.download_button("Download model evaluation",json.dumps({k:v for k,v in json.loads(path.read_text()).items() if k.startswith(prefix)},indent=2),file_name=f"{prefix}_evaluation.json")
            market=APP/"market_evaluation.json"
            if prefix=="team" and market.exists():
                st.download_button("Download historical market comparison",market.read_text(),file_name=market.name)
        st.caption("These checks use the 2025–26 season, held back from training.")


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
.forecast-form-record {display:block; font-size:1.4rem;}
.forecast-form-coverage {display:block; margin-top:.35rem;}
.forecast-win-bar {display:flex; height:.65rem; margin:.7rem 0 0; border-radius:999px; overflow:hidden;
    background:#f3eee4;}
.forecast-win-bar span {display:block; flex:none; height:100%;}
.forecast-win-bar span+span {border-inline-start:2px solid #fffdf8; box-sizing:border-box;}
.st-key-team_swap_sides {width:100%; display:flex; justify-content:center; margin-top:1.75rem;}
.st-key-team_swap_sides [data-testid="stTooltipHoverTarget"] {justify-content:center !important;}
.st-key-team_swap_sides button {position:relative; width:2.4rem; height:2.5rem; min-width:0; padding:.35rem;}
.st-key-team_swap_sides button > span {
    position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); margin:0;
}
.st-key-team_swap_sides button [data-testid="stMarkdownContainer"] {
    position:absolute; width:1px; height:1px; overflow:hidden; clip-path:inset(50%); white-space:nowrap;
}
@media(max-width:640px) {
    .forecast-side {padding:.65rem;}
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .st-key-team_swap_sides) {
        flex-wrap:wrap; gap:.45rem;
    }
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .st-key-team_swap_sides)
        > [data-testid="stColumn"] {width:auto; min-width:0; flex:1 1 0;}
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .st-key-team_swap_sides)
        > [data-testid="stColumn"]:nth-child(2) {flex:0 0 2.4rem;}
    [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] .st-key-team_swap_sides)
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
        cards.append(
            f'<article class="forecast-side" style="--accent:{colors[name]}">'
            f'<small>{side.title()}</small><h4>{escape(name)}</h4>'
            f'<strong class="forecast-score">{score:.1f}</strong><small>Projected points</small>'
            f'<b class="forecast-chance">{probability:.1%} win chance</b></article>'
        )
    st.html(
        '<div class="forecast-scoreboard">' + "".join(cards) + '</div>'
        '<div class="forecast-win-bar" aria-hidden="true">'
        f'<span style="width:{result["away_win"]:.6%};background:{colors[away]}"></span>'
        f'<span style="width:{result["home_win"]:.6%};background:{colors[home]}"></span></div>'
    )


def forecast_margin_chart(result, home, away, colors):
    import plotly.graph_objects as go

    margin = result["margin"]
    low = result["distribution"]["low"]
    high = result["distribution"]["high"]
    extent = max(abs(low), abs(high), abs(margin), 4) * 1.15
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[low, high], y=[0, 0], mode="lines+markers",
        line=dict(color="#637783", width=5), marker=dict(size=8),
        text=[forecast_margin_label(value, home, away, 0) for value in (low, high)],
        hovertemplate="%{text}<extra>80% range endpoint</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[margin], y=[0], mode="markers",
        marker=dict(symbol="diamond", size=13, color=colors[home if margin >= 0 else away]),
        hovertemplate=f"{forecast_margin_label(margin, home, away)}<extra>Projected margin</extra>",
    ))
    fig.add_vline(x=0, line_color="#697681", line_dash="dot")
    fig.update_xaxes(range=[-extent, extent], title_text="Away advantage  ←  Point margin  →  Home advantage",
                     tickformat=".0f")
    fig.update_yaxes(visible=False, range=[-1, 1], fixedrange=True)
    fig.update_layout(height=150, margin=dict(l=24, r=24, t=12, b=48), showlegend=False)
    return fig


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
        hover_data=["opponent", "game_result"],
        labels={"date": "Game date", "team_name": "Team", "margin": "Scoring margin (points)",
                "opponent": "Opponent", "game_result": "Final score"},
    )
    fig.add_hline(y=0, line_color="#697681", line_dash="dot")
    fig.update_layout(height=330, margin=dict(l=45, r=15, t=12, b=52),
                      legend=dict(orientation="h"))
    fig.update_yaxes(tickformat=".0f", hoverformat="+.0f")
    st.plotly_chart(fig, use_container_width=True)


def team_forecast_matchup(names, version, latest):
    mode = st.radio(
        "Find a matchup", ["Upcoming games", "Past games", "Custom matchup"],
        key="team_matchup_mode", horizontal=True,
    )
    if mode != "Upcoming games":
        try:
            tasks = bundle("team", version)["tasks"]
            cutoff = max(pd.Timestamp(task["inference_available_after"]) for task in tasks.values())
        except (ValueError, FileNotFoundError) as exc:
            st.warning(str(exc))
            return None
        earliest = cutoff.date() + timedelta(days=1)
        if mode == "Custom matchup":
            return custom_matchup(names, "team", latest, compact=True, earliest=earliest)

    today = pd.Timestamp(datetime.now(ZoneInfo("America/Chicago")).date())
    is_upcoming = mode == "Upcoming games"
    if is_upcoming:
        fixtures = schedule_fixtures(names, version).sort_values(["date", "home_team_id"])
        games = fixtures.loc[fixtures.date.ge(today)]
        if games.empty:
            st.info("The schedule snapshot has no upcoming games. Choose Past games or Custom matchup above.")
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
            st.info("No recorded games in this snapshot fall within the model’s supported dates. Try Custom matchup.")
            return None
        team_picker, opponent_picker = st.columns(2)
        game_picker = st

    if "team_fixture_filter" not in st.session_state:
        st.session_state["team_fixture_filter"] = st.session_state.get("team_fixture_selection", 0)
    team_id = team_picker.selectbox(
        "Find by team", [0, *names], key="team_fixture_filter",
        format_func=lambda tid: names[tid] if tid else "All teams",
    )
    st.session_state["team_fixture_selection"] = team_id
    if team_id:
        games = games.loc[games.home_team_id.eq(team_id) | games.away_team_id.eq(team_id)]
    if games.empty:
        kind = "upcoming" if is_upcoming else "recorded past"
        game_picker.info(f"No {kind} games for this team are in the snapshot. Try All teams or a custom matchup.")
        return None

    if is_upcoming:
        limit = dates_picker.selectbox(
            "Dates to show", [3, 7, 14, 30, "all"], key="team_upcoming_limit",
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
        game_id = game_picker.selectbox("Upcoming matchup", list(labels), format_func=labels.get, key="team_upcoming_game")
        st.caption(f"Showing {len(days)} game {'date' if len(days) == 1 else 'dates'} in the schedule snapshot.")
    else:
        opponent = 0
        if team_id:
            opponents = set(games.loc[games.home_team_id.eq(team_id), "away_team_id"])
            opponents.update(games.loc[games.away_team_id.eq(team_id), "home_team_id"])
            opponent = opponent_picker.selectbox(
                "Opponent", [0, *sorted(opponents, key=names.get)], key=f"team_past_opponent_{team_id}",
                format_func=lambda tid: names[tid] if tid else "Any opponent",
                help="Includes meetings at either team's home court.",
            )
            if opponent:
                games = games.loc[games.home_team_id.eq(opponent) | games.away_team_id.eq(opponent)]
        month_picker, day_picker = st.columns(2)
        game_picker = st.container()
        months = games.date.dt.strftime("%Y-%m")
        month_options = sorted(months.unique(), reverse=True)
        previous_month = st.session_state.get("team_past_month")
        previous_day = st.session_state.get("team_past_date")
        filters = (team_id, opponent)
        changed_filter = st.session_state.get("team_past_last_filter") != filters
        if previous_month not in month_options or (
            changed_filter and previous_day is not None and not games.date.eq(pd.Timestamp(previous_day)).any()
        ):
            previous_month = month_options[0]
        st.session_state["team_past_last_filter"] = filters
        st.session_state["team_past_month"] = previous_month
        month = month_picker.selectbox(
            "Month", month_options,
            format_func=lambda value: pd.Period(value, freq="M").strftime("%B %Y"), key="team_past_month",
        )
        month_games = games.loc[months.eq(month)]
        game_counts = month_games.groupby(month_games.date.dt.date).game_id.nunique().sort_index(ascending=False)
        days = {
            day: f"{day:%b} {day.day} · {count} {'game' if count == 1 else 'games'}"
            for day, count in game_counts.items()
        }
        st.session_state["team_past_date"] = previous_day if previous_day in days else next(iter(days))
        day = day_picker.selectbox("Game day", list(days), format_func=days.get, key="team_past_date")
        slate = month_games.loc[month_games.date.eq(pd.Timestamp(day))].set_index("game_id")
        labels = {gid: f"{names[row.away_team_id]} at {names[row.home_team_id]}" for gid, row in slate.iterrows()}
        game_id = game_picker.selectbox("Matchup", list(labels), format_func=labels.get, key="team_past_game")
    selected = slate.loc[game_id]
    return selected.home_team_id, selected.away_team_id, selected.date.date()


@st.cache_data(show_spinner=False, max_entries=256)
def cached_team_forecast(version, model_modified, home, away, when, spread):
    from src.models import team

    return team.predict(table("team_games", version), home, away, when, spread,
                        model("team", version, model_modified))


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


def forecast_actual_score(actual, home, away, forecast):
    st.write(f"**Actual final** · {away} {actual.away_points:.0f} · {home} {actual.home_points:.0f}")
    if forecast is None:
        return
    home_chance = round(100 * forecast["home_win"], 1)
    away_chance = round(100 * forecast["away_win"], 1)
    if home_chance == away_chance:
        st.caption("The forecast gave both teams the same displayed win chance.")
        return
    favorite = home if home_chance > away_chance else away
    winner = home if actual.home_points > actual.away_points else away
    if favorite == winner:
        st.caption(f"{favorite}, the forecast favorite, won.")
    else:
        st.caption(f"{winner} won. The forecast favored {favorite}.")


def team_page(t, teams, version):
    st.html(TEAM_FORECAST_STYLE)
    st.header("Team Forecasts")
    st.write("Pick a matchup to see each team’s chance of winning, the projected score, and how both teams have played lately.")
    names = teams.set_index("team_id").team_name.to_dict()
    matchup_choice = team_forecast_matchup(names, version, t.date.max())
    if matchup_choice is None:
        return
    h, a, when = matchup_choice
    st.caption(f"Forecast uses box scores before game day, available through {t.date.max():%b %d, %Y}.")
    home, away = names[h], names[a]
    colors = {name: team_color(teams, tid) for tid, name in [(a, away), (h, home)]}
    actual = team_actual_result(version, h, a, when)

    forecast = st.container()
    with st.expander("Spreads and market lines"):
        use_spread = st.checkbox("Include a home spread")
        spread = st.number_input("Home spread", value=-4.5, step=.5) if use_spread else None
        if use_spread:
            st.caption("A negative spread means the home team is favored. For example, −4.5 means it must win by at least 5 to cover.")
        spread_result = st.empty()
        odds = APP / "odds_today.csv"
        if odds.exists():
            st.write("**Cached market lines**")
            st.dataframe(pd.read_csv(odds), hide_index=True)
            st.caption("Check the retrieval time. Choose a matchup and enter its spread manually.")
        else:
            st.caption("Market lines are unavailable in this snapshot. You can enter a spread manually.")

    result = None
    try:
        model_path = APP.parent / "artifacts" / "team.pkl"
        result = cached_team_forecast(version, model_path.stat().st_mtime_ns, h, a, when, spread)
    except (ValueError, FileNotFoundError) as exc:
        forecast.warning(str(exc))
    with forecast:
        if result is not None:
            st.subheader("Historical forecast" if actual is not None else "Matchup at a glance")
            forecast_scoreboard(result, home, away, colors)
            if actual is not None:
                forecast_actual_score(actual, home, away, result)
            margin = forecast_margin_label(result["margin"], home, away)
            st.write(f"**Projected margin:** {margin} · **Projected total:** {result['total']:.1f} points")
            if result["disagreement"]:
                st.info("The projected score and the win chances favor different teams. Each comes from a separate model.")
            st.write("**How close could it be?**")
            dist = result["distribution"]
            low = forecast_margin_label(dist["low"], home, away, 0)
            high = forecast_margin_label(dist["high"], home, away, 0)
            st.write(f"Approximate **80% margin range** · {low} to {high}")
            st.plotly_chart(forecast_margin_chart(result, home, away, colors), use_container_width=True)
            if dist["low"] < 0 < dist["high"]:
                st.caption("The range includes wins for either team.")
            st.caption("The diamond marks the projected margin. The dotted line marks an even score.")
            if spread is not None:
                spread_result.write(
                    f"**{home} {spread:+g}** · Home covers {dist['home_cover']:.0%} · "
                    f"Away covers {dist['away_cover']:.0%} · Push {dist['push']:.0%}"
                )
        elif actual is not None:
            forecast_actual_score(actual, home, away, None)

    team_recent_form(t, h, a, when, names, colors)
    performance("team")
    with st.expander("How to read Team Forecasts"):
        st.markdown(
            f"""
- **Win chance** — The model’s estimate of how often a team would win a matchup like this one.
- **Projected score** — The expected points for each team, derived from the projected total and margin. The win chance comes from a separate model.
- **80% margin range** — An approximate range based on past forecast errors. The wider the range, the more room there is for a different result.
- **Recent form** — Each dot is one game. Point margin is points scored minus points allowed.
- **Spread** — Home covers when its final margin plus the signed home spread is positive. A push means that adjusted margin is zero.
- **Coverage** — Forecasts use earlier games from the available snapshot. [Historical NBA box scores]({SOURCE_NBA})
            """
        )
        if result is not None:
            st.caption(f"This model supports dates after {result['cutoff']}. Dataset version {result['version']}.")


def player_page(p,t,teams,version):
    st.header("Player Matchup Lab")
    st.caption("Pick a game and one player on each side. Compare expected points, rebounds and assists against the opposing team.")
    home,away,when=matchup(teams,version,"player",p.date.max())
    prior=p[p.date.lt(pd.Timestamp(when)) & p.played]
    ordered=prior.sort_values(["date","game_id"])
    roster=ordered.drop_duplicates("player_id",keep="last").copy()
    recent=ordered.groupby("player_id").tail(10)
    roster["recent_minutes"]=roster.player_id.map(recent.groupby("player_id").minutes.mean())
    roster=roster[roster.season_start.eq(roster.season_start.max())]
    st.caption("Players are listed by recent minutes with their last recorded team. Availability and individual guarding assignments are unconfirmed.")
    c1,c2=st.columns(2)
    with c1: a=choose(roster[roster.team_id.eq(home)],"p_a","Home player")
    with c2: b=choose(roster[roster.team_id.eq(away)],"p_b","Away player")
    if a is None or b is None: st.info("No supported historical roster for this date."); return
    if st.button("Compare players & predict"):
        try:
            from src.models import player
            from threadpoolctl import threadpool_limits
            models=bundle("player",version)
            with threadpool_limits(limits=1,user_api="openmp"):
                left,_=player.predict(p,t,a,away,when,True,models)
                right,_=player.predict(p,t,b,home,when,False,models)
            left["player"]=roster.set_index("player_id").loc[a,"player_name"]
            right["player"]=roster.set_index("player_id").loc[b,"player_name"]
            result=pd.concat([left,right])
            result["stat"]=result.stat.str.title()
            result["upper"]=result.high-result.prediction
            result["lower"]=result.prediction-result.low
            st.plotly_chart(px.bar(result,x="stat",y="prediction",color="player",barmode="group",error_y="upper",error_y_minus="lower",color_discrete_sequence=[team_color(teams,home),team_color(teams,away)],labels={"stat":"Statistic","prediction":"Expected per game","player":"Player"}),use_container_width=True)
            st.caption("Whiskers show the approximate 80% prediction range based on historical errors.")
            with st.expander("Compare with each player’s recent average"):
                detail=result[["player","stat","prediction","baseline","low","high"]].copy()
                detail.columns=["Player","Statistic","Forecast","Recent baseline","Lower estimate","Upper estimate"]
                st.dataframe(detail.round(1),hide_index=True)
                st.caption("The baseline averages up to ten prior games this season, using a training average when no games are available.")
            encounter=player.encounters(p,a,b,when)
            st.write(f"Recorded opposing-player encounters: {len(encounter)}")
            if len(encounter)<3: st.info("Sparse encounter history. Model uses broader player and opponent-team context, not an invented defender effect.")
            if len(encounter):
                with st.expander("Home player’s past games against the selected player"):
                    detail=encounter[["date","season","points","rebounds","assists","minutes"]].sort_values("date",ascending=False)
                    st.dataframe(detail.rename(columns=str.title),hide_index=True)
        except (ValueError,FileNotFoundError) as exc: st.warning(str(exc))
    performance("player")


def breakout_page(seasons,version):
    st.header("Breakout Watch")
    path=APP/"breakout_candidates.csv.gz"
    if not path.exists(): st.info("Breakout model not prepared. Run the offline training command."); return
    f=table("breakout_candidates",version)
    st.caption("Preseason estimates from the latest completed season. Rookies excluded. Probabilities are model estimates, not guarantees.")
    st.caption("Explore the highest preseason estimates, then select a player to track their minutes and production.")
    leaders=f.nlargest(10,"probability").sort_values("probability")
    chart=px.bar(leaders,x="probability",y="player_name",orientation="h",labels={"probability":"Estimated breakout chance","player_name":"Player"},color_discrete_sequence=["#de793c"])
    chart.update_xaxes(tickformat=".0%")
    st.plotly_chart(chart,use_container_width=True)
    pid=choose(f,"breakout_player")
    if pid is not None:
        selected=f[f.player_id.eq(pid)].iloc[0]
        st.metric(f"{selected.player_name} · Estimated breakout chance",f"{selected.probability:.0%}")
        hist=scouting.canonical(seasons)
        hist=hist[hist.player_id.eq(pid)].sort_values("season_start")
        st.plotly_chart(px.line(hist.rename(columns={"mpg":"Minutes per game","pra_per36":"Points + rebounds + assists per 36 minutes"}),x="season",y=["Minutes per game","Points + rebounds + assists per 36 minutes"],markers=True,labels={"variable":"Measure","value":"Season average","season":"Season"}),use_container_width=True)
        st.caption("Current-season observations are a separate tracker, not inputs retroactively added to the preseason forecast.")

    st.write("A breakout here means playing at least 20 minutes per game next season, gaining at least five minutes per game, and climbing 15 percentile points in combined points, rebounds and assists per 36 minutes.")
    performance("breakout")
    back=APP/"backtest_breakout_breakout.csv.gz"
    if back.exists():
        st.subheader("Held-out candidate backtest")
        cohort=table("backtest_breakout_breakout",version).query("period == 'test'").nlargest(15,"prediction")
        st.write(f"{int(cohort.actual.sum())} of the model’s 15 highest-ranked candidates met the breakout definition.")
