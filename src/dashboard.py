"""Presentation UI consuming only compact app-ready files and trusted models."""
from datetime import timedelta
import json
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from src.pipeline import APP
from src.features import scouting,impact
from src.models import team,player
from src.models.common import load

SOURCE_NBA="https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores"
SOURCE_ODDS="https://www.kaggle.com/datasets/cviaxmiwnptr/nba-betting-data-october-2007-to-june-2024"


@st.cache_data
def table(name,version):
    path=APP/f"{name}.csv.gz"
    frame=pd.read_csv(path,low_memory=False)
    if "date" in frame: frame["date"]=pd.to_datetime(frame.date)
    return frame


def choose(frame,key,label="Player"):
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


def scouting_page(seasons,version):
    st.header("Player Scouting Lab")
    st.caption("Production, efficiency & league context in one place.")
    available=sorted(seasons.loc[seasons.season_start>=2023,"season"].unique(),reverse=True)
    season=st.selectbox("Season",available,index=min(1,len(available)-1),key="scout_season")
    f=scouting.canonical(seasons)
    f=f[f.season.eq(season)]
    pid=choose(f,"scout_player")
    if pid is None: st.info("No player seasons available."); return
    lens=st.selectbox("Scouting lens",["All-Around","Shooting"])
    row=f[f.player_id.eq(pid)].iloc[0]
    st.subheader(row.player_name)
    for col,label,value in zip(st.columns(4),["Games","Minutes / game","Points / game","Assists / game"],[row.games,row.mpg,row.points_pg,row.assists_pg]):
        col.metric(label,f"{value:.1f}" if pd.notna(value) else "N/A")
    ranks=scouting.rankings(seasons,season,lens)
    b=ranks[ranks.player_id.eq(pid)]
    if not b.qualified.all(): st.info("Some axes are not qualified. N/A axes are not replaced with zero or a league-average value.")
    st.plotly_chart(scouting.radar(b),use_container_width=True)
    st.dataframe(b[["label","value","percentile","rank","population","qualified"]],hide_index=True,width="stretch")
    badges,text=scouting.report(scouting.rankings(seasons,season).query("player_id == @pid"))
    st.write(" · ".join(badges) if badges else "No qualifying badges")
    st.write(text)
    st.caption("Badges and summary use the All-Around lens consistently, even when the shooting chart is selected.")
    st.subheader("Advanced Player Statistics")
    advanced=pd.DataFrame([dict(metric=k,value=row.get(k,np.nan),meaning=label) for k,label in scouting.ADVANCED.items()])
    st.dataframe(advanced,hide_index=True,width="stretch")
    st.caption("Percentages are fractions (0.60 = 60%). TS/eFG are calculated from season totals. Other season advanced values show N/A until a reliable aggregation is validated.")


def impact_page(impacts,teams):
    st.header("On/Off Impact")
    available=sorted(impacts.loc[impacts.season_start>=2023,"season"].unique(),reverse=True)
    season=st.selectbox("Season",available,index=min(1,len(available)-1),key="impact_season")
    f=impacts[impacts.season.eq(season)].copy()
    pid=choose(f,"impact_player")
    if pid is None: st.info("No impact data."); return
    lookup=teams.set_index("team_id").team_name.to_dict()
    player_rows=f[f.player_id.eq(pid)]
    tid=st.selectbox("Team stint",player_rows.team_id.tolist(),format_func=lambda x:lookup.get(x,str(x)),key="impact_team")
    row=player_rows[player_rows.team_id.eq(tid)].iloc[0]
    st.subheader(row.player_name)
    st.caption(f"Reliability: {row.reliability}; {row.minutes_on:.0f} on minutes / {row.minutes_off:.0f} off minutes")
    for col,field,label in zip(st.columns(4),["on_off_diff","on_per48","off_per48","game_score"],["On/off difference","On per 48","Off per 48","Mean Game Score"]):
        value=row[field]; col.metric(label,f"{value:+.2f}" if pd.notna(value) else "N/A")
    st.info(impact.missed_message(row))
    st.dataframe(pd.DataFrame([{"group":label,"win_pct":row[f"{label}_win_pct"],"net_rating":row[f"{label}_netrtg"],"margin":row[f"{label}_margin"]} for label in ["with","without"]]),hide_index=True)
    minimum=st.slider("Leaderboard minimum on-court minutes",0,2500,500,100)
    qualified=f[f.games.ge(20)&f.minutes_on.ge(minimum)]
    st.plotly_chart(impact.scatter(qualified,pid),use_container_width=True)
    st.dataframe(qualified.sort_values("on_off_diff",ascending=False)[["player_name","team_id","minutes_on","minutes_off","on_off_diff","with_win_pct","without_win_pct","reliability"]],hide_index=True,width="stretch")


