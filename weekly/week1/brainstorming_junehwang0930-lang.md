# Week 1 — Brainstorming — June Hwang
**Name / GitHub handle: **June Hwang / junehwang0930-lang


**Team number / file + function you are editing / page block:

 Team 2 / src/views.py / render_player_profile() / Players page - Player selection and season summary**

## Before Wednesday's meeting

- **Comparable tool + direct page URL: NBA.com Player Stats - https://www.nba.com/stats/players/traditional**
- **Useful interaction/visual and the user question it answers: 

A searchable player selection dropdown with clearly displayed season statistics. It helps users quickly answer questions like "How many points, rebounds, and assists does this player average per game?" without searching large statistics tables.**
- **One improvement or original CourtIQ idea:

Add a side-by-side player comparison feature allowing users to select two NBA players and compare their stats directly. This would make it easier to identify differences in player performance.**
- **My component's rough sketch:** use a few text boxes/arrows or a brief layout description.

Place a player selection dropdown at the top of the profile. Below it, display four statistic cards in one row: Games Played (GP), Points Per Game (PPG), Rebounds Per Game (RPG), and Assists Per Game (APG). Show the data source, season, season type, and retrieval timestamp in a small caption underneath.
- **One visual improvement:** what should be larger, highlighted, simplified or moved—and how does that help the user? See the assignment's “Make the page easy to scan” ideas. 

Make Points Per Game (PPG) larger and more visually prominent than the other statistics because scoring is often one of the first things users want to check. Keep GP, RPG, and APG clearly visible alongside it so users can quickly understand the player's overall performance.
- **Data I need:** exact column names, where they come from, season/period, units, and what one row represents.

PLAYER_ID (unique player identifier), PLAYER_NAME (player name), GP (games played), PTS_PER_GAME (points per game), REB_PER_GAME (rebounds per game), and AST_PER_GAME (assists per game). These columns come from the supplied NBA.com player statistics table for the 2025–26 Regular Season. GP is measured in games, while PPG, RPG, and APG are measured per game. Each row represents one player's statistics for the selected season and season type. The metadata also provides the source and retrieval timestamp.
- **Rules behind my result:** who is included, how the calculation works, and what happens with equal or missing values; write “display only” if no calculation.

The player selector includes all players in the supplied data table and uses PLAYER_ID to uniquely identify each player. GP, PPG, RPG, and APG are displayed directly without recalculation. Missing statistics are shown as "Unavailable" instead of zero. If the table is empty, an informational message is displayed. Equal statistics are displayed as provided, without ranking or tie-breaking.
- **What my function receives → what it produces → where it belongs on the page:**

The function receives a pandas DataFrame (frame) containing NBA player statistics and a metadata dictionary (metadata) containing source information. It produces an interactive player selection dropdown, four statistic cards (GP, PPG, RPG, APG), and a caption with the data source, season, season type, and retrieval time. This component belongs at the top of the CourtIQ Players page.
- **One question or risk for the meeting:**

How should we display players with missing statistics or very few games played? Should we add a minimum games-played filter to help users compare players more fairly?

## After the meeting — shared plan, my contribution
*Since I wasn't able to participate in meetings, I left all the informations that I don't know yet as TBD

- **Issue comment/link recording the team's agreed wireframe:**

TBD
- **What moves, gets larger, or changes in my block; why:**

Keep the player selection dropdown at the top and make PPG more visually prominent while keeping GP, RPG, and APG easy to read. This would help users quickly find a player's scoring average without losing the broader statistical context. Team approval TBD.
- **Agreed column names and which component will use my result:**

My player profile component uses PLAYER_ID, PLAYER_NAME, GP, PTS_PER_GAME, REB_PER_GAME, and AST_PER_GAME from the supplied player table. The render_player_profile() function in src/views.py displays these values on the Players page. The source, season, season type, and retrieval time come from metadata. These are the current implementation columns; team agreement TBD
- **My new idea is:** this week's approved scope / later candidate / needs investigation.

A side-by-side player comparison feature that allows users to select two NBA players and compare their GP, PPG, RPG, and APG. This is outside my assigned Week 1 implementation scope though.

- **Additional data/effort if we adopt that idea:**

Additional development would include adding a second player dropdown, displaying two players' statistics side by side, and handling missing values. We would also need to ensure both players are compared using the same season and season type.


## Before my PR is reviewed

- **Real-data command/result and one descriptive observation:** no unsupported causal claims.

Ran python -m scripts.fetch_data players and successfully downloaded 582 NBA player records for the 2025–26 Regular Season. Tested the Players page using Local NBA snapshots. A.J. Lawson had 24 GP and 4.2 PPG, while Aaron Wiggins had 65 GP and 9.4 PPG in the retrieved snapshot. Switching between players correctly updated the displayed statistics.
- **Unusual case checked** (e.g. missing value or empty table) **and expected/actual result:**

Tested an empty player DataFrame using Streamlit AppTest. Expected an informational message, and the actual result was "No player records are available for this period." with no errors. Also tested a player with a missing PTS_PER_GAME value. Expected "Unavailable" instead of zero, and the actual displayed value was "Unavailable" with no errors.
- **Teammate/component I reviewed; did its result fit what the next component needs? One finding:**

Pending review, but I plan to review Jason's player_scoring_distribution() component to check whether the scoring visualization uses the supplied player statistics correctly and fits the Players page layout.
- **Remaining blocker or connection needed next week:**

Confirming the team's agreed page layout, complete a teammate review, and coordinate with the scoring visualization and percentile components so the Players page presents consistent information. No blocking issue was found during my component tests.