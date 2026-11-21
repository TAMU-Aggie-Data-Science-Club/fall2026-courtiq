"""Interpretable season-transition model; partial future outcomes never train it."""
import json
import numpy as np
import pandas as pd
from src.features.breakout import FEATURES,season_features,training_transitions
from src.models.common import APP,fit_task,save,metrics


def train(seasons):
    latest=json.loads((APP/"manifest.json").read_text())["latest_completed_start"]
    f=training_transitions(seasons,latest)
    f["base_season_start"]=f.season_start
    f["season_start"]+=1  # Evaluation groups by outcome season, not feature season.
    task=fit_task(f,FEATURES,"label",True,weights=True)
    task["training_cutoff"]=f"{latest-3}-07-01"
    cohorts=[]
    for season,g in f.groupby("season_start"):
        cohorts.append(dict(outcome_season=int(season),candidates=len(g),base_rate=float(g.label.mean())))
    test_ids=task["predictions"].query("period == 'test'").player_id
    test=f[f.season_start.eq(latest)&f.player_id.isin(test_ids)].copy()
    predictions=task["predictions"].query("period == 'test'")
    top=predictions.nlargest(15,"prediction")
    summary=dict(precision_at_15=float(top.actual.mean()),base_rate=float(test.label.mean()),
                 baseline=metrics(test.label,test.baseline_flag,True),cohorts=cohorts)
    live=season_features(seasons)
    live=live[(live.season_start==latest)&live.games.ge(20)&live.mpg.ge(15)&live.pra_pctl.lt(80)].copy()
    live["probability"]=task["model"].predict_proba(live[FEATURES])[:,1]
    # Linear coefficients explain signed contributions; trees use descriptive fields only.
    reasons=[]
    if task["selected"]=="linear":
        transformed=task["model"][:-1].transform(live[FEATURES])
        effects=transformed*task["model"][-1].coef_[0]
        for values in effects:
            idx=np.argsort(values)[-3:][::-1]
            reasons.append("; ".join(f"{FEATURES[i]}: signed log-odds contribution {values[i]:+.2f}" for i in idx))
    else:
        reference=f[f.season_start<=latest-3][FEATURES].median()
        effects=[]
        for feature in FEATURES:
            changed=live[FEATURES].copy()
            changed[feature]=reference[feature]
            effects.append(live.probability.to_numpy()-task["model"].predict_proba(changed)[:,1])
        effects=np.array(effects).T
        for values in effects:
            idx=np.argsort(np.abs(values))[-3:][::-1]
            reasons.append("; ".join(f"{FEATURES[i]}: model sensitivity {values[i]:+.3f} vs training median" for i in idx))
    live["reasons"]=reasons
    live.sort_values("probability",ascending=False).to_csv(APP/"breakout_candidates.csv.gz",index=False)
    save("breakout",dict(task=task,summary=summary))
    return {"breakout":task}
