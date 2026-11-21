"""Train CPU-friendly models offline from the full processed CSVs."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from src.pipeline import PROCESSED,APP
from src.models import team,player,breakout

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile",choices=["core"],default="core")
    parser.add_argument("--feature",choices=["all","team","player","breakout"],default="all")
    args=parser.parse_args()
    tables={n:pd.read_csv(PROCESSED/f"{n}.csv.gz",parse_dates=["date"] if n!="player_season" else None,low_memory=False) for n in ["team_games","player_games","player_season"]}
    results={}
    for name,fn,params in [("team",team.train,[tables["team_games"]]),("player",player.train,[tables["player_games"],tables["team_games"]]),("breakout",breakout.train,[tables["player_season"]])]:
        if args.feature not in ("all",name): continue
        print("Training",name,flush=True)
        tasks=fn(*params)
        for target,task in tasks.items():
            results[f"{name}_{target}"]=dict(selected=task["selected"],training_cutoff=task["training_cutoff"],inference_available_after=task["inference_available_after"],split_counts=task["split_counts"],results=task["results"],calibration=task["calibration"])
            task["predictions"].to_csv(APP/f"backtest_{name}_{target}.csv.gz",index=False)
        print(json.dumps({k:v for k,v in results.items() if k.startswith(name)},indent=2),flush=True)
    previous=json.loads((APP/"evaluation.json").read_text()) if (APP/"evaluation.json").exists() else {}
    previous.update(results)
    (APP/"evaluation.json").write_text(json.dumps(previous,indent=2),encoding="utf-8")
    from src.models.common import load
    baselines={}
    for name in ["team","player","breakout"]:
        try:
            bundle=load(name)
        except (FileNotFoundError,ValueError): continue
        baselines[name]=bundle.get("benchmarks",bundle.get("baseline",bundle.get("summary")))
    (APP/"baselines.json").write_text(json.dumps(baselines,indent=2),encoding="utf-8")

if __name__=="__main__": main()
