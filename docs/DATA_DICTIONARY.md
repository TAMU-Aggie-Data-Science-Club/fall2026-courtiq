# Shared application data dictionary

Generated with `python scripts/document_dataset.py` from the real deployed schema.

Source: [NBA box scores](https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores) and [historical odds](https://www.kaggle.com/datasets/cviaxmiwnptr/nba-betting-data-october-2007-to-june-2024).

All percentages are internal fractions unless explicitly labeled percentile (0-100). No missing statistic is filled with zero. Player season team_id=0 is the single canonical TOT record, also supplied for single-team players. Nonzero rows describe team stints.

USG/AST%/individual ratings/PIE are unavailable at season level pending validated aggregation. Source duration gaps and score discrepancies are reported, not fabricated.

## games

Full rows: 13429; deployed rows: 3910.

| Column | dtype | Units | Meaning |

| --- | --- | --- | --- |

| game_id | int64 | identifier | Stable source NBA game ID; regular season starts with numeric prefix 2 |

| date | datetime64[ns] | date | Source Eastern-calendar game date, timezone-naive; same-date history excluded |

| season | object | YYYY-YY | Regular-season label from the shared pipeline |

| season_start | int64 | year | Start year derived from game ID with date-established century |

| home_team_id | int64 | identifier | Canonical source entity identifier |

| away_team_id | int64 | identifier | Canonical source entity identifier |

| home_points | int64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| away_points | int64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| margin | int64 | points | Home-minus-away in games table; team-minus-opponent in team table |

| home_win | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| duration | float64 | minutes | Elapsed game duration, 48 plus 5 per overtime; unavailable when reconstruction fails |

| total | int64 | points | Actual home plus away score |

| overtime | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

## team_games

Full rows: 26858; deployed rows: 7820.

| Column | dtype | Units | Meaning |

| --- | --- | --- | --- |

| game_id | int64 | identifier | Stable source NBA game ID; regular season starts with numeric prefix 2 |

| team_id | int64 | identifier | Stable franchise ID; 0 denotes canonical all-teams TOT season record |

| opponent_id | int64 | identifier | Opposing stable franchise ID |

| date | datetime64[ns] | date | Source Eastern-calendar game date, timezone-naive; same-date history excluded |

| season | object | YYYY-YY | Regular-season label from the shared pipeline |

| season_start | int64 | year | Start year derived from game ID with date-established century |

| team_name | object | text | Source display/biographical metadata; names are never canonical join keys |

| home | int64 | boolean | Source home-team indicator |

| points | int64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| opp_points | int64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| margin | int64 | points | Home-minus-away in games table; team-minus-opponent in team table |

| win | float64 | boolean | Team won this completed game |

| duration | float64 | minutes | Elapsed game duration, 48 plus 5 per overtime; unavailable when reconstruction fails |

| possessions | float64 | estimated possessions | Mean of both teams' FGA + .44*FTA - OREB + TOV |

| ortg | float64 | points/100 possessions | Team rating from points/estimated possessions; season player value unavailable |

| drtg | float64 | points allowed/100 possessions | Team defensive rating; lower generally preferable; season player value unavailable |

| netrtg | float64 | points/100 possessions | ORTG minus DRTG on the same basis; season player value unavailable |

| pace | float64 | possessions/48 min | Estimated possessions times 48 divided by elapsed duration |

| rest | float64 | days | Days between prior observed game and target date minus one, clipped at zero |

| reb_pct | float64 | fraction | Team rebound opportunity share or TOV/(FGA+.44*FTA+TOV), see pipeline formula |

| efg_pct | float64 | fraction | (FGM+.5*3PM)/FGA, from totals |

| tov_pct | float64 | fraction | Team rebound opportunity share or TOV/(FGA+.44*FTA+TOV), see pipeline formula |

| pre_points_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_points_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_points_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_points_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_points_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_opp_points_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_opp_points_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_opp_points_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_opp_points_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_opp_points_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_margin_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_margin_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_margin_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_margin_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_margin_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_win_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_win_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_win_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_win_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_win_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_ortg_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_ortg_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_ortg_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_ortg_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_ortg_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_drtg_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_drtg_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_drtg_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_drtg_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_drtg_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_netrtg_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_netrtg_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_netrtg_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_netrtg_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_netrtg_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_pace_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_pace_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_pace_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_pace_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_pace_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_reb_pct_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_reb_pct_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_reb_pct_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_reb_pct_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_reb_pct_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_efg_pct_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_efg_pct_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_efg_pct_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_efg_pct_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_efg_pct_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_tov_pct_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_tov_pct_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_tov_pct_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_tov_pct_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_tov_pct_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

## player_games

Full rows: 284075; deployed rows: 83916.

| Column | dtype | Units | Meaning |

| --- | --- | --- | --- |

| game_id | int64 | identifier | Stable source NBA game ID; regular season starts with numeric prefix 2 |

| player_id | int64 | identifier | Stable NBA person ID, never a display-name join |

| team_id | int64 | identifier | Stable franchise ID; 0 denotes canonical all-teams TOT season record |

| opponent_id | int64 | identifier | Opposing stable franchise ID |

| date | datetime64[ns] | date | Source Eastern-calendar game date, timezone-naive; same-date history excluded |

| season | object | YYYY-YY | Regular-season label from the shared pipeline |

| season_start | int64 | year | Start year derived from game ID with date-established century |

| player_name | object | text | Source display/biographical metadata; names are never canonical join keys |

| minutes | float64 | minutes | Sum of played player minutes for season rows; actual player duration for game rows |

| played | bool | boolean | Numeric minutes greater than zero; DNPs are false |

| home | int64 | boolean | Source home-team indicator |

| points | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| rebounds | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| assists | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| fg3m | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| steals | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| blocks | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| turnovers | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| plus_minus | float64 | points | Team score differential while player was on court; sum for season rows |

| pra | float64 | counts | Points + rebounds + assists |

| game_score | float64 | Game Score units | Hollinger box-score formula; season value is played-game mean |

| pre_points_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_points_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_points_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_points_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_points_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_rebounds_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_rebounds_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_rebounds_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_rebounds_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_rebounds_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_assists_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_assists_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_assists_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_assists_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_assists_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_minutes_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_minutes_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_minutes_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_minutes_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_minutes_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_pra_3 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_pra_5 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_pra_10 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_pra_20 | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| pre_pra_season | float64 | source metric units | Strictly earlier-date mean, grouped by entity and season; window suffix is games or season-to-date. First game is missing. |

| rest | float64 | days | Days between prior observed game and target date minus one, clipped at zero |

| back_to_back | bool | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

## player_season

Full rows: 13698; deployed rows: 13698.

| Column | dtype | Units | Meaning |

| --- | --- | --- | --- |

| player_id | int64 | identifier | Stable NBA person ID, never a display-name join |

| team_id | int64 | identifier | Stable franchise ID; 0 denotes canonical all-teams TOT season record |

| season_start | int64 | year | Start year derived from game ID with date-established century |

| season | object | YYYY-YY | Regular-season label from the shared pipeline |

| minutes | float64 | minutes | Sum of played player minutes for season rows; actual player duration for game rows |

| points | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| assists | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| rebounds | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| oreb | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| dreb | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| steals | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| blocks | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| turnovers | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| fouls | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| fgm | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| fga | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| fg3m | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| fg3a | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| ftm | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| fta | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| plus_minus | float64 | points | Team score differential while player was on court; sum for season rows |

| games | int64 | games | Count of played appearances in player summaries |

| game_score | float64 | Game Score units | Hollinger box-score formula; season value is played-game mean |

| starts | int64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| player_name | object | text | Source display/biographical metadata; names are never canonical join keys |

| team_name | object | text | Source display/biographical metadata; names are never canonical join keys |

| mpg | float64 | minutes/game | Season player minutes divided by played games |

| ts_pct | float64 | fraction | PTS / [2*(FGA+.44*FTA)], zero denominator unavailable |

| efg_pct | float64 | fraction | (FGM+.5*3PM)/FGA, from totals |

| fg_pct | float64 | fraction | FGM/FGA |

| fg3_pct | float64 | fraction | 3PM/3PA |

| ft_pct | float64 | fraction | FTM/FTA |

| fg2_pct | float64 | fraction | (FGM-3PM)/(FGA-3PA) |

| ftr | float64 | ratio | FTA/FGA |

| ast_tov | float64 | ratio | AST/TOV; zero TOV is undefined |

| pra | float64 | counts | Points + rebounds + assists |

| points_pg | float64 | counts/game | Season total divided by played games, or played-game mean for opponent summaries |

| points_per36 | float64 | counts/36 minutes | 36 times season count divided by total played minutes |

| rebounds_pg | float64 | counts/game | Season total divided by played games, or played-game mean for opponent summaries |

| rebounds_per36 | float64 | counts/36 minutes | 36 times season count divided by total played minutes |

| assists_pg | float64 | counts/game | Season total divided by played games, or played-game mean for opponent summaries |

| assists_per36 | float64 | counts/36 minutes | 36 times season count divided by total played minutes |

| steals_pg | float64 | counts/game | Season total divided by played games, or played-game mean for opponent summaries |

| steals_per36 | float64 | counts/36 minutes | 36 times season count divided by total played minutes |

| blocks_pg | float64 | counts/game | Season total divided by played games, or played-game mean for opponent summaries |

| blocks_per36 | float64 | counts/36 minutes | 36 times season count divided by total played minutes |

| pra_pg | float64 | counts/game | Season total divided by played games, or played-game mean for opponent summaries |

| pra_per36 | float64 | counts/36 minutes | 36 times season count divided by total played minutes |

| usage | float64 | fraction | Advanced season usage unavailable until authoritative aggregation validated |

| ast_pct | float64 | fraction | Advanced season assist percentage unavailable until validated |

| ortg | float64 | points/100 possessions | Team rating from points/estimated possessions; season player value unavailable |

| drtg | float64 | points allowed/100 possessions | Team defensive rating; lower generally preferable; season player value unavailable |

| netrtg | float64 | points/100 possessions | ORTG minus DRTG on the same basis; season player value unavailable |

| pie | float64 | fraction | Advanced season PIE unavailable until validated |

| birthDate | object | text | Source display/biographical metadata; names are never canonical join keys |

| draftNumber | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| fromYear | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| age | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| experience | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| is_top50 | bool | boolean | Player belongs to frozen prior completed-season Top 50 by PRA/game with GP>=40 |

## on_off

Full rows: 7269; deployed rows: 7269.

| Column | dtype | Units | Meaning |

| --- | --- | --- | --- |

| player_id | int64 | identifier | Stable NBA person ID, never a display-name join |

| team_id | int64 | identifier | Stable franchise ID; 0 denotes canonical all-teams TOT season record |

| season_start | int64 | year | Start year derived from game ID with date-established century |

| season | object | YYYY-YY | Regular-season label from the shared pipeline |

| player_name | object | text | Source display/biographical metadata; names are never canonical join keys |

| games | int64 | games | Count of played appearances in player summaries |

| minutes_on | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| minutes_off | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| on_per48 | float64 | points/48 minutes | 48*sum(player +/-)/sum(player minutes), valid played-game subset |

| off_per48 | float64 | points/48 minutes | 48*sum(team margin-player +/-)/sum(duration-player minutes), same subset |

| on_off_diff | float64 | points/48 minutes | on_per48 minus off_per48, not isolated causal impact |

| plus_minus | float64 | points | Team score differential while player was on court; sum for season rows |

| game_score | float64 | Game Score units | Hollinger box-score formula; season value is played-game mean |

| games_missed | int64 | games | Explicit DNP rows only within recorded team stint; not all absent roster rows |

| observed_rows | int64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| valid_on_games | int64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| with_win_pct | float64 | fraction or metric units | Explicit played/DNP game subset: win fraction, mean point margin or aggregate net rating per 100 possessions |

| with_margin | float64 | fraction or metric units | Explicit played/DNP game subset: win fraction, mean point margin or aggregate net rating per 100 possessions |

| with_netrtg | float64 | fraction or metric units | Explicit played/DNP game subset: win fraction, mean point margin or aggregate net rating per 100 possessions |

| without_win_pct | float64 | fraction or metric units | Explicit played/DNP game subset: win fraction, mean point margin or aggregate net rating per 100 possessions |

| without_margin | float64 | fraction or metric units | Explicit played/DNP game subset: win fraction, mean point margin or aggregate net rating per 100 possessions |

| without_netrtg | float64 | fraction or metric units | Explicit played/DNP game subset: win fraction, mean point margin or aggregate net rating per 100 possessions |

| reliability | object | category | Low: on<500 or off<250; High: on>=1500 and off>=500; otherwise Medium |

## top50_players

Full rows: 50; deployed rows: 50.

| Column | dtype | Units | Meaning |

| --- | --- | --- | --- |

| player_id | int64 | identifier | Stable NBA person ID, never a display-name join |

| team_id | int64 | identifier | Stable franchise ID; 0 denotes canonical all-teams TOT season record |

| season_start | int64 | year | Start year derived from game ID with date-established century |

| season | object | YYYY-YY | Regular-season label from the shared pipeline |

| minutes | float64 | minutes | Sum of played player minutes for season rows; actual player duration for game rows |

| points | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| assists | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| rebounds | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| oreb | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| dreb | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| steals | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| blocks | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| turnovers | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| fouls | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| fgm | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| fga | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| fg3m | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| fg3a | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| ftm | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| fta | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| plus_minus | float64 | points | Team score differential while player was on court; sum for season rows |

| games | int64 | games | Count of played appearances in player summaries |

| game_score | float64 | Game Score units | Hollinger box-score formula; season value is played-game mean |

| starts | int64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| player_name | object | text | Source display/biographical metadata; names are never canonical join keys |

| team_name | object | text | Source display/biographical metadata; names are never canonical join keys |

| mpg | float64 | minutes/game | Season player minutes divided by played games |

| ts_pct | float64 | fraction | PTS / [2*(FGA+.44*FTA)], zero denominator unavailable |

| efg_pct | float64 | fraction | (FGM+.5*3PM)/FGA, from totals |

| fg_pct | float64 | fraction | FGM/FGA |

| fg3_pct | float64 | fraction | 3PM/3PA |

| ft_pct | float64 | fraction | FTM/FTA |

| fg2_pct | float64 | fraction | (FGM-3PM)/(FGA-3PA) |

| ftr | float64 | ratio | FTA/FGA |

| ast_tov | float64 | ratio | AST/TOV; zero TOV is undefined |

| pra | float64 | counts | Points + rebounds + assists |

| points_pg | float64 | counts/game | Season total divided by played games, or played-game mean for opponent summaries |

| points_per36 | float64 | counts/36 minutes | 36 times season count divided by total played minutes |

| rebounds_pg | float64 | counts/game | Season total divided by played games, or played-game mean for opponent summaries |

| rebounds_per36 | float64 | counts/36 minutes | 36 times season count divided by total played minutes |

| assists_pg | float64 | counts/game | Season total divided by played games, or played-game mean for opponent summaries |

| assists_per36 | float64 | counts/36 minutes | 36 times season count divided by total played minutes |

| steals_pg | float64 | counts/game | Season total divided by played games, or played-game mean for opponent summaries |

| steals_per36 | float64 | counts/36 minutes | 36 times season count divided by total played minutes |

| blocks_pg | float64 | counts/game | Season total divided by played games, or played-game mean for opponent summaries |

| blocks_per36 | float64 | counts/36 minutes | 36 times season count divided by total played minutes |

| pra_pg | float64 | counts/game | Season total divided by played games, or played-game mean for opponent summaries |

| pra_per36 | float64 | counts/36 minutes | 36 times season count divided by total played minutes |

| usage | float64 | fraction | Advanced season usage unavailable until authoritative aggregation validated |

| ast_pct | float64 | fraction | Advanced season assist percentage unavailable until validated |

| ortg | float64 | points/100 possessions | Team rating from points/estimated possessions; season player value unavailable |

| drtg | float64 | points allowed/100 possessions | Team defensive rating; lower generally preferable; season player value unavailable |

| netrtg | float64 | points/100 possessions | ORTG minus DRTG on the same basis; season player value unavailable |

| pie | float64 | fraction | Advanced season PIE unavailable until validated |

| birthDate | object | text | Source display/biographical metadata; names are never canonical join keys |

| draftNumber | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| fromYear | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| age | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| experience | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| rank | int64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

## teams

Full rows: 30; deployed rows: 30.

| Column | dtype | Units | Meaning |

| --- | --- | --- | --- |

| team_id | int64 | identifier | Stable franchise ID; 0 denotes canonical all-teams TOT season record |

| team_name | object | text | Source display/biographical metadata; names are never canonical join keys |

| teamAbbrev | object | text | Source display/biographical metadata; names are never canonical join keys |

| team_code | object | text | Source display/biographical metadata; names are never canonical join keys |

## player_vs_team

Full rows: 137016; deployed rows: 137016.

| Column | dtype | Units | Meaning |

| --- | --- | --- | --- |

| player_id | int64 | identifier | Stable NBA person ID, never a display-name join |

| opponent_id | int64 | identifier | Opposing stable franchise ID |

| season | object | YYYY-YY | Regular-season label from the shared pipeline |

| games | int64 | games | Count of played appearances in player summaries |

| points_pg | float64 | counts/game | Season total divided by played games, or played-game mean for opponent summaries |

| rebounds_pg | float64 | counts/game | Season total divided by played games, or played-game mean for opponent summaries |

| assists_pg | float64 | counts/game | Season total divided by played games, or played-game mean for opponent summaries |

## odds_history

Full rows: 13429; deployed rows: 3910.

| Column | dtype | Units | Meaning |

| --- | --- | --- | --- |

| game_id | int64 | identifier | Stable source NBA game ID; regular season starts with numeric prefix 2 |

| date | datetime64[ns] | date | Source Eastern-calendar game date, timezone-naive; same-date history excluded |

| season | object | YYYY-YY | Regular-season label from the shared pipeline |

| season_start | int64 | year | Start year derived from game ID with date-established century |

| home_team_id | int64 | identifier | Canonical source entity identifier |

| away_team_id | int64 | identifier | Canonical source entity identifier |

| home_points | int64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| away_points | int64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| margin | int64 | points | Home-minus-away in games table; team-minus-opponent in team table |

| home_win | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| duration | float64 | minutes | Elapsed game duration, 48 plus 5 per overtime; unavailable when reconstruction fails |

| total | int64 | points | Actual home plus away score |

| overtime | float64 | source/count/context | Named source box-score count or documented derived context; missing values remain unavailable. See src/pipeline.py and source manifest for transformation. |

| spread_home | float64 | points | Signed home spread: negative home favorite |

| total_line | float64 | points | Historical market total |

| moneyline_home | float64 | American odds | Historical market quote; timing not established |

| moneyline_away | float64 | American odds | Historical market quote; timing not established |

| implied_home | float64 | probability | American moneyline implied probability normalized across the same game's two sides |

| implied_away | float64 | probability | American moneyline implied probability normalized across the same game's two sides |

| home_covered | float64 | boolean/nullable | Retrospective outcome, never a model input; home_covered is missing for pushes |

| push | object | boolean/nullable | Retrospective outcome, never a model input; home_covered is missing for pushes |

| went_over | float64 | boolean/nullable | Retrospective outcome, never a model input; home_covered is missing for pushes |

| line_timing | object | text | Unknown historical line timing; retrospective comparison only |

## Model-generated assets

`team_elo.csv.gz`: game_id/team_id -> pregame Elo computed from full historical games. `backtest_*.csv.gz`: game_id and/or player_id, season, season_start, actual target, out-of-sample prediction, period (calibration/test). `breakout_candidates.csv.gz`: canonical completed-season player fields, historical changes, baseline_flag, probability and explicitly labeled reasons. `evaluation.json`: model selection, split counts, availability cutoff, actual evaluation/calibration. Model-specific feature order lives in its trusted artifact. These assets never trigger API requests.