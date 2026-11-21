"""Team model features shared between historical training and manual inference."""
import numpy as np
import pandas as pd
from src.models.common import fit_task, save, load, cover_distribution, metrics

BASE=["netrtg","ortg","drtg","pace","reb_pct","efg_pct","tov_pct","margin","win"]


def add_elo(teams):
    f=teams.sort_values(["date","game_id"]).copy()
    f["pre_elo"]=np.nan
    ratings={}; previous=None
    for gid,g in f.groupby("game_id",sort=False):
        season=int(g.season_start.iloc[0])
        if previous is not None and season!=previous:
            ratings={k:1500+.75*(v-1500) for k,v in ratings.items()}
        previous=season
        home=g[g.home.eq(1)]; away=g[g.home.eq(0)]
        if len(home)!=1 or len(away)!=1: raise ValueError("Expected home/away team pair")
        h=home.iloc[0]; a=away.iloc[0]
        rh=ratings.get(h.team_id,1500); ra=ratings.get(a.team_id,1500)
        f.loc[home.index,"pre_elo"]=rh; f.loc[away.index,"pre_elo"]=ra
        prob=1/(1+10**((ra-rh-65)/400))
        delta=20*(h.win-prob)
        ratings[h.team_id]=rh+delta; ratings[a.team_id]=ra-delta
    return f,ratings


def differences(home,away):
    out={}
    for stat in BASE:
        for window in [5,10,20,"season"]:
            key=f"pre_{stat}_{window}"
            out[f"diff_{stat}_{window}"]=home.get(key,np.nan)-away.get(key,np.nan)
            # Combined scoring environment is essential for total-points predictions.
            out[f"sum_{stat}_{window}"]=home.get(key,np.nan)+away.get(key,np.nan)
    out["diff_rest"]=home.get("rest",np.nan)-away.get("rest",np.nan)
    out["diff_elo"]=home.get("pre_elo",1500)-away.get("pre_elo",1500)+65
    return out


def matchups(teams):
    f,ratings=add_elo(teams)
    rows=[]
    for _,g in f.groupby("game_id",sort=False):
        h=g[g.home.eq(1)].iloc[0]; a=g[g.home.eq(0)].iloc[0]
        rows.append({**differences(h,a),"game_id":h.game_id,"date":h.date,"season":h.season,
                     "season_start":h.season_start,"home_win":h.win,"margin":h.margin,"total":h.points+h.opp_points})
    return pd.DataFrame(rows),ratings


def train(teams):
    f,ratings=matchups(teams)
    from src.pipeline import APP
    elo_frame,_=add_elo(teams)
    elo_frame[["game_id","team_id","pre_elo"]].to_csv(APP/"team_elo.csv.gz",index=False)
    from src.pipeline import PROCESSED
    f.to_csv(PROCESSED/"team_matchups_model.csv.gz",index=False)
    features=[c for c in f if c.startswith(("diff_","sum_"))]
    tasks={target:fit_task(f,features,target,target=="home_win") for target in ["home_win","margin","total"]}
    test=f[f.season_start.eq(f.season_start.max()-1)]
    # Baseline periods come from the model test predictions, never the partial current season.
    test=f[f.game_id.isin(tasks["margin"]["predictions"].query("period == 'test'").game_id)]
    train=f[f.date<=pd.to_datetime(tasks["home_win"]["training_cutoff"])]
    baseline=float(train.home_win.mean())
    benchmarks=[dict(model="home_rate",**metrics(test.home_win,np.repeat(baseline,len(test)),True)),
                dict(model="elo",**metrics(test.home_win,1/(1+10**(-test.diff_elo/400)),True))]
    save("team",dict(tasks=tasks,ratings=ratings,baseline=baseline,benchmarks=benchmarks))
    return tasks


def snapshot(teams,team_id,when,ratings):
    hist=teams[(teams.team_id==team_id)&(teams.date<pd.Timestamp(when))].sort_values(["date","game_id"])
    if hist.empty: raise ValueError("No earlier history for selected team")
    latest=hist.iloc[-1]
    requested=pd.Timestamp(when)
    season_start=requested.year if requested.month>=7 else requested.year-1
    current=hist[hist.season_start.eq(season_start)]
    row={"rest":max(0,(pd.Timestamp(when).normalize()-latest.date).days-1),"pre_elo":ratings.get(team_id,1500)}
    for stat in BASE:
        for w in [5,10,20]: row[f"pre_{stat}_{w}"]=current.tail(w)[stat].mean()
        row[f"pre_{stat}_season"]=current[stat].mean()
    return row


def predict(teams,home_id,away_id,when,spread=None):
    if home_id==away_id: raise ValueError("Choose different teams")
    bundle=load("team")
    cutoff=max(pd.Timestamp(task["inference_available_after"]) for task in bundle["tasks"].values())
    if pd.Timestamp(when)<=cutoff: raise ValueError("Use saved backtests for dates before the model training cutoff")
    # Ship full-history pregame anchors so truncated app exports don't reset Elo.
    from src.pipeline import APP
    anchors=pd.read_csv(APP/"team_elo.csv.gz")
    history=teams[teams.date<pd.Timestamp(when)].merge(anchors,on=["game_id","team_id"],validate="one_to_one")
    opponent=history[["game_id","team_id","pre_elo"]].rename(columns={"team_id":"opponent_id","pre_elo":"opp_elo"})
    history=history.merge(opponent,on=["game_id","opponent_id"],validate="one_to_one")
    probability=1/(1+10**((history.opp_elo-history.pre_elo-np.where(history.home.eq(1),65,-65))/400))
    history["post_elo"]=history.pre_elo+20*(history.win-probability)
    ratings=history.sort_values(["date","game_id"]).drop_duplicates("team_id",keep="last").set_index("team_id").post_elo.to_dict()
    x=pd.DataFrame([differences(snapshot(teams,home_id,when,ratings),snapshot(teams,away_id,when,ratings))])
    result={}
    for name,task in bundle["tasks"].items():
        model=task["model"]
        result[name]=float(model.predict_proba(x[task["features"]])[0,1] if name=="home_win" else model.predict(x[task["features"]])[0])
    result["away_win"]=1-result["home_win"]
    result["home_score"]=(result["total"]+result["margin"])/2
    result["away_score"]=(result["total"]-result["margin"])/2
    if min(result["home_score"],result["away_score"])<0: raise ValueError("Model produced invalid expected score")
    result["distribution"]=cover_distribution(result["margin"],bundle["tasks"]["margin"]["residuals"],spread if spread is not None else 0)
    result["cutoff"]=str(cutoff.date()); result["version"]=bundle["dataset_version"]
    result["disagreement"]=(result["home_win"]>=.5)!=(result["margin"]>=0)
    return result