def performance(prefix):
    path=APP/"evaluation.json"
    if not path.exists(): return
    with st.expander("Actual model performance & backtests"):
        summaries=json.loads(path.read_text())
        rows=[]
        for name,task in summaries.items():
            if name.startswith(prefix):
                for result in task["results"]: rows.append(dict(task=name,**result))
        st.dataframe(pd.DataFrame(rows),hide_index=True,width="stretch")
        for name,task in summaries.items():
            if name.startswith(prefix):
                st.write(name, "Calibration / interval check",task.get("calibration","Pending regeneration"))
        baseline_path=APP/"baselines.json"
        if baseline_path.exists():
            st.write("Baseline comparison",json.loads(baseline_path.read_text()).get(prefix))
        if prefix=="team" and (APP/"market_evaluation.json").exists():
            st.write("Retrospective market comparison",json.loads((APP/"market_evaluation.json").read_text()))
        st.caption("Model selection uses validation only. Calibration-period errors estimate intervals; final test outcomes never select the model. See model cards for exact periods and baseline comparisons.")


def team_page(t,teams,version):
    st.header("Team Matchup Predictor")
    lookup=teams.set_index("team_id").team_name.to_dict(); ids=list(lookup)
    c1,c2=st.columns(2)
    h=c1.selectbox("Home team",ids,format_func=lookup.get)
    a=c2.selectbox("Away team",[x for x in ids if x!=h],format_func=lookup.get)
    when=st.date_input("Game date",value=(t.date.max()+timedelta(days=1)).date(),key="team_date")
    use_spread=st.checkbox("Include a signed home spread")
    spread=st.number_input("Home spread (negative means home favorite)",value=-4.5,step=.5) if use_spread else None
    odds=APP/"odds_today.csv"
    if odds.exists():
        with st.expander("Cached upcoming market lines"):
            st.dataframe(pd.read_csv(odds),hide_index=True)
            st.caption("Snapshot only. Check retrieval time; manual selections are not automatically matched to a quote.")
    else: st.caption("Manual mode. No live odds cache is loaded; no API request is made.")
    if st.button("Predict team matchup"):
        try:
            r=team.predict(t,h,a,when,spread)
            st.session_state["team_prediction"]=(h,a,str(when),spread,r)
        except (ValueError,FileNotFoundError) as exc: st.warning(str(exc))
    saved=st.session_state.get("team_prediction")
    if saved and saved[:4]==(h,a,str(when),spread):
        r=saved[4]
        st.subheader(f"{lookup[h]} {r['home_score']:.1f} : {r['away_score']:.1f} {lookup[a]}")
        for col,label,value in zip(st.columns(4),["Home win","Away win","Home margin","Total points"],[f"{r['home_win']:.1%}",f"{r['away_win']:.1%}",f"{r['margin']:+.1f}",f"{r['total']:.1f}"]): col.metric(label,value)
        dist=r["distribution"]
        st.write(f"Approximate 80% margin prediction interval: {dist['low']:.0f} to {dist['high']:.0f}")
        if spread is not None: st.write({k:dist[k] for k in ["home_cover","away_cover","push"]})
        if r["disagreement"]: st.warning("Winner classifier and margin regressor disagree. These are separate estimates.")
        st.caption(f"Model available after validation/calibration through {r['cutoff']}; data version {r['version']}. Historical cutoff enforced.")
    window=st.selectbox("Comparison window",[5,10,20])
    history=t[t.date<pd.Timestamp(when)]
    recent=history[history.team_id.isin([h,a])].sort_values("date").groupby("team_id").tail(window)
    st.subheader("Recent team context")
    st.dataframe(recent.groupby("team_name")[["ortg","drtg","netrtg","reb_pct","efg_pct","tov_pct","pace","win"]].mean(),width="stretch")
    st.caption("Recent game means are descriptive. Model inputs are separately cutoff-safe. Lower DRTG/TOV% is generally preferable.")
    st.plotly_chart(px.line(recent,x="date",y="margin",color="team_name",labels={"margin":"Actual point margin"}),use_container_width=True)
    performance("team")


