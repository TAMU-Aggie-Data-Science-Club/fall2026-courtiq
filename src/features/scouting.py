"""Season-wide, metric-specific scouting ranks. No UI or fetching."""
import numpy as np
import pandas as pd

ALL_AROUND = {"points_pg":"Points / game", "assists_pg":"Assists / game",
               "rebounds_pg":"Rebounds / game", "steals_pg":"Steals / game",
               "blocks_pg":"Blocks / game", "ts_pct":"True shooting",
               "fg3_pct":"Three-point %", "ft_pct":"Free-throw %"}
SHOOTING = {"fg_pct":"Field-goal %", "fg2_pct":"Two-point %", "fg3_pct":"Three-point %",
            "ft_pct":"Free-throw %", "ts_pct":"True shooting", "efg_pct":"Effective FG %",
            "fg3a_pg":"3PA / game", "ftr":"Free-throw rate"}
ADVANCED = {
    "ts_pct": ("True shooting", ".1%", "Scoring efficiency including free throws."),
    "efg_pct": ("Effective FG%", ".1%", "Field-goal percentage with extra weight for made threes."),
    "ast_tov": ("Assist-to-turnover ratio", ".2f", "Assists per turnover. Available when the player has a turnover."),
    "points_per36": ("Points per 36 minutes", ".1f", "Scoring scaled to 36 minutes of playing time."),
    "rebounds_per36": ("Rebounds per 36 minutes", ".1f", "Rebounding scaled to 36 minutes of playing time."),
    "assists_per36": ("Assists per 36 minutes", ".1f", "Assists scaled to 36 minutes of playing time."),
}

METRIC_DETAILS = {
    "points_pg": ("Points per game", "Points scored per appearance.", "scoring volume"),
    "assists_pg": ("Assists per game", "Assists credited per appearance.", "setting up teammates"),
    "rebounds_pg": ("Rebounds per game", "Offensive and defensive rebounds per appearance.", "rebounding"),
    "steals_pg": ("Steals per game", "Steals credited per appearance.", "getting steals"),
    "blocks_pg": ("Blocks per game", "Shots blocked per appearance.", "blocking shots"),
    "ts_pct": ("True shooting", "Scoring efficiency including twos, threes and free throws.", "overall scoring efficiency"),
    "efg_pct": ("Effective FG%", "Field-goal percentage with extra weight for made threes.", "efficiency from the field"),
    "fg_pct": ("Field-goal %", "Share of shots from the field that went in.", "field-goal accuracy"),
    "fg2_pct": ("Two-point %", "Share of two-point attempts that went in.", "two-point accuracy"),
    "fg3_pct": ("Three-point %", "Share of three-point attempts that went in.", "three-point accuracy"),
    "ft_pct": ("Free-throw %", "Share of free-throw attempts that went in.", "free-throw accuracy"),
    "fg3a_pg": ("3PA per game", "Three-point attempts per appearance. Shows shot volume.", "three-point volume"),
    "ftr": ("Free-throw rate", "Free-throw attempts per 100 field-goal attempts.", "getting to the free-throw line"),
}
PLAYMAKING = {"assists_pg": "Assists / game", "assists_per36": "Assists / 36 minutes",
              "ast_tov": "Assists per turnover", "points_pg": "Points / game"}
METRIC_DETAILS.update({
    "assists_per36": ("Assists /36", "Assists scaled to 36 minutes of playing time.", "assists per 36 minutes"),
    "ast_tov": ("Assists per turnover", "Season assists divided by season turnovers.", "assists per turnover"),
})
DEFENSE_LENS = "Defense & Rebounding"
DEFENSE = {
    "steals_per36": ("Steals /36", "Steals per 36 minutes of playing time.", "steal production"),
    "blocks_per36": ("Blocks /36", "Blocked shots per 36 minutes of playing time.", "shot blocking"),
    "dreb_per36": ("Def. rebounds /36", "Defensive rebounds per 36 minutes.", "defensive rebounding volume"),
    "team_dreb_share": ("Team DREB share", "Share of team defensive rebounds in games the player appeared in, including rebounds collected while they sat.", "share of team defensive rebounds"),
    "oreb_per36": ("Off. rebounds /36", "Offensive rebounds per 36 minutes.", "offensive rebounding volume"),
    "drtg": ("Defensive Rating", "Points allowed per 100 possessions while on the floor. Lower ranks higher.", "defensive efficiency"),
    "fouls_per36": ("Foul Avoidance", "Fewer personal fouls per 36 minutes rank higher. Role and assignments can affect foul rate.", "foul avoidance"),
    "netrtg": ("Net Rating", "Team points scored minus points allowed per 100 possessions while on the floor.", "on-court scoring margin"),
}
METRIC_DETAILS.update(DEFENSE)
LENSES = {"All-Around": ALL_AROUND, "Shooting": SHOOTING,
          DEFENSE_LENS: {metric: details[0] for metric, details in DEFENSE.items()},
          "Playmaking": PLAYMAKING}
