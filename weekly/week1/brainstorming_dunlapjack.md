# Week 1 — Brainstorming — Jack Dunlap

Copy to `brainstorming_<github-handle>.md`; keep this template unchanged. Short bullets are enough: aim for 10–15 minutes of writing across the week. Link this in your component PR. Do not attach downloaded data or generated charts.

**Name / GitHub handle:** Jack Dunlap / dunlapjack
**Team number / file + function you are editing / page block:** Team 3 / `src/charts.py` → `team_efficiency()` / Teams page, "League efficiency" block (T3)

## Before Wednesday's meeting

- **Comparable tool + direct page URL:** Databallr (There is a "Matchup Matrix" tool under the "Compare" tab that has player vs player, per possession matchup data.) https://databallr.com/matchups/1628983/shai-gilgeous-alexander/1629029/luka-doncic/2024/2026 
- **Useful interaction/visual and the user question it answers:** Scatter plot to show recent FG % vs career or season, or shots vs pts: Who is overperforming vs underperforming? | Minutes vs. +/- scatter (minutes vs +/-): Who is getting too many/too few minutes? | Contract value scatter plot (+/- vs AAV): Who is worth their contract?/Which teams are getting a bargain? | Bar graph that shows team efficiency per quarter. Users can select a team, and will see the net rating for each quarter (green if positive, red if negative): Which teams are better each quarter (useful for live betting).
- **One improvement or original CourtIQ idea:** Under "Trends", upcoming matchups that have unique trends (ex: "This player is 5-0 against this team or player and they play tonight").
- **My component's rough sketch:** Scatterplot, one dot per team. X = offensive rating (right = better), Y = defensive rating reversed (up = better). Dotted league-average lines split it into four groups; the top right is "good at both". The selected team is a large red star labeled with its name; other teams are muted gray dots. Hover shows name, ORTG, DRTG and net rating.
- **One visual improvement:** Only the selected team gets color, a star shape and a name label, so it stands out even without color. The reversed y-axis puts every "better" direction toward the top right, so users don't have to remember that lower DRTG is better.
- **Data I need:** `TEAM_ID, TEAM_NAME, OFF_RATING, DEF_RATING, NET_RATING, SEASON` from NBA.com via `nba_api` (`python -m scripts.fetch_data ratings`), 2025-26 Regular Season. Ratings are points per 100 possessions. One row = one team's season.
- **Rules behind my result:** Display only. Teams missing either rating are left off the chart (not treated as zero). League-average lines are the mean of the plotted teams. If the table is empty or the selected team is unavailable, the function returns `None` so the app shows its "no result" message.
- **What my function receives → what it produces → where it belongs on the page:** Ratings table + selected `TEAM_ID` → Plotly scatter figure (or `None`) → Teams page "League efficiency" block, under the team selector.
- **One question or risk for the meeting:** Is reversing the defensive axis clear to users, or should we keep it normal and label "lower is better"? Should the app also show net rating (Michael's result) on hover once his checks are connected?

## After the meeting — shared plan, my contribution

- **Issue comment/link recording the team's agreed wireframe:** Unknown
- **What moves, gets larger, or changes in my block; why:** Unknown
- **Agreed column names and which component will use my result:** Teams -> League Efficiency
- **My new idea is:** Comparison feature, similar to the "Matchup Matrix" in the website linked above, that can analyze how players perform vs each other using advanced per possession defensive data. Useful for highlighting offensive-favored, defender-favored, new, historical, and unique matchups across the league.
- **Additional data/effort if we adopt that idea:** Find a source for the per possession data. Import this data and create a user-friendly visualization to make the data useful.

## Before my PR is reviewed

- **Real-data command/result and one descriptive observation:** `python -m scripts.preview_component team-chart --id 1610612760` → saved chart of all 30 teams (2025-26 Regular Season) with the Oklahoma City Thunder highlighted. Observation: the Thunder have the league's lowest defensive rating (106.5) and best net rating (+11.1), while Denver has the highest offensive rating (121.2). 12 teams are better than average on both sides and 10 are worse on both. This describes where teams sit; it doesn't explain why.
- **Unusual case checked** (e.g. missing value or empty table) **and expected/actual result:** (1) Unknown team ID `--id 999` → expected no chart; got `NO OUTPUT`. (2) Empty table → expected `None`; got `None`. (3) One team's DEF_RATING set to missing → expected that team to be left off and the other 29 plotted; got 29 points, and selecting the missing team returned `None`. The input table was unchanged afterward.
- **Teammate/component I reviewed; did its result fit what the next component needs? One finding:** TODO(Jack)
- **Remaining blocker or connection needed next week:** None blocking. On Windows, `fetch_data` saves the data but then crashes printing "→" (UnicodeEncodeError); setting `PYTHONUTF8=1` should avoid it (not retested, to avoid a second request). Next week: connect Michael's checked ratings to this chart.