def player_page(p,t,teams):
    st.header("Player Matchup Lab")
    st.caption("Opposing-player encounters, not verified guarding assignments. Predictions are player versus team.")
    lookup=teams.set_index("team_id").team_name.to_dict(); ids=list(lookup)
    home=st.selectbox("Home team",ids,format_func=lookup.get,key="p_home")
    away=st.selectbox("Away team",[x for x in ids if x!=home],format_func=lookup.get,key="p_away")
    when=st.date_input("Game date",value=(p.date.max()+timedelta(days=1)).date(),key="p_date")
    prior=p[(p.date<pd.Timestamp(when))&p.played].sort_values(["date","game_id"])
    roster=prior.drop_duplicates("player_id",keep="last")
    st.caption(f"Player lists use each player's last recorded team before the chosen date, latest source game {prior.date.max().date() if not prior.empty else 'N/A'}. Not confirmed active rosters or injury status.")
    c1,c2=st.columns(2)
    with c1: a=choose(roster[roster.team_id.eq(home)],"p_a","Home player")
    with c2: b=choose(roster[roster.team_id.eq(away)],"p_b","Away player")
    if a is None or b is None: st.info("No supported historical roster for this date."); return
    if st.button("Compare players & predict"):
        try:
            left,bundle=player.predict(p,t,a,away,when,True)
            right,_=player.predict(p,t,b,home,when,False)
            left["player"]=roster.set_index("player_id").loc[a,"player_name"]
            right["player"]=roster.set_index("player_id").loc[b,"player_name"]
            result=pd.concat([left,right])
            st.dataframe(result,hide_index=True,width="stretch")
            st.plotly_chart(px.bar(result,x="stat",y="prediction",color="player",barmode="group"),use_container_width=True)
            st.caption("low/high are empirical approximate 80% prediction bounds from held-out errors, not guarantees. Baseline is previous 10 played games.")
            encounter=player.encounters(p,a,b,when)
            st.write(f"Recorded opposing-player encounters: {len(encounter)}")
            if len(encounter)<3: st.info("Sparse encounter history. Model uses broader player and opponent-team context, not an invented defender effect.")
            st.dataframe(encounter[["date","season","points","rebounds","assists","minutes"]],hide_index=True)
            versus=prior[prior.player_id.eq(a)&prior.opponent_id.eq(away)]
            st.write("Home player's recorded averages against this team:")
            st.dataframe(versus[["points","rebounds","assists"]].mean().to_frame("per game"))
        except (ValueError,FileNotFoundError) as exc: st.warning(str(exc))
    performance("player")


def breakout_page(seasons,version):
    st.header("Breakout Watch")
    path=APP/"breakout_candidates.csv.gz"
    if not path.exists(): st.info("Breakout model not prepared. Run the offline training command."); return
    f=table("breakout_candidates",version)
    st.caption("Preseason estimates from the latest completed season. Rookies excluded. Probabilities are model estimates, not guarantees.")
    st.dataframe(f.sort_values("probability",ascending=False)[["player_name","probability","age","mpg","pra_per36","pra_pctl","reasons"]].head(30),hide_index=True,width="stretch")
    pid=choose(f,"breakout_player")
    if pid is not None:
        hist=scouting.canonical(seasons)
        hist=hist[hist.player_id.eq(pid)].sort_values("season_start")
        st.plotly_chart(px.line(hist,x="season",y=["mpg","pra_per36"],markers=True),use_container_width=True)
        st.caption("Current-season observations are a separate tracker, not inputs retroactively added to the preseason forecast.")
        st.dataframe(hist[["season","games","mpg","pra_per36","points_pg"]].tail(3),hide_index=True)
    st.write("Breakout target: next-season MPG ≥20, MPG increase ≥5 & PRA-per-36 percentile increase ≥15. Candidates are below the 80th percentile in the base season. Missing future outcomes are excluded from retrospective labels, never treated as failures.")
    performance("breakout")
    back=APP/"backtest_breakout_breakout.csv.gz"
    if back.exists():
        st.subheader("Held-out candidate backtest")
        st.dataframe(table("backtest_breakout_breakout",version).query("period == 'test'").nlargest(15,"prediction"),hide_index=True)