RATE_METRICS = {"ts_pct", "efg_pct", "fg_pct", "fg2_pct", "fg3_pct", "ft_pct", "ftr", "team_dreb_share"}
DEFENSE_COUNTS = {
    "steals_per36": "steals", "blocks_per36": "blocks", "dreb_per36": "dreb",
    "oreb_per36": "oreb", "fouls_per36": "fouls",
}
MISSING_DEFENSE = {
    "team_dreb_share": "Complete player and team rebound totals unavailable",
    "drtg": "Player on-court Defensive Rating unavailable",
    "netrtg": "Player on-court Net Rating unavailable",
}
DEFENSIVE_BADGES = {
    "Defensive Playmaker": ("🛡️", {"steals_per36": 85, "blocks_per36": 85}),
    "Shot Blocker": ("🚫", {"blocks_per36": 90}),
    "Ball Hawk": ("⚡", {"steals_per36": 90}),
    "Glass Cleaner": ("🧹", {"dreb_per36": 85, "team_dreb_share": 85}),
    "Second-Chance Creator": ("🔁", {"oreb_per36": 90}),
}


def percentile_color(value):
    if pd.isna(value):
        return "#697681"
    value = round(value)
    # Diverging orange (high) / blue (low) scale, checked for red-green color vision.
    if value >= 85:
        return "#a8441a"
    if value >= 50:
        return "#e08b4f"
    if value >= 30:
        return "#4d8fd6"
    return "#1f5bab"


def percentile_label(value):
    number = round(value)
    suffix = "th"
    if number % 100 not in (11, 12, 13):
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


def display_value(metric, value):
    if pd.isna(value):
        return "Unavailable"
    if metric == "ast_tov":
        return f"{value:.2f} per turnover"
    if metric == "ftr":
        return f"{value * 100:.1f} per 100 FGA"
    if metric in RATE_METRICS:
        return f"{value:.1%}"
    if metric == "fouls_per36":
        return f"{value:.1f} fouls per 36 min"
    if metric.endswith("_per36"):
        return f"{value:.1f} per 36 min"
    if metric in ("drtg", "netrtg"):
        return f"{value:.1f} per 100 poss."
    return f"{value:.1f} per game"


def ranking_status(metric, row, min_games=20):
    if not (row.games >= min_games and row.mpg >= 15):
        return f"Needs {min_games} games and 15 minutes per game"
    if metric == "fg3_pct" and row.fg3a < 50:
        return "Needs 50 three-point attempts"
    if metric == "ft_pct" and row.fta < 50:
        return "Needs 50 free-throw attempts"
    if metric in ("drtg", "netrtg") and row.get("ratings_coverage", 1) < .95:
        return "Needs ratings coverage for at least 95% of minutes"
    return MISSING_DEFENSE.get(metric, "Stat unavailable")


def canonical(frame):
    """Prefer TOT, otherwise require the sole team record; never silently double count."""
    groups = frame.groupby(["player_id", "season"], sort=False)
    total = frame.team_id.eq(0)
    selected = frame[total | groups.team_id.transform("size").eq(1)]
    if len(selected) != groups.ngroups or selected.duplicated(["player_id", "season"]).any():
        raise ValueError("Ambiguous combined player-season records")
    return selected.reset_index(drop=True)



