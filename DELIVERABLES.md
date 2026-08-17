# Deliverables & Timeline

> **How to read this file.** This is the PMs' best current estimate of what PlayPulse needs to ship and roughly when. It is a **living plan, not a contract**. The authoritative picture lives in **GitHub Issues and the Project board**.

## Milestones (suggested)

| # | Deliverable | Description | Owner (role) | Target |
|---|-------------|-------------|--------------|--------|
| 1 | Project scoping | Pick the target season(s) and the one prediction task for v1 (win probability vs. player prop). Define success metric (accuracy, log-loss, calibration). | PM | Week 1 |
| 2 | Data ingestion | Reproducible fetcher using `nba_api` with caching, throttling, and idempotent re-runs. Documented in [`DATA.md`](DATA.md). | Members | Weeks 1–2 |
| 3 | EDA | Profile the data: schema, missingness, distribution of the target, rolling-average sanity checks. | Members | Week 2 |
| 4 | Feature engineering | Team/player rolling averages, opponent strength, home/away, rest days, back-to-backs. | Members | Weeks 3–4 |
| 5 | Baseline model | Logistic regression with time-based splits and calibration. First result to beat. | Members | Week 4 |
| 6 | Gradient-boosted model | XGBoost / LightGBM with proper CV. Compare against baseline on calibration + accuracy. | Members | Weeks 5–6 |
| 7 | Streamlit dashboard | Matchup / player selector, model predictions, feature-contribution view, and a couple of exploratory charts. | Members + PM | Weeks 6–7 |
| 8 | Handoff & retro | Reproducibility check, short writeup, lessons learned. | PM | Week 8 |

## Timeline (rough)

```
Week:   1     2     3     4     5     6     7     8
        |-----|-----|-----|-----|-----|-----|-----|
Scope   ██
Ingest        ████
EDA                 ██
Features                  ████
Baseline                        ██
Boosted                              ████
Dashboard                                  ████
Retro                                              ██
```

## Working agreements

- **Each deliverable maps to one or more GitHub Issues.** The board is the source of truth; this file is the summary.
- **Dates are estimates.** When reality diverges, update the issue and this file if the shift is material.
- **"Done" is defined per issue** via acceptance criteria — not by a date passing.
- **Reprioritize openly.** If a deliverable changes, a PM notes why in the issue so the decision is auditable.
