# Data

This file explains **PlayPulse's** data sources — where they come from, how to get them, and how to think about using them.

> **`DATA.md` is tracked in git. The `data/` folder is not.** Raw data is often large or governed by ToS, and must never be committed. Clone the repo, then populate `data/` locally.

## Selected data sources

| Source                         | Origin / URL                         | Access method                                  | License                                                     | Sensitivity | Notes                                                                                                                                                                            |
| ------------------------------ | ------------------------------------ | ---------------------------------------------- | ----------------------------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| NBA Stats API (unofficial)     | https://github.com/swar/nba_api      | `pip install nba_api`                          | MIT package; NBA data subject to NBA terms                  | None        | **Primary source.** Current player/team stats, game logs, advanced stats, rankings, play-by-play, and shot-chart data.                                                           |
| Basketball-Reference           | https://www.basketball-reference.com | HTML scrape via `basketball_reference_scraper` | Educational use — respect site restrictions and rate limits | None        | **Secondary analytics source.** Advanced and historical metrics such as PER, TS%, USG%, Win Shares, BPM, VORP, and per-possession statistics.                                    |
| `nbadb` / Kaggle NBA Database  | https://github.com/wyattowalsh/nbadb | Download database/Parquet/CSV or use Kaggle    | Per-dataset / repository terms                              | None        | **Historical data source.** Bulk historical NBA data for long-term trends, league comparisons, and potential ML training without repeatedly requesting old seasons from NBA.com. |
| NBA API `stats.nba.com` direct | https://stats.nba.com                | HTTP via `nba_api`                             | Unofficial                                                  | None        | Same source `nba_api` wraps; use directly only if the wrapper is missing a required endpoint.                                                                                    |

## How to think about using each source

* **Primary pipeline.** Use `nba_api` for current player, team, and game data. This should support most profile features, recent 5/10/20-game analysis, team performance, rankings, and shot-chart visualizations.
* **Advanced statistics.** Use Basketball-Reference when established advanced metrics or historical season-level statistics are needed. Scrape conservatively, cache results locally, and do not request Basketball-Reference pages every time a user opens the application.
* **Historical data.** Use `nbadb` as a bulk historical source when large amounts of past NBA data are needed for historical comparisons, trends, similar-player analysis, or future machine-learning models.
* **Rate limits.** `nba_api`, stats.nba.com, and Basketball-Reference can block excessive requests. Cache fetched data to `data/raw/` and avoid repeatedly requesting unchanged historical data.
* **Vintage.** NBA definitions and available statistics can change across eras. If comparing players or teams across long time periods, document differences in available metrics.
* **Fitness.** Play-by-play data is large and noisy. Box scores, season statistics, advanced metrics, and shot data should be enough for most core PlayPulse features.
* **License / ToS.** Stay conservative with all sources: do not republish full raw datasets, respect source rate limits and terms, and keep raw downloaded data outside the repository.

Choosing and vetting a source is a **judgment call** — surface major data-source changes to a PM rather than changing the project's data direction alone.

## Local layout convention

```text
data/
├── raw/          # exactly as fetched from the API — never edit by hand
├── interim/      # cleaned + joined game logs, per-season parquets
└── processed/    # feature tables and model-ready splits
```

Because `data/` isn't in git, the **pipeline that fetches and builds these folders** is what must be committed and reproducible — not the data itself.
