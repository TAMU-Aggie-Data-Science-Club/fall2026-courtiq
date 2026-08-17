# PlayPulse — Beginner

*ADSC Catalyst Project · Fall 2026*

## Overview

PlayPulse models NBA player and team performance by ingesting publicly available game logs, box scores, and play-by-play data. The final artifact is a Streamlit dashboard that surfaces trends, predicts outcomes, and gives you actual evidence for the takes you'd otherwise just tweet.

## Objective

Build models on public NBA data that predict a well-defined outcome (e.g., single-game win probability, player scoring above their season average), and expose them through an interactive dashboard.

## Suggested tech stack

- **Data processing:** Python, Pandas, NumPy, Scikit-learn
- **Modeling / ML:** Logistic regression + gradient boosting (XGBoost / LightGBM) baselines
- **Visualization:** Plotly, Matplotlib, Seaborn
- **Dashboard:** Streamlit
- **Data sources:** `nba_api` package (NBA Stats), Basketball-Reference

See [`DATA.md`](DATA.md) for concrete data sources and how to access them.

## What team members will gain

- Real NBA play-by-play data going back decades
- Predictive modeling on messy, non-toy data
- A dashboard that could genuinely settle group-chat debates

## Suggested scope (v1)

Pick **one season** and **one prediction task**. Two clean options:

1. **Team-level win probability** given a partial box score at end of Q1 / Q2 / Q3.
2. **Player prop** — predict whether a player scores above their season average, given rolling recent-form features.

Build:

1. Ingestion for a single season (`nba_api`),
2. Feature engineering (team rolling averages, home/away, rest days, opponent strength),
3. Baseline + gradient-boosted model with proper time-based splits (no future leakage),
4. Streamlit dashboard with a matchup selector, model probabilities, and per-feature contributions.

**Out of scope for v1:** live in-game updates, injury data ingestion, betting-odds integration, deep learning.

See [`DELIVERABLES.md`](DELIVERABLES.md) for the suggested deliverable breakdown and rough timeline.

## Repository map

| File / folder | Purpose |
|---|---|
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | **Start here.** How the team runs the project on GitHub — PM vs. member roles, the issue → PR → `main` flow, branching, worktrees, reviews. |
| [`DELIVERABLES.md`](DELIVERABLES.md) | Suggested deliverables and rough timeline. A living plan, not a contract. |
| [`DATA.md`](DATA.md) | Suggested data sources, how to access them, and the source register. |
| [`data/`](data/) | Local working folder for datasets. **Git-ignored** — data is never committed. |
| [`AGENTS.md`](AGENTS.md) | Machine-facing workflow rules for AI coding agents. |

## Notes for PMs

This README, [`DELIVERABLES.md`](DELIVERABLES.md), and [`DATA.md`](DATA.md) are **suggestions**, not commitments. They're a starting point so you don't stare at a blank file on day one. Rewrite them as the team scopes the real project.

## Notes for members

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before touching code. Then pick up an issue from the board.
