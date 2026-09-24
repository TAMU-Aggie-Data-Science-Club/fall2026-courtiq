# PlayPulse — Beginner

*ADSC Catalyst Project · Fall 2026*

## Overview

PlayPulse is an interactive NBA analytics platform that organizes current and historical player, team, and game data into clear profiles and visualizations. The goal is to make NBA statistics easier to understand for casual fans and fantasy basketball players without requiring them to search across multiple websites or interpret large statistical tables.

The final product will be a Streamlit application where users can explore player and team performance, compare players or teams, analyze recent trends, and understand how performance compares to league benchmarks.

## Objective

Build an NBA analytics platform that allows users to:

* Search for NBA players and teams.
* View season statistics and recent performance.
* Compare performance against league averages and percentiles.
* Explore player shot charts and other interactive visualizations.
* View team records, rankings, offensive and defensive performance, and recent form.
* Compare players or teams using normalized statistics.
* Track meaningful changes in performance over time.
* Filter analysis by season or recent periods such as the last 5, 10, or 20 games.

If the core application is completed ahead of schedule, the project may also explore player similarity and machine-learning models for player performance or game outcome forecasting.

## Suggested tech stack

* **Data processing:** Python, Pandas, NumPy
* **Database:** PostgreSQL
* **Visualization:** Plotly, Matplotlib, Seaborn
* **Dashboard:** Streamlit
* **Data exploration:** Jupyter Notebook
* **Data sources:** `nba_api` (NBA.com Stats), Basketball-Reference, and `nbadb` for historical data
* **Stretch modeling / ML:** Scikit-learn, XGBoost

See [`DATA.md`](DATA.md) for the selected data sources and how they will be used.

## What team members will gain

* Experience working with real-world NBA datasets.
* Building reproducible data collection and cleaning pipelines.
* Database design and data organization.
* Data analysis and feature creation using Pandas and NumPy.
* Interactive data visualization with Plotly.
* Building and integrating features into a Streamlit web application.
* Collaborative software development using GitHub Issues, branches, pull requests, and code reviews.
* Optional experience with introductory machine-learning models if the core project is completed early.

## Project scope

The core project focuses on **player and team analytics rather than prediction**.

Build:

1. A reproducible pipeline for collecting and cleaning NBA player, team, and game data.
2. A shared PostgreSQL database containing the processed data needed by the application.
3. Searchable player profiles containing season statistics, recent performance, league percentiles, strengths and weaknesses, shot charts, and performance trends.
4. Searchable team profiles containing records, league rankings, offensive and defensive performance, recent form, and efficiency or shot-distribution visualizations.
5. Player and team comparison tools using normalized statistics and interactive visualizations.
6. Filters for seasons and recent periods such as the last 5, 10, or 20 games.
7. Trend analysis that identifies meaningful changes in player and team performance.
8. One integrated Streamlit application containing the completed features.

**Stretch scope:** similar-player search, player performance forecasting, and NBA game outcome prediction.

**Out of scope for the core release:** live in-game updates, betting-odds integration, deep learning, and features that would delay completion of the core analytics platform.

See [`DELIVERABLES.md`](DELIVERABLES.md) for the deliverable breakdown and timeline.

## Repository map

| File / folder                        | Purpose                                                                                                                                         |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | **Start here.** How the team runs the project on GitHub — PM vs. member roles, the issue → PR → `main` flow, branching, worktrees, and reviews. |
| [`DELIVERABLES.md`](DELIVERABLES.md) | Current project milestones and rough timeline. A living plan, not a contract.                                                                   |
| [`DATA.md`](DATA.md)                 | Selected data sources, how to access them, and guidelines for using them.                                                                       |
| [`data/`](data/)                     | Local working folder for datasets. **Git-ignored** — raw data is never committed.                                                               |
| [`AGENTS.md`](AGENTS.md)             | Machine-facing workflow rules for AI coding agents.                                                                                             |
| [`CODEOWNERS`](CODEOWNERS)           | **Team roster + review policy.** PMs, members, and the code-owner rule for PRs into `main`.                                                     |

## Team

The current PMs and members for this project are listed in [`CODEOWNERS`](CODEOWNERS). PMs listed there are the code owners for PRs into `main`.

## Notes for PMs

This README, [`DELIVERABLES.md`](DELIVERABLES.md), and [`DATA.md`](DATA.md) describe the current project direction and should be updated when major scope, timeline, or technical decisions change.

## Notes for members

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before touching code. Then pick up an issue from the board.
