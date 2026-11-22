"""Presentation UI consuming only compact app-ready files and trusted models."""
from datetime import timedelta
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
