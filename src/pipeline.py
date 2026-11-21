"""One shared CSV pipeline. No fetching, UI or model training."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app_data"
RAW = ROOT / "data/raw"
PROCESSED = ROOT / "data/processed"
COUNTS = {"points": "points", "assists": "assists", "reboundsTotal": "rebounds",
          "reboundsOffensive": "oreb", "reboundsDefensive": "dreb", "steals": "steals",
          "blocks": "blocks", "turnovers": "turnovers", "foulsPersonal": "fouls",
          "fieldGoalsMade": "fgm", "fieldGoalsAttempted": "fga", "threePointersMade": "fg3m",
          "threePointersAttempted": "fg3a", "freeThrowsMade": "ftm", "freeThrowsAttempted": "fta"}
ADVANCED = {"usagePercentage": "usage", "assistPercentage": "ast_pct",
            "offensiveRating": "ortg", "defensiveRating": "drtg",
            "netRating": "netrtg", "playerImpactEstimate": "pie"}


def divide(a, b):
    """Missing or zero denominator is undefined, never infinite."""
    if isinstance(b, pd.Series):
        return a / b.replace(0, np.nan)
    return a / b if pd.notna(b) and b != 0 else np.nan


def season_fields(frame, start=2015):
    f = frame.copy()
    f["game_id"] = pd.to_numeric(f["gameId"], errors="raise").astype("int64")
    f["date"] = pd.to_datetime(f["gameDateTimeEst"], errors="raise").dt.normalize()
    # Date establishes the century, ID establishes the season start's final two digits.
    year = f.date.dt.year
    yy = (f.game_id // 100000) % 100
    f["season_start"] = (year // 100) * 100 + yy
    f.loc[f.season_start > year, "season_start"] -= 100
    f = f.loc[(f.game_id // 10000000 == 2) & (f.season_start >= start)].copy()
    f["season_start"] = f.season_start.astype(int)
    f["season"] = f.season_start.astype(str) + "-" + ((f.season_start + 1) % 100).astype(str).str.zfill(2)
    return f.sort_values(["date", "game_id"])


def read_filtered(name, columns=None, start=2015):
    """Filter in chunks; never read the large play-by-play file."""
    path = RAW / "kaggle" / name
    available = pd.read_csv(path, nrows=0).columns
    cols = None if columns is None else list(dict.fromkeys(columns + ["gameId", "gameDateTimeEst"]))
    if cols:
        cols = [c for c in cols if c in available]
    pieces = [season_fields(c, start) for c in pd.read_csv(path, usecols=cols, chunksize=150000, low_memory=False)]
    return pd.concat([p for p in pieces if not p.empty], ignore_index=True)


def shooting(f):
    f = f.copy()
    for name, numerator, denominator in [
        ("ts_pct", f.points, 2 * (f.fga + .44 * f.fta)),
        ("efg_pct", f.fgm + .5 * f.fg3m, f.fga),
        ("fg_pct", f.fgm, f.fga), ("fg3_pct", f.fg3m, f.fg3a),
        ("ft_pct", f.ftm, f.fta), ("fg2_pct", f.fgm-f.fg3m, f.fga-f.fg3a),
        ("ftr", f.fta, f.fga), ("ast_tov", f.assists, f.turnovers)]:
        f[name] = divide(numerator, denominator)
    f["pra"] = f.points + f.rebounds + f.assists
    return f


def game_score(f):
    return (f.points + .4*f.fgm - .7*f.fga - .4*(f.fta-f.ftm) + .7*f.oreb
            + .3*f.dreb + f.steals + .7*f.assists + .7*f.blocks - .4*f.fouls - f.turnovers)


def pregame(frame, entity, metrics, windows=(3, 5, 10, 20)):
    """Strictly earlier dates only. Reject ambiguous multiple entity games per day."""
    f = frame.sort_values([entity, "season_start", "date", "game_id"]).copy()
    if f.duplicated([entity, "date"]).any():
        raise ValueError(f"Multiple {entity} records on one date need timestamp-level handling")
    groups = f.groupby([entity, "season_start"], sort=False)
    for metric in metrics:
        for w in windows:
            f[f"pre_{metric}_{w}"] = groups[metric].transform(lambda s: s.shift(1).rolling(w, min_periods=1).mean())
        f[f"pre_{metric}_season"] = groups[metric].transform(lambda s: s.shift(1).expanding().mean())
    f["rest"] = f.groupby(entity).date.diff().dt.days.sub(1).clip(lower=0)
    f["back_to_back"] = f.rest.eq(0)
    return f.sort_values(["date", "game_id", entity])


def aggregate_seasons(players):
    played = players.loc[players.played].copy()
    keys = ["player_id", "team_id", "season_start", "season"]
    totals = ["minutes"] + list(COUNTS.values()) + ["plus_minus"]
    def aggregate(f, group):
        g = f.groupby(group, dropna=False)
        out = g[totals].sum(min_count=1)
        out["games"] = g.size()
        out["game_score"] = g.game_score.mean()
        out["starts"] = g.started.sum()
        out["player_name"] = g.player_name.first()
        return out.reset_index()
    team = aggregate(played, keys)
    combined = aggregate(played, ["player_id", "season_start", "season"])
    combined["team_id"] = 0  # Canonical combined record for ALL players, even one-team seasons.
    combined["team_name"] = "TOT"
    team["team_name"] = team.team_id.astype(str)
    out = pd.concat([team, combined], ignore_index=True)
    out["mpg"] = divide(out.minutes, out.games)
    out = shooting(out)
    for stat in ["points", "rebounds", "assists", "steals", "blocks", "pra"]:
        out[f"{stat}_pg"] = divide(out[stat], out.games)
        out[f"{stat}_per36"] = 36 * divide(out[stat], out.minutes)
    # Non-reconstructible advanced season metrics deliberately remain unavailable.
    for col in ADVANCED.values():
        out[col] = np.nan
    return out


def impact_table(players, teams):
    p = players.merge(teams[["game_id", "team_id", "margin", "duration", "win", "points", "opp_points", "possessions"]],
                      on=["game_id", "team_id"], suffixes=("", "_team"), validate="many_to_one")
    rows = []
    for (pid, tid, ss, season), g in p.groupby(["player_id", "team_id", "season_start", "season"]):
        on = g.loc[g.played & g.minutes.notna() & g.plus_minus.notna() & g.duration.notna()].copy()
        valid = on.minutes.le(on.duration + .05)
        on = on.loc[valid]
        mins = on.minutes.sum(min_count=1)
        off = (on.duration-on.minutes).clip(lower=0).sum(min_count=1)
        a = 48*divide(on.plus_minus.sum(min_count=1), mins)
        b = 48*divide((on.margin-on.plus_minus).sum(min_count=1), off)
        row = dict(player_id=pid, team_id=tid, season_start=ss, season=season,
                   player_name=g.player_name.iloc[0], games=int(g.played.sum()), minutes_on=mins,
                   minutes_off=off, on_per48=a, off_per48=b, on_off_diff=a-b,
                   plus_minus=on.plus_minus.sum(min_count=1), game_score=g.loc[g.played, "game_score"].mean(),
                   games_missed=int((~g.played).sum()), observed_rows=len(g), valid_on_games=len(on))
        for label, subset in [("with", g[g.played]), ("without", g[~g.played])]:
            row[f"{label}_win_pct"] = subset.win.mean()
            row[f"{label}_margin"] = subset.margin.mean()
            row[f"{label}_netrtg"] = 100*divide((subset.points_team-subset.opp_points).sum(min_count=1), subset.possessions.sum(min_count=1))
        row["reliability"] = reliability(mins, off)
        rows.append(row)
    return pd.DataFrame(rows)


def reliability(on, off):
    if pd.isna(on) or pd.isna(off) or on < 500 or off < 250:
        return "Low"
    return "High" if on >= 1500 and off >= 500 else "Medium"


def build(start=2015):
    APP.mkdir(exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    tcols = list(COUNTS) + ["teamId", "opponentTeamId", "teamCity", "teamName", "home", "win", "teamScore", "opponentScore", "numMinutes"]
    t = read_filtered("TeamStatistics.csv", tcols, start).rename(columns={**COUNTS,
        "teamId":"team_id", "opponentTeamId":"opponent_id", "teamScore":"points",
        "opponentScore":"opp_points", "numMinutes":"team_minutes"})
    # Team source has teamScore instead of the player 'points' field.
    t["team_name"] = t.teamCity.fillna("") + " " + t.teamName.fillna("")
    t["margin"] = t.points-t.opp_points
    t = t.loc[t.points.notna() & t.opp_points.notna() & t.points.ne(t.opp_points)].copy()
    if t.duplicated(["game_id", "team_id"]).any():
        raise ValueError("Duplicate team-game keys")
    pcols = list(COUNTS) + ["personId", "playerteamId", "opponentteamId", "firstName", "lastName", "numMinutes", "home", "startingPosition", "plusMinusPoints"]
    p = read_filtered("PlayerStatistics.csv", pcols, start).rename(columns={**COUNTS,
        "personId":"player_id", "playerteamId":"team_id", "opponentteamId":"opponent_id",
        "numMinutes":"minutes", "plusMinusPoints":"plus_minus"})
    p["minutes"] = pd.to_numeric(p.minutes, errors="coerce")
    p["played"] = p.minutes.gt(0)
    p["started"] = p.startingPosition.fillna("").ne("") & p.played
    p["player_name"] = p.firstName.fillna("") + " " + p.lastName.fillna("")
    if p.duplicated(["game_id", "player_id"]).any():
        raise ValueError("Duplicate player-game keys")
    p = p.loc[p.game_id.isin(t.game_id)].copy()
    identity=t[["game_id","home","team_id","opponent_id"]].rename(columns={"team_id":"resolved_team","opponent_id":"resolved_opponent"})
    p=p.merge(identity,on=["game_id","home"],validate="many_to_one")
    if (p.team_id.notna() & p.team_id.ne(p.resolved_team)).any():
        raise ValueError("Player team ID conflicts with game home/away identity")
    p["team_id"]=p.team_id.fillna(p.resolved_team).astype("int64")
    p["opponent_id"]=p.opponent_id.fillna(p.resolved_opponent).astype("int64")
    durations = p.groupby(["game_id", "team_id"]).minutes.sum(min_count=1).div(5)
    t = t.join(durations.rename("fallback_duration"), on=["game_id", "team_id"])
    source_duration = pd.to_numeric(t.team_minutes, errors="coerce") / 5
    nearest = 48 + np.maximum(0, np.round((source_duration-48)/5))*5
    fallback = 48 + np.maximum(0, np.round((t.fallback_duration-48)/5))*5
    t["duration"] = source_duration.where((source_duration-nearest).abs() <= .2)
    t["duration"] = t.duration.fillna(fallback.where((t.fallback_duration-fallback).abs() <= .2))
    t["duration"] = t.duration.where(t.duration >= 48)
    t = shooting(t)
    est = t.fga+.44*t.fta-t.oreb+t.turnovers
    opponent = pd.DataFrame({"game_id":t.game_id, "team_id":t.opponent_id, "opp_est":est})
    t = t.merge(opponent, on=["game_id", "team_id"], validate="one_to_one")
    t["possessions"] = (t.fga+.44*t.fta-t.oreb+t.turnovers+t.opp_est)/2
    t["ortg"] = 100*divide(t.points,t.possessions)
    t["drtg"] = 100*divide(t.opp_points,t.possessions)
    t["netrtg"] = t.ortg-t.drtg
    t["pace"] = 48*divide(t.possessions,t.duration)
    other = t[["game_id","team_id","rebounds","oreb","dreb"]].rename(columns={"team_id":"opponent_id","rebounds":"opp_rebounds","oreb":"opp_oreb","dreb":"opp_dreb"})
    t = t.merge(other,on=["game_id","opponent_id"],validate="one_to_one")
    t["reb_pct"] = divide(t.rebounds,t.rebounds+t.opp_rebounds)
    t["orb_pct"] = divide(t.oreb,t.oreb+t.opp_dreb)
    t["drb_pct"] = divide(t.dreb,t.dreb+t.opp_oreb)
    t["tov_pct"] = divide(t.turnovers,t.fga+.44*t.fta+t.turnovers)
    t = pregame(t,"team_id",["points","opp_points","margin","win","ortg","drtg","netrtg","pace","reb_pct","efg_pct","tov_pct"])
    p = shooting(p)
    p["game_score"] = game_score(p)
    p["game_index"] = p.groupby("player_id").cumcount()+1
    played = pregame(p[p.played],"player_id",["points","rebounds","assists","minutes","pra"])
    precols = [c for c in played if c.startswith("pre_")] + ["rest","back_to_back"]
    p = p.merge(played[["game_id","player_id"]+precols],on=["game_id","player_id"],validate="one_to_one")
    seasons = aggregate_seasons(p)
    bio = pd.read_csv(RAW/"kaggle/Players.csv", usecols=["personId","birthDate","fromYear","draftNumber"]).rename(columns={"personId":"player_id"})
    seasons = seasons.merge(bio,on="player_id",validate="many_to_one")
    birth = pd.to_datetime(seasons.birthDate,errors="coerce")
    season_date = pd.to_datetime(seasons.season_start.astype(str)+"-10-01")
    seasons["age"] = (season_date-birth).dt.days/365.2425
    seasons["experience"] = seasons.season_start-pd.to_numeric(seasons.fromYear,errors="coerce")
    impacts = impact_table(p,t)
    combined = seasons[seasons.team_id==0].copy()
    latest = int(t.season_start.max())-1
    top = combined[(combined.season_start==latest)&(combined.games>=40)].nlargest(50,"pra_pg").copy()
    top["rank"] = np.arange(1,len(top)+1)
    seasons["is_top50"] = seasons.player_id.isin(top.player_id)
    games = t[t.home.eq(1)][["game_id","date","season","season_start","team_id","opponent_id","points","opp_points","margin","win","duration"]].rename(columns={"team_id":"home_team_id","opponent_id":"away_team_id","points":"home_points","opp_points":"away_points","win":"home_win"})
    games["total"] = games.home_points+games.away_points
    games["overtime"] = (games.duration-48)/5
    teams = t.sort_values("date").drop_duplicates("team_id",keep="last")[["team_id","team_name"]]
    history = pd.read_csv(RAW/"kaggle/TeamHistories.csv")
    history = history.sort_values("seasonActiveTill").drop_duplicates("teamId",keep="last")
    teams = teams.merge(history[["teamId","teamAbbrev"]],left_on="team_id",right_on="teamId",how="left").drop(columns="teamId")
    teams["team_code"] = teams.teamAbbrev.str.strip()
    odds = match_odds(games,teams)
    vst = p[p.played].groupby(["player_id","opponent_id","season"]).agg(games=("game_id","size"),points_pg=("points","mean"),rebounds_pg=("rebounds","mean"),assists_pg=("assists","mean")).reset_index()
    tables = dict(games=games,team_games=t,player_games=p,player_season=seasons,on_off=impacts,
                  top50_players=top,teams=teams,player_vs_team=vst,odds_history=odds)
    manifest = {"built_at":datetime.now(timezone.utc).isoformat(), "start_season":start,
                "source_urls":["https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores", "https://www.kaggle.com/datasets/cviaxmiwnptr/nba-betting-data-october-2007-to-june-2024"],
                "unresolved_duration_games":games.loc[games.duration.isna(),"game_id"].tolist(),
                "latest_completed_start":latest, "source":"Kaggle NBA box scores and historical betting CSV",
                "license_verification":"Supplied specification reports CC0; downloaded files include no license/version metadata. Public redistribution requires verification.",
                "advanced_metrics":"TS/eFG reconstructed from totals. USG/AST%/ORTG/DRTG/NRTG/PIE season values unavailable: no authoritative aggregation supplied.",
                "sources":[]}
    for path in sorted((RAW/"kaggle").glob("*.csv")) + sorted((RAW/"kaggle_odds").glob("*.csv")):
        manifest["sources"].append(dict(file=path.name,bytes=path.stat().st_size,sha256=hashlib.file_digest(path.open("rb"),"sha256").hexdigest()))
    manifest["season_game_counts"] = {str(k):int(v) for k,v in games.groupby("season").size().items()}
    for name, table in tables.items():
        table.to_csv(PROCESSED/f"{name}.csv.gz",index=False)
        deploy = table
        if "season_start" in table and name not in ("player_season","on_off","top50_players"):
            deploy = table[table.season_start>=2023]
        # Runtime game tables omit raw source fields and retain selected analytical inputs.
        if name=="player_games":
            cols=["game_id","player_id","team_id","opponent_id","date","season","season_start","player_name","minutes","played","home","points","rebounds","assists","fg3m","steals","blocks","turnovers","plus_minus","pra","game_score"]+precols
            deploy=deploy[cols]
        if name=="team_games":
            cols=["game_id","team_id","opponent_id","date","season","season_start","team_name","home","points","opp_points","margin","win","duration","possessions","ortg","drtg","netrtg","pace","rest","reb_pct","efg_pct","tov_pct"]+[c for c in t if c.startswith("pre_")]
            deploy=deploy[cols]
        deploy.to_csv(APP/f"{name}.csv.gz",index=False)
        manifest.setdefault("tables",{})[name] = {"rows":len(table),"app_rows":len(deploy),"columns":{c:str(deploy[c].dtype) for c in deploy},"app_bytes":(APP/f"{name}.csv.gz").stat().st_size}
    manifest["pipeline_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    manifest["version"] = hashlib.sha256((json.dumps(manifest["sources"],sort_keys=True)+manifest["pipeline_sha256"]).encode()).hexdigest()[:12]
    (APP/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps({"games":len(games),"players":len(p),"seasons":len(seasons),"version":manifest["version"]}))
    return tables


def match_odds(games, teams):
    paths=list((RAW/"kaggle_odds").glob("*.csv"))
    if len(paths)!=1:
        raise ValueError("Expected one historical odds CSV")
    o=pd.read_csv(paths[0])
    aliases={r.team_code.lower():r.team_id for r in teams.itertuples()}
    for old,new in {"gs":"gsw","sa":"san","sas":"san","wsh":"was","no":"nop","ny":"nyk","bk":"bkn","brk":"bkn","pho":"phx","utah":"uta","was":"was"}.items():
        if new in aliases: aliases[old]=aliases[new]
    o["date"]=pd.to_datetime(o.date,errors="raise").dt.normalize()
    o["home_team_id"]=o.home.str.lower().map(aliases)
    o["away_team_id"]=o.away.str.lower().map(aliases)
    # Original spread is favorite magnitude; verify outcome/sign in validation.
    o["spread_home"]=pd.to_numeric(o.spread,errors="coerce").abs()*np.where(o.whos_favored.eq("home"),-1,1)
    cols=["date","home_team_id","away_team_id"]
    if o.duplicated(cols).any(): raise ValueError("Ambiguous historical odds joins")
    result=games.merge(o[cols+["spread_home","total","moneyline_home","moneyline_away"]],on=cols,how="left",suffixes=("","_line"),validate="one_to_one")
    for side in ["home","away"]:
        ml=result[f"moneyline_{side}"]
        result[f"implied_{side}"]=np.where(ml<0,(-ml)/(-ml+100),100/(ml+100))
    denom=result.implied_home+result.implied_away
    for side in ["home","away"]: result[f"implied_{side}"]=divide(result[f"implied_{side}"],denom)
    adj=result.margin+result.spread_home
    result["home_covered"]=adj.gt(0).astype(float).where(adj.notna() & adj.ne(0))
    result["push"]=adj.eq(0).where(adj.notna())
    result["went_over"]=(result.total>result.total_line).astype(float).where(result.total_line.notna())
    result["line_timing"]="Unknown; retrospective benchmark only"
    return result
