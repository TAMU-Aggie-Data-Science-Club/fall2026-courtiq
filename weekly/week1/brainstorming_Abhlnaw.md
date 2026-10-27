# Week 1 Brainstorming: Sri Abhinav Thatavarthi

My code & checks for #17 are done. These are my design ideas to bring to the team, not decisions we've already agreed on. I still need to join the discussion & exchange feedback with a teammate.

**Name / GitHub handle:** Sri Abhinav Thatavarthi / Abhlnaw
**Team / function / page block:** Team 2 / `src/analytics.py`, `calculate_percentiles()` / player league context. Related to #11 & assigned sub-issue #17.

## Research & my design ideas

- **Comparable tool + direct page URL:** [NBA Stats: Players Traditional](https://www.nba.com/stats/players/traditional). Checked October 26, 2026 as a design reference, not a new data source.
- **Useful interaction & the question it answers:** The season, season-type & per-mode controls make the comparison context clear. I'd keep that context visible so people know what they're comparing.
- **One CourtIQ idea:** Put three horizontal percentile bars right below the player's basic stats, one each for points, rebounds & assists. That way someone can get a quick feel for where the player sits without digging through a whole table.
- **Rough sketch:** Player selector & season at the top, then GP/points/rebounds/assists cards, then the three percentile bars. Put the source & a short explanation underneath.
- **One visual improvement:** Give every bar the same 0-100 scale & show the actual percentile beside it. Label them directly instead of making people rely on color. If a stat is missing, show N/A instead of an empty bar that looks like zero.
- **Data I need:** `PLAYER_ID, PLAYER_NAME, GP, PTS_PER_GAME, REB_PER_GAME, AST_PER_GAME, SEASON` from the supplied NBA.com/nba_api table. It's 2025-26 Regular Season, with one row per player. The stats are already per-game averages.
- **Rules behind my result:** Filter to GP >= 20 first, then calculate each stat with `rank(method="average", pct=True) * 100`. Ties get the same average rank. Missing stats stay missing & don't count in that stat's denominator. The input stays unchanged. An empty group still returns the five required columns.
- **Input -> output -> page:** Player table -> `PLAYER_ID, SEASON, PTS_PCTL, REB_PCTL, AST_PCTL` -> the player league-context section. The page can match those results back to the selected player using ID & season.
- **One question for the discussion:** How do we explain percentiles without making them look like an overall player rating? I'd keep GP >= 20 visible & add a short note that this is our prototype comparison group, not an official NBA qualification rule.

## Shared plan & my contribution

- **Discussion link / agreed wireframe:** Still pending. I haven't posted these ideas or recorded team feedback yet.
- **What I'd change in my block & why:** My proposal is to put the bars right after the basic stats so the raw numbers & league context are close together. This still needs team input.
- **Column names & who uses the result:** The assignment requires `PLAYER_ID, SEASON, PTS_PCTL, REB_PCTL, AST_PCTL`. Cemal handles connecting the reviewed calculation to the player page later.
- **Where my idea stands:** Proposal for discussion. The calculation is this week's assigned work; the bars are a display idea, not extra UI code I've added or something the team has approved.
- **Extra data / effort:** No extra dataset is needed for the proposed bars. The page would need to select the right ID/season, render the three values, handle N/A & show the source/cohort note. That UI work would need to be agreed on separately.

## Checks & review

- **Real-data run:** `python -m scripts.fetch_data players` saved the NBA snapshot at `2026-10-23T09:20:30.930698+00:00`. The final print hit a Windows UnicodeEncodeError, but the saved snapshot validated fine. The preview reused it with UTF-8 console output, with no second NBA request.
- **Preview command & result:** `python -m scripts.preview_component player-percentiles` passed. There were 582 source rows & 452 players with GP >= 20. The output has the exact five required columns.
- **One observation:** In this snapshot, Luka Doncic has 33.5 points/game over 64 games & a points percentile of 100. Shai Gilgeous-Alexander has 31.1 points/game & about 99.78. That's their scoring position in this group, not a claim about who's the better overall player.
- **Unusual cases:** The supplied practice table passed: ID 103 at GP=19 is excluded & ID 102 at GP=20 stays in. IDs 102/104 tie at about 83.33 for points. ID 104's missing assists stay NaN; ID 102 gets 100 for assists because the missing value doesn't count in that denominator.
- **Other checks:** Empty input & an empty eligible group return the right columns with zero rows. The original table stays unchanged. Real-data IDs, missing values, percentile bounds & an independent count-based check of the top points rank passed. An AST comparison confirmed the imports & other functions weren't changed.
- **Environment:** The environment verifier, `python -m pip check` & `python -m compileall -q src` passed. The final real-data preview also passed using the cached snapshot.
- **Teammate review & one finding:** Still pending. I can exchange screenshots & feedback under the PM's guidance, but I haven't completed that exchange yet. I'll add the person's name, what I checked & one actual finding afterward.

## What's left

- Share the design proposal & record the discussion link/feedback.
- Review a teammate's work & record a real finding. Get feedback on mine too.
- Commit the final notes/comment cleanup, push `deliverable1-Abhlnaw` & open the PR into `deliverable1`.
- Include `Related to #11`, reference #17 & request Cemal's review.
- Keep downloaded data, generated output & credentials out of the PR. Those stay local.
