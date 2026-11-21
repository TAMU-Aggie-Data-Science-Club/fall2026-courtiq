# CourtIQ setup & presentation walkthrough

Use Python 3.12. From the repository root in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
python -m streamlit run app.py
```

No database, Docker, GPU or key is needed. Do not push/deploy without authorization.

## Rebuild from original downloads

Download/extract [NBA CSVs](https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores) into `data/raw/kaggle/` and [betting CSV](https://www.kaggle.com/datasets/cviaxmiwnptr/nba-betting-data-october-2007-to-june-2024) into `data/raw/kaggle_odds/`. Preserve filenames. Do not commit raw data. The large play-by-play file is unused.

```powershell
python scripts/build_dataset.py --start-season 2015
python scripts/validate_data.py
python scripts/train_models.py --profile core
python scripts/evaluate_models.py
python -m unittest discover -s tests -v
python -m compileall -q app.py src scripts tests
```

Training happens offline. Do not retrain on Streamlit interaction. Changed data requires rebuilding artifacts. `app_data/manifest.json` records hashes, versions, column types, coverage and sizes. The source version cannot be inferred from the download filename alone.

## Presentation (about five minutes)

1. **Players / Scouting Lab:** use 2025-26, choose a well-known eligible player, inspect the eight-axis radar, raw-value table, ranking population and badge summary. Change to Shooting. Explain why the advanced table is stable across lenses and why unsupported values show N/A.
2. **Players / On/Off Impact:** select the same season/player. If traded, choose a team stint. Compare on/off and explicit-DNP with/without separately. Change the minimum-minutes slider. Explain reliability and lineup confounding.
3. **Teams:** choose distinct teams and a date after the latest observed game. Predict. Explain home/away probability, home-minus-away margin, expected score, empirical 80% interval and actual model evaluation. Add a manual signed home spread. Negative means home favorite; pushes are separate.
4. **Compare:** select opposing teams and one supported player from each. Predict points/rebounds/assists, compare to the previous-10-game baseline and inspect encounter logs. Historical roster associations are not confirmed active lineups, and encounters are not guarding assignments.
5. **Trends:** inspect candidate probabilities and the held-out breakout backtest. Select a candidate to compare season history with the partial current-season tracker. Explain the three-part target, missing-outcome exclusion and that model probabilities are estimates.

Use records actually present in the selectors. See `app_data/demo_records.json` for verified source-backed example records generated during preparation. Do not present invented screenshots or treat an empty current-season qualification cohort as a calculation bug.

## Optional current odds

Set the secret in the current shell, then run an explicit refresh:

```powershell
$env:ODDS_API_KEY = "YOUR_PRIVATE_KEY"
python scripts/refresh_odds.py
```

The [Odds API](https://the-odds-api.com/) refresh reuses today's UTC cache. Featured markets can consume multiple credits per HTTP request; verify your account's current quota before activation. No props/paid history/automatic polling. Don't paste keys into chat or logs. On hosted Streamlit, refresh is an externally managed preparation step with environment secrets; the normal app never calls the API. Runtime filesystem writes are not durable deployment storage.

## Troubleshooting & limitations

- Missing exports: build the datasets. Missing/incompatible models: train the models after rebuilding.
- `.venv` failing to launch: verify the installed Python 3.12 path in `pyvenv.cfg`; recreate the environment only after preserving any needed settings.
- Four current-season games have no reliable duration/player-minute coverage. Source score mismatches are reported in local validation output. Missing values stay unavailable.
- Dataset licenses are reported as CC0 in the supplied specification but not bundled with the download; verify current terms before public redistribution/deployment.
- All work is local. Human authorization is required for any push or deployment.
