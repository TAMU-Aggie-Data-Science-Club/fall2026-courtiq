# CourtIQ CSV implementation report

Prepared November 20, 2026 from executed local builds and tests. Work is on local `main`; no push or deployment was performed.

## What works

- One shared CSV pipeline, compact app exports, source hashes and exact-column dictionary.
- Player Scouting Lab: All-Around/Shooting radar, full-league qualified percentiles, exact-value table, deterministic badges and advanced-stat N/A handling.
- On/Off Impact: separate team stints, on/off per 48, explicit-DNP with/without, Game Score, reliability, scatter and minimum-minutes leaderboard.
- Team prediction: manual teams/date/spread, chronological Elo/logistic/tree candidates, margin/total regressors, held-out empirical intervals and cover/push probabilities.
- Player prediction: opposing-team points/rebounds/assists, prior-10-game baseline, empirical bounds and descriptive opposing-player logs. No guarding assignments are claimed.
- Breakout Watch: season-transition labels, baseline and logistic/tree candidates, actual backtest, candidate scores, model-sensitivity explanations and separate current-season tracker.
- Explicit daily odds-cache command with mocked failure/quota/malformed-response handling. Normal navigation makes no API call.

## Source attribution and real-data coverage

The user confirmed these exact download sources:

- [Historical NBA Data and Player Box Scores, Eoin A Moore](https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores).
- [NBA Betting Data, cviaxmiwnptr](https://www.kaggle.com/datasets/cviaxmiwnptr/nba-betting-data-october-2007-to-june-2024).
- Optional current quotes: [The Odds API](https://the-odds-api.com/).

The build reads 11 supplied CSVs; the large play-by-play file is not loaded. Full processed coverage begins 2015-16 and extends into 2026-27, through November 19, 2026 in the supplied download. Full outputs contain **13,429 games, 26,858 team-game rows, 284,075 player-game rows and 13,698 player-season/stint rows**. All 30 teams remain available; the Top 50 is a separate frozen list.

The deployed game tables contain 2023-24 onward: 1,230, 1,224, 1,230 and 226 games respectively. Full season rows are retained for trends and breakout. Historical odds cover 100% of recorded games in the three deployed completed seasons. Current 2026-27 historical odds are correctly unavailable. The latest test season has spreads but no matched two-sided moneyline prices; no market win probabilities are invented.

Source exceptions: **114 player/team score-reconciliation discrepancies** are saved for inspection in ignored `data/processed/score_mismatches.csv`. Four games (`22600088`, `22600124`, `22600142`, `22600144`) lack usable duration/player-minute coverage; their durations stay missing. Reported missing 2024-25 IDs remain absent, and actual season coverage is reported rather than assuming 1,230. Missing player team IDs are resolved only from unique game/home-away identity. Source data are never edited.

Dataset version is `888fbe7340f0`, including raw-file hashes and pipeline code fingerprint. Downloaded files lack original Kaggle version/license metadata. The PDF reports CC0, but verify current license/redistribution terms before public release. No deployment is authorized.

## Actual chronological model results

For game models: train through 2022-23, validate 2023-24, use 2024-25 for residual/calibration diagnostics and test 2025-26. Preprocessing fits training data only. Models remain fixed while prior completed games update rolling context. Historical dates before validation/calibration availability are rejected by interactive inference; stored backtests remain available.

| Target | Selected | Final-test result |
| --- | --- | --- |
| Home winner | Logistic regression | 67.56% accuracy; log loss 0.6044; Brier 0.2079; ROC-AUC 0.7299; 1,230 games |
| Home-minus-away margin | Ridge | MAE 11.39 points; RMSE 14.61 |
| Total points | Ridge | MAE 15.44 points; RMSE 19.35 |
| Player points | Histogram gradient boosting | MAE 4.650; RMSE 6.057; 26,648 played appearances |
| Player rebounds | Histogram gradient boosting | MAE 1.916; RMSE 2.514 |
| Player assists | Histogram gradient boosting | MAE 1.359; RMSE 1.842 |
| Breakout | Histogram gradient boosting | Precision@15 13.33% (2/15), test base rate 5.18%, PR-AUC 0.1428; 193 candidates |

Team winner baselines: home-rate log loss 0.6878; Elo log loss 0.6080 and accuracy 67.80%. The selected classifier is slightly better on probability loss, not winner accuracy. Full same-cohort player baselines, breakout baseline/cohorts and calibration buckets are stored in `app_data/baselines.json` and `evaluation.json`; the interface shows them alongside results.

Spread evaluation is retrospective because line timing is unknown: **48.36% home-cover classification accuracy excluding pushes**, 10 pushes across 1,230 test games, three-class Brier 0.5372. Approximate 80% margin intervals cover **77.56%** of test outcomes. These results do not establish a profitable or market-beating system. No thresholds were tuned to make the final test appear stronger.

## Verification actually executed

| Command/check | Result |
| --- | --- |
| `python scripts/build_dataset.py --start-season 2015` | PASS: real shared outputs built |
| `python scripts/document_dataset.py` | PASS: actual schema and verified demo records |
| `python scripts/validate_data.py` | PASS: zero structural failures; documented source exceptions retained |
| `python scripts/train_models.py --profile core` | PASS: all core model groups trained and persisted |
| `python scripts/evaluate_models.py` | PASS: actual held-out and retrospective market evaluation |
| `python -m unittest discover -s tests -v` | PASS: 21 tests, zero skipped |
| `python -m scripts.check_starter` | PASS: 11 retained offline starter-support checks |
| `python scripts/verify_environment.py` | PASS in existing and fresh environments after sklearn import-name fix |
| `python -m pip check` | PASS in existing and fresh environments |
| `python -m compileall -q app.py src scripts tests` | PASS |
| Fresh Python 3.12 venv + `pip install -r requirements.txt` | PASS |
| Trusted artifact reload in fresh environment | PASS: matching dataset version |
| Fresh-environment local Streamlit startup | PASS: HTTP 200 `ok` health response; temporary server stopped |
| Live Odds API request/account authorization | NOT RUN: mocked tests only; no quota consumed |
| Public cloud deployment | NOT RUN: not authorized |

Unit tests cover formulas, game-ID century handling, DNP/on-off example, ties, eligibility boundaries, empty/missing axes, TOT uniqueness, direction, future-feature invariance, reliability, spread pushes and reproducibility. Integration tests exercise all five tools, actual prediction buttons, invalid teams/historical dates and mocked API/cache failures. Streamlit AppTest verifies rendered application behavior; no manual mobile-browser visual certification is claimed.

## Files and responsibilities

- `src/pipeline.py`: shared cleaning, identity resolution, derived metrics, season/impact/opponent outputs, odds join, compact export and manifest.
- `src/features/`: deterministic scouting, impact helpers and breakout definitions.
- `src/models/`: train-only preprocessing, chronological evaluation, team/player/breakout model training, persistence and inference.
- `src/dashboard.py`, `app.py`: five integrated tools, shared navigation, selection, chart/table rendering and missing-data states.
- `src/odds_api.py`, `scripts/refresh_odds.py`, `.env.example`: optional explicit daily odds refresh; secret never committed.
- `scripts/build_dataset.py`, `validate_data.py`, `document_dataset.py`, `train_models.py`, `evaluate_models.py`: executable preparation/verification workflow.
- `scripts/verify_environment.py`: correct distribution/import name mapping for scikit-learn.
- `tests/test_core.py`, `test_integration.py`: executed deterministic, real-data, model, API and Streamlit checks.
- `app_data/`: compact reviewed derived tables, provenance, evaluation, baseline summaries and backtests. No raw files.
- `artifacts/`: three trusted locally generated model bundles with preprocessing, schema, versions and cutoffs.
- `README.md`, `ARCHITECTURE.md`, `DATA.md`, `DELIVERABLES.md`, `docs/`: current contract, exact source attribution, setup, dictionary, model cards and walkthrough. Historical onboarding files are preserved.
- `requirements.txt`: approved pinned scikit-learn and compatible support dependencies; retained historical dependencies still support onboarding checks.

`data/` and `.planning/` remain ignored. No credentials, raw downloads, local venvs, backups or private notes are committed.

## Asset footprint and launch

Application CSV/metadata assets total about **17.3 MB**, largest file **7.24 MB**. Trusted models total **9.53 MB**, largest **9.02 MB**. These are within the PDF's file-size limits; no claim of deployed cloud peak-memory benchmarking is made.

```powershell
cd C:\Users\abhit\Documents\courtiq
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

See [DEMO.md](DEMO.md) for rebuilding, explicit optional odds refresh and the five-minute walkthrough, with verified example records in `app_data/demo_records.json`.

## Remaining limitations

- Six authoritative season advanced-stat values (USG, AST%, ORTG, DRTG, NRTG, PIE) remain N/A pending validated aggregation. TS/eFG are supported from totals.
- Starter-share, dated roster/injury information, confirmed defensive assignments and specialized hustle/shot-location data are not assumed.
- Breakout labels exclude missing future outcomes, creating survivorship bias. One held-out final season and a separate calibration period are used, rather than claiming two untouched final tests. Probabilities are measured estimates, not guaranteed calibrated probabilities.
- Neural models, SHAP, BPM/VORP, shrinkage and market-aware training are intentionally deferred. Training/inference speed benchmarks and mobile-browser visual checks are not certified.
- Optional odds refresh writes a local CSV cache/log; it does not automatically identify active rosters, publish durable cloud storage or map every quote to a canonical schedule game. Manual matchup/line selection remains the supported core path.
- Verify Kaggle and odds redistribution terms before any public push/deployment of data derivatives. All commits are local, and the user controls all pushes.

## Suggested review title and description

**Title:** Integrate CSV-backed CourtIQ scouting, impact and prediction tools

**Description:** Implements the approved unified specification as one Streamlit app with shared CSV preparation, five analytical tools, offline chronological models, source attribution and reproducible validation. Includes actual held-out evaluation and explicit source/coverage limitations. Core 21-test suite and retained 11-check starter suite pass; fresh-environment install/reload/startup verified. Optional live odds account access and public deployment were not tested or authorized. Review the model cards and source exceptions before presentation or release.
