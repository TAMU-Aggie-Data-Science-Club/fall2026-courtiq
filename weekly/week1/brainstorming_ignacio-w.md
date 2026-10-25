# Week 1 — Brainstorming — Ignacio Wijatno

Copy to `brainstorming_<github-handle>.md`; keep this template unchanged. Short bullets are enough: aim for 10–15 minutes of writing across the week. Link this in your component PR. Do not attach downloaded data or generated charts.

**Name / GitHub handle:** Ignacio Wijatno (ignacio-w)
**Team number / file + function you are editing / page block:** Team 1 / data.clean_players / Players?

## Before Wednesday's meeting

- **Comparable tool + direct page URL:** https://courtsketch.com/stat-win-rate
- **Useful interaction/visual and the user question it answers:**
    - Shows on average how important out performing your opponent in a particular stat is in the outcome of a game
    - Answers "How has the recipe for winning a game evolved over time?"
- **One improvement or original CourtIQ idea:** 
    - Historical Stat Impact Trendlines (Later Candidate): A multi-decade macro chart tracking win-rate correlations of key metrics (like 3-point volume vs. turnovers) from the 1980s to today to visualize the modern analytics revolution, paired with a complete season-by-season correlation ranking table.
    - In the future, an option to toggle between a League Macro View and Team-Specific View (single-team historical performance vs. league average) or just another chart/table
- **My component's rough sketch:** use a few text boxes/arrows or a brief layout description.
    - The sketch below is my later-candidate idea; its numbers and strength labels are illustrative, not measured results or approved thresholds.
```text
[ Stat Multiselect: [ TS% ] [ 3P% ] [ TOV ] ]  [ Season Slider: [ 2024-25 ] ]
┌────────────────────────────────────────────────────────────────────────┐
│  Historical Stat Impact Trendline (Win Correlation vs. Season)         │
│                                                                        │
│   1.0 +                                              /                 │
│       |                                       ┌──────────────────────┐ │
│   0.5 +                                  ────►│ Season: 2024         │ │
│       |                    ───────────        │ • TS%: +0.68         │ │
│   0.0 +───────────────────────────────────────│ • 3P%: +0.55         │ │
│       1980            1990            2000    └──────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│  Season Win-Correlation Ranking (Most Positive to Most Negative)       │
│  ┌──────────────────────────┬──────────────────┬────────────────────┐  │
│  │ Statistic                │ Win Correlation  │ Impact Type        │  │
│  ├──────────────────────────┼──────────────────┼────────────────────┤  │
│  │ 1. True Shooting % (TS%) │ +0.68 (Highlighted)│ Strong Positive  │  │
│  │ 2. Three-Point % (3P%)   │ +0.55 (Highlighted)│ Strong Positive  │  │
│  │ 3. Rebounding Diff.      │ +0.42            │ Moderate Positive  │  │
│  │ ...                      │ ...              │ ...                │  │
│  │ 10. Turnovers (TOV)      │ -0.52 (Highlighted)│ Strong Negative  │  │
│  └──────────────────────────┴──────────────────┴────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```
- **One visual improvement:**
    - Showing all core stats ranked from most positive to most negative correlation in the summary table while highlighting/pinning the user's active line-chart selections gives both immediate macro-ranking context and clear focused tracking without cluttering the screen
    - Coloring the statistics in the summary table to show the strength of correlation allows user to see most impactful factors at a glance
- **Data I need:** Historical team-game logs over multiple decades (1980–present), including season, game/team/opponent identifiers, traditional and available advanced box-score statistics, and final win/loss outcomes. Coverage and source permissions need review before choosing the available seasons and metrics.
- **Rules behind my result:**
    - Match each team's statistics to its opponent in the same game, then calculate season-by-season correlations between stat differentials and win/loss outcomes. These describe associations, not causal effects; the exact method and handling of missing historical statistics need investigation.
- **What my function receives → what it produces → where it belongs on the page:**
    - The proposed component receives historical team-game statistics and outcomes, plus the selected metrics and season range. It produces correlation values by season and metric for the trendlines and a ranked summary for the selected season. It could belong in Trends, with the metric controls above the chart and the ranking table below; placement is not yet confirmed.
- **One question or risk for the meeting:** How should we handle missing play-by-play or advanced stat tracking for older eras (e.g., pre-1990s 3-point volume or tracking data)?

## After the meeting — shared plan, my contribution

- **Issue comment/link recording the team's agreed wireframe:**
    - Nothing
- **What moves, gets larger, or changes in my block; why:**
    - Proposed layout, pending meeting confirmation: give the historical trendline chart the main space in a Trends block, place metric/season controls above it, and put the season ranking table underneath. This would show changes over time alongside the selected season's context. No layout change is confirmed here.
- **Agreed column names and which component will use my result:**
    - Exact column names and meeting agreement are unconfirmed. Proposed result fields describe the season, statistic, correlation coefficient, and number of games used. The trendline chart would use the season-by-statistic results; the ranking table would use the selected season's results. These are proposed field meanings, not a finalized schema.
- **My new idea is:** The stat correlation idea above.
- **Additional data/effort if we adopt that idea:**
    - Check historical game-log coverage and source permissions with PMs, match opponents within games, define comparable metrics across eras, and agree on the correlation method and missing-data treatment before building trendlines and the ranking table. The optional team-specific view would also need enough games per team/season for meaningful comparisons.

## Before my PR is reviewed

- **Real-data command/result and one descriptive observation:** 
    - *Command:* `python -m scripts.preview_component clean-players`
    - *Verification:* An in-memory check confirmed 582 rows: input shape (582, 6), output shape (582, 7). No preview export was needed for this check.
    - *Observation:* Cleaning preserved all 582 player rows, added SEASON, and renamed the already averaged statistics to explicit per-game fields. The original raw DataFrame remained unchanged.
- **Unusual case checked** (e.g. missing value or empty table) **and expected/actual result:** 
    - *Checked:* Missing PLAYER_ID, duplicate PLAYER_ID, and a missing AST value using fictional practice inputs.
    - *Expected/actual:* Missing and duplicate IDs each raised ValueError as expected. Missing AST stayed missing in AST_PER_GAME; no zero was inserted.
- **Teammate/component I reviewed; did its result fit what the next component needs? One finding:** 
    - In my review of Jack's team-efficiency scatterplot, we discussed whether to flip the y-axis; I suggested keeping its current orientation. The chart should state that lower defensive rating is better. Its intended input is the team ratings table, separate from my player cleaner.
- **Remaining blocker or connection needed next week:** 
    - Connect the reviewed player cleaner to the Players summary, percentiles, and scoring distribution; the preview currently runs these independently. Confirm the agreed wireframe/comment link and keep historical trendlines as a later candidate until scope and data feasibility are reviewed.
