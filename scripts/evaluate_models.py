"""Report actual saved chronological evaluation; never silently retrain."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.pipeline import APP
from src.models.common import load,cover_distribution,metrics
import numpy as np
import pandas as pd


def market_comparison():
    bundle=load("team")
    task=bundle["tasks"]["margin"]
    preds=task["predictions"].query("period == 'test'")
    odds=pd.read_csv(APP/"odds_history.csv.gz")
    f=preds.merge(odds[["game_id","spread_home","implied_home","margin"]],on="game_id",validate="one_to_one")
    f=f[f.spread_home.notna()]
    adjusted=f.margin+f.spread_home
    distributions=[cover_distribution(r.prediction,task["residuals"],r.spread_home) for r in f.itertuples()]
    p=np.array([[d["home_cover"],d["away_cover"],d["push"]] for d in distributions])
    actual=np.column_stack([adjusted.gt(0),adjusted.lt(0),adjusted.eq(0)]).astype(float)
    nonpush=adjusted.ne(0)
    result=dict(n=len(f),line_timing="Unknown; retrospective evaluation only",pushes=int((~nonpush).sum()),
                cover_accuracy_excluding_pushes=float(np.mean((p[nonpush,0]>=p[nonpush,1])==adjusted[nonpush].gt(0))),
                three_class_brier=float(np.mean(np.sum((p-actual)**2,axis=1))),
                interval_80_coverage=task["calibration"]["prediction_interval_80_coverage"])
    # Historical moneylines are absent for some recent seasons; do not invent prices.
    winner=bundle["tasks"]["home_win"]["predictions"].query("period == 'test'")
    priced=winner.merge(odds[["game_id","implied_home"]],on="game_id").dropna(subset=["implied_home"])
    result["moneyline_games"]=len(priced)
    result["market_win_metrics"]=metrics(priced.actual,priced.implied_home,True) if len(priced) else "Unavailable: no matched two-sided moneyline quotes in test season"
    (APP/"market_evaluation.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result

if __name__=="__main__":
    path=APP/"evaluation.json"
    if not path.exists(): raise SystemExit("No evaluation saved. Run scripts/train_models.py first.")
    print(json.dumps(json.loads(path.read_text()),indent=2))
    print("Market comparison:",json.dumps(market_comparison(),indent=2))
