# Week 1 — Brainstorming — Ignacio Wijatno

Copy to `brainstorming_<github-handle>.md`; keep this template unchanged. Short bullets are enough: aim for 10–15 minutes of writing across the week. Link this in your component PR. Do not attach downloaded data or generated charts.

**Name / GitHub handle:** Ignacio Wijatno (ignacio-w)
**Team number / file + function you are editing / page block:** Team 1 / data.clean_players / Players

## Before Wednesday's meeting

- **Comparable tool + direct page URL:** https://courtsketch.com/stat-win-rate
- **Useful interaction/visual and the user question it answers:**
    - Shows on average how important out performing your opponent in a particular stat is in the outcome of a game
    - Answers "How has the recipe for winning a game evolved over time?"
- **One improvement or original CourtIQ idea:** 
    - Historical Stat Impact Trendlines (Later Candidate): A multi-decade macro chart tracking win-rate correlations of key metrics (like 3-point volume vs. turnovers) from the 1980s to today to visualize the modern analytics revolution, paired with a complete season-by-season correlation ranking table.
    - In the future, an option to toggle between a League Macro View and Team-Specific View (single-team historical performance vs. league average) or just another chart/table
- **My component's rough sketch:** use a few text boxes/arrows or a brief layout description.
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
- **Data I need:** Historical team-game logs over multiple decades (1980–present), tracking traditional/advanced box-score differentials and final win/loss outcomes
- **Rules behind my result:** Season-by-season correlation coefficients calculated across league games to measure how strongly outperforming an opponent in a given metric predicts a win.
- **What my function receives → what it produces → where it belongs on the page:**
- **One question or risk for the meeting:** How should we handle missing play-by-play or advanced stat tracking for older eras (e.g., pre-1990s 3-point volume or tracking data)?

## After the meeting — shared plan, my contribution

- **Issue comment/link recording the team's agreed wireframe:**
- **What moves, gets larger, or changes in my block; why:**
- **Agreed column names and which component will use my result:**
- **My new idea is:** this week's approved scope / later candidate / needs investigation.
- **Additional data/effort if we adopt that idea:**

## Before my PR is reviewed

- **Real-data command/result and one descriptive observation:** 
    - *Command:* `python -m scripts.preview_component clean-players`
    - *Observation:* Successfully loaded the raw player snapshot, converted statistics to numeric types, and outputted a clean player table with 400+ rows containing standardized per-game averages and IDs.
- **Unusual case checked** (e.g. missing value or empty table) **and expected/actual result:** 
    - *Checked:* Missing player ID (if an id was None/null) and duplicate player ID
    - *Result:* The component successfully handles the missing player IDs and duplicate player IDs by throwing a ValueError
- **Teammate/component I reviewed; did its result fit what the next component needs? One finding:** 
    - (haven't done it yet)
- **Remaining blocker or connection needed next week:** 
    - Nothing
