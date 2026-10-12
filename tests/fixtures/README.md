# Synthetic onboarding fixture

[synthetic_player_stats.csv](synthetic_player_stats.csv) is authored teaching material for CourtIQ, not downloaded NBA data. All names, teams, seasons and statistics are invented. It contains 12 fictional players, including exactly 20 games and fewer than 20 games, and intentionally different rankings by totals and averages. There are no missing values or tied scoring averages in this beginner exercise; handling those is later work.

| Column | Meaning |
| --- | --- |
| `PLAYER_ID` | Synthetic identifier; not an NBA ID |
| `PLAYER_NAME` | Invented name |
| `TEAM_ABBREVIATION` | Invented team; not an NBA team |
| `SEASON` | Synthetic season label |
| `GP` | Games played (integer) |
| `PTS_TOTAL` | Total points across all games |
| `PTS_PER_GAME` | Points per game, already calculated as `PTS_TOTAL / GP` |
| `REB_PER_GAME` | Rebounds per game, already averaged |
| `AST_PER_GAME` | Assists per game, already averaged |

Do not divide any `*_PER_GAME` column by games played again. NBA endpoints vary in units: inspect their parameters and definitions before applying this schema to real data.

This fixture is intentionally tracked outside `data/`. Real downloads and caches remain ignored under `data/`, as described in [DATA.md](../../DATA.md).
