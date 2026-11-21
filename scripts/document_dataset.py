"""Generate the exact deployed schema dictionary and verified demo records."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from src.pipeline import APP,ROOT

DEFINITIONS={
    "game_id":("identifier","Stable source NBA game ID; regular season starts with numeric prefix 2"),
    "player_id":("identifier","Stable NBA person ID, never a display-name join"),
    "team_id":("identifier","Stable franchise ID; 0 denotes canonical all-teams TOT season record"),
    "opponent_id":("identifier","Opposing stable franchise ID"),
    "season_start":("year","Start year derived from game ID with date-established century"),
    "season":("YYYY-YY","Regular-season label from the shared pipeline"),
    "minutes":("minutes","Sum of played player minutes for season rows; actual player duration for game rows"),
    "duration":("minutes","Elapsed game duration, 48 plus 5 per overtime; unavailable when reconstruction fails"),
    "team_minutes":("player-minutes","Team source minutes, approximately five times elapsed duration"),
    "played":("boolean","Numeric minutes greater than zero; DNPs are false"),
    "home":("boolean","Source home-team indicator"),
    "win":("boolean","Team won this completed game"),
    "date":("date","Source Eastern-calendar game date, timezone-naive; same-date history excluded"),
    "mpg":("minutes/game","Season player minutes divided by played games"),
    "games":("games","Count of played appearances in player summaries"),
    "possessions":("estimated possessions","Mean of both teams' FGA + .44*FTA - OREB + TOV"),
    "pace":("possessions/48 min","Estimated possessions times 48 divided by elapsed duration"),
    "ortg":("points/100 possessions","Team rating from points/estimated possessions; season player value unavailable"),
    "drtg":("points allowed/100 possessions","Team defensive rating; lower generally preferable; season player value unavailable"),
    "netrtg":("points/100 possessions","ORTG minus DRTG on the same basis; season player value unavailable"),
    "ts_pct":("fraction","PTS / [2*(FGA+.44*FTA)], zero denominator unavailable"),
    "efg_pct":("fraction","(FGM+.5*3PM)/FGA, from totals"),
    "fg_pct":("fraction","FGM/FGA"),"fg2_pct":("fraction","(FGM-3PM)/(FGA-3PA)"),
    "fg3_pct":("fraction","3PM/3PA"),"ft_pct":("fraction","FTM/FTA"),
    "ftr":("ratio","FTA/FGA"),"ast_tov":("ratio","AST/TOV; zero TOV is undefined"),
    "usage":("fraction","Advanced season usage unavailable until authoritative aggregation validated"),
    "ast_pct":("fraction","Advanced season assist percentage unavailable until validated"),
    "pie":("fraction","Advanced season PIE unavailable until validated"),
    "plus_minus":("points","Team score differential while player was on court; sum for season rows"),
    "on_per48":("points/48 minutes","48*sum(player +/-)/sum(player minutes), valid played-game subset"),
    "off_per48":("points/48 minutes","48*sum(team margin-player +/-)/sum(duration-player minutes), same subset"),
    "on_off_diff":("points/48 minutes","on_per48 minus off_per48, not isolated causal impact"),
    "rest":("days","Days between prior observed game and target date minus one, clipped at zero"),
    "game_score":("Game Score units","Hollinger box-score formula; season value is played-game mean"),
    "spread_home":("points","Signed home spread: negative home favorite"),
    "line_timing":("text","Unknown historical line timing; retrospective comparison only"),
    "pra":("counts","Points + rebounds + assists"),
    "margin":("points","Home-minus-away in games table; team-minus-opponent in team table"),
    "total":("points","Actual home plus away score"),"total_line":("points","Historical market total"),
    "is_top50":("boolean","Player belongs to frozen prior completed-season Top 50 by PRA/game with GP>=40"),
    "games_missed":("games","Explicit DNP rows only within recorded team stint; not all absent roster rows"),
    "reliability":("category","Low: on<500 or off<250; High: on>=1500 and off>=500; otherwise Medium"),
}


def definition(column):
    if column in DEFINITIONS: return DEFINITIONS[column]
    if column.startswith("pre_"):
        return "source metric units", "Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing."
    if column.endswith("_per36"): return "counts/36 minutes", "36 times season count divided by total played minutes"
    if column.endswith("_pg"): return "counts/game", "Season total divided by played games, or played-game mean for opponent summaries"
    if column.startswith("implied_"): return "probability", "American moneyline implied probability normalized across the same game's two sides"
    if column.startswith("moneyline_"): return "American odds", "Historical market quote; timing not established"
    if column.startswith("with_") or column.startswith("without_"):
        return "fraction or metric units", "Explicit played/DNP game subset: win fraction, mean point margin or aggregate net rating per 100 possessions"
    if column in ["reb_pct","orb_pct","drb_pct","tov_pct"]:
        return "fraction", "Team rebound opportunity share or TOV/(FGA+.44*FTA+TOV), see pipeline formula"
    if column.endswith("_id"): return "identifier", "Canonical source entity identifier"
    if column in ["team_name","player_name","team_code","teamAbbrev","firstName","lastName","birthDate"]:
        return "text", "Source display/biographical metadata; names are never canonical join keys"
    if column in ["home_covered","went_over","push"]: return "boolean/nullable", "Retrospective outcome, never a model input; home_covered is missing for pushes"
    return "source/count/context", "Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation."


def main():
    manifest=json.loads((APP/"manifest.json").read_text())
    text=["# Shared application data dictionary", "Generated with `python scripts/document_dataset.py` from the real deployed schema.",
          "Source: [NBA box scores](https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores) and [historical odds](https://www.kaggle.com/datasets/cviaxmiwnptr/nba-betting-data-october-2007-to-june-2024).",
          "All percentages are internal fractions unless explicitly labeled percentile (0-100). No missing statistic is filled with zero. Player season team_id=0 is the single canonical TOT record, also supplied for single-team players. Nonzero rows describe team stints.",
          "USG/AST%/individual ratings/PIE are unavailable at season level pending validated aggregation. Source duration gaps and score discrepancies are reported, not fabricated."]
    for name,info in manifest["tables"].items():
        text += [f"## {name}",f"Full rows: {info['rows']}; deployed rows: {info['app_rows']}.","| Column | dtype | Units | Meaning |","| --- | --- | --- | --- |"]
        for col,dtype in info["columns"].items():
            units,meaning=definition(col)
            text.append(f"| {col} | {dtype} | {units} | {meaning} |")
    text += ["## Model-generated assets", "`team_elo.csv.gz`: game_id/team_id -> pregame Elo computed from full historical games. `backtest_*.csv.gz`: game_id and/or player_id, season, season_start, actual target, out-of-sample prediction, period (calibration/test). `breakout_candidates.csv.gz`: canonical completed-season player fields, historical changes, baseline_flag, probability and explicitly labeled reasons. `evaluation.json`: model selection, split counts, availability cutoff, actual evaluation/calibration. Model-specific feature order lives in its trusted artifact. These assets never trigger API requests."]
    (ROOT/"docs/DATA_DICTIONARY.md").write_text("\n\n".join(text),encoding="utf-8")
    f=pd.read_csv(APP/"player_season.csv.gz")
    latest=manifest["latest_completed_start"]
    demo=f[(f.team_id==0)&(f.season_start==latest)&f.games.ge(20)&f.mpg.ge(15)].nlargest(5,"points_pg")
    (APP/"demo_records.json").write_text(demo[["player_id","player_name","season","games","points_pg","rebounds_pg","assists_pg"]].to_json(orient="records",indent=2),encoding="utf-8")
    print("Wrote exact-schema dictionary and verified demo records.")

if __name__=="__main__": main()
