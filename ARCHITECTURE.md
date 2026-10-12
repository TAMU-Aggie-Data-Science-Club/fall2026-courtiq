# CourtIQ application plan

## Purpose and audience

CourtIQ helps casual NBA fans and people comparing player/team performance understand basketball statistics through clear context and interactive charts. Core work is descriptive analytics. Forecasting and similar-player models are approved stretch work only.

## Current implementation status

Implemented in this starter: a runnable Streamlit navigation shell in [app.py](app.py), a shared Python environment, an offline synthetic teaching fixture and a guided notebook. The shell has **no data retrieval, calculations, charts or database**. Everything in the feature table below is planned. The onboarding chart is a student exercise using fictional data, not a product feature.

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

Initially, local cached tables support development without adding a running database requirement. PostgreSQL remains the planned shared structured store for the semester; integration is tracked with milestones 2 and 7 and is not implemented in this setup. The offline synthetic fixture follows a separate teaching path straight to pandas; it never feeds product pages. API network requests must not run on every Streamlit rerender. Future collection should have bounded timeouts, conservative request rates, cache timestamps and visible failure handling, after source review in [DATA.md](DATA.md).

## Responsibility boundaries and suggested structure

Use plain Python functions and DataFrames first. Create future modules only as their features are assigned; do not add empty packages now.

```text
app.py                         # implemented navigation + placeholders
requirements.txt               # implemented shared environment
scripts/verify_environment.py  # implemented offline verification
notebooks/00_onboarding.ipynb   # implemented guided experiment, TODOs unanswered
tests/fixtures/                # implemented fictional teaching data
docs/                          # implemented setup, assignment and issue draft

# Planned as later issues, not present yet:
courtiq/data.py                 # collection, source schema, cleaning, local I/O
courtiq/analytics.py            # deterministic calculations on supplied tables
courtiq/charts.py               # Plotly figures from calculated tables
courtiq/views.py                # Streamlit selection, filters, explanations
scripts/fetch_data.py           # explicit collection entry point after source review
data/raw/, interim/, processed/ # ignored local NBA responses and derived tables
```

Collection owns endpoint parameters, IDs, units and freshness. Analytics receives tables, documents formulas/cohorts and does not fetch data or render UI. Charts receive analytics outputs and label axes/periods. UI owns navigation, user inputs, empty states and explanatory context; it does not duplicate formulas. Notebooks are exploratory; approved calculations move to ordinary functions for testing and reuse. Schema naming and database design are later review decisions, not silently fixed by this suggested structure.

## Feature dependencies and roadmap

| Milestone | Contribution to application | Gate before moving forward |
| --- | --- | --- |
| 0 — Before first meeting (PM sets date) | Each member installs tools, explores synthetic data and proposes one idea | Executed individual notebook, verification evidence and proposal reviewed |
| 1 — Sept 26–Oct 4 | Scope, shell, architecture and working agreements | PM reviews this starter; planning dates retained rather than assumed completed |
| 2 — Oct 5–Oct 16 | Common player/team/game tables, cache policy and planned storage | Verify source permission, units, IDs and data quality before retrieval |
| 3 & 4 — Oct 17–Nov 6 | Players and Teams profile slices plus later core profile requirements | Depend on milestone 2; share validated definitions |
| 5 & 6 — Nov 7–Nov 20 | Compare and Trends, recent-period controls | Reuse profiles/game logs; review normalization, cohorts and noise interpretation |
| 7 — Nov 21–Nov 29 | Connect all sections, storage and error states | Integrated workflow and reproducible refresh |
| 8 — Nov 30–Dec 6 | Quality checks, usability, release and demo | Test calculations, freshness, missing data and communication |

These are the existing planning dates, not claims that earlier work is finished. The current date may be past a target; PMs update actual scheduling through issues rather than this starter arbitrarily shifting deadlines. No ML packages, authentication, Docker or database implementation are part of this change.
