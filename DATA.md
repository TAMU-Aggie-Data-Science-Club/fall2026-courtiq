# Data

## Current CSV application (November 2026)

The presentation build follows the approved unified specification. The older API/database sections below describe the retained onboarding prototype, not the current runtime. No new source is fetched on page navigation.

| Source | Origin/URL | Access method | License | Sensitivity | Notes |
| --- | --- | --- | --- | --- | --- |
| Historical NBA Data and Player Box Scores, Eoin A Moore | https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores | User's manual CSV download into `data/raw/kaggle/` | CC0 reported by supplied specification; downloaded archive lacks license/version metadata | Public sports statistics; player birthdates retained only for age calculation | Exact file hashes in `app_data/manifest.json`; no play-by-play loaded. Verify redistribution rights before public release. |
| NBA Betting Data, cviaxmiwnptr | https://www.kaggle.com/datasets/cviaxmiwnptr/nba-betting-data-october-2007-to-june-2024 | User's manual CSV download into `data/raw/kaggle_odds/` | CC0 reported by supplied specification; independently verified version/license TBD | Public game/market statistics | Actual file is `nba_2008-2026.csv`; favorite-magnitude spread normalized to signed home spread. Opening/closing timing unknown: retrospective benchmark only. |
| The Odds API | https://the-odds-api.com/ | Explicit daily cached API request; key from `ODDS_API_KEY` | Provider terms; verify account quota and redistribution terms before activation | Public event/market quotes; API key is secret | No historical paid calls, props or roster/injury claims. No live request made during implementation tests. |

`data/` remains ignored. `app_data/` contains only compact derived application assets, not raw downloads. All commits are local; public deployment is not authorized. The pipeline writes source hashes, date/season coverage, sizes, schema and source limitations. Four games have missing duration/player coverage; score reconciliation exceptions remain visible in ignored `data/processed/validation_report.md` and `score_mismatches.csv`. No values are silently repaired.

The data dictionary is [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md). Do not treat game-level arithmetic means of advanced metrics as authoritative season values. Unsupported season advanced values remain N/A. Missing player team IDs are resolved only through unique game/home-away identity.

## Historical onboarding documentation

This file explains **CourtIQ's** data sources — where they come from, how to get them, and how to think about using them.

> **`DATA.md` is tracked in git. The `data/` folder is not.** Raw data is often large or governed by ToS, and must never be committed. Clone the repo, then populate `data/` locally.

## Selected data sources

| Source                         | Origin / URL                         | Access method                                  | License                                                     | Sensitivity | Notes                                                                                                                                                                            |
| ------------------------------ | ------------------------------------ | ---------------------------------------------- | ----------------------------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| NBA Stats API (unofficial)     | https://github.com/swar/nba_api      | `pip install nba_api`                          | MIT package; NBA data subject to NBA terms                  | None        | **Primary source.** Use first for player/team stats, including advanced team ratings. Week 1 uses bounded local educational requests; package licensing does not grant NBA data rights.                                                           |
| Basketball-Reference           | https://www.basketball-reference.com | TBD — export or permission-reviewed retrieval; no official public API or scraper adopted | Sports Reference terms; permission for CourtIQ application use TBD | None        | **Secondary for advanced statistics when needed.** Check NBA API first. Review access/use permission before exports or scraping; no scraper dependency is installed.                                    |
| `nbadb` / Kaggle NBA Database  | https://github.com/wyattowalsh/nbadb | Download database/Parquet/CSV or use Kaggle    | Per-dataset / repository terms                              | None        | **Historical candidate, not active Week 1 input.** Investigate only if selected sources cannot meet an approved requirement; per-dataset permission review required. |
| Synthetic onboarding fixture | [weekly/week0/player_stats_backup.csv](weekly/week0/player_stats_backup.csv) — authored for CourtIQ | Local `pandas.read_csv`; no network | TBD — no repository-wide redistribution license declared; internal teaching fixture | None — all identities and values invented | Tracked outside `data/` solely for reproducible onboarding; not actual NBA observations. |
| NBA API `stats.nba.com` direct | https://stats.nba.com                | HTTP via `nba_api`                             | Unofficial                                                  | None        | Same source `nba_api` wraps; use directly only if the wrapper is missing a required endpoint.                                                                                    |
| StatMuse | https://www.statmuse.com/nba | TBD — alternative-source investigation only; no API/scraper adopted | TBD — terms, access and redistribution review required | TBD — no dataset selected | Candidate if primary/secondary sources have issues; currently a design reference, not an active pipeline input. |

## Onboarding data

The starter [weekly/week0/onboarding.py](weekly/week0/onboarding.py) defaults to the clearly fictional backup, tracked alongside the assignment outside `data/`. It supplies `GP` (games played), `PTS_TOTAL` (backup-only total points), and already averaged `PTS_PER_GAME`, `REB_PER_GAME`, `AST_PER_GAME`. Never divide averages by games played again.

