# Week 01 — Build the first pieces of CourtIQ

**Due: Saturday, October 24, 2026, 11:59 PM Central.** We meet Wednesday, October 21 to discuss the page designs. PR review is planned for Sunday; the next assignment is targeted for Monday, October 26.

**Plan for 2–3 hours total**, including the meeting, research, coding, checks and peer review. If you are still stuck after two hours, contact Cemal so we can adjust the task. Stop at three hours and record what remains. Asking for help is part of the work.

**Task card:** [Issue #11](https://github.com/TAMU-Aggie-Data-Science-Club/fall2026-courtiq/issues/11). **PR base after release:** `issue-11/integration`. Starter publication is pending; wait for the PM announcement that the instructions and starter are available on that branch before starting a submission branch.

## 1. What we are building, and why

A useful basketball app does more than list numbers. It helps someone answer: “What does this player contribute?” or “How does this team compare with the league?”

This week, each person builds one piece of that experience: preparing data, calculating context, drawing a chart, or displaying a profile. Together we should have player/team summaries, two interactive charts, and checked calculations. The starter already gives each piece its own place in the app, so you can begin without waiting for a teammate's code.

**Real NBA data is required.** Exploratory data analysis (EDA) means inspecting what the data contains and using summaries or charts to understand it. Use the supplied NBA snapshots for your final check and record one descriptive observation in your brainstorming copy. Fictional practice and the onboarding database do not satisfy this requirement.

We will agree on the page flow together on Wednesday. Connecting every piece through one shared data path comes afterward. Recent games, shot charts, database loading and predictions are not coding tasks this week.

## 2. Get to your starting point

1. Open the published Issue and find your task in the table below.
2. Create your branch/worktree using [CONTRIBUTING](../../CONTRIBUTING.md#for-members-developers). A **worktree** is a separate working folder; your **branch** keeps your changes separate until review. Replace `your-handle` with your GitHub username:

```sh
git fetch origin
git worktree add -b issue-11/your-handle ../courtiq-week1-your-handle origin/issue-11/integration
cd ../courtiq-week1-your-handle
```

3. Follow [setup](../../docs/SETUP.md#1-local-python-environment) to create/activate Python 3.12 in that folder and install the pinned packages. A new worktree needs its own environment. Run:

```sh
python scripts/verify_environment.py
python -m pip check
```

Expect `PASS` and `No broken requirements found.` Docker/database setup is not needed for this assignment. If setup takes too long, tell Cemal; it counts toward your time limit.

## 3. Find your piece

Open the file listed below and search for your name. A **function** is a named piece of code that receives information and produces a result. Its name follows `def`; its body is the indented code underneath. Comments beginning with `#` explain the steps. Replace the unfinished TODO code inside **your function only**.

A pandas **DataFrame** is a table, much like a spreadsheet. In our functions, `frame` or `raw` is that table. `return` sends your result back to the app. Chart functions return a Plotly figure; calculation/cleanup functions return a table. June and Casey's functions display Streamlit elements directly.

| Member / team | Open file → find function | What you are making; how to check it | Reviewer |
| --- | --- | --- | --- |
| Aiden / 1 | [data.py](../../src/data.py) → `audit_source()` | A data inspection report: what columns exist, their types, and how much is missing. Return `FIELD, DTYPE, MISSING`; report repeated player IDs, where/when data came from, and one cache/failure check. | Cemal |
| Ignacio / 1 | [data.py](../../src/data.py) → `clean_players()` | A consistent player table the app can read. Select required columns, convert numeric values, reject missing/repeated IDs, keep missing statistics, and rename the per-game fields. Leave the original table unchanged. | Aiden |
| Andrew / 1 | [data.py](../../src/data.py) → `clean_teams()` | A consistent team table. Check missing/repeated IDs, convert numeric values, and require whole, nonnegative games/wins/losses with `W + L = GP`. Keep the supplied win percentage and missing statistics. | Aiden |
| June / 2 | [views.py](../../src/views.py) → `render_player_profile()` | A player selector and summary showing games played, points, rebounds and assists per game. Switch players and check the displayed values; show a useful message for missing data. | Jason, then Cemal |
| Jason / 2 | [charts.py](../../src/charts.py) → `player_scoring_distribution()` | A histogram showing how scoring averages are distributed, with one player highlighted. Include players with `GP >= 20`; label the chart and handle an empty table or unavailable selection. | June |
| Sri / 2 | [analytics.py](../../src/analytics.py) → `calculate_percentiles()` | A table showing players' relative ranks in points, rebounds and assists. Use `GP >= 20`, the supplied tie rule, and the practice example below. Missing statistics stay missing. | June |
| Michael / 3 | [analytics.py](../../src/analytics.py) → `prepare_ratings()` | Checked team efficiency values. Check IDs/types, calculate net rating, and compare it with the source within `0.2`. Keep source values; report missing ratings and unexpected differences. | Casey, then Cemal |
| Casey / 3 | [views.py](../../src/views.py) → `render_team_profile()` | A team selector and summary showing games, wins/losses, win percentage and basic per-game statistics. Switch teams and check values, missing-data messages and source information. | Michael |
| Jack / 3 | [charts.py](../../src/charts.py) → `team_efficiency()` | A scatterplot placing teams by offensive/defensive rating, with one team highlighted. Label units and which direction is better; handle missing values and unavailable selections. | Michael |

**Several people share each file.** Keep other functions, imports and helper code unchanged. Keep your function's name and arguments unchanged so the app can call it. Do not create a personal copy of the Python module. Cemal handles merging and conflicts between PRs.

The cleanup tasks focus on the checks above. Further name/range/infinity checks and detailed win-percentage validation are deferred until before database/production use. Report questionable values instead of silently changing them.

## 4. Get data and try your code

An **API** lets a program request data. The supplied download command already handles the request; you do not need to build a collector. It saves a **snapshot**—a local copy—so rerunning your work does not repeatedly contact NBA servers.

Use **2025-26 Regular Season**. Run only the command for your task, from the worktree root:

| Members | Download once; later runs reuse the saved copy |
| --- | --- |
| Aiden, Ignacio, June, Jason, Sri | `python -m scripts.fetch_data players` |
| Andrew, Casey | `python -m scripts.fetch_data teams` |
| Michael, Jack | `python -m scripts.fetch_data ratings` |

Raw responses and source details go under ignored `data/raw/week1/`. The command allows 20 seconds per request and does not automatically retry. `--refresh` deliberately replaces a snapshot; do not repeatedly refresh a failing request. Follow [DATA.md](../../DATA.md): NBA API first; ask PMs before changing sources or building a scraper.

If a request fails, post the command/error in the Issue and continue with the fictional practice option. A practice run helps development, but final checks must use real NBA data. Do not share downloaded datasets or upload them to GitHub.

Each worktree downloads its own local copy; the PM's files are not included in Git. Week 1 reads these files directly. Loading real NBA data into PostgreSQL is later work.

**Preview a data/calculation/chart function:**

```sh
python -m scripts.preview_component source-audit --demo
```

`-m` runs the named script from this project. `--demo` chooses invented practice data. Replace `source-audit` with your component:

| Aiden | Ignacio | Andrew | Jason | Sri | Michael | Jack |
| --- | --- | --- | --- | --- | --- | --- |
| `source-audit` | `clean-players` | `clean-teams` | `player-chart` | `player-percentiles` | `team-ratings` | `team-chart` |

Remove `--demo` to use your saved NBA data. Chart previews also accept `--id <numeric-ID>` to choose a player/team. Finished tables save under ignored `data/interim/week1/` or `data/processed/week1/`; chart previews save as `.html` files you can open in a browser and hover over.

`NO OUTPUT` means the function is unfinished or the selection has no chart. It does not prove completion; an older preview file may still exist. Aiden can run `python -m scripts.check_starter` for a safe offline cache/failure check; this tests the supplied helpers, not anyone's TODOs. The source-audit preview prints request details for the PR evidence; `audit_source()` itself receives only the table.

**Preview in the app**—June/Casey use this, and everyone can inspect their block:

```sh
python -m streamlit run app.py
```

Open Players or Teams. Under **Development settings**, choose **Fictional practice** or **Local NBA snapshots**. **Placeholders only** shows the page sketch. Stop the app with Ctrl+C to return to terminal commands. Unfinished messages are expected until you replace the TODOs. The app reads files; changing a selector makes no NBA request.

## 5. Understand what your result means

### Preparing data: preserve meaning

A player's name is for display; their **ID** is the number we use to match records reliably. The same player can appear in different seasons, so season + ID identifies a season record. Repeated keys can cause double counting—report them rather than keeping an arbitrary row.

Inspect before changing anything:

```python
print(frame.shape)          # Number of rows and columns
print(frame.dtypes)         # Are numbers actually stored as numbers?
print(frame.isna().sum())   # Missing entries in each column
```

Use `.copy()` before editing so another component can still use the original. `pd.to_numeric(..., errors="raise")` converts values and reports something it cannot interpret. **Missing is not zero:** an unknown assist average does not mean the player had no assists.

`GP` means games played. `PTS_PER_GAME`, `REB_PER_GAME` and `AST_PER_GAME` are already averages—do not divide by GP again. `W_PCT` is a fraction: `0.625` displays as `62.5%`.

### Calculations: give numbers context

**Percentiles** describe position within a comparison group, not overall player quality. Use `series.rank(method="average", pct=True) * 100`. For `[10, 10, 30]`, this produces `[50, 50, 100]`: equal values share a rank. Missing values stay missing and are excluded from that statistic's count. Our `GP >= 20` group includes exactly 20; it is a prototype rule, not official NBA qualification.

Sri can use the single supplied practice table: player ID `103` is excluded; ID `102` has points percentile about `83.33`; ID `104` has no assists percentile because its input is missing. These check the boundary, ties and missingness without another test dataset.

**Team ratings** account for possessions: ORTG is points scored per 100 possessions; DRTG is points allowed. Higher ORTG and lower DRTG are better. `NETRTG = ORTG - DRTG`: for example, `115 - 110 = +5`. Michael checks the calculated result against the source with tolerance `0.2` for rounding. Points per game cannot substitute for these ratings.

### Make the page easy to scan

- Start with the user question. Jason's chart asks “Where does this player's scoring sit?” Jack's asks “Where does this team sit offensively and defensively?” A relationship on a chart does not establish its cause.
- Keep selection/season together and use a compact row of statistic cards. Give the main chart more room; highlight the selection and mute other points/bars.
- Keep units, period and comparison group visible; use hover for exact values. Use labels/shapes as well as color, readable text and consistent spacing across both pages.
- Percentile bars or a radar chart could use Sri's outputs later. Radar axes must share the same 0–100 scale; do not mix raw points and rebounds on an unexplained common scale.
- Put filenames/debugging in the development panel. Recent games and shot charts are future ideas, not extra coding tasks.

The view functions show a selector example. `st.selectbox` chooses a record, `st.metric` displays a value, `st.columns` arranges content, and `st.plotly_chart` displays a figure. Use native controls; custom CSS/new packages are not required.

## 6. Keep the pieces compatible — exact reference

The supplied helper selects/renames columns for each independent preview. It does not need another person's unfinished function. Later, Cemal connects the reviewed cleanup/calculations to the pages.

A **column name** is how one function finds another's result. Keep these exact names, much as matching plugs must have matching connections:

| Table | Columns |
| --- | --- |
| Player | `PLAYER_ID, PLAYER_NAME, GP, PTS_PER_GAME, REB_PER_GAME, AST_PER_GAME, SEASON` |
| Team | `TEAM_ID, TEAM_NAME, GP, W, L, W_PCT, PTS_PER_GAME, REB_PER_GAME, AST_PER_GAME, SEASON` |
| Ratings | `TEAM_ID, TEAM_NAME, OFF_RATING, DEF_RATING, NET_RATING, SEASON` |
| Sri's result | `PLAYER_ID, SEASON, PTS_PCTL, REB_PCTL, AST_PCTL` |
| Michael's result | Ratings columns plus `CALCULATED_NET_RATING` |

Raw NBA tables use `PTS/REB/AST`; the request uses **PerGame** units. Cleanup renames these to make the units obvious. IDs and GP/W/L are integers; names/seasons are text; statistics are numeric and may be missing. Calculations should not request data, and chart/display code should not duplicate calculations.

**Metadata** is the accompanying source information: where data came from, season/type, request settings and UTC retrieval time. June/Casey receive it separately and should display it. Practice data uses `SYNTHETIC-01` and has no real retrieval timestamp. Ask PMs before changing shared names, definitions or sources.

## 7. Discuss, check and submit

Copy [brainstorming.md](brainstorming.md) to `weekly/week1/brainstorming_<github-handle>.md`—replace `your-handle` first:

```sh
python -c "from pathlib import Path; Path('weekly/week1/brainstorming_your-handle.md').open('xb').write(Path('weekly/week1/brainstorming.md').read_bytes())"
```

Write short bullets. Before Wednesday, coordinate research on one comparable tool and bring an early sketch/output, one idea and the data it needs. On Wednesday, team 2 discusses Players, team 3 discusses Teams, and team 1 checks data feasibility across both. Decide order, size, visuals and exact data needs; PMs record approved changes in the Issue. Keep space for selection, summary, league context, source/missing-data explanations and future recent performance.

Before Saturday, review a teammate's work and record one finding in your document. If you are not a listed reviewer, agree on a PR to check at the meeting. Check your own work with real data and one unusual case, such as an empty table, missing value or repeated ID. Compare a few results with the input. For charts, test hover/highlighting; for selectors, switch records. Run `python -m compileall -q src` to catch Python syntax errors.

A **pull request (PR)** asks others to review your branch. Include only your function changes and personal brainstorming file. For example, replace the paths below with yours:

```sh
git add src/data.py weekly/week1/brainstorming_your-handle.md
git diff --cached
```

Check that only your function changed. Then follow [the commit/push and PR walkthrough](../../CONTRIBUTING.md#open-a-pull-request-members). Use base `issue-11/integration`, once published. Include your name/team, `Related to #11`, commands/results and any blocker. Request the listed reviewer and Cemal; link the PR in the Issue.

Keep downloaded data, generated CSV/HTML, environments and `.env` out of the PR. No screenshots are required. **Cemal handles merges and conflicts; members address feedback on their own code.** PMs decide final integration into `main`. Sunday review may lead to revisions rather than immediate acceptance.

**Ready for review means:**

- Your assigned function produces the required result using **real NBA data**; you include the command/result and one descriptive observation. If real-data verification is blocked, state that clearly and contact Cemal.
- You checked one unusual case and compared important displayed/calculated values with their inputs.
- Your personal brainstorming copy records the meeting decisions and peer-review finding, or identifies a pending review.
- Your PR contains only your assigned changes and targets the published integration branch.

**Cemal's check:** run the environment checks above, `python -m scripts.check_starter`, `python -m compileall -q app.py src scripts`, and each submitted component's real-data preview command. In Streamlit, check both profile selectors and charts using **Local NBA snapshots**, then visit all four sections. Compare results with the task table; confirm source/missing-data messages, no API calls during interaction, and no unrelated changes. Mark a member complete after their required work and peer review are accepted and merged; support checks alone do not establish completion.

## 8. What comes afterward

Next week starts with unfinished work, connecting validated data/calculations to the views, shared selection, and visual consistency. A small local PostgreSQL pilot needs schema/connection approval first; this week uses files, and the database still contains teaching data only.

Add one recent-performance feature only after the shared data path and current views work. PMs choose actual next tasks from verified results within the same time budget. Finishing these pieces does not complete the semester's full profile requirements.

References when needed: [pandas selection](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html), [rank](https://pandas.pydata.org/docs/reference/api/pandas.Series.rank.html), [Plotly histograms](https://plotly.com/python/histograms/), [scatterplots](https://plotly.com/python/line-and-scatter/), [Streamlit controls](https://docs.streamlit.io/develop/api-reference), [NBA definitions](https://www.nba.com/stats/help/glossary).
