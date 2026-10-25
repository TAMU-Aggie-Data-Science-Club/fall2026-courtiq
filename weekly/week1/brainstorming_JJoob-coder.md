# Week 1 — Brainstorming — Your Name

Copy to `brainstorming_<github-handle>.md`; keep this template unchanged. Short bullets are enough: aim for 10–15 minutes of writing across the week. Link this in your component PR. Do not attach downloaded data or generated charts.

**Name: Jason K. / GitHub handle: JJoob-coder**
**Team number: #11 / chart.py + player_scoring_distribution() / page block:**

## Before Wednesday's meeting

- **Comparable tool + direct page URL:**
 * Basketball-Reference player stats page
- **Useful interaction/visual and the user question it answers:**
 * The stats table puts a player’s per-game numbers next to the rest of the league, which answers “how does this player compare with the rest of the league?”
- **One improvement or original CourtIQ idea:**
 * Currently still thinking of some

- **My component's rough sketch:** use a few text boxes/arrows or a brief layout description.

   * Title and subtitle (season, player count) -> histogram of points per game in muted gray bars -> red dashed line plus name label for the selected player -> dotted gray league-average line -> legend below the chart


- **One visual improvement:** 
   * Muted all bars to gray and made the selected player the only red element, so the eye goes straight to where they sit in the league instead of scanning every bar.
- **Data I need:** exact column names, where they come from, season/period, units, and what one row represents.
   * Columns: PLAYER_ID, PLAYER_NAME, GP, PTS_PER_GAME, SEASON
   * Source: NBA.com via nba_api (LeagueDashPlayerStats)
   * Period: 2025-26 Regular Season
   * Units: points per game, already averaged
   * One row: one player’s season

- **Rules behind my result:** who is included, how the calculation works, and what happens with equal or missing values; write “display only” if no calculation.
    * Only used players who played 20 or more games during the 2025-2026 NBA season and had non-missing PPG(points per game). If a selected player is unknown or ineligible the chart 

- **What my function receives → what it produces → where it belongs on the page:**
   *  player_scoring_distribution() takes in a player table and a player_id, and produces a histogram modeling the distribution of the number of players and the average amount of points they scored during the 2025-26 season. This feature will be on the front page of the player section of courtiq, speicifically under the highlight section.
- **One question or risk for the meeting:**
* Don't have any right now.

## After the meeting — shared plan, my contribution

- **Issue comment/link recording the team's agreed wireframe:**
    * Did not attend team Issue meeting.

- **What moves, gets larger, or changes in my block; why:**
   * The chart is dynamic and as the this NBA season continues on the chart will be constantly be changing based on the new data it recieves.

- **Agreed column names and which component will use my result:**
   * PLAYER_ID, PLAYER_NAME, GP, PTS_PER_GAME, REB_PER_GAME, AST_PER_GAME, SEASON

- **My new idea is:** this week's approved scope / later candidate / needs investigation.
   * Currently still thinking of new ideas to add 

- **Additional data/effort if we adopt that idea:**
   *N/A

## Before my PR is reviewed

- **Real-data command/result and one descriptive observation:** 
   * Used python -m scripts.preview_component player-chart --id [ID] to test cases of the output.
   * Observation: Higher PPG averages drop off after about 14 points per-game.

- **Unusual case checked** (e.g. missing value or empty table) **and expected/actual result:**
   * Ran --id 999999999, expected NO OUTPUT; result was NO OUTPUT.
- **Teammate/component I reviewed; did its result fit what the next component needs? One finding:**
   * I have not entirely reviewed my teams componets, however I was able to look at Jack's final results for his graph
- **Remaining blocker or connection needed next week:**

   * The chart isn’t connected to June’s player selector yet.