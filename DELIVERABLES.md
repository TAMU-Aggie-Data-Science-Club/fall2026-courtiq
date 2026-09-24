# Deliverables & Timeline

> **How to read this file.** This is the PMs' best current estimate of what CourtIQ needs to ship and roughly when. It is a **living plan, not a contract**. The authoritative picture lives in **GitHub Issues and the Project board**.

## Milestones

| # | Deliverable                          | Description                                                                                                                                                                                                                     | Owner (role)        | Target        |
| - | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------- |
| 1 | Project setup and architecture       | Finalize project scope, team roles, data sources, GitHub workflow, development tools, application architecture, and shared data format.                                                                                         | PM + Technical Lead | Sept 26–Oct 4 |
| 2 | Data foundation                      | Build a reproducible data pipeline using `nba_api`, Basketball-Reference, and approved historical sources. Clean and organize player, team, and game data into the shared database and provide sample datasets for development. | Members             | Oct 5–Oct 16  |
| 3 | Player profile MVP                   | Build searchable player profiles displaying season statistics, recent performance, league percentiles, strengths and weaknesses, shot charts, and interactive performance visualizations.                                       | Members             | Oct 17–Nov 6  |
| 4 | Team profile MVP                     | Build searchable team profiles displaying records, league rankings, offensive and defensive performance, recent form, and efficiency or shot-distribution visualizations.                                                       | Members             | Oct 17–Nov 6  |
| 5 | Comparisons and recent-form analysis | Allow users to compare players or teams using normalized statistics and interactive visualizations. Add filters for season and recent periods such as the last 5, 10, or 20 games.                                              | Members             | Nov 7–Nov 20  |
| 6 | Trend detection                      | Identify meaningful changes in player and team performance over time and display the statistics and visualizations behind those changes.                                                                                        | Members             | Nov 7–Nov 20  |
| 7 | Integration and feature completion   | Connect the data pipeline, database, player profiles, team profiles, comparison tools, and visualizations into one functional Streamlit application. Resolve missing requirements and integration issues.                       | Members + PM        | Nov 21–Nov 29 |
| 8 | Final release                        | Test calculations and data quality, handle missing or outdated data, improve usability, deploy the application, and prepare the final presentation/demo.                                                                        | PM + Members        | Nov 30–Dec 6  |

## Stretch Deliverables

These features should only begin if the core application is ahead of schedule:

| Deliverable                    | Description                                                                                                                  |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| Similar-player search          | Find current or historical NBA players with similar statistical profiles and play styles.                                    |
| Player performance forecasting | Predict upcoming player performance using recent form, opponent, schedule, and other available features.                     |
| Game outcome prediction        | Build an introductory model for forecasting NBA game outcomes and explain the most important factors behind each prediction. |

## Timeline (rough)

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
