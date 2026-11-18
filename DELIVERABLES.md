# Deliverables & Timeline

> **How to read this file.** This is the PMs' best current estimate of what CourtIQ needs to ship and roughly when. It is a **living plan, not a contract**. Future task tracking lives in **GitHub Issues and the Project board**. Week 0 uses the PM's Discord announcement and reviewed PRs into `deliverable0`.

This file is the high-level semester roadmap. Detailed weekly instructions live in the [weekly assignment index](weekly/README.md). [The deliverable structure](weekly/deliverables_structure.md) describes creation, proposed team responsibilities and review. Individual GitHub Issues remain authoritative for owners, task status, deadlines and changes; weekly documents explain the work and link to those issues. Week 0 requires no Issue; its deadline/updates are announced in Discord and individual submissions are reviewed through PRs into `deliverable0`.

## Milestones

| # | Deliverable                          | Description                                                                                                                                                                                                                     | Owner (role)        | Target        |
| - | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------- |
| 0 | Technical onboarding | [Local Python, required Docker/PostgreSQL setup and a small Python exercise](weekly/week0/week-00-onboarding.md), using a prepared NBA API request or synthetic backup. The supplied fictional table/loader and health/SELECT 1 check prepare everyone for later storage work; production schemas and NBA ingestion remain deferred. | Each member + PM review | Before first meeting |
| 1 | Project setup and architecture       | Finalize project scope, team roles, data sources, GitHub workflow, development tools, application architecture, and shared data format.                                                                                         | PM + Co-PM | Oct 14-21 |
| 2 | Data foundation                      | Build a reproducible data pipeline using primary `nba_api`, with existing secondary/historical sources only after permission review. Clean and organize player, team, and game data into the shared database and provide sample datasets for development. | Members             | Oct 14-21  |
| 3 | Player profile MVP                   | Build searchable player profiles displaying season statistics, recent performance, league percentiles, strengths and weaknesses, shot charts, and interactive performance visualizations.                                       | Members             | Oct 21-Nov 6  |
| 4 | Team profile MVP                     | Build searchable team profiles displaying records, league rankings, offensive and defensive performance, recent form, and efficiency or shot-distribution visualizations.                                                       | Members             | Oct 21–Nov 6  |
| 5 | Comparisons and recent-form analysis | Allow users to compare players or teams using normalized statistics and interactive visualizations. Add filters for season and recent periods such as the last 5, 10, or 20 games.                                              | Members             | Nov 7–Nov 20  |
| 6 | Trend detection                      | Identify meaningful changes in player and team performance over time and display the statistics and visualizations behind those changes.                                                                                        | Members             | Nov 7–Nov 20  |
| 7 | Integration and feature completion   | Connect the data pipeline, database, player profiles, team profiles, comparison tools, and visualizations into one functional Streamlit application. Resolve missing requirements and integration issues.                       | Members + PM        | Nov 21–Nov 29 |
| 8 | Final release                        | Test calculations and data quality, handle missing or outdated data, improve usability, deploy the application, and prepare the final presentation/demo.                                                                        | PM + Members        | Nov 30–Dec 6  |

## Implementation status and section dependencies

The starter implements local environment/setup materials, a PostgreSQL-only Compose service with a supplied fictional table/loader, private admin/read-only credentials, checked local backups/recovery, Deliverable 0, and a four-section navigation shell. This foundation gives members the same starting data and a recovery path without making schema implementation a Week 0 task. Production NBA collection, production schemas/ingestion and all product analytics/visualizations remain planned; no milestone is considered complete solely because its target date has passed.

The [current Week 1 assignment](weekly/week1/week-01-player-team-prototypes.md), tracked in [Issue #11](https://github.com/TAMU-Aggie-Data-Science-Club/fall2026-courtiq/issues/11), requires bounded **real NBA data EDA**, cleanup and independent player/team components by **Oct 24, 11:59 PM Central**. Its snapshot collector and preview scaffolding are implemented; member TODOs remain unfinished. This weekly slice starts work across the milestones without assigning the full data foundation or database ingestion. The milestone dates above and historical ASCII dates below conflict; they are retained for PM review and are not the current weekly deadline.

Players maps to milestone 3; Teams to 4; Compare to 5; Trends to 6. All depend on milestone 2's validated data and metric definitions, and come together in 7–8. [ARCHITECTURE.md](ARCHITECTURE.md) separates the first usable slices from later core requirements without dropping the semester scope.

Deliverable 0 is a pre-meeting prerequisite, not a rescheduling of milestones 1–8. Their existing targets are retained; the PM sets the meeting/submission date in Discord and tracks Week 0 completion through reviewed PRs. Future deliverables use Issues and the board.

## Stretch Deliverables

These features should only begin if the core application is ahead of schedule:

| Deliverable                    | Description                                                                                                                  |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| Similar-player search          | Find current or historical NBA players with similar statistical profiles and play styles.                                    |
| Player performance forecasting | Predict upcoming player performance using recent form, opponent, schedule, and other available features.                     |
| Game outcome prediction        | Build an introductory model for forecasting NBA game outcomes and explain the most important factors behind each prediction. |

## Timeline (rough)

Onboarding (0): before the first meeting, exact date set by PM; prepares the team for setup and data work below. Existing semester date estimates are unchanged.

```text
Date:        Sep 26   Oct 5    Oct 17   Nov 7    Nov 21   Nov 30   Dec 6
             |--------|---------|---------|---------|---------|--------|

Setup        ████████

Data                  ███████████

Profiles                          ███████████████████

Compare/Trends                                      █████████████

Integration                                                       ████████

Final Release                                                               ███████
```

## Working agreements

* **Future deliverables map to one or more GitHub Issues.** Week 0 is the approved Discord/PR exception. This file remains the semester summary.
* **Dates are estimates.** When reality diverges, update the Issue (Discord for Week 0) and this file if the shift is material.
* **"Done" follows acceptance criteria** in the assignment or Issue, not a date passing.
* **Reprioritize openly.** If a deliverable changes, a PM records why in the Issue (Discord for Week 0) so the decision is auditable.
* **Core features come before stretch features.** Prediction and machine-learning work should not begin at the expense of completing the player, team, comparison, and trend-analysis requirements.