The prepared `nba_api` option requests one season with `PerGame` units, names NBA.com as its source, and falls back to the backup on failure. Private classroom use follows [NBA terms](https://www.nba.com/termsofuse). Public product/database use still needs PM permission review. The client's MIT license does not license NBA data. Secondary-source application permissions and the repository's redistribution license remain TBD; no secondary source is fetched by onboarding.

Before production retrieval, a PM confirms source terms, allowed caching/publication, sensitivity and request limits. Keep real downloads and generated charts under ignored `data/`; do not redistribute raw datasets.

## Source order and access decisions

PM decision for Week 1: **focus on `nba_api`; use Basketball-Reference for advanced statistics if a needed metric is unavailable; investigate StatMuse or other alternatives if problems arise.** Selection of a source is not a grant of rights to its data. No secondary retrieval or new dependency is part of this assignment.

- **NBA API first:** basic and advanced statistics, profiles and future game logs. The package is MIT-licensed; NBA data remains subject to [NBA terms](https://www.nba.com/termsofuse). Week 1 is local educational exploration, not public hosting or redistribution approval.
- **Basketball-Reference when needed:** Sports Reference says it [does not provide an API](https://www.sports-reference.com/blog/2022/10/new-bot-filtering-and-content-delivery-network-for-sports-reference-sites/). Third-party Python packages called an “API” may be scrapers. Its [data-use policy](https://www.sports-reference.com/data_use.html) requires permission for tools built from scraped data; review this and [bot/access guidance](https://www.sports-reference.com/bot-traffic.html) before assigning retrieval. A scraper is not automatically necessary or authorized. Public application-use permission remains **TBD**.
- **Alternatives:** StatMuse is a candidate to investigate if there is a demonstrated gap; access method, terms and permission are **TBD**. `nbadb`/Kaggle remain historical candidates, not automatically approved inputs. Raise source issues to PMs rather than swapping sources or bypassing access controls.
- **Attribution and limits:** keep source, season, units and retrieval time with data. Cache bounded requests locally, respect access restrictions, and never commit downloads. Public hosting, redistribution and secondary ingestion need a separate reviewed decision.

## Week 1 local snapshots

The supplied `python -m scripts.fetch_data players` command (or `teams` / `ratings`) makes one explicit, bounded request for 2025-26 Regular Season. It preserves the raw JSON response plus request parameters, source, UTC timestamp and checksum under ignored `data/raw/week1/`. Matching snapshots are reused; refresh is deliberate. The app reads local files only. No secondary source is queried.

Member-owned functions in `src/` independently inspect the same input shapes through `scripts/preview_component.py` and save local outputs under `data/interim/week1/` or `data/processed/week1/`; reviewed components can be consolidated later. Provided practice records are authored in Python, all fictional, and used only for offline development/edge cases. They introduce no real dataset. Practice mode does not satisfy real NBA verification and never silently replaces a failed request. The repository-wide redistribution license remains TBD, as for the existing internal teaching fixture.

## Local layout convention

```text
data/
├── raw/          # exactly as fetched from the API — never edit by hand
├── interim/      # cleaned + joined game logs, per-season parquets
└── processed/    # feature tables and model-ready splits
```

Because `data/` isn't in git, the **pipeline that fetches and builds these folders** is what must be committed and reproducible — not the data itself.

## Cache and eventual storage

Future cached API responses belong in `data/raw/`; cleaned tables in `data/interim/`; application-ready tables in `data/processed/`. Preserve source, retrieval time, season, endpoint parameters and units alongside local outputs. Do not repeat live requests on every UI interaction. Week 1 adds a local snapshot reader and an explicit educational collection command; a production refresh pipeline remains future work.

PostgreSQL is a required Week 0 setup prerequisite via [Compose](compose.yaml). The provided [database command](scripts/database.py) creates `courtiq.player_season_stats` from the existing fictional fixture, with source `synthetic` and dataset version `synthetic-onboarding-v1`; it introduces no new source or real NBA ingestion. Fields mirror the CSV in lowercase, preserving totals versus per-game units. The source register's internal-teaching/license limitations still apply. Members run the setup and verify health/`SELECT 1;`; they do not implement schemas. Production NBA schemas, application connection handling and ingestion are future deliverable work.

The loader validates required fields, nonnegative finite metrics, provenance and duplicate keys before a transaction. A composite dataset-version/season/player key prevents duplicate loads; matching rows are updated, other rows preserved. All members using the same repo fixture get the same starting records; local edits do not synchronize. A new dataset/version or real NBA source still requires PM review.

Compose keeps database files in a Docker-managed named volume outside Git; stop/down preserve it unless volume removal is explicitly requested. Local `.env` credentials remain ignored, while the empty [.env.example](.env.example) documents settings. Setup generates administrator and read-only application credentials and restricts connections to localhost with SCRAM password authentication. Use the application role for future reads, not the administrator.

Checked compressed database archives and integrity manifests stay under ignored `data/processed/backups/`, outside the Docker volume, with private local permissions where supported. Setup registers an hourly host check that backs up when the latest intact archive is at least 24 hours old, provided the host and database are available. Existing archives are retained; backups are also made before subsequent fixture/schema setup changes. Restoration uses a new recovery database and leaves the original intact. Roles/passwords are excluded from archives and recreated from local settings during recovery. These local backups do not protect against losing the computer/disk; no off-device copy is configured. See [backup and recovery](docs/SETUP.md#7-backups-and-recovery).

The fictional onboarding backup is the only supplied tabular example tracked outside `data/`; real downloaded or derived NBA datasets and database archives must never be committed anywhere in the repo.
