# Week 1 — Brainstorming — Sri Abhinav Thatavarthi

Copy to `brainstorming_<github-handle>.md`; keep this template unchanged. Short bullets are enough: aim for 10–15 minutes of writing across the week. Link this in your component PR. Do not attach downloaded data or generated charts.

**Name / GitHub handle:** Sri Abhinav Thatavarthi / Abhlnaw
**Team number / file + function you are editing / page block:** Team 2 / `src/analytics.py`, `calculate_percentiles()` / player league context. Related to #11; assigned sub-issue #17.

## Before Wednesday's meeting

- **Comparable tool + direct page URL:** Pending personal research.
- **Useful interaction/visual and the user question it answers:** Pending personal research.
- **One improvement or original CourtIQ idea:** Pending; I will write my own design ideas.
- **My component's rough sketch:** Pending personal design ideas.
- **One visual improvement:** Pending personal design ideas.
- **Data I need:** `PLAYER_ID, PLAYER_NAME, GP, PTS_PER_GAME, REB_PER_GAME, AST_PER_GAME, SEASON` from the supplied NBA.com/nba_api player table; 2025-26 Regular Season, one row per player in the season. GP is games played; the three statistics are per-game averages.
- **Rules behind my result:** Include GP >= 20 before ranking each statistic independently with `rank(method="average", pct=True) * 100`. Ties share their average rank. Missing statistics remain missing and do not count toward that statistic's denominator. Work on a copy; empty cohorts return the same output columns. This is a prototype comparison cohort, not an official NBA qualification rule or a measure of overall player quality.
- **What my function receives → what it produces → where it belongs on the page:** Supplied player table → `PLAYER_ID, SEASON, PTS_PCTL, REB_PCTL, AST_PCTL` → player league context, with the final display arrangement pending team discussion.
- **One question or risk for the meeting:** Pending preparation for the design discussion.

## After the meeting — shared plan, my contribution

- **Issue comment/link recording the team's agreed wireframe:** Pending; I have not yet contributed to the page-design discussion.
- **What moves, gets larger, or changes in my block; why:** Pending team discussion.
- **Agreed column names and which component will use my result:** Assignment contract: `PLAYER_ID, SEASON, PTS_PCTL, REB_PCTL, AST_PCTL`. Cemal connects the reviewed calculation to the player page later; no meeting decision is claimed here.
- **My new idea is:** Pending personal proposal and team discussion.
- **Additional data/effort if we adopt that idea:** Pending selection of a design idea.

## Before my PR is reviewed

- **Real-data command/result and one descriptive observation:** `python -m scripts.fetch_data players` saved a validated NBA snapshot retrieved at `2026-10-23T09:20:30.930698+00:00`; its final success message hit a Windows console UnicodeEncodeError. No second request was made. With UTF-8 console output, `python -m scripts.preview_component player-percentiles` succeeded: 582 source rows, 452 eligible players, five required output columns. In this snapshot Luka Doncic (PLAYER_ID 1629029) has 33.5 points/game in 64 games and a points percentile of 100; Shai Gilgeous-Alexander has 31.1 points/game and approximately 99.78. These describe this cohort, not causes or overall player quality.
- **Unusual case checked** (e.g. missing value or empty table) **and expected/actual result:** Supplied practice preview and assertions passed: ID 103 (GP=19) excluded; ID 102 (GP=20) included; IDs 102/104 share points percentile 83.3333; ID 104's missing assists stay NaN. ID 102's assists percentile is 100 because the missing statistic is excluded from its denominator. Empty input and an empty eligible cohort return zero rows with the exact five columns; the source frame remains unchanged. Environment verifier, pip check and `python -m compileall -q src` passed.
- **Teammate/component I reviewed; did its result fit what the next component needs? One finding:** Pending; no teammate PR reviewed yet.
- **Remaining blocker or connection needed next week:** Complete comparable-tool research, contribute to the design discussion, and review a teammate before claiming full assignment completion. Final page integration remains Cemal's work. PR target is `deliverable1` and reviewer is Cemal per task card, overriding stale assignment branch/reviewer text.
