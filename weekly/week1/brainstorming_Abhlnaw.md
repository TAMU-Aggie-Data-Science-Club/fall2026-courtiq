# Week 1 Brainstorming: Sri Abhinav Thatavarthi

My code & checks for #17 are done. These are my design ideas to bring to the team, not decisions we've already agreed on. I still need to join the discussion & exchange feedback with a teammate.

**Name / GitHub handle:** Sri Abhinav Thatavarthi / Abhlnaw
**Team / function / page block:** Team 2 / `src/analytics.py`, `calculate_percentiles()` / player league context. Related to #11 & assigned sub-issue #17.

## Research & my design ideas

- **Comparable tool + direct page URL:** [NBA Stats: Players Traditional](https://www.nba.com/stats/players/traditional). Checked October 26, 2026 as a design reference, not a new data source.
- **Useful interaction & the question it answers:** The season, season-type & per-mode controls make the comparison context clear. I'd keep that context visible so people know what they're comparing.
- **One CourtIQ idea:** Add a "What does this player bring?" summary with points, rebounds & assists per game right next to their percentiles. It gives people the actual production & league context in one place instead of making them jump between sections.
- **Rough sketch:** Player selector & season at the top, then GP & three rows: stat name, per-game average & percentile. Keep the source & GP >= 20 comparison group visible underneath.
- **One visual improvement:** Line up the raw numbers & percentiles so they're easy to scan. Keep per-game units & percentile labels explicit. Missing values show N/A, not zero. If we later add bars, they should all use the same 0-100 scale.
- **Data I need:** `PLAYER_ID, PLAYER_NAME, GP, PTS_PER_GAME, REB_PER_GAME, AST_PER_GAME, SEASON` from the supplied NBA.com/nba_api table. It's 2025-26 Regular Season, with one row per player. The stats are already per-game averages.
- **Rules behind my result:** Filter to GP >= 20 first, then calculate each stat with `rank(method="average", pct=True) * 100`. Ties get the same average rank. Missing stats stay missing & don't count in that stat's denominator. The input stays unchanged. An empty group still returns the five required columns.
- **Input -> output -> page:** Player table -> `PLAYER_ID, SEASON, PTS_PCTL, REB_PCTL, AST_PCTL` -> the player league-context section. The page can match those results back to the selected player using ID & season.
- **One question for the discussion:** How do we explain percentiles without making them look like an overall player rating? I'd keep GP >= 20 visible & add a short note that this is our prototype comparison group, not an official NBA qualification rule.

## Shared plan & my contribution

- **Discussion link / agreed wireframe:** Pending an actual discussion link & team decision. My idea is to compare each stat with its percentile beside it. A later idea is to explore an overall metric like BPM or WS/48 & its percentile, but that needs a source/definition review & PM approval. The three current percentiles alone don't measure overall impact on a team.
- **What I'd change in my block & why:** Pair each per-game stat with its percentile in the player summary. That keeps production & context together. This still needs team input.
- **Column names & who uses the result:** The assignment requires `PLAYER_ID, SEASON, PTS_PCTL, REB_PCTL, AST_PCTL`. Cemal handles connecting the reviewed calculation to the player page later.
- **Where my idea stands:** Proposal for discussion. The calculation is this week's assigned work; the summary is a display idea, not extra UI code I've added or something the team has approved. BPM/WS/48 is a later investigation idea.
- **Extra data / effort:** The summary uses the existing player table & percentile output. The page would match ID/season, display the values & handle N/A. An overall metric would need separate source & definition checks; I haven't added or fetched one.

## Checks & review

- **Real-data run:** `python -m scripts.fetch_data players` saved the NBA snapshot at `2026-10-23T09:20:30.930698+00:00`. The final print hit a Windows UnicodeEncodeError, but the saved snapshot validated fine. The preview reused it with UTF-8 console output, with no second NBA request.
- **Preview command & result:** `python -m scripts.preview_component player-percentiles` passed. There were 582 source rows & 452 players with GP >= 20. The output has the exact five required columns.
- **One observation:** In this snapshot, Luka Doncic has 33.5 points/game over 64 games & a points percentile of 100. Shai Gilgeous-Alexander has 31.1 points/game & about 99.78. That's their scoring position in this group, not a claim about who's the better overall player.
- **Unusual cases:** The supplied practice table passed: ID 103 at GP=19 is excluded & ID 102 at GP=20 stays in. IDs 102/104 tie at about 83.33 for points. ID 104's missing assists stay NaN; ID 102 gets 100 for assists because the missing value doesn't count in that denominator.
- **Other checks:** Empty input & an empty eligible group return the right columns with zero rows. The original table stays unchanged. Real-data IDs, missing values, percentile bounds & an independent count-based check of the top points rank passed. An AST comparison confirmed the imports & other functions weren't changed.
- **Environment:** The environment verifier, `python -m pip check` & `python -m compileall -q src` passed. The final real-data preview also passed using the cached snapshot.
- **Teammate review & one finding:** Pending. I plan to exchange feedback with alionthebeat or find someone in #questions-help. I'll record who I reviewed & one actual finding once the exchange happens.

## What's left

- **Done locally:** Assigned calculation, completed TODO cleanup, research/design proposal, real-data run & unusual-case checks.
- **Pending discussion:** Share the proposal & record the actual discussion link/feedback.
- **Pending teammate exchange:** Review someone's work, give feedback & record a real finding. Get feedback on mine too.
- **Submission:** Publish `deliverable1-Abhlnaw` & open the PR into `deliverable1`, with `Related to #11`, a reference to #17 & Cemal requested as reviewer. Discussion/review items above remain pending until actually completed.
- **Files to submit:** Only `src/analytics.py` & this personal notes file. Downloaded data, generated output & credentials stay local.