def rankings(frame, season, lens="All-Around", min_games=20, min_mpg=15, directions=None):
    f=canonical(frame)
    f=f[f.season.eq(season)].copy()
    if lens == DEFENSE_LENS:
        minutes = f.minutes.where(f.minutes.gt(0))
        for metric, count in DEFENSE_COUNTS.items():
            f[metric] = 36 * f[count] / minutes
        for metric in MISSING_DEFENSE:
            if metric not in f:
                f[metric] = np.nan
    elif lens == "Shooting":
        f["fg3a_pg"] = f.fg3a / f.games.replace(0, np.nan)
    metrics = LENSES[lens]
    base=f.games.ge(min_games)&f.mpg.ge(min_mpg)
    pieces=[]
    for metric,label in metrics.items():
        threshold=f.fg3a.ge(50) if metric=="fg3_pct" else f.fta.ge(50) if metric=="ft_pct" else True
        eligible=base&threshold&f[metric].notna()
        values=f[metric].where(eligible)
        higher_better=(directions or {}).get(metric, metric not in ("drtg", "fouls_per36"))
        pieces.append(pd.DataFrame({"player_id":f.player_id,"season":season,"metric":metric,
            "label":label,"value":f[metric],"percentile":values.rank(method="average",pct=True,ascending=higher_better)*100,
            "rank":values.rank(method="min",ascending=not higher_better),
            "tied":values.notna()&values.duplicated(keep=False),"population":int(eligible.sum()),
            "qualified":eligible}))
    return pd.concat(pieces,ignore_index=True)


def report(breakdown, player_name="This player"):
    lookup=breakdown.dropna(subset=["percentile"]).set_index("metric").percentile
    badges=[]
    for metric,cut,label in [("points_pg",90,"Elite Scorer"),("fg3_pct",85,"Sharpshooter"),
        ("assists_pg",85,"Playmaker"),("rebounds_pg",90,"Rebounding Specialist")]:
        if lookup.get(metric,-1)>=cut: badges.append(label)
    if len(lookup[lookup.ge(75)])>=4: badges.append("All-Around Contributor")
    return badges[:3], scouting_summary(breakdown, player_name)


def scouting_summary(breakdown, player_name):
    valid = breakdown.dropna(subset=["percentile"]).sort_values("percentile", ascending=False)
    if valid.empty:
        return f"{player_name} has too little qualifying data for a league comparison this season."
    leaders = valid.head(2)
    strongest = " and ".join(METRIC_DETAILS[metric][2] for metric in leaders.metric)
    if leaders.percentile.min() >= 85:
        summary = f"{player_name} stands out among eligible players this season for {strongest}."
    else:
        summary = f"{player_name} ranks highest in {strongest} among the stats available for this profile."
    low = valid.iloc[-1]
    lower_area = METRIC_DETAILS[low.metric][2]
    if len(valid) <= 2:
        summary += " Too few stats qualify to give a fuller picture of this season."
    elif low.percentile < 30:
        summary += f" The lowest mark comes in {lower_area}, at the {percentile_label(low.percentile)} percentile."
    elif low.percentile < 50:
        summary += f" The profile is more modest in {lower_area}, the lowest league-relative ranking shown here."
    else:
        summary += " Every ranked stat reaches at least the middle of its league comparison group."
    return summary


def defensive_badges(breakdown):
    percentiles = breakdown.set_index("metric").percentile
    earned = [
        badge for badge, (_, requirements) in DEFENSIVE_BADGES.items()
        if all(percentiles.get(metric, np.nan) >= cutoff for metric, cutoff in requirements.items())
    ]
    if "Defensive Playmaker" in earned:
        earned = [badge for badge in earned if badge not in ("Shot Blocker", "Ball Hawk")]
    return earned


