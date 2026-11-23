"""Presentation UI consuming only compact app-ready files and trusted models."""
from datetime import timedelta
from html import escape
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


def matchup(teams, version, key, latest):
    lookup = teams.set_index("team_id").team_name.to_dict()
    manual = st.toggle("Build a custom matchup", key=key+"_manual")
    if manual:
        c1,c2=st.columns(2)
        home=c1.selectbox("Home team",list(lookup),format_func=lookup.get,key=key+"_home")
        away=c2.selectbox("Away team",[tid for tid in lookup if tid!=home],format_func=lookup.get,key=key+"_away")
        when=st.date_input("Game date",(latest+timedelta(days=1)).date(),key=key+"_date")
        return home,away,when
    games=table("games",version)
    fixtures=games[["game_id","date","home_team_id","away_team_id"]]
    if (APP/"schedule.csv.gz").exists():
        fixtures=pd.concat([fixtures,table("schedule",version)]).drop_duplicates("game_id")
    fixtures=fixtures[fixtures.date.gt(pd.Timestamp("2025-04-13")) & fixtures.home_team_id.isin(lookup) & fixtures.away_team_id.isin(lookup)]
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


def impact_page(impacts,teams):
    st.header("On/Off Impact")
    st.caption("Pick a player and team stint to see how the team’s scoring margin changes while they play. Use the minutes filter to compare players with similar playing time.")
    available=sorted(impacts.loc[impacts.season_start>=2023,"season"].unique(),reverse=True)
    season=st.selectbox("Season",available,index=min(1,len(available)-1),key="impact_season")
    f=impacts[impacts.season.eq(season)].copy()
    pid=choose(f,"impact_player")
    if pid is None: st.info("No impact data."); return
    lookup=teams.set_index("team_id").team_name.to_dict()
    player_rows=f[f.player_id.eq(pid)]
    tid=st.selectbox("Team stint",sorted(player_rows.team_id,key=lookup.get),format_func=lambda x:lookup.get(x,str(x)),key="impact_team")
    row=player_rows[player_rows.team_id.eq(tid)].iloc[0]
    heading(row.player_name,team_color(teams,tid))
    st.caption(f"Reliability: {row.reliability}; {row.minutes_on:.0f} on minutes / {row.minutes_off:.0f} off minutes")
    for col,field,label in zip(st.columns(4),["on_off_diff","on_per48","off_per48","game_score"],["On/off difference","On per 48","Off per 48","Mean Game Score"]):
        value=row[field]; col.metric(label,f"{value:+.2f}" if pd.notna(value) else "N/A")
    st.info(impact.missed_message(row))
    comparison=pd.DataFrame({"Availability":["Played","Missed game"],"Average scoring margin":[row.with_margin,row.without_margin],"Win rate":[row.with_win_pct,row.without_win_pct]})
    st.plotly_chart(px.bar(comparison,x="Availability",y="Average scoring margin",hover_data={"Win rate":":.0%"},color_discrete_sequence=[team_color(teams,tid)]),use_container_width=True)
    minimum=st.slider("Leaderboard minimum on-court minutes",0,2500,500,100)
    qualified=f[f.games.ge(20)&f.minutes_on.ge(minimum)]
    st.plotly_chart(impact.scatter(qualified,pid),use_container_width=True)
    with st.expander("Compare player minutes and impact"):
        detail=qualified.nlargest(30,"on_off_diff")[["player_name","minutes_on","minutes_off","on_off_diff","reliability"]].copy()
        detail.columns=["Player","Minutes on court","Minutes off court","Margin swing per 48","Reliability"]
        st.dataframe(detail.round(1),hide_index=True,width="stretch")


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


def team_page(t,teams,version):
    st.header("Team Matchup Predictor")
    st.caption("Choose a game to forecast the final score and each team’s chance of winning. Compare their recent scoring margins below.")
    lookup=teams.set_index("team_id").team_name.to_dict()
    h,a,when=matchup(teams,version,"team",t.date.max())
    color_map={lookup[h]:team_color(teams,h),lookup[a]:team_color(teams,a)}
    use_spread=st.checkbox("Include a signed home spread")
    spread=st.number_input("Home spread (negative means home favorite)",value=-4.5,step=.5) if use_spread else None
    odds=APP/"odds_today.csv"
    if odds.exists():
        with st.expander("Cached upcoming market lines"):
            st.dataframe(pd.read_csv(odds),hide_index=True)
            st.caption("Snapshot only. Check retrieval time; manual selections are not automatically matched to a quote.")
    else: st.caption("Live market lines are unavailable in this snapshot.")
    if st.button("Predict team matchup"):
        try:
            from src.models import team
            r=team.predict(t,h,a,when,spread,bundle("team",version))
            st.session_state["team_prediction"]=(h,a,str(when),spread,r)
        except (ValueError,FileNotFoundError) as exc: st.warning(str(exc))
    saved=st.session_state.get("team_prediction")
    if saved and saved[:4]==(h,a,str(when),spread):
        r=saved[4]
        heading(f"{lookup[h]} {r['home_score']:.1f} : {r['away_score']:.1f} {lookup[a]}",color_map[lookup[h]])
        for col,label,value in zip(st.columns(4),["Home win","Away win","Home margin","Total points"],[f"{r['home_win']:.1%}",f"{r['away_win']:.1%}",f"{r['margin']:+.1f}",f"{r['total']:.1f}"]): col.metric(label,value)
        dist=r["distribution"]
        st.write(f"Approximate 80% margin prediction interval: {dist['low']:.0f} to {dist['high']:.0f}")
        if spread is not None: st.write(f"Spread outcomes · Home covers {dist['home_cover']:.0%} · Away covers {dist['away_cover']:.0%} · Tie {dist['push']:.0%}")
        if r["disagreement"]: st.warning("Winner classifier and margin regressor disagree. These are separate estimates.")
        st.caption(f"Model available after validation/calibration through {r['cutoff']}; data version {r['version']}. Historical cutoff enforced.")
    window=st.selectbox("Comparison window",[5,10,20])
    history=t[t.date<pd.Timestamp(when)]
    recent=history[history.team_id.isin([h,a])].sort_values("date").groupby("team_id").tail(window)
    st.subheader("Recent team context")
    st.caption("Above zero means the team outscored its opponent. Pick a point to see the game date.")
    st.plotly_chart(px.line(recent,x="date",y="margin",color="team_name",markers=True,color_discrete_map=color_map,labels={"date":"Game date","team_name":"Team","margin":"Scoring margin"}),use_container_width=True)
    performance("team")


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
