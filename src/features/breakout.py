"""Completed-season breakout labels with strictly prior-season predictors."""
import numpy as np
from src.features.scouting import canonical

FEATURES=["age","experience","mpg","games","points_per36","rebounds_per36",
          "assists_per36","ts_pct","efg_pct","mpg_change","pra_change","pra_pctl"]


def season_features(frame):
    f=canonical(frame).sort_values(["player_id","season_start"]).copy()
    eligible=f.games.ge(20)&f.mpg.ge(15)
    f["pra_pctl"]=f.pra_per36.where(eligible).groupby(f.season).rank(method="average",pct=True)*100
    for source,target in [("mpg","mpg_change"),("pra_per36","pra_change")]:
        prev=f.groupby("player_id")[source].shift(1)
        contiguous=f.season_start.sub(f.groupby("player_id").season_start.shift(1)).eq(1)
        f[target]=(f[source]-prev).where(contiguous)
    f["baseline_flag"]=(f.age.le(24)&f.mpg_change.ge(3)&f.pra_pctl.ge(50)).astype(int)
    return f


def target(next_mpg, delta_mpg, delta_pctl):
    return (next_mpg>=20)&(delta_mpg>=5)&(delta_pctl>=15)


def training_transitions(frame, latest_completed):
    f=season_features(frame)
    next_rows=f[["player_id","season_start","mpg","games","pra_pctl"]].copy()
    next_rows["season_start"]-=1
    next_rows=next_rows.rename(columns={"mpg":"next_mpg","games":"next_games","pra_pctl":"next_pctl"})
    merged=f.merge(next_rows,on=["player_id","season_start"],how="inner",validate="one_to_one")
    merged=merged[(merged.season_start<latest_completed)&merged.games.ge(20)&merged.mpg.ge(15)
                  &merged.pra_pctl.lt(80)&merged.next_games.ge(20)&merged.next_pctl.notna()].copy()
    merged["label"]=target(merged.next_mpg,merged.next_mpg-merged.mpg,merged.next_pctl-merged.pra_pctl).astype(int)
    return merged
