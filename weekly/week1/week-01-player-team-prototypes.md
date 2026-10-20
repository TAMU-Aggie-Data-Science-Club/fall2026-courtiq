# Week 01 — NBA data and visual page prototypes

**PRs due Saturday, October 24, 2026, 11:59 PM Central.** Design meeting: Wednesday, October 21. PR review target: Sunday, October 25. Next assignment target: Monday, October 26.

**Effort: 2–3 hours each, including meeting, brainstorming, checks and peer review.** The published GitHub Issue holds actual owners, status, approved changes and the integration branch. **Issue URL/number: pending PM publication.** The local `deliverable1` branch is preparation, not the student PR target.

Budget roughly 45–60 minutes for meeting/research/brainstorming/peer review, 60–90 for coding, and 20–30 for checks and submission. If the component is not nearly working after two hours, contact Cemal to reduce the remaining scope. Stop at three hours and record unresolved work; setup/API trouble and teammate support count toward the same limit. These are targets, not a guarantee that everyone will finish at the same pace.

## 1. Start here

This week: inspect real NBA data, implement **one owned component**, and help design the Players/Teams pages. The supplied blocks are movable starting points. Independent components and reviewed designs are the finish line; a unified production pipeline and finished profiles come later. No database work, new packages, notebooks, game logs or prediction models.

Use your Python 3.12 environment from [setup](../../docs/SETUP.md). Nobody is currently reported blocked; tell Cemal early if that changes. Docker is not needed for these file-based prototypes. From your member worktree root:

```sh
python scripts/verify_environment.py
python -m pip check
python -m streamlit run app.py
```

Open Players/Teams. **Placeholders only** shows the wires; **Fictional practice** runs your component with invented inputs; **Local NBA snapshots** reads your downloaded files. None of these modes makes API requests. Stop Streamlit with Ctrl+C.

