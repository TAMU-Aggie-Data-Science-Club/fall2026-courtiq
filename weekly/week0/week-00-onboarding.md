# Week 00 — Python, PostgreSQL setup and NBA data practice

**Deliverable 0 · Individual · Time estimate: about an hour First-time Docker installation, WSL setup or restarts may add another 30 minutes or more.** The PM announces the deadline and updates in Discord. Week 0 uses individual PRs into `deliverable0`; no GitHub Issue is required yet. Use any text editor; this assignment is a regular Python script. Expected time: environment setup 20–40 minutes, coding/chart 30 minutes, and GitHub submission 20 minutes. Installation or troubleshooting can take longer.

All 10 members complete the same individual exercise this week; later team specializations and Co-PM review responsibilities are described in [the deliverable structure](../deliverables_strucutre.md).

## 1. Get the project and your branch

If GitHub is new to you, first read [the GitHub terms and PR walkthrough](../../CONTRIBUTING.md#new-to-github). Your **PR** is the request to review your completed code.

This assignment should be completed by Friday 11:59PM, Oct 16th 2026, in order to diagnose issues early on. Each member submits independently by submitting a PR for their branch; you do not need an Issue number or Issue link for deliverable 0. Future tasks will be assigned, tracked, and completed using GitHub Projects and Issues.

Open PowerShell/Command Prompt on Windows or Terminal on macOS/Linux. Copy only the commands inside each code block, paste one at a time and press Enter after each. `cd` changes the folder you are working in; a successful command may print nothing.

Install [Python 3.12](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads/). Accept your repository invitation and make sure you can push feature branches. The PM must first publish the reviewed starter files on the shared `deliverable0` branch. Repository Write access is required to push the feature branches used below; ask the PM if your invitation or permissions are missing.

**Before running the commands below**, replace `your-handle` with your GitHub username (the `@name` on your profile, not your full display name). If you have already cloned the repo, enter its folder and start at `git fetch origin`. Additionally, in order to have access permission to the GitHub repo, please join through the link provided in #announcements on the CourtIQ Discord.

```sh
git clone https://github.com/TAMU-Aggie-Data-Science-Club/fall2026-courtiq.git
cd fall2026-courtiq
git fetch origin
git worktree add -b deliverable0-your-handle ../courtiq-your-handle origin/deliverable0
cd ../courtiq-your-handle
```

The commands download the repo, learn about the PM's remote branches, create your feature branch in a separate worktree folder, then enter that folder. Like `git checkout -b`, `git worktree add -b` creates and checks out a new branch; a worktree uses a separate folder, while checkout switches the branch in your current folder. Both folders share the same Git history. Confirm your branch:

```sh
git branch --show-current
```

It should show `deliverable0-<your-username>`, rather than `main` or the shared `deliverable0` branch. If the integration branch is missing or the branch/folder already exists, stop and ask the PM how to continue; do not overwrite or delete earlier work. Follow [CONTRIBUTING.md](../../CONTRIBUTING.md); the PM prepares the shared `deliverable0` branch once. Use flat member branch names such as `deliverable0-your-handle`; `deliverable0/your-handle` cannot coexist with a branch named `deliverable0`.

## 2. Set up Python and PostgreSQL

Every member must complete [the shared setup guide](../../docs/SETUP.md):

1. Create/activate the local Python 3.12 `.venv`, install `requirements.txt`, and pass the verifier and `pip check`.
2. Install and launch Docker Desktop (or the documented Linux Engine/Compose alternative). Confirm `docker version` shows Client **and Server**, and `docker compose version` succeeds.
3. Run `python scripts/database.py setup` with `.venv` active. The provided script creates private credentials, starts PostgreSQL, loads the fictional starting table and configures backups. Keep `.env` out of Git and shared messages; there is no schema/ingestion coding task.
4. Run the database commands from your member worktree root:

```sh
docker compose config -q
docker compose up -d
docker compose ps
```

Wait until `postgres` shows **healthy**, then verify SQL:

```sh
docker compose exec -T postgres psql -U courtiq -d courtiq -c "SELECT 1;"
```

Expect a result containing `1` and `(1 row)`. The setup guide also shows the interactive SQL prompt, platform installation steps and troubleshooting. Briefly report whether the database checks passed in your PR description; no screenshots or attachments are required.

When finished with the database check:

```sh
docker compose stop
docker compose ps -a
```

Database files persist in Docker's named volume. Use `docker compose up -d` to start again; do not delete volumes to stop the service. If Docker cannot reach its engine, launch Docker Desktop and wait; if port 5432 is busy, change `POSTGRES_PORT` in `.env` to a free port such as 5433 and rerun `python scripts/database.py setup` to finish loading and backup setup. Other errors are covered in [setup troubleshooting](../../docs/SETUP.md#troubleshooting).

**Docker runs only PostgreSQL.** Python scripts, Streamlit and any later Jupyter use stay local in `.venv`. This week's database task is running/verifying the supplied setup: do not implement an application schema, write ingestion code or connect the exercise to PostgreSQL. The shared setup guide explains the supplied fictional table and backup/recovery commands.

## 3. Start coding

**Start with [onboarding.py](onboarding.py).** Make your own copy from the activated terminal:

```sh
python -c "from pathlib import Path; p=Path('weekly/week0/your-handle_onboarding.py'); p.open('xb').write(Path('weekly/week0/onboarding.py').read_bytes())"
python weekly/week0/your-handle_onboarding.py
```

Replace `your-handle` first. The copy command creates your own file without overwriting an existing copy. Open that `.py` file in a plain text editor, replace the TODO placeholders with your code, save, and rerun `python weekly/week0/your-handle_onboarding.py` after each change. `None` means unfinished; the supplied reminders stay visible until you replace those values. If the copy already exists, open it instead of copying again. Complete:

1. Inspect the table's shape and data types.
2. Keep players with **at least 20 games**, including exactly 20.
3. Find the top five by `PTS_PER_GAME`, highest first.
4. Make a Plotly bar chart using player names and points per game. Saving and labeling are provided. Open `data/processed/onboarding_chart.html` in a browser and try hovering over a bar.

The data-loading code is provided. With `USE_API = False`, it loads [player_stats_backup.csv](player_stats_backup.csv): all names, teams and statistics are **fictional**. To try fetching the selected season yourself, change `USE_API = True` and read the prepared `LeagueDashPlayerStats` call. If the request fails, the script clearly switches to the backup; either source is acceptable for this assignment. The private classroom API option uses NBA.com attribution; broader data use follows [DATA.md](../../DATA.md).

`GP` means games played. `PTS_PER_GAME`, `REB_PER_GAME` and `AST_PER_GAME` are **already averages**. Do not divide them by `GP` again. The backup also includes `PTS_TOTAL` to illustrate the difference; the API's PerGame response does not supply that total. Rank by `PTS_PER_GAME`, not totals. Do not interpret synthetic results as actual NBA findings.

Useful references: [pandas selection](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html), [pandas sorting](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html), [Plotly bar charts](https://plotly.com/python/bar-charts/), [the prepared NBA endpoint](https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/leaguedashplayerstats.md).

## 4. Submit your script

Run your completed script and the environment/database checks. Submit only `weekly/week0/your-handle_onboarding.py`; keep the common starter and backup unchanged. Briefly summarize the commands you ran and their results in your PR description. No screenshots or file attachments are required. Generated charts and real downloaded data belong under ignored `data/`, not in your submission.

From the same member worktree root, run the commands below after replacing `your-handle` with your GitHub username.

```sh
git status --short
git add weekly/week0/your-handle_onboarding.py
git diff --cached --stat
```

`git status` lists changed files. `git add` selects only your script for the next saved change. `git diff --cached --stat` lets you confirm what is selected: it should show only your script. **Check that result before running `git commit`.** Once the selected files are correct, save and upload your change:

```sh
git commit -m "Complete CourtIQ onboarding exercise"
git push -u origin deliverable0-your-handle
```

A commit saves locally; push uploads that commit to your GitHub feature branch. Neither command creates the PR.

If Git needs your identity, set `git config --local user.name "Your Name"` and `git config --local user.email "your-email@example.com"` with your details. HTTPS pushes require GitHub authentication, not your account password; see [GitHub's guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github).

On the GitHub repository page, select **Pull requests → New pull request**. Set **base** to `deliverable0` and **compare** to `deliverable0-your-handle`, replacing `your-handle`. Base is the destination; compare is your work. Inspect the files, then create the PR with a title such as `Week 0: Your Name`.

In the description include your name/team, data source, Python verification result, database setup/status result, Docker health/SQL result as a brief text summary. No Issue reference is required. Select the Co-PM Cemal and PM Ali (adurmusoglu) in **Reviewers**; if that option is unavailable, send your PR link in Discord and ask the PM to arrange review. Share your PR link in the assignment's Discord channel under the deliverable in the forum so that the PM and Co-PM can track your submission. If the PM creates an Issue later, they can link your existing PR without changing your branch.

Read review comments, edit the same local script, rerun it, commit and push fixes on the same branch; the existing PR updates automatically. Wait for approval before merging under CONTRIBUTING's rules. The [full PR walkthrough](../../CONTRIBUTING.md#open-a-pull-request-members) explains the website steps.

For problems: a missing integration branch means the PM must finish setup; permission denied on push means you should check your invitation/authentication with the PM; “nothing to commit” means Git sees no saved file changes. If confused, report the exact command and error in Discord, with private credentials removed.

## Done when

- [ ] Local Python 3.12 environment verification and `pip check` pass.
- [ ] The supplied database setup succeeds; `python scripts/database.py status` shows 12 fictional starter rows and a verified backup. Docker/PostgreSQL is healthy.
- [ ] `SELECT 1;` succeeds; the verification results are summarized in the PR description.
- [ ] You can stop/restart PostgreSQL without deleting its named volume; no schema/ingestion work is required.
- [ ] Your script loads API or backup data and answers every TODO.
- [ ] Only players with at least 20 games appear in the descending top five.
- [ ] The interactive chart matches those five rows and clearly identifies the source.
- [ ] Your individual script is submitted through a PR targeting `deliverable0`, with a brief verification summary; no data, environments, `.env` credentials or database files are included.
