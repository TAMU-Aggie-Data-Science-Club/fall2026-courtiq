"""Player prediction: baseline versus regularized/tree regressors."""
import numpy as np
import pandas as pd
from src.models.common import fit_task,save,load,metrics

FEATURES=[f"pre_{m}_{w}" for m in ["points","rebounds","assists","minutes","pra"] for w in [5,10,20,"season"]]+["home","rest","opp_drtg","opp_pace"]


def inputs(players,teams):
    f=players[players.played].copy()
    opp=teams[["game_id","team_id","pre_drtg_10","pre_pace_10"]].rename(columns={"team_id":"opponent_id","pre_drtg_10":"opp_drtg","pre_pace_10":"opp_pace"})
    return f.merge(opp,on=["game_id","opponent_id"],validate="many_to_one")


def train(players,teams):
    f=inputs(players,teams)
    tasks={target:fit_task(f,FEATURES,target) for target in ["points","rebounds","assists"]}
    baseline=[]
    for target,task in tasks.items():
        prediction=task["predictions"].query("period == 'test'")
        test=f.merge(prediction[["game_id","player_id"]],on=["game_id","player_id"])
        training=f[f.date<=pd.Timestamp(task["training_cutoff"])]
        fallback=float(training[target].mean())
        task["fallback"]=fallback
        baseline_prediction=test[f"pre_{target}_10"].fillna(fallback)
        baseline.append(dict(target=target,n=len(test),fallback="training mean when no prior season games",**metrics(test[target],baseline_prediction)))
    save("player",dict(tasks=tasks,baseline=baseline))
    return tasks


def predict(players,teams,player_id,opponent_id,when,home,bundle=None):
    from src.models.team import snapshot
    if bundle is None: bundle=load("player")
    cutoff=max(pd.Timestamp(t["inference_available_after"]) for t in bundle["tasks"].values())
    if pd.Timestamp(when)<=cutoff: raise ValueError("Use saved backtests before the model training cutoff")
    history=players[(players.player_id==player_id)&players.played&(players.date<pd.Timestamp(when))].sort_values(["date","game_id"])
    if history.empty: raise ValueError("No earlier played games for this player")
    # Limit rolling features to the same season, matching training grouping.
    requested=pd.Timestamp(when)
    season_start=requested.year if requested.month>=7 else requested.year-1
    current=history[history.season_start.eq(season_start)]
    row={"home":int(home),"rest":max(0,(pd.Timestamp(when).normalize()-history.iloc[-1].date).days-1)}
    for metric in ["points","rebounds","assists","minutes","pra"]:
        for w in [5,10,20]: row[f"pre_{metric}_{w}"]=current.tail(w)[metric].mean()
        row[f"pre_{metric}_season"]=current[metric].mean()
    opp=snapshot(teams,opponent_id,when,{})
    row["opp_drtg"]=opp["pre_drtg_10"]; row["opp_pace"]=opp["pre_pace_10"]
    x=pd.DataFrame([row]); rows=[]
    for target,task in bundle["tasks"].items():
        estimate=max(0,float(task["model"].predict(x[task["features"]])[0]))
        residuals=task["residuals"]
        baseline=row[f"pre_{target}_10"]
        if pd.isna(baseline): baseline=task["fallback"]
        rows.append(dict(stat=target,prediction=estimate,baseline=baseline,
                         low=max(0,estimate+float(np.quantile(residuals,.1))),
                         high=max(0,estimate+float(np.quantile(residuals,.9)))))
    return pd.DataFrame(rows),bundle


def encounters(players,a,b,when):
    f=players[players.played&(players.date<pd.Timestamp(when))]
    left=f[f.player_id.eq(a)]; right=f[f.player_id.eq(b)]
    joint=left.merge(right[["game_id","team_id"]],on="game_id",suffixes=("","_other"))
    return joint[joint.team_id.ne(joint.team_id_other)]