def defense_report(breakdown, player_name):
    ranked = breakdown.dropna(subset=["percentile"]).set_index("metric")
    profile = ranked.drop(index="fouls_per36", errors="ignore").sort_values("percentile", ascending=False)
    if profile.empty:
        summary = f"{player_name} has too little qualifying data for a defensive comparison this season."
    else:
        high, low = profile.iloc[0], profile.iloc[-1]
        high_area = DEFENSE[high.name][2]
        high_rank = percentile_label(high.percentile)
        summary = f"{player_name}'s highest available comparison is {high_area}, at the {high_rank} percentile."
        if len(profile) > 1 and low.percentile < high.percentile:
            low_area = DEFENSE[low.name][2]
            low_rank = percentile_label(low.percentile)
            summary += f" The lowest is {low_area}, at the {low_rank} percentile."
    if "fouls_per36" in ranked.index:
        foul_rank = percentile_label(ranked.loc["fouls_per36", "percentile"])
        summary += f" Foul avoidance is at the {foul_rank} percentile, based on how often they foul."
    return summary


def starting_position(row):
    positions = []
    for label, column in (("Guard", "guard_starts"), ("Forward", "forward_starts"), ("Center", "center_starts")):
        count = row.get(column, np.nan)
        if pd.notna(count) and count > 0:
            positions.append((label, int(count)))
    if not positions:
        return "", ""
    positions.sort(key=lambda position: position[1], reverse=True)
    total = sum(count for _, count in positions)
    shown = [positions[0]]
    shown.extend(position for position in positions[1:] if position[1] >= 2 and position[1] * 4 >= total)
    labels = " / ".join(label for label, _ in shown)
    counts = ", ".join(f"{label}: {count}" for label, count in shown)
    return labels, f"Recorded starting positions ({total} starts): {counts}"


def rank_label(rank, tied=False):
    """Standard competition rank: tied players share the best position, shown as T-107."""
    if pd.isna(rank):
        return "—"
    return f"T-{rank:.0f}" if tied else f"{rank:.0f}"


def radar(breakdown, color="#b54b1c", *, show_crowns=True, player_name="Selected player", neutral="#697681"):
    import plotly.graph_objects as go
    b=breakdown.reset_index(drop=True)
    if b.empty:
        return go.Figure()
    labels=b.metric.tolist()
    values=b.percentile.tolist()
    ticks = []
    for metric, value, rank in zip(labels, values, b["rank"]):
        title = METRIC_DETAILS[metric][0]
        crown = " 👑" if show_crowns and rank == 1 else ""
        placement = f"<b>{percentile_label(value)} pctile</b>" if pd.notna(value) else "Unranked"
        ticks.append(f"{title}{crown}<br>{placement}")
    red, green, blue = bytes.fromhex(color.lstrip("#"))
    complete=all(pd.notna(v) for v in values)
    fig=go.Figure()
    fig.add_trace(go.Scatterpolar(r=[50]*(len(labels)+1),theta=labels+[labels[0]],
        name="50th percentile",line=dict(color=neutral,dash="dot"),hoverinfo="skip"))
    theta=labels+[labels[0]]
    r=values+[values[0]]
    custom = [[METRIC_DETAILS[row.metric][0], display_value(row.metric, row.value),
               rank_label(row["rank"], row.get("tied", False)), row.population] for _, row in b.iterrows()]
    fig.add_trace(go.Scatterpolar(r=r,theta=theta,fill="toself" if complete else "none",
        connectgaps=False,mode="lines+markers",name=player_name,customdata=custom+[custom[0]],
        line=dict(color=color,width=3),fillcolor=f"rgba({red},{green},{blue},.16)",
        marker=dict(color=[percentile_color(value) for value in r],size=9),
        hovertemplate="%{customdata[0]}<br>%{customdata[1]}<br>%{r:.0f} percentile<br>Rank %{customdata[2]} of %{customdata[3]}<extra></extra>"))
    fig.update_layout(
        paper_bgcolor="#f3eee4",
        font=dict(color="#202c36"),
        polar=dict(
            bgcolor="#fffdf8",
            angularaxis=dict(tickmode="array",tickvals=labels,ticktext=ticks,gridcolor="#e7ddce"),
            radialaxis=dict(range=[0,100],tickvals=[0,25,50,75,100],angle=22.5,
                            tickfont=dict(color="#384653",size=12),gridcolor="#d2c6b8"),
        ),
        height=440,margin=dict(l=90,r=90,t=45,b=65),
        legend=dict(orientation="h",x=.5,xanchor="center",y=-.16),
    )
    return fig
