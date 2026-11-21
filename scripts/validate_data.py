"""Standalone real-data validator. Failures exit 1; source exceptions are reported."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from src.pipeline import APP,PROCESSED


def validate():
    lines=[]; failures=[]
    def check(name,ok,detail):
        text=f"{'PASS' if ok else 'FAIL'} {name}: {detail}"
        lines.append(text); print(text)
        if not ok: failures.append(name)
    manifest=json.loads((APP/"manifest.json").read_text())
    tables={name:pd.read_csv(PROCESSED/f"{name}.csv.gz",low_memory=False) for name in manifest["tables"]}
    keys={"games":["game_id"],"team_games":["game_id","team_id"],"player_games":["game_id","player_id"],
          "player_season":["player_id","team_id","season"],"on_off":["player_id","team_id","season"],
          "top50_players":["player_id"],"teams":["team_id"],"player_vs_team":["player_id","opponent_id","season"],"odds_history":["game_id"]}
    for name,f in tables.items():
        check(name+" keys",not f[keys[name]].isna().any().any() and not f.duplicated(keys[name]).any(),f"{len(f)} rows")
        app=pd.read_csv(APP/f"{name}.csv.gz")
        check(name+" app schema",app.columns.tolist()==list(manifest["tables"][name]["columns"]),f"{len(app)} deployed rows")
    g=tables["games"]; t=tables["team_games"]; p=tables["player_games"]
    groups=t.groupby("game_id")
    check("two team rows",groups.size().eq(2).all(),groups.size().value_counts().to_dict())
    check("one home and winner",groups.home.sum().eq(1).all() and groups.win.sum().eq(1).all(),len(groups))
    check("foreign games",t.game_id.isin(g.game_id).all() and p.game_id.isin(g.game_id).all(),len(g))
    sums=p.groupby(["game_id","team_id"]).points.sum(min_count=1)
    compare=t.set_index(["game_id","team_id"]).points-sums
    mismatch=compare.abs().gt(.01) | compare.isna()
    # Preserve evidence of source discrepancies without repairing scores or hiding rows.
    compare[mismatch].to_csv(PROCESSED/"score_mismatches.csv")
    lines.append(f"SOURCE EXCEPTION player/team score mismatches: {int(mismatch.sum())}; see score_mismatches.csv")
    known_missing={22600088,22600124,22600142,22600144}
    unknown=set(g.loc[g.duration.isna(),"game_id"])-known_missing
    check("valid known game duration",not unknown and ((g.duration.dropna()-48)%5).abs().lt(.01).all(),f"unresolved source games={g.loc[g.duration.isna(),'game_id'].tolist()}; never imputed")
    duration=p.merge(t[["game_id","team_id","duration"]],on=["game_id","team_id"],validate="many_to_one")
    check("player minutes",not ((duration.minutes<0)|(duration.minutes>duration.duration+.05)).any(),"compared to actual game duration")
    check("Top 50",len(tables["top50_players"])==50 and tables["top50_players"].player_id.isin(tables["player_season"].player_id).all(),len(tables["top50_players"]))
    first=t.sort_values(["date","game_id"]).groupby(["team_id","season_start"]).head(1)
    check("first-game rolling",first.pre_points_10.isna().all(),f"{len(first)} team-seasons")
    o=tables["odds_history"]
    matched=o.spread_home.notna()
    corr=o.loc[matched,"spread_home"].corr(o.loc[matched,"margin"])
    check("odds sign",pd.notna(corr) and corr<-.2,f"spread vs margin correlation={corr:.3f}")
    sums=o.implied_home+o.implied_away
    check("no-vig probabilities",np.allclose(sums.dropna(),1),f"{sums.notna().sum()} matched prices")
    sizes=[x.stat().st_size for x in APP.glob("*") if x.is_file()]
    check("app sizes",sum(sizes)<100_000_000 and max(sizes)<50_000_000,f"total={sum(sizes):,}; largest={max(sizes):,}")
    lines.append("Season counts: "+json.dumps(manifest["season_game_counts"]))
    lines.append("Known reported missing IDs present: "+str(g.game_id.isin([22400532,22400537,22400538,22400617]).sum()))
    lines.append("Odds match rate by season: "+o.assign(matched=matched).groupby("season").matched.mean().to_json())
    lines.append("Null counts: "+json.dumps({n:f.isna().sum().to_dict() for n,f in tables.items()},default=int))
    (PROCESSED/"validation_report.md").write_text("\n\n".join(lines),encoding="utf-8")
    print(f"SUMMARY: {len(failures)} failed checks; source score discrepancies explicitly reported")
    return not failures

if __name__=="__main__": sys.exit(0 if validate() else 1)
