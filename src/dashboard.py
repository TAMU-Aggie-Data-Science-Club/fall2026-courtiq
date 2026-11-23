"""Presentation UI consuming only compact app-ready files and trusted models."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from html import escape
import json
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from src.pipeline import APP
from src.features import scouting,impact
from src.features.breakout import season_features

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
def ranks(version, season, lens, min_games, ratings_modified, _league):
    return scouting.rankings(_league, season, lens, min_games=min_games)


def custom_matchup(lookup, key, latest, earliest):
    c1, swap_picker, c2, date_picker = st.columns([1.25, .24, 1.25, 1], gap="small")
    home = c1.selectbox("Home team", list(lookup), format_func=lookup.get, key=key+"_home")
    away = c2.selectbox("Away team", [tid for tid in lookup if tid != home], format_func=lookup.get, key=key+"_away")
    def swap_sides():
        home_key, away_key = key+"_home", key+"_away"
        st.session_state[home_key], st.session_state[away_key] = (
            st.session_state[away_key], st.session_state[home_key],
        )

    swap_picker.button(
        "Swap home and away", icon=":material/swap_horiz:", help="Swap home and away",
        on_click=swap_sides, key=key+"_swap_sides",
    )
    default = max((latest + timedelta(days=1)).date(), earliest)
    when = date_picker.date_input("Game date", default, min_value=earliest, key=key+"_date")
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


def sources_and_limitations(route):
    notes = {
        "scouting-lab": [
            "**Rankings** — Percentiles depend on who qualifies for that season and stat. Small samples can make rankings shift quickly.",
            "**What box scores capture** — Steals and blocks describe part of a defender’s contribution. Defensive and net ratings also reflect teammates and opponents.",
        ],
        "on-off-impact": [
            "**Game coverage** — The tool uses recorded minutes and scores. Games with missing duration or player minutes can reduce the sample for on/off comparisons.",
            "**Interpreting impact** — Teammates, opponents, and rotations all influence the splits. The difference describes team results during those minutes.",
        ],
        "team-forecasts": [
            "**Forecasts** — Estimates use earlier results in the available snapshot. Changes such as injuries and lineup decisions can affect the actual outcome.",
            f"**Market lines** — The app displays cached lines when available. Timing is unknown for lines in the historical evaluation. [The Odds API](https://the-odds-api.com/) · [Historical betting data]({SOURCE_ODDS})",
        ],
        "player-matchups": [
            "**Projections** — Estimates use recorded appearances. The snapshot cannot confirm future lineups, injuries, or who will guard whom.",
            "**Past meetings** — A few games can be heavily influenced by minutes, role, or shooting variance. Treat them as context for the matchup.",
        ],
        "breakout-watch": [
            "**Preseason forecasts** — Estimates use the prior completed season. The tracker uses newer games as they become available in the snapshot.",
            "**Early-season rankings** — A smaller sample and a changing comparison group can make provisional percentiles swing.",
            "**Historical test** — The season shown in the backtest is a single evaluation of how the watchlist performed.",
        ],
    }
    with st.expander("Sources & limitations"):
        source = f"**NBA box scores** — This page uses the game and player records available in the app’s data snapshot. [Historical NBA box scores]({SOURCE_NBA})"
        st.markdown("\n".join(f"- {item}" for item in [source, *notes[route]]))


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
    st.plotly_chart(
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


FORECAST_STYLE = """
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


