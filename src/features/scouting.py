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
ADVANCED = {"ts_pct":"True shooting, from totals", "efg_pct":"Effective FG%, from totals",
            "usage":"Usage: involvement, not quality", "ast_pct":"Share of teammate baskets assisted",
            "ortg":"Offensive rating, points/100 possessions", "drtg":"Defensive rating, lower generally better",
            "netrtg":"Net rating, same basis as offense/defense", "pie":"Player Impact Estimate, box-score context"}


LENSES = {"All-Around": ALL_AROUND, "Shooting": SHOOTING,
          "Rebounding & defense": {"rebounds_pg": "Rebounds / game", "rebounds_per36": "Rebounds / 36 minutes",
                                   "blocks_pg": "Blocks / game", "steals_pg": "Steals / game"},
          "Playmaking": {"assists_pg": "Assists / game", "assists_per36": "Assists / 36 minutes",
                         "ast_tov": "Assists per turnover", "points_pg": "Points / game"}}

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
    f["fg3a_pg"]=f.fg3a/f.games.replace(0,np.nan)
    metrics=LENSES[lens]
    base=f.games.ge(min_games)&f.mpg.ge(min_mpg)
    pieces=[]
    for metric,label in metrics.items():
        threshold=f.fg3a.ge(50) if metric=="fg3_pct" else f.fta.ge(50) if metric=="ft_pct" else True
        eligible=base&threshold&f[metric].notna()
        values=f[metric].where(eligible)
        higher_better=(directions or {}).get(metric,True)
        pieces.append(pd.DataFrame({"player_id":f.player_id,"season":season,"metric":metric,
            "label":label,"value":f[metric],"percentile":values.rank(method="average",pct=True,ascending=higher_better)*100,
            "rank":values.rank(method="average",ascending=not higher_better),"population":int(eligible.sum()),
            "qualified":eligible}))
    return pd.concat(pieces,ignore_index=True)


def report(breakdown):
    valid=breakdown.dropna(subset=["percentile"]).sort_values("percentile",ascending=False)
    if valid.empty: return [], "Not enough qualifying data for a scouting report."
    lookup=valid.set_index("metric").percentile
    badges=[]
    for metric,cut,label in [("points_pg",90,"Elite Scorer"),("fg3_pct",85,"Sharpshooter"),
        ("assists_pg",85,"Playmaker"),("rebounds_pg",90,"Rebounding Specialist")]:
        if lookup.get(metric,-1)>=cut: badges.append(label)
    if len(lookup[lookup.ge(75)])>=4: badges.append("All-Around Contributor")
    strongest=", ".join(valid.head(2).label)
    low=valid.iloc[-1]
    kind="Relative weakness" if low.percentile<=30 else "Lowest relative ranking"
    elite="Elite relative strength" if valid.iloc[0].percentile>=85 else "Strongest relative area"
    return badges[:3],f"{elite}: {strongest}. {kind}: {low.label}. Rankings describe this season's qualifying group, not overall player quality."


def radar(breakdown, color="#df7835"):
    import plotly.graph_objects as go
    b=breakdown.reset_index(drop=True)
    labels=b.label.tolist()
    values=b.percentile.tolist()
    complete=all(pd.notna(v) for v in values)
    fig=go.Figure()
    fig.add_trace(go.Scatterpolar(r=[50]*(len(labels)+1),theta=labels+[labels[0]],name="Median percentile reference (50)",line=dict(color="gray",dash="dot")))
    theta=labels+[labels[0]]
    r=values+[values[0]]
    custom=b[["value","rank","population"]].values.tolist()
    fig.add_trace(go.Scatterpolar(r=r,theta=theta,fill="toself" if complete else "none",
        connectgaps=False,mode="lines+markers",name="Selected player",customdata=custom+[custom[0]],
        line=dict(color=color),hovertemplate="%{theta}<br>Raw: %{customdata[0]:.3f}<br>Percentile: %{r:.1f}<br>Rank: %{customdata[1]} / %{customdata[2]}<extra></extra>"))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,100],tickvals=[25,50,75,100])),height=480,legend=dict(orientation="h"))
    return fig