Create your member branch/worktree using the actual published Issue number and [CONTRIBUTING](../../CONTRIBUTING.md#for-members-developers). Wait for the PM-published starter; do not branch from another student's work. For example, replacing `N` with that actual number and `your-handle` first:

```sh
git fetch origin
git worktree add -b issue-N/your-handle ../courtiq-week1-your-handle origin/issue-N/integration
cd ../courtiq-week1-your-handle
```

A new worktree needs its own Python environment; follow the short commands in setup. Do not rerun Docker setup or replace another checkout's credentials. Worktree/environment setup time counts toward the budget; ask Cemal to reduce scope if it runs long.

## 2. Your task and page block

**Edit only your named TODO function and your personal brainstorming copy.** Application code lives in `src/`; names and teaching hints are comments beside each function. Teams are numbered groups, not permanent specialties. More experienced members support teammates within the same time budget.

| Team | Member | Module / function / block | Required result and acceptance | Reviewer |
| --- | --- | --- | --- | --- |
| 1 | Aiden · advanced | `src/data.py` → `audit_source()` · supports Players | Use the supplied collection command; audit fields/types/missingness and repeated player IDs. Return `FIELD, DTYPE, MISSING`; report request provenance and one safe failure/cache check. | Cemal |
| 1 | Ignacio · beginner | `src/data.py` → `clean_players()` · supports Players | Select required fields, convert numeric columns, reject missing/duplicate player IDs, preserve missing metrics, and rename per-game columns without changing raw input. Additional range/name validation is deferred. | Aiden |
| 1 | Andrew · novice | `src/data.py` → `clean_teams()` · supports Teams | Select required fields, convert numeric columns, reject missing/duplicate team IDs, and check integer nonnegative GP/W/L with W+L=GP. Preserve missing metrics and source W_PCT; detailed percentage/range checks are deferred. | Aiden |
| 2 | June · intermediate | `src/views.py` → `render_player_profile()` · P1 | Player selector using stable ID; GP and PTS/REB/AST per game; source/period/freshness and readable missing states. Display only—no fetch or analytics formulas. | Jason, then Cemal |
| 2 | Jason · beginner | `src/charts.py` → `player_scoring_distribution()` · P2 | Interactive scoring histogram for GP ≥ 20; highlight a selected player, label units/cohort/season, handle empty/unknown/ineligible selection. | June |
| 2 | Sri · beginner | `src/analytics.py` → `calculate_percentiles()` · P3 | Calculate PTS/REB/AST percentile ranks for GP ≥ 20 with the supplied tie rule. Preserve missing metrics; return the named columns. Use the one supplied practice table to check GP=19/20, ties and missing values. | June |
| 3 | Michael · advanced | `src/analytics.py` → `prepare_ratings()` · T2 | Validate advanced team ratings and key uniqueness; calculate net rating and compare with the source within 0.2. Preserve source values and report missing data. | Casey, then Cemal |
| 3 | Casey · intermediate | `src/views.py` → `render_team_profile()` · T1 | Team selector using stable ID; GP, W/L, source win percentage and basic averages; provenance and missing states. | Michael |
| 3 | Jack · beginner–intermediate | `src/charts.py` → `team_efficiency()` · T3 | Interactive offensive-vs-defensive-rating chart highlighting a team; readable labels/hover and explicit rating direction; handle empty/unknown selection. | Michael |

Each assigned function contains a small example and named TODOs. `None`/unfinished messages are intentional placeholders, not completed work. Several people share a module but own different function bodies. Keep module imports, shared helpers, signatures and other members' functions unchanged; Cemal handles cross-PR conflicts. Do not make a personal copy of the module.

This week's reduced cleanup is for prototypes. Deferred validation must be completed and reviewed before outputs are treated as production-quality or loaded into an application database; do not silently fix questionable values.

**Run independently:**

- Data/calculation/chart owners: `python -m scripts.preview_component source-audit --demo`. Replace `source-audit` with your component: Aiden `source-audit`; Ignacio `clean-players`; Andrew `clean-teams`; Jason `player-chart`; Sri `player-percentiles`; Michael `team-ratings`; Jack `team-chart`. Omit `--demo` for your local real snapshot. Chart previews also accept `--id <numeric-ID>`.
- June/Casey: run the app, select your page and input mode; your function appears in P1/T1. Your block runs without another student's results.
- CLI tables/figures save under ignored `data/interim/week1/` or `data/processed/week1/`. Open a generated `.html` in a browser to test hover.

## 3. Get your own real data—no waiting for another student

Use **2025-26 / Regular Season** only. All source choices follow [DATA.md](../../DATA.md): `nba_api` first; Basketball-Reference only if needed and approved for the intended access/use; investigate alternatives with PMs rather than switching silently. Week 1 needs no scraper.

Run **only your input kind** once; reruns reuse a matching cache:

| Your task | Command |
| --- | --- |
| Aiden, Ignacio, June, Jason, Sri | `python -m scripts.fetch_data players` |
| Andrew, Casey | `python -m scripts.fetch_data teams` |
| Michael, Jack | `python -m scripts.fetch_data ratings` |

The supplied command uses one bounded request per kind, a 20-second timeout, no automatic retries, and explicit season/units. It preserves the response and provenance under ignored `data/raw/week1/`. `--refresh` is a deliberate replacement, not something to run repeatedly. Failed network requests do not replace a valid cache. A corrupt cache produces an error; ask Cemal before replacing it.

**If blocked:** post the command/error in the Issue. Continue with labeled practice inputs, but do not claim real-data acceptance until verified. No silent fictional fallback, source switch, bypass, public upload or sharing of downloaded datasets. An API block is not your fault; report it rather than spending the whole allocation retrying.

## 4. Small shared contract

The helper provides selection/renaming for independent previews; it does **not** call a teammate's cleanup. That is why everyone can start now. Cemal will connect validated outputs later.

| Input/output | Columns and meaning |
| --- | --- |
| Raw snapshots | Native endpoint field names, including `PTS/REB/AST` in **PerGame** mode; exact response plus metadata |
| Canonical player table | `PLAYER_ID, PLAYER_NAME, GP, PTS_PER_GAME, REB_PER_GAME, AST_PER_GAME, SEASON` |
| Canonical basic team table | `TEAM_ID, TEAM_NAME, GP, W, L, W_PCT, PTS_PER_GAME, REB_PER_GAME, AST_PER_GAME, SEASON` |
| Canonical ratings table | `TEAM_ID, TEAM_NAME, OFF_RATING, DEF_RATING, NET_RATING, SEASON` |
| Sri's output | `PLAYER_ID, SEASON, PTS_PCTL, REB_PCTL, AST_PCTL` |
| Michael's output | Canonical ratings plus `CALCULATED_NET_RATING` |

IDs and GP/W/L are integers, names/seasons text, metrics numeric with missing values retained. Keys are season + player/team ID. For unexpected player duplicates, report the row grain; do not blindly keep the first or aggregate. Metadata travels separately: source, season/type, request parameters and UTC retrieval time. Practice uses `SYNTHETIC-01`, never an invented retrieval timestamp.

Functions receive a DataFrame and return a DataFrame/Plotly figure. June/Casey receive a canonical table plus metadata and render it. Keep input data unchanged (`.copy()`), collection outside the UI, and calculations outside chart/UI code. Shared helpers/imports, `app.py` and `scripts/` are PM-owned this week. Own a function, not the whole module; the app calls each function independently.

## 5. Learn while you build

**Inspect before cleaning.** These show different problems:

```python
print(frame.shape, frame.dtypes)
print(frame.isna().sum())
print(frame.duplicated(["SEASON", "PLAYER_ID"]).sum())
```

Convert deliberately with `pd.to_numeric(..., errors="raise")`; investigate bad values rather than deleting rows. Missing is not zero. Per-game statistics are already averages.

**A chart answers a question.** Jason: “Where does this player's scoring sit?” Jack: “Where does this team sit offensively and defensively?” Label axes, units, period and cohort; use hover for detail. Color should communicate selection; do not rely on color alone.

**Percentiles:** use `series.rank(method="average", pct=True) * 100`. `[10, 10, 30]` gives `[50, 50, 100]`. Count nonmissing observations separately for each metric. GP ≥ 20 is our prototype cohort, not official NBA eligibility. Percentiles are relative ranks, not overall player quality. ORTG/DRTG are points scored/allowed per 100 possessions; lower DRTG is better. NETRTG = ORTG − DRTG; do not substitute points/game.

**Streamlit:** `st.selectbox` chooses an ID; `st.columns` arranges content; `st.metric` displays a value; `st.plotly_chart` renders a Plotly figure. The view functions contain a short selector example. Reordering containers changes layout without changing calculations.

### Make the page easy to scan

Use the supplied layout as a starting sketch. Bring one visual improvement to Wednesday's discussion; these ideas do not add coding requirements.

| Area | Ideas to explore |
| --- | --- |
| Profile summary | Keep the selector and season together; use one compact row of clearly labeled statistic cards. |
| Main visual | Give the most useful chart the most space. Highlight the selected player/team with one accent color and mute league peers. |
| Player context | A distribution with a player marker works this week. Percentile bars or a radar chart are later options using Sri's outputs; radar axes must share the same 0–100 scale. |
| Team context | Make the selected team stand out on the efficiency scatterplot. A short caption should explain which direction is better. |
| Detail | Put exact values in hover labels; keep units, season and sample size visible. Use readable text, whitespace and consistent alignment; avoid a box or alert for every sentence. |

Keep styling consistent across both pages. Support color with labels/marker shapes, distinguish missing values from zero, and explain abbreviations. Use native Streamlit/Plotly controls; custom CSS and new design packages are not required. Reserve recent-form/shot-chart ideas for future work. Put filenames, ownership and debugging output in the development panel rather than the main page.

Useful references: [pandas selection](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html), [percentile ranks](https://pandas.pydata.org/docs/reference/api/pandas.Series.rank.html), [Plotly histogram](https://plotly.com/python/histograms/), [Plotly scatter](https://plotly.com/python/line-and-scatter/), [Streamlit basics](https://docs.streamlit.io/develop/api-reference), [NBA metric definitions](https://www.nba.com/stats/help/glossary).

## 6. Brainstorm together, submit individually

Copy [brainstorming.md](brainstorming.md) to **`weekly/week1/brainstorming_<github-handle>.md`**. Fill short bullets, not an essay. Use your GitHub handle at the end of the filename; do not edit the template.

```sh
python -c "from pathlib import Path; Path('weekly/week1/brainstorming_your-handle.md').open('xb').write(Path('weekly/week1/brainstorming.md').read_bytes())"
```

Before Wednesday: inspect one comparable tool (coordinate within your team), bring an early sketch/output and identify needed data. Your code can be incomplete at the meeting.

During the meeting: team 2 proposes Players flow, team 3 proposes Teams flow, team 1 checks data feasibility across both. Decide what should be larger, order of blocks, visual choices, exact fields/definitions and who reviews what. Keep the section purposes; changing scope, names, sources or interfaces requires PM agreement. Record the shared decision in the Issue; each person adds the implication for their component to their own document.

Minimum wireframes retain selection/summary, league comparison, provenance/missing states and reserved recent-performance space. Recent games, shooting context, pace, shot charts and additional ideas are design discussion—not extra coding this week. No predictions.

Before Saturday: exchange a focused peer review or short walkthrough. Record one compatibility check and one useful finding in your personal document. Everyone owns code **and** participates in the shared design.

## 7. Check and submit

Run `python -m compileall -q src`, then check your component with real data and at least one meaningful edge case from your TODOs. June/Casey switch selections and try an empty table; chart owners inspect hover/highlighting and empty input. For data work, compare a few outputs to raw values. **Practice-only checks do not establish real NBA completion.**

Your PR should change only your assigned function in its app module and your personal brainstorming `.md`. Stage those two paths, inspect `git diff --cached` to confirm no other functions changed, then commit/push your member feature branch as explained in CONTRIBUTING. No generated CSV/HTML, screenshots, NBA responses, `.env` or environment files.

PR base: **the published `issue-<actual-number>/integration`**, not `main` or local `deliverable1`. Include name/team, **`Related to #<actual-number>`**, changed component, real-data command/result, edge-case result, and a blocker if present. Link your PR in the Issue, request the listed peer and Cemal, and address feedback on your own branch.

**Cemal handles merging, cross-PR conflicts and integration. Members do not merge/rebase other branches.** PMs retain the final review/merge decision for `main`. Sunday review is a target, not a guarantee every PR merges without revisions. Monday's assignment depends on verified results.

Done: your component works independently with real data; checks and personal brainstorming are present; peer feedback is addressed; inputs/outputs match the agreed page plan. Completed components do not mean the full Players/Teams milestones are complete.

## 8. What follows — planning, not extra work this week

Saturday's target is working player/team summaries, the two charts, percentile/rating calculations, and audit/cleanup functions submitted in reviewable PRs. Sunday is review and merging of accepted work. Independent previews can still have separate selectors and inputs.

Next week's first priority is to finish blockers, connect validated outputs to the views, unify selectors, and apply Wednesday's visual decisions. A small local PostgreSQL pilot is a candidate after approval of its NBA table schema and connection approach. Week 1 currently uses ignored local files; the existing database contains the fictional teaching table only.

Add **one bounded recent-performance feature only after the shared data paths and core views work**. If collection, validation or components remain incomplete, finish those instead of adding features. Cemal/Ali will choose next week's actual tasks from verified results, within the same 2–3-hour budget.
