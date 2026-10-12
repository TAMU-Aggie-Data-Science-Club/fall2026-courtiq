# Deliverables & Timeline

> **How to read this file.** This is the PMs' best current estimate of what CourtIQ needs to ship and roughly when. It is a **living plan, not a contract**. The authoritative picture lives in **GitHub Issues and the Project board**.

This file is the high-level semester roadmap. Detailed weekly instructions live in the [weekly assignment index](weekly/README.md). Individual GitHub Issues remain authoritative for owners, task status, deadlines and changes; weekly documents explain the work and link to those issues.

## Milestones

| # | Deliverable                          | Description                                                                                                                                                                                                                     | Owner (role)        | Target        |
| - | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------- |
| 0 | Technical onboarding and product exploration | [Individual 1–2 hour assignment](weekly/week-00-onboarding.md) for all nine members: shared environment, synthetic-data notebook and one proposal each, to prepare the first meeting without requiring live API access. | Each member + PM review | Before first meeting; PM sets date |
| 1 | Project setup and architecture       | Finalize project scope, team roles, data sources, GitHub workflow, development tools, application architecture, and shared data format.                                                                                         | PM + Technical Lead | Sept 26–Oct 4 |
| 2 | Data foundation                      | Build a reproducible data pipeline using primary `nba_api`, with existing secondary/historical sources only after permission review. Clean and organize player, team, and game data into the shared database and provide sample datasets for development. | Members             | Oct 5–Oct 16  |
| 3 | Player profile MVP                   | Build searchable player profiles displaying season statistics, recent performance, league percentiles, strengths and weaknesses, shot charts, and interactive performance visualizations.                                       | Members             | Oct 17–Nov 6  |
| 4 | Team profile MVP                     | Build searchable team profiles displaying records, league rankings, offensive and defensive performance, recent form, and efficiency or shot-distribution visualizations.                                                       | Members             | Oct 17–Nov 6  |
| 5 | Comparisons and recent-form analysis | Allow users to compare players or teams using normalized statistics and interactive visualizations. Add filters for season and recent periods such as the last 5, 10, or 20 games.                                              | Members             | Nov 7–Nov 20  |
| 6 | Trend detection                      | Identify meaningful changes in player and team performance over time and display the statistics and visualizations behind those changes.                                                                                        | Members             | Nov 7–Nov 20  |
| 7 | Integration and feature completion   | Connect the data pipeline, database, player profiles, team profiles, comparison tools, and visualizations into one functional Streamlit application. Resolve missing requirements and integration issues.                       | Members + PM        | Nov 21–Nov 29 |
| 8 | Final release                        | Test calculations and data quality, handle missing or outdated data, improve usability, deploy the application, and prepare the final presentation/demo.                                                                        | PM + Members        | Nov 30–Dec 6  |

## Implementation status and section dependencies

The starter implements environment/setup materials, Deliverable 0, and a four-section navigation shell. NBA collection, database storage and all product analytics/visualizations remain planned; no milestone is considered complete solely because its target date has passed.

Players maps to milestone 3; Teams to 4; Compare to 5; Trends to 6. All depend on milestone 2's validated data and metric definitions, and come together in 7–8. [ARCHITECTURE.md](ARCHITECTURE.md) separates the first usable slices from later core requirements without dropping the semester scope.

Deliverable 0 is a pre-meeting prerequisite, not a rescheduling of milestones 1–8. Their existing targets are retained; the PM sets the meeting/submission date in the [proposed issue](docs/ONBOARDING_ISSUE.md) and reconciles actual progress with the board.

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

* **Each deliverable maps to one or more GitHub Issues.** The board is the source of truth; this file is the summary.
* **Dates are estimates.** When reality diverges, update the issue and this file if the shift is material.
* **"Done" is defined per issue** via acceptance criteria — not by a date passing.
* **Reprioritize openly.** If a deliverable changes, a PM notes why in the issue so the decision is auditable.
* **Core features come before stretch features.** Prediction and machine-learning work should not begin at the expense of completing the player, team, comparison, and trend-analysis requirements.