def forecast_matchup(names, version, latest, tool):
    mode = st.radio(
        "Find a matchup", ["Upcoming games", "Past games", "Custom matchup"],
        key=f"{tool}_matchup_mode", horizontal=True,
    )
    if mode != "Upcoming games":
        try:
            tasks = bundle(tool, version)["tasks"]
            cutoff = max(pd.Timestamp(task["inference_available_after"]) for task in tasks.values())
        except (ValueError, FileNotFoundError) as exc:
            st.warning(str(exc))
            return None
        earliest = cutoff.date() + timedelta(days=1)
        if mode == "Custom matchup":
            return custom_matchup(names, tool, latest, earliest)

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

    if f"{tool}_fixture_filter" not in st.session_state:
        st.session_state[f"{tool}_fixture_filter"] = st.session_state.get(f"{tool}_fixture_selection", 0)
    team_id = team_picker.selectbox(
        "Find by team", [0, *names], key=f"{tool}_fixture_filter",
        format_func=lambda tid: names[tid] if tid else "All teams",
    )
    st.session_state[f"{tool}_fixture_selection"] = team_id
    if team_id:
        games = games.loc[games.home_team_id.eq(team_id) | games.away_team_id.eq(team_id)]
    if games.empty:
        kind = "upcoming" if is_upcoming else "recorded past"
        game_picker.info(f"No {kind} games for this team are in the snapshot. Try All teams or a custom matchup.")
        return None

    if is_upcoming:
        limit = dates_picker.selectbox(
            "Dates to show", [3, 7, 14, 30, "all"], key=f"{tool}_upcoming_limit",
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
        game_label, game_key = "Upcoming matchup", f"{tool}_upcoming_game"
    else:
        opponent = 0
        if team_id:
            opponents = set(games.loc[games.home_team_id.eq(team_id), "away_team_id"])
            opponents.update(games.loc[games.away_team_id.eq(team_id), "home_team_id"])
            opponent = opponent_picker.selectbox(
                "Opponent", [0, *sorted(opponents, key=names.get)], key=f"{tool}_past_opponent_{team_id}",
                format_func=lambda tid: names[tid] if tid else "Any opponent",
                help="Includes meetings at either team's home court.",
            )
            if opponent:
                games = games.loc[games.home_team_id.eq(opponent) | games.away_team_id.eq(opponent)]
        month_picker, day_picker = st.columns(2)
        game_picker = st.container()
        months = games.date.dt.strftime("%Y-%m")
        month_options = sorted(months.unique(), reverse=True)
        previous_month = st.session_state.get(f"{tool}_past_month")
        previous_day = st.session_state.get(f"{tool}_past_date")
        filters = (team_id, opponent)
        changed_filter = st.session_state.get(f"{tool}_past_last_filter") != filters
        if previous_month not in month_options or (
            changed_filter and previous_day is not None and not games.date.eq(pd.Timestamp(previous_day)).any()
        ):
            previous_month = month_options[0]
        st.session_state[f"{tool}_past_last_filter"] = filters
        st.session_state[f"{tool}_past_month"] = previous_month
        month = month_picker.selectbox(
            "Month", month_options,
            format_func=lambda value: pd.Period(value, freq="M").strftime("%B %Y"), key=f"{tool}_past_month",
        )
        month_games = games.loc[months.eq(month)]
        game_counts = month_games.groupby(month_games.date.dt.date).game_id.nunique().sort_index(ascending=False)
        days = {
            day: f"{day:%b} {day.day} · {count} {'game' if count == 1 else 'games'}"
            for day, count in game_counts.items()
        }
        st.session_state[f"{tool}_past_date"] = previous_day if previous_day in days else next(iter(days))
        day = day_picker.selectbox("Game day", list(days), format_func=days.get, key=f"{tool}_past_date")
        slate = month_games.loc[month_games.date.eq(pd.Timestamp(day))].set_index("game_id")
        labels = {gid: f"{names[row.away_team_id]} at {names[row.home_team_id]}" for gid, row in slate.iterrows()}
        game_label, game_key = "Matchup", f"{tool}_past_game"
    if not labels:
        game_picker.info("No matchups are available for the current filters.")
        return None
    if st.session_state.get(game_key) not in labels:
        st.session_state[game_key] = next(iter(labels))
    game_id = game_picker.selectbox(game_label, list(labels), format_func=labels.get, key=game_key)
    if game_id not in labels:
        game_picker.info("The selected matchup is no longer available. Choose a game from the list.")
        return None
    if is_upcoming:
        st.caption(f"Showing {len(days)} game {'date' if len(days) == 1 else 'dates'} in the schedule snapshot.")
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
    st.html(FORECAST_STYLE)
    st.header("Team Forecasts")
    st.write("Pick a matchup to see each team’s chance of winning, the projected score, and how both teams have played lately.")
    names = teams.set_index("team_id").team_name.to_dict()
    matchup_choice = forecast_matchup(names, version, t.date.max(), "team")
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
            """
        )
        if result is not None:
            st.caption(f"This model supports dates after {result['cutoff']}. Dataset version {result['version']}.")


PLAYER_MATCHUP_STYLE = """
<style>
.player-forecast-stat {border-top:1px solid color-mix(in srgb,var(--accent) 30%,transparent);
    padding:.45rem 0;}
.player-forecast-stat:first-of-type {margin-top:.6rem;}
.player-forecast-values {display:flex; align-items:baseline; flex-wrap:wrap; gap:.15rem .6rem;}
.player-forecast-values strong {font-size:1.5rem;}
.player-forecast-values span,.player-forecast-stat small {font-size:.83rem;}
.player-forecast-stat small {display:block;}
.player-meeting-table {width:100%; table-layout:fixed; border-collapse:collapse; font-size:.9rem;}
.player-meeting-table th,.player-meeting-table td {padding:.6rem .7rem; vertical-align:top;
    text-align:left; border-bottom:1px solid color-mix(in srgb,currentColor 18%,transparent);
    overflow-wrap:anywhere;}
.player-meeting-table thead {background:color-mix(in srgb,currentColor 8%,transparent);}
.player-meeting-table tbody tr:nth-child(even) {background:rgba(181,75,28,.035);}
.player-meeting-date {width:6rem;}
.player-meeting-team {display:block; margin-bottom:.35rem; font-size:.82rem;}
.player-meeting-stats {display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.2rem;}
.player-meeting-stats span {display:flex; flex-direction:column; padding:.15rem .25rem;}
.player-meeting-stats .player-meeting-lead {
    border-radius:.35rem; background:rgba(22,132,88,.15);
}
.player-meeting-lead small::after {content:" ↑";}
.player-meeting-stats strong {font-variant-numeric:tabular-nums;}
.player-meeting-stats small,.player-meeting-table time small {font-size:.72rem;}
@media(max-width:640px) {
    .player-meeting-table th,.player-meeting-table td {padding:.5rem .38rem;}
    .player-meeting-date {width:3.65rem;}
    .player-meeting-stats {grid-template-columns:repeat(2,minmax(0,1fr));}
}
</style>
"""


@st.cache_data(show_spinner=False, max_entries=512)
def cached_player_forecast(version, model_modified, player_id, opponent_id, when, home):
    from src.models import player
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1, user_api="openmp"):
        forecast, _ = player.predict(
            table("player_games", version), table("team_games", version),
            player_id, opponent_id, when, home, model("player", version, model_modified),
        )
    return forecast


def player_forecast_cards(sides, forecasts, recent):
    from html import escape

    stat_labels = {"points": "PTS", "rebounds": "REB", "assists": "AST"}
    cards = []
    for (side, player_id, player_name, team_name, color), forecast in zip(sides, forecasts):
        games = recent.loc[recent.player_id.eq(player_id)].tail(10)
        stats = []
        for row in forecast.itertuples():
            count = int(games[row.stat].count())
            baseline_label = "recent avg." if count else "training avg."
            stats.append(
                f'<div class="player-forecast-stat"><b>{stat_labels[row.stat]}</b>'
                '<div class="player-forecast-values">'
                f'<strong>{row.prediction:.1f}</strong><span>projected</span>'
                f'<span>{row.baseline:.1f} {baseline_label}</span></div>'
                f'<small>80% range {row.low:.1f}–{row.high:.1f}</small></div>'
            )
        availability = f"Recent averages use {len(games)} {'game' if len(games) == 1 else 'games'} this season."
        if games.empty:
            availability = "No earlier games this season. The comparison uses a training average."
        cards.append(
            f'<article class="forecast-side" style="--accent:{color}">'
            f'<small>{side} · {escape(team_name)}</small><h4>{escape(player_name)}</h4>'
            + "".join(stats) + f"<small>{availability}</small></article>"
        )
    st.html('<div class="forecast-scoreboard player-forecast-cards">' + "".join(cards) + "</div>")


def player_forecast_charts(sides, forecasts, recent):
    import plotly.graph_objects as go

    st.markdown("**Compare projections and ranges**")
    st.caption("Bar length shows the projection. ○ marks the recent average (or training average), and the line shows the approximate 80% range.")
    stats = (("points", "Points"), ("rebounds", "Rebounds"), ("assists", "Assists"))
    forecasts_by_stat = [forecast.set_index("stat") for forecast in forecasts]
    row_labels = [side[2] for side in sides]
    if row_labels[0] == row_labels[1]:
        row_labels = [f"{side[2]} ({side[0]})" for side in sides]
    with st.container(key="player_forecast_charts"):
        for stat, title in stats:
            values = [forecast.loc[stat] for forecast in forecasts_by_stat]
            fig = go.Figure(go.Bar(
                x=[row.prediction for row in values], y=[1, 0], orientation="h", width=.48,
                marker=dict(color=[side[4] for side in sides]), opacity=.6, hovertext=row_labels,
                hovertemplate="%{hovertext}<br>Projection: %{x:.1f}<extra></extra>",
            ))
            maximum = max(1, *(max(row.prediction, row.baseline, row.high) for row in values))
            for y, side, row in zip((1, 0), sides, values):
                _, pid, name, _, _ = side
                game_values = recent.loc[recent.player_id.eq(pid), stat].tail(10)
                baseline = "Recent average" if game_values.notna().any() else "Training average"
                fig.add_trace(go.Scatter(
                    x=[row.low, row.high], y=[y, y], mode="lines",
                    line=dict(color="#425563", width=3),
                    hovertemplate=f"{name}<br>80% range: {row.low:.1f}–{row.high:.1f}<extra></extra>",
                ))
                fig.add_trace(go.Scatter(
                    x=[row.baseline], y=[y], mode="markers",
                    marker=dict(color="#202c36", symbol="circle-open", size=13, line=dict(width=2)),
                    hovertemplate=f"{name}<br>{baseline}: %{{x:.1f}}<extra></extra>",
                ))
            fig.update_layout(
                title=dict(text=title, x=.03, font=dict(size=15)),
                height=210, margin=dict(l=110, r=22, t=38, b=32), showlegend=False,
            )
            fig.update_yaxes(
                tickmode="array", tickvals=[1, 0], ticktext=row_labels,
                range=[-.55, 1.55], automargin=True, fixedrange=True, tickfont=dict(size=11),
            )
            fig.update_xaxes(range=[0, maximum * 1.12], fixedrange=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def player_past_meetings(players, away_id, home_id, when, away_name, home_name, teams):
    from html import escape
    from src.models import player

    st.subheader("Past meetings")
    meetings = player.encounters(players, away_id, home_id, when)
    count = len(meetings)
    st.write(f"**{count} recorded {'meeting' if count == 1 else 'meetings'}**")
    st.caption("Both players appeared on opposing teams in these games. The box scores don’t show who guarded whom.")
    if not count:
        return
    if count < 3:
        st.info("This is a small sample. A single game can give a very different impression of the matchup.")
    st.caption("A highlight and arrow mark the higher total for points, rebounds, or assists in each game.")
    columns = ["game_id", "points", "rebounds", "assists", "minutes"]
    home_games = players.loc[players.player_id.eq(home_id) & players.played, columns]
    meetings = meetings.merge(home_games, on="game_id", validate="one_to_one", suffixes=("", "_other"))
    meetings = meetings.sort_values("date", ascending=False)

    def box_score(game, suffix):
        team = teams.get(getattr(game, f"team_id{suffix}"), "Team unavailable")
        stats = []
        other_suffix = "" if suffix else "_other"
        for stat, label in (("points", "PTS"), ("rebounds", "REB"), ("assists", "AST"), ("minutes", "MIN")):
            value = getattr(game, f"{stat}{suffix}")
            other = getattr(game, f"{stat}{other_suffix}")
            display = f"{value:.0f}" if pd.notna(value) else "—"
            leads = stat != "minutes" and pd.notna(value) and pd.notna(other) and value > other
            marker = f' class="player-meeting-lead" title="Led in {stat}"' if leads else ""
            stats.append(f"<span{marker}><strong>{display}</strong><small>{label}</small></span>")
        return (
            f'<td><span class="player-meeting-team">{escape(team)}</span>'
            f'<div class="player-meeting-stats">{"".join(stats)}</div></td>'
        )

    rows = []
    for game in meetings.itertuples():
        date = game.date
        rows.append(
            f'<tr><th scope="row"><time datetime="{date:%Y-%m-%d}">'
            f'{date:%b} {date.day}<br><small>{date.year}</small></time></th>'
            f'{box_score(game, "")}{box_score(game, "_other")}</tr>'
        )
    st.html(
        '<table class="player-meeting-table" aria-label="Past meeting box scores">'
        '<thead><tr><th class="player-meeting-date" scope="col">Game date</th>'
        f'<th scope="col">{escape(away_name)}</th><th scope="col">{escape(home_name)}</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table>'
    )


def player_page(p, t, teams, version):
    st.html(FORECAST_STYLE + PLAYER_MATCHUP_STYLE)
    st.header("Player Matchup Lab")
    st.write("Pick a game and one player on each side to compare projected points, rebounds, and assists. See how both players did in recorded meetings.")
    if p.empty:
        st.info("No player game logs are available in this snapshot.")
        return
    team_names = teams.set_index("team_id").team_name.to_dict()
    matchup_choice = forecast_matchup(team_names, version, p.date.max(), "player")
    if matchup_choice is None:
        return
    home, away, when = matchup_choice
    st.caption(f"Player box scores are available through {p.date.max():%b %d, %Y}. Forecasts use games before the selected date.")

    prior = p.loc[p.date.lt(pd.Timestamp(when)) & p.played].sort_values(["date", "game_id"])
    roster = prior.drop_duplicates("player_id", keep="last").copy()
    recent = prior.groupby("player_id").tail(10)
    roster["recent_minutes"] = roster.player_id.map(recent.groupby("player_id").minutes.mean())
    roster = roster.loc[roster.season_start.eq(roster.season_start.max())]
    st.caption("Choose players from their last recorded teams before this matchup. The snapshot doesn’t confirm active lineups.")
    away_col, home_col = st.columns(2)
    with away_col:
        away_id = choose(roster.loc[roster.team_id.eq(away)], "p_b", "Away player")
    with home_col:
        home_id = choose(roster.loc[roster.team_id.eq(home)], "p_a", "Home player")
    if away_id is None or home_id is None:
        st.info("A player is needed from both teams. Try another date or matchup with recorded rosters.")
        return

    player_names = roster.set_index("player_id").player_name
    sides = [
        ("Away", away_id, player_names[away_id], team_names[away], team_color(teams, away)),
        ("Home", home_id, player_names[home_id], team_names[home], team_color(teams, home)),
    ]
    st.subheader("Player forecasts")
    try:
        modified = (APP.parent / "artifacts" / "player.pkl").stat().st_mtime_ns
        forecasts = [
            cached_player_forecast(version, modified, away_id, home, when, False),
            cached_player_forecast(version, modified, home_id, away, when, True),
        ]
    except (ValueError, FileNotFoundError) as exc:
        st.warning(str(exc))
    else:
        game_day = pd.Timestamp(when)
        season_start = game_day.year if game_day.month >= 7 else game_day.year - 1
        recent_season = prior.loc[prior.season_start.eq(season_start)]
        player_forecast_cards(sides, forecasts, recent_season)
        st.caption("Projections and ranges are estimates for each player against the opposing team.")
        player_forecast_charts(sides, forecasts, recent_season)

    player_past_meetings(p, away_id, home_id, when, player_names[away_id], player_names[home_id], team_names)
    performance("player")
    with st.expander("How to read Player Matchups"):
        st.markdown(
            f"""
- **Projected PTS, REB, and AST** — Estimated points, rebounds, and assists for each player against the opposing team.
- **Recent average** — Up to 10 earlier played games in the same season. When none are available for a stat, the comparison uses the training average.
- **80% range** — An approximate set of outcomes based on historical forecast errors. Players can finish outside it.
- **Past meetings** — Games in this snapshot before the selected date where both players appeared for opposing teams. The box scores show each player's team and individual result.
            """
        )


@st.cache_data(show_spinner=False)
def breakout_history(seasons):
    return season_features(seasons)


def breakout_progress_chart(history, metric, label, color, target=None):
    chart = px.line(
        history, x="season", y=metric, markers=True, custom_data=["games"],
        labels={"season": "Season", metric: label}, color_discrete_sequence=[color],
    )
    chart.update_traces(
        connectgaps=False,
        hovertemplate=f"%{{x}}<br>{label} %{{y:.1f}}<br>%{{customdata[0]}} games played<extra></extra>",
    )
    if target is not None:
        chart.add_hline(y=target, line_dash="dash", line_color=color)
    chart.update_layout(height=285, margin=dict(l=8, r=12, t=12, b=8))
    chart.update_xaxes(title=None, type="category")
    chart.update_yaxes(range=[0, 100] if metric == "pra_pctl" else None, rangemode="tozero")
    st.plotly_chart(chart, use_container_width=True)


BREAKOUT_CARD_STYLE = """
<style>
.breakout-panel {border:1px solid #8794a455;border-radius:.7rem;overflow:hidden;}
.breakout-targets {display:grid;gap:0 1rem;padding:.85rem 1rem;}
.breakout-target {min-width:0;}
.breakout-target h4 {font-size:1.08rem;margin:0;border-bottom:3px solid var(--accent);padding:.25rem 0 .55rem;}
.breakout-row {display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:.5rem;
    align-items:baseline;padding:.55rem 0;border-bottom:1px solid #8794a433;}
.breakout-row small {font-size:.85rem;}
.breakout-current strong {font-size:1.35rem;line-height:1.2;}
.breakout-status {font-size:.9rem;}
.breakout-qualification {display:grid;gap:.25rem;padding:.5rem 1rem;font-size:.85rem;}
.breakout-qualification ul {display:flex;flex-wrap:wrap;gap:.25rem 1rem;list-style:none;margin:0;padding:0;}
.breakout-check {font-weight:700;}
.breakout-check.met {color:#168458;}
.breakout-raw {display:flex;flex-wrap:wrap;align-items:baseline;gap:.25rem .75rem;
    background:color-mix(in srgb,#168458 8%,transparent);padding:.75rem 1rem;}
.breakout-raw strong {font-size:1.12rem;}
@media(min-width:641px) {
    .breakout-targets {grid-template-columns:repeat(2,minmax(0,1fr));}
    .breakout-target {display:contents;}
    .breakout-target > * {grid-column:var(--track);}
    .breakout-target > :nth-child(1) {grid-row:1;}
    .breakout-target > :nth-child(2) {grid-row:2;}
    .breakout-target > :nth-child(3) {grid-row:3;}
    .breakout-target > :nth-child(4) {grid-row:4;}
    .breakout-target > :nth-child(5) {grid-row:5;}
}
@media(max-width:640px) {.breakout-target + .breakout-target {margin-top:.8rem;}}
</style>
"""


def breakout_progress_column(title, track, color, baseline, current, target, unit, in_progress, pending,
                             provisional=False):
    from html import escape

    current_value = f"{current:.2f}" if pd.notna(current) else "Unavailable"
    if pd.isna(current):
        status = pending
    elif current >= target:
        status = "At or above target so far" if in_progress else "Target met"
    else:
        gap = target - current
        distance = f"{gap:.2f}" if gap >= 0.01 else "Less than 0.01"
        gap_unit = "percentile points" if unit == "league percentile" else unit
        status = f"{distance} {gap_unit} to go" if in_progress else f"Finished {distance.lower()} {gap_unit} short"
    return f"""
    <article class="breakout-target" style="--accent:{color};--track:{track}">
        <h4>{escape(title)} <small>· {escape(unit)}</small></h4>
        <div class="breakout-row breakout-current"><small>This season{" · provisional" if provisional else ""}</small><strong>{current_value}</strong></div>
        <div class="breakout-row"><small>Last season</small><strong>{baseline:.2f}</strong></div>
        <div class="breakout-row"><small>Target</small><strong>{target:.2f}</strong></div>
        <div class="breakout-row breakout-status"><small>Progress</small><strong>{escape(status)}</strong></div>
    </article>
    """


def breakout_chance_label(probability):
    if probability < 0.001:
        return "<0.1%"
    if probability < 0.10:
        return f"{probability:.1%}"
    return f"{probability:.0%}"


def breakout_test_results(cohort, history):
    for outcome_start, season_test in cohort.groupby("season_start", sort=False):
        outcome_start = int(outcome_start)
        outcome = f"{outcome_start}-{(outcome_start + 1) % 100:02d}"
        baseline = f"{outcome_start - 1}-{outcome_start % 100:02d}"
        ranked = season_test.sort_values("prediction", ascending=False, kind="stable")
        ranked = ranked.assign(rank=range(1, len(ranked) + 1))
        top = ranked.head(15)
        heading(f"How the model did in {outcome}", "#3675a2")
        st.write(
            f"We ranked players using their {baseline} stats, then checked who met all three "
            f"breakout criteria in {outcome}."
        )
        leaders_score, cohort_score = st.columns(2)
        leaders_score.metric(f"Broke out among the top {len(top)} predictions", f"{int(top.actual.sum())} of {len(top)}")
        cohort_score.metric("Breakout rate across all players in the test", f"{ranked.actual.mean():.1%}")
        st.caption(f"{int(ranked.actual.sum())} of {len(ranked)} players in the test broke out.")

        fields = ["player_id", "season_start", "player_name", "mpg", "pra_pctl"]
        before = history.loc[history.season_start.eq(outcome_start - 1), fields]
        after = history.loc[history.season_start.eq(outcome_start), fields]
        hits = ranked.loc[ranked.actual.eq(1)].merge(
            before.drop(columns="season_start"), on="player_id", how="left", validate="one_to_one",
        ).merge(
            after.drop(columns="season_start"), on="player_id", how="left",
            suffixes=("_before", "_after"), validate="one_to_one",
        )

        def change(before_value, after_value, suffix=""):
            if pd.isna(before_value) or pd.isna(after_value):
                return "Unavailable"
            return f"{before_value:.1f} → {after_value:.1f} ({after_value - before_value:+.1f}{suffix})"

        rows = pd.DataFrame({
            "Preseason Rank": hits["rank"],
            "Player": hits.player_name_after.fillna(hits.player_name_before).fillna(hits.player_id.map("Player {}".format)),
            "Minutes per Game": [change(a, b) for a, b in zip(hits.mpg_before, hits.mpg_after)],
            "Production Percentile": [change(a, b, " pts") for a, b in zip(hits.pra_pctl_before, hits.pra_pctl_after)],
            "Predicted Breakout Chance": hits.prediction.map(breakout_chance_label),
        })
        st.markdown(f"**Who broke out among the top {len(top)} predictions?**")
        top_hits = rows.loc[rows["Preseason Rank"].le(len(top))]
        if top_hits.empty:
            st.write("None of the top predictions met all three breakout criteria.")
        else:
            st.dataframe(top_hits, hide_index=True, use_container_width=True)
        if not rows.empty:
            st.caption(f"Each row shows {baseline} → {outcome}, with the change in parentheses. Rank is within the test group.")
            with st.expander(f"See all {len(rows)} players who broke out in {outcome}"):
                st.dataframe(rows, hide_index=True, use_container_width=True)


def breakout_page(seasons, version):
    st.markdown(FORECAST_STYLE, unsafe_allow_html=True)
    st.header("Breakout Watch")
    st.write("Find players projected to earn a bigger role and improve their production, then follow their progress through the forecast season.")
    if not (APP / "breakout_candidates.csv.gz").exists():
        st.info("Breakout forecasts are unavailable until the model has been prepared.")
        return
    candidates = table("breakout_candidates", version).sort_values(
        ["probability", "player_name"], ascending=[False, True],
    ).reset_index(drop=True)
    if candidates.empty:
        st.info("No breakout candidates are available.")
        return

    baseline_start = int(candidates.iloc[0].season_start)
    forecast_start = baseline_start + 1
    forecast_season = f"{forecast_start}-{(forecast_start + 1) % 100:02d}"
    baseline_season = candidates.iloc[0].season
    latest_completed = json.loads((APP / "manifest.json").read_text())["latest_completed_start"]
    st.caption(f"{forecast_season} preseason forecast · Based on the completed {baseline_season} season")
    with st.container(border=True):
        st.markdown("**What counts as a breakout? A player must hit all three marks.**")
        st.markdown(
            "- Average **at least 20 minutes per game**.\n"
            "- Add **at least 5 minutes per game** compared with the prior season.\n"
            "- Gain **at least 15 percentile points** in combined points, rebounds, and assists per 36 minutes."
        )
        st.caption("Production percentiles compare players in the same season with at least 20 games played and 15 minutes per game.")

    heading("Preseason watchlist", "#bd652e")
    pid = choose(candidates, "breakout_player", "Search for a candidate")
    selected = candidates.loc[candidates.player_id.eq(pid)].iloc[0]
    chance_label = breakout_chance_label(selected.probability)
    leaders = candidates.head(10).copy()
    leaders["label"] = [f"{i + 1}. {name}" for i, name in leaders.player_name.items()]
    leaders["chance_label"] = leaders.probability.map(breakout_chance_label)
    chart = px.bar(
        leaders, x="probability", y="label", orientation="h", text="chance_label",
        labels={"probability": "Estimated breakout chance", "label": "Player"},
    )
    chart.update_traces(
        marker_color=["#bd652e" if player == pid else "#637e90" for player in leaders.player_id],
        textposition="outside", cliponaxis=False,
        hovertemplate="%{y}<br>Estimated chance %{text}<extra></extra>",
    )
    chart.update_xaxes(tickformat=".0%", range=[0, 1])
    chart.update_yaxes(autorange="reversed", title=None)
    chart.update_layout(height=365, margin=dict(l=8, r=38, t=8, b=8))
    st.plotly_chart(chart, use_container_width=True)
    st.caption("The chart shows the top 10. Search covers all candidates. Eligibility requires 20 games, 15 minutes per game, and a production percentile below 80 in the prior season. Incoming rookies have no NBA baseline.")

    heading(selected.player_name, "#bd652e")
    with st.container(border=True):
        st.metric("Preseason forecast · Breakout chance", chance_label,
                  delta=f"Rank {selected.name + 1} of {len(candidates)}", delta_color="off")
        chance_phrase = "less than a **0.1% chance**" if chance_label == "<0.1%" else f"a **{chance_label} chance**"
        st.write(
            f"The model estimates {chance_phrase} that {selected.player_name} "
            f"meets both the playing-time and production targets by the end of {forecast_season}."
        )
    st.write(
        f"{selected.player_name} averaged **{selected.pra_per36:.1f} combined points, rebounds, and assists "
        f"per 36 minutes** across **{int(selected.games)} games** in {baseline_season}."
    )
    if pd.notna(selected.mpg_change) and abs(selected.mpg_change) >= 0.1:
        direction = "up" if selected.mpg_change > 0 else "down"
        st.caption(f"Playing time was {direction} {abs(selected.mpg_change):.1f} minutes per game from the season before.")

    heading(f"{forecast_season} season progress", "#3675a2")
    games = table("player_games", version)
    through = games.loc[
        games.season_start.eq(forecast_start) & games.played.eq(1) & games.minutes.gt(0), "date"
    ].max()
    if pd.notna(through):
        st.caption(f"League box scores through {through:%b} {through.day}, {through.year}")
    all_history = breakout_history(seasons)
    in_progress = forecast_start > latest_completed
    season_players = all_history.loc[all_history.season_start.eq(forecast_start)]
    min_games = 20
    if in_progress and not season_players.empty:
        team_games = table("team_games", version)
        counts = team_games.loc[team_games.season.eq(forecast_season)].groupby("team_id").game_id.nunique()
        if counts.reindex(table("teams", version).team_id, fill_value=0).lt(20).any():
            min_games = 5
    provisional = min_games < 20
    if provisional:
        eligible = season_players.games.ge(min_games) & season_players.mpg.ge(15)
        tracker_ranks = season_players.pra_per36.where(eligible).rank(method="average", pct=True) * 100
        st.info(
            f"**Early-season production rank.** For now, the minimum is {min_games} games played and 15 MPG "
            f"({tracker_ranks.count()} qualifying players). Percentiles can shift substantially as more "
            "games are played and more players qualify. The standard 20-game minimum returns once every "
            "team has 20 recorded games."
        )
    history = all_history.loc[all_history.player_id.eq(pid) & all_history.season_start.le(forecast_start)].copy()
    if provisional:
        current_season = history.season_start.eq(forecast_start)
        history.loc[current_season, "pra_pctl"] = tracker_ranks.reindex(history.index[current_season])
    forecast_row = history.loc[history.season_start.eq(forecast_start)]
    if forecast_row.empty:
        st.info("No games for this player are available in the forecast season.")
    elif in_progress:
        st.info(f"In progress · {int(forecast_row.iloc[0].games)} games played in the available data. Averages and league percentiles can shift as more games are played.")
    st.caption("Dashed lines show the player's individual breakout targets. The preseason estimate stays fixed.")

    minutes_target = max(20, selected.mpg + 5)
    percentile_target = selected.pra_pctl + 15
    current = forecast_row.iloc[0] if not forecast_row.empty else None
    pending = "No forecast-season stats available."
    qualification = ""
    if current is not None:
        pending = "Qualification pending" if in_progress else "Percentile unavailable"
        requirements = [
            (current.games >= min_games, f"{int(current.games)} of {min_games} games played"
             if current.games < min_games else f"At least {min_games} games played"),
            (current.mpg >= 15, "At least 15 MPG"),
        ]
        items = []
        for met, label in requirements:
            icon, state = ("✓", "Met") if met else ("○", "Not met")
            style = " met" if met else ""
            items.append(f'<li><span class="breakout-check{style}" role="img" aria-label="{state}">{icon}</span> {label}</li>')
        qualification = f'<div class="breakout-qualification"><strong>Production rank requirements</strong><ul>{"".join(items)}</ul></div>'
        if current.mpg >= minutes_target:
            playing_time = "is at or above the playing-time target" if in_progress else "met the playing-time target"
        else:
            gap = minutes_target - current.mpg
            distance = f"{gap:.2f} MPG" if gap >= 0.01 else "less than 0.01 MPG"
            playing_time = f"is {distance} short of the playing-time target" if in_progress else f"finished {distance} short of the playing-time target"
        if pd.isna(current.pra_pctl):
            production = "the production rank is still pending" if in_progress else "the final production rank was unavailable"
        else:
            position = "at or above" if current.pra_pctl >= percentile_target else "below"
            rank_type = "provisional production rank" if provisional else "production rank"
            production = f"the {rank_type} is {position} the production target"
        st.markdown(f"**Progress at a glance.** {selected.player_name} {playing_time}, and {production}.")
    else:
        st.markdown(f"**Progress at a glance.** There are no recorded {forecast_season} games for {selected.player_name} yet.")
    minutes_column = breakout_progress_column(
        "Playing time", 1, "#3675a2", selected.mpg,
        current.mpg if current is not None else float("nan"), minutes_target, "MPG",
        in_progress, "No forecast-season minutes available.",
    )
    production_column = breakout_progress_column(
        "Production rank", 2, "#168458", selected.pra_pctl,
        current.pra_pctl if current is not None else float("nan"), percentile_target,
        "league percentile", in_progress, pending,
        provisional=provisional,
    )
    raw_production = (
        f"{current.pra_per36:.1f}"
        if current is not None and pd.notna(current.pra_per36) else "Unavailable"
    )
    st.html(f"""
        {BREAKOUT_CARD_STYLE}
        <section class="breakout-panel" aria-label="Breakout progress">
            <div class="breakout-targets">{minutes_column}{production_column}</div>
            {qualification}
            <div class="breakout-raw"><span>Production per 36 min this season</span>
                <strong>{raw_production}</strong><small>Points + rebounds + assists</small>
            </div>
        </section>
    """)
    if provisional:
        st.caption("This season’s production percentile uses a 5-game minimum. Last season’s baseline and the official breakout criteria use 20 games.")
    st.caption("The playing-time target covers both requirements: 20 MPG or more and an increase of at least 5 MPG over last season.")
    st.markdown(f"**Minutes per game · Target {minutes_target:.2f}**")
    breakout_progress_chart(history, "mpg", "Minutes per game", "#3675a2", minutes_target)
    chart_title = "Production percentile (current season provisional)" if provisional else "Production percentile"
    st.markdown(f"**{chart_title} · Target {percentile_target:.2f}**")
    breakout_progress_chart(history, "pra_pctl", "Production percentile", "#168458", percentile_target)
    st.caption("Production rank compares combined points, rebounds, and assists per 36 minutes with eligible players in the same season. The standard ranking requires at least 20 games played and 15 MPG.")
    with st.expander("See production per 36 minutes"):
        st.caption("Combined points, rebounds, and assists per 36 minutes. This view also shows seasons when the player has too few games to earn a percentile.")
        breakout_progress_chart(history, "pra_per36", "Points + rebounds + assists per 36", "#168458")

    if (APP / "backtest_breakout_breakout.csv.gz").exists():
        cohort = table("backtest_breakout_breakout", version).query("period == 'test'")
        breakout_test_results(cohort, all_history)
    performance("breakout")
    with st.expander("How to read Breakout Watch"):
        st.markdown(
            f"""
- **Preseason chance** — The model estimates the chance of meeting all three breakout marks by season’s end. It uses the prior completed season’s stats and stays fixed as new games are added.
- **Who makes the watchlist** — Players with at least 20 games, at least 15 minutes per game, and a production percentile below 80 in the prior season. Incoming rookies have no NBA baseline.
- **Playing time** — Minutes per game counts games the player appeared in. The individual target is whichever is higher: 20 MPG or their prior-season average plus 5 MPG.
- **Production per 36** — Points, rebounds, and assists added together and scaled to 36 minutes. The **production percentile** ranks that rate against eligible players in the same season. The breakout target is a gain of at least 15 percentile points.
- **Early-season rankings** — The tracker can show provisional percentiles for players with 5 games and 15 MPG. It returns to the 20-game minimum once every team has 20 recorded games. Early ranks can move as players log more games and the comparison group grows.
- **Historical test** — The backtest ranks players using prior-season data, then checks who met all three criteria in a season held back from training. The top 15 are part of the full test group.
            """
        )
