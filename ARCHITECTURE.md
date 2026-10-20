# CourtIQ application plan

## Purpose and audience

CourtIQ helps casual NBA fans and people comparing player/team performance understand basketball statistics through clear context and interactive charts. Core work is descriptive analytics. Forecasting and similar-player models are approved stretch work only.

## Current implementation status

Implemented in this starter: a runnable Streamlit navigation shell in [app.py](app.py), a shared local Python environment, PostgreSQL-only Docker Compose setup, a guided Python onboarding script with synthetic backup and a prepared optional NBA API request. The shell has **no completed product profiles or database connection**. Week 1 adds movable Players/Teams wireframe blocks and independently runnable member TODO functions in the shared `src/` application modules. A supplied explicit NBA snapshot command supports local exploration; the app only reads snapshots and never retrieves data on rerender. Practice inputs are clearly fictional. Member calculations/charts remain unfinished until reviewed. The separate database now has a reproducible fictional starter table, strong private credentials, read-only application access, checked local backups and recovery tools. Production NBA schemas/ingestion remain planned, as does everything in the feature table below. The onboarding chart is a student exercise, not an application feature. Week 1 component previews likewise do not establish finished profiles or a production pipeline. Backup results are explicitly fictional; API results identify NBA.com as their source.

## Navigation and requirements

| Section | First usable slice (MVP) | Later core functionality | Requirements and dependencies |
| --- | --- | --- | --- |
| Players | Search/select a player, display one season's clearly labeled basic per-game statistics and recent game log | League percentiles, contextual strengths/weaknesses, shot charts, season filters and recent 5/10/20-game views | Stable player IDs, season tables, game dates and units; percentiles require a defined eligible league population; shot charts require coordinates and court conventions |
| Teams | Search/select a team, show record and recent results with basic statistical charts | League rankings, offensive/defensive efficiency, shot distribution and period filters | Team IDs, season records and game logs; efficiency needs documented possession/pace definitions |
| Compare | Two players or two teams in the same period; normalized metrics and an interactive chart | Broader metric sets, season/recent-period filters and richer contextual explanations | Reuse profile calculations; never mix teams and players; same units, eligible population and periods; explain pace, minutes and sample size |
| Trends | Dated performance series with a rolling average and recent-versus-season summary | 5/10/20-game controls and more carefully evaluated change explanations | Ordered game logs, documented rolling windows, minimum observations and missing-game handling; do not label normal noise as a causal or significant change |

MVP means the first integrated usable slice, **not a reduction of the existing semester requirements**. Later core items remain in [DELIVERABLES.md](DELIVERABLES.md). All pages must expose metric definitions, units, period and data freshness; empty/missing/stale data must have readable explanations. Avoid fabricated values and ambiguous rankings. Student proposals inform design discussion and require PM approval before entering scope.

## Data flow

```text
NBA API (nba_api; source permissions checked before retrieval)
  → Python/pandas collection and cleaning
  → ignored local cached data (raw → interim → processed)
  → analytics functions
  → Streamlit UI + Plotly charts

Later: processed tables → PostgreSQL → analytics functions → UI
```

Local cached tables support development; PostgreSQL runs locally in Docker Compose during Week 0. [scripts/database.py](scripts/database.py) prepares the same versioned fictional table for each member and provides admin loading, read-only application access, backups and recovery. Local databases do not synchronize. Production NBA schemas, source-approved ingestion and app integration remain future milestones 2 and 7; the final deployed app can use hosted PostgreSQL after that work is reviewed. The onboarding script loads its synthetic backup or makes one bounded NBA request for private classroom practice; this separate exercise never feeds product pages. API network requests must not run on every Streamlit rerender. Future collection should have bounded timeouts, conservative request rates, cache timestamps and visible failure handling, after source review in [DATA.md](DATA.md).

## Responsibility boundaries and suggested structure

Use plain Python functions and DataFrames first. Create future modules only as their features are assigned; do not add empty packages now.

