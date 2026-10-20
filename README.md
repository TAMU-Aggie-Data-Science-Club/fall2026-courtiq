# CourtIQ

*ADSC Catalyst Project · Fall 2026*

## Overview

CourtIQ is an interactive NBA analytics platform that organizes current and historical player, team, and game data into clear profiles and visualizations. The goal is to make NBA statistics easier to understand for casual fans and fantasy basketball players without requiring them to search across multiple websites or interpret large statistical tables.

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

## Application sections and current status

| Section | Planned purpose |
| --- | --- |
| Players | Search/select players; season and recent performance, percentiles, strengths/weaknesses and shot charts |
| Teams | Search/select teams; records, rankings, offensive/defensive efficiency and recent form |
| Compare | Two players or two teams; normalized metrics and interactive charts with fair comparison context |
| Trends | Rolling averages and recent-versus-season views that explain changes without overstating noise |

**Implemented now:** four-section Streamlit navigation with movable Week 1 Players/Teams placeholder blocks, independent component previews, an explicit local NBA snapshot command and clearly labeled fictional practice inputs, shared environment, local PostgreSQL with a reproducible fictional starter table, private admin/read-only credentials, checked backups/recovery and onboarding materials. **Planned:** application data collection, analytics, product charts and production NBA schemas/storage. The onboarding script has a separate optional API request for classroom practice. The synthetic backup is teaching material only.

## Selected tech stack

* **Environment:** Python 3.12 with one local `venv`.
* **Processing:** pandas and NumPy; **primary source:** `nba_api`.
* **Application and charts:** Streamlit and Plotly.
* **Onboarding:** a regular Python script; use any text editor.
* **Database:** local PostgreSQL in Docker Compose; supplied setup loads fictional starter data and configures backups. Production NBA schemas/ingestion remain planned.
* **Approved stretch work only:** scikit-learn and XGBoost (not installed).

Data flows from NBA API → Python/pandas → local cached data (eventually PostgreSQL) → analytics functions → Streamlit/Plotly. See [ARCHITECTURE.md](ARCHITECTURE.md) for boundaries, feature dependencies and the roadmap, and [DATA.md](DATA.md) for source restrictions. Existing secondary sources remain documented there; onboarding does not fetch them.

## Quick start

Install Python 3.12 and Git. For Deliverable 0 submissions, first create your member worktree from the PM-published integration branch using [Week 00](weekly/week0/week-00-onboarding.md#1-get-the-project-and-your-branch); install the environment there. From the chosen checkout root, first follow [the shared setup guide](docs/SETUP.md) for the local Python environment and required Docker/PostgreSQL check. The Python-only app commands on macOS/Linux are:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/verify_environment.py
python -m pip check
python -m streamlit run app.py
```

Open `http://localhost:8501` and use the sidebar. On Windows use `py -3.12 -m venv .venv` and `.\.venv\Scripts\Activate.ps1`, then the same `python` commands. See [Week 00](weekly/week0/week-00-onboarding.md) for cloning, the required database check and the first coding exercise.

After installing Docker and activating `.venv`, `python scripts/database.py setup` prepares the local database, generates private passwords, loads the same fictional data for everyone and installs daily backup checks. Use `python scripts/database.py status` to verify it, and `python scripts/database.py backup` for an immediate archive. [Setup and recovery](docs/SETUP.md#7-backups-and-recovery) explain restoration into a separate database and the limits of local backups. Each member's database is independent; future hosting provides shared data for the deployed application.

For the current development increment, use [Week 1: NBA data and visual prototypes](weekly/week1/week-01-player-team-prototypes.md): movable Players/Teams blocks, named TODO functions in the app modules and a personal brainstorming copy. These are teaching previews, not completed product profiles.

Browse the [weekly assignments](weekly/README.md), starting with [Deliverable 0](weekly/week0/week-00-onboarding.md) before the first meeting. Copy [weekly/week0/onboarding.py](weekly/week0/onboarding.py), run it with Python, and complete its TODOs using the prepared API request or synthetic backup.

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

Planned semester requirements (not implemented by this starter):

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
| [Development setup](docs/SETUP.md) | Local Python plus Docker/PostgreSQL installation, health/SQL verification, shutdown and troubleshooting. |
| [PostgreSQL Compose](compose.yaml) | One local database service with persistent storage; configure your private `.env` from [.env.example](.env.example). |
| [Database tools](scripts/database.py) | Provided setup/fixture loader, read-only application access, checked backups, scheduling and recovery; [starter schema](scripts/database.sql). |
| [Deliverable structure](weekly/deliverables_structure.md) | How assignments are created, proposed team responsibilities, Co-PM checks and submission. |
| [Weekly assignments](weekly/README.md) | Assignment index and reusable template; Week 0 uses Discord/PRs, future work uses GitHub Issues. |
| [Week 00 / Deliverable 0](weekly/week0/week-00-onboarding.md) | Complete individual pre-meeting assignment, setup and submission instructions. |
| [Architecture](ARCHITECTURE.md) | Product plan, module boundaries, MVP/later requirements and status. |
| [`src/`](src/) | Application data, analytics, charts and views; member names mark the current TODO functions. |
| [Onboarding script](weekly/week0/onboarding.py) | Start here for basic coding with prepared NBA API loading or synthetic backup. |
| [Verification script](scripts/verify_environment.py) | Offline environment and fixture smoke check. |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | **Start here.** Beginner terms, click-by-click Issue/PR guidance and the team contribution workflow. |
| [`DELIVERABLES.md`](DELIVERABLES.md) | Current project milestones and rough timeline. A living plan, not a contract.                                                                   |
| [`DATA.md`](DATA.md)                 | Selected data sources, how to access them, and guidelines for using them.                                                                       |
| [`data/`](data/)                     | Local working folder for datasets. **Git-ignored** — raw data is never committed.                                                               |
| [`AGENTS.md`](AGENTS.md)             | Machine-facing workflow rules for AI coding agents.                                                                                             |
| [`CODEOWNERS`](CODEOWNERS)           | **Team roster + review policy.** PMs, members, and the code-owner rule for PRs into `main`.                                                     |

## Team

The numbered member groups and current assignment links are in [the deliverable structure](weekly/deliverables_structure.md). [`CODEOWNERS`](CODEOWNERS) defines the repository review policy; PMs own the final integration-to-`main` review.

## Notes for PMs

This README, [`DELIVERABLES.md`](DELIVERABLES.md), and [`DATA.md`](DATA.md) describe the current project direction and should be updated when major scope, timeline, or technical decisions change.

## Notes for members

New to GitHub? Start with [the beginner terms and walkthrough](CONTRIBUTING.md#new-to-github). Follow the PM's Discord announcement and [Week 0](weekly/week0/week-00-onboarding.md); submit your individual PR into `deliverable0`. Week 0 does not require an Issue.