```text
app.py                         # implemented navigation + placeholders
requirements.txt               # implemented local Python environment
compose.yaml                   # implemented PostgreSQL service and named volume
.env.example                   # shared empty-password settings; .env stays private
docs/SETUP.md                  # local Python + Docker database setup instructions
scripts/database.py            # provided fictional loader, credentials, backup/schedule/recovery
scripts/database.sql           # fictional starter table; production schemas remain planned
scripts/verify_environment.py  # implemented offline verification
weekly/week0/onboarding.py           # implemented guided script; student TODOs unanswered
weekly/week0/player_stats_backup.csv # fictional teaching data
weekly/week1/                  # assignment guide, personal brainstorming template and PM notes
weekly/                        # assignment index and reusable template
src/data.py                # snapshot I/O, shared input shapes; Aiden/Ignacio/Andrew TODOs
src/analytics.py           # deterministic percentile/rating calculations; Sri/Michael TODOs
src/charts.py              # Plotly figures from supplied tables; Jason/Jack TODOs
src/views.py               # Streamlit profile display; June/Casey TODOs
scripts/fetch_data.py          # explicit bounded NBA snapshot collection, outside the UI
scripts/preview_component.py   # run an app function independently against local/practice input
scripts/check_starter.py       # offline snapshot/cache checks; not student completion
data/raw/, interim/, processed/ # ignored local NBA responses and derived tables
```

For Week 1, each member owns a named TODO function in a shared application module. Supplied table shapes allow independent previews without calling another unfinished function. Students edit only their function body and a personal brainstorming copy; module imports, shared helpers and page wiring stay PM-owned. Cemal consolidates validated components and handles shared-file merge conflicts. The package now holds the assigned application components; production ingestion and database schemas remain future work.

Collection owns endpoint parameters, IDs, units and freshness. Analytics receives tables, documents formulas/cohorts and does not fetch data or render UI. Charts receive analytics outputs and label axes/periods. UI owns navigation, user inputs, empty states and explanatory context; it does not duplicate formulas. Approved calculations from onboarding move to ordinary functions for testing and reuse. Schema naming and database design are later review decisions, not silently fixed by this suggested structure.

## Feature dependencies and roadmap

**Date inconsistency:** the historical dates below and DELIVERABLES.md's ASCII timeline conflict with its milestone table. They are not current weekly deadlines. The [Week 1 assignment](weekly/week1/week-01-player-team-prototypes.md) sets the Oct 21 design meeting, Oct 24 PR deadline, Oct 25 review target and Oct 26 next-assignment target. Other milestones are not silently rescheduled.

| Milestone | Contribution to application | Gate before moving forward |
| --- | --- | --- |
| 0 — Before first meeting (PM sets date) | Each member sets up local Python, verifies Docker/PostgreSQL and completes a small API/backup-data exercise | Individual script reviewed; Python, database health/SELECT 1 and chart checks summarized in the PR |
| 1 — Sept 26–Oct 4 | Scope, shell, architecture and working agreements | PM reviews this starter; planning dates retained rather than assumed completed |
| 2 — Oct 5–Oct 16 | Common player/team/game tables, cache policy and planned storage | Verify source permission, units, IDs and data quality before retrieval |
| 3 & 4 — Oct 17–Nov 6 | Players and Teams profile slices plus later core profile requirements | Depend on milestone 2; share validated definitions |
| 5 & 6 — Nov 7–Nov 20 | Compare and Trends, recent-period controls | Reuse profiles/game logs; review normalization, cohorts and noise interpretation |
| 7 — Nov 21–Nov 29 | Connect all sections, storage and error states | Integrated workflow and reproducible refresh |
| 8 — Nov 30–Dec 6 | Quality checks, usability, release and demo | Test calculations, freshness, missing data and communication |

These are planning dates, not claims that earlier work is finished. PMs update actual scheduling rather than this starter arbitrarily shifting deadlines. Docker runs only PostgreSQL. Python, any locally used Jupyter and Streamlit stay in venv; production NBA schemas/ingestion, ML and application-user authentication remain deferred. Local database credentials and read-only permissions are implemented. Backups stay outside the database volume but on the same computer; [recovery instructions](docs/SETUP.md#7-backups-and-recovery) document that limitation.
