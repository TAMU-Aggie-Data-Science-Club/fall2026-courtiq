# Week 00 — Python, PostgreSQL setup and NBA data practice

**Deliverable 0 · Individual · About 75–120 minutes with Python/Git/Docker installed. First-time Docker installation, WSL setup or restarts may add 30–60 minutes.** The GitHub onboarding Issue provides the actual deadline, owners and status. Use any text editor; this assignment is a regular Python script.

All nine members complete the same individual exercise this week; later team specializations and Co-PM review responsibilities are described in [the deliverable structure](../deliverables_strucutre.md).

## 1. Get the project and your branch

If GitHub is new to you, first read [the terms and Issue walkthrough](../../CONTRIBUTING.md#new-to-github). The **Issue** is the shared assignment task card; your **PR** will contain your completed code.

Open the Issue URL sent by the PM, read its deadline and linked instructions, and comment with your name, GitHub username and team to claim your individual submission. Its number appears beside the title and at the end of the URL. The Issue is shared by all nine members; keep it open.

Open PowerShell/Command Prompt on Windows or Terminal on macOS/Linux. Copy only the commands inside each code block, paste one at a time and press Enter after each. `cd` changes the folder you are working in; a successful command may print nothing.

Install [Python 3.12](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads/). Accept your repository invitation and make sure you can push feature branches. The PM must first publish the onboarding Issue and its integration branch containing the starter files.

**Before running the commands below**, replace `42` with that actual Issue number and `your-handle` with your GitHub username (the `@name` on your profile, not your full display name). If you have already cloned the repo, enter its folder and start at `git fetch origin`.

```sh
git clone https://github.com/TAMU-Aggie-Data-Science-Club/fall2026-courtiq.git
cd fall2026-courtiq
git fetch origin
git worktree add -b issue-42/onboarding-your-handle ../courtiq-your-handle origin/issue-42/integration
cd ../courtiq-your-handle
```

The commands download the repo, learn about the PM's remote branches, create your feature branch in a separate worktree folder, then enter that folder. Confirm your branch:

```sh
git branch --show-current
```

It should show `issue-<actual-number>/onboarding-<your-username>`, not `main` or the integration branch. If the integration branch is missing or the branch/folder already exists, stop and ask the PM how to continue; do not overwrite or delete earlier work. Follow [CONTRIBUTING.md](../../CONTRIBUTING.md); the PM prepares the shared integration branch once.

## 2. Set up Python and PostgreSQL

All nine members must complete [the shared setup guide](../../docs/SETUP.md):

1. Create/activate the local Python 3.12 `.venv`, install `requirements.txt`, and pass the verifier and `pip check`.
2. Install and launch Docker Desktop (or the documented Linux Engine/Compose alternative). Confirm `docker version` shows Client **and Server**, and `docker compose version` succeeds.
3. Copy `.env.example` to a private `.env`, set your local database password, and keep that file out of Git and screenshots.
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

Expect a result containing `1` and `(1 row)`. The setup guide also shows the interactive SQL prompt, platform installation steps and troubleshooting. Capture the healthy service and query output for your PR.

When finished with the database check:

```sh
docker compose stop
docker compose ps -a
```

Database files persist in Docker's named volume. Use `docker compose up -d` to start again; do not delete volumes to stop the service. If Docker cannot reach its engine, launch Docker Desktop and wait; if port 5432 is busy, change `POSTGRES_PORT` in `.env` to 5433 and rerun startup. Other errors are covered in [setup troubleshooting](../../docs/SETUP.md#troubleshooting).

**Docker runs only PostgreSQL.** Python scripts, Streamlit and any later Jupyter use stay local in `.venv`. This week's database task is setup/verification only: do not create a schema, write ingestion code or connect the exercise to PostgreSQL.

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
5. Add two Python comments: what the result shows and one limitation.

The data-loading code is provided. With `USE_API = False`, it loads [player_stats_backup.csv](player_stats_backup.csv): all names, teams and statistics are **fictional**. To try fetching the selected season yourself, change `USE_API = True` and read the prepared `LeagueDashPlayerStats` call. If the request fails, the script clearly switches to the backup; either source is acceptable for this assignment. The private classroom API option uses NBA.com attribution; broader data use follows [DATA.md](../../DATA.md).

`GP` means games played. `PTS_PER_GAME`, `REB_PER_GAME` and `AST_PER_GAME` are **already averages**. Do not divide them by `GP` again. The backup also includes `PTS_TOTAL` to illustrate the difference; the API's PerGame response does not supply that total. Rank by `PTS_PER_GAME`, not totals. Do not interpret synthetic results as actual NBA findings.

Useful references: [pandas selection](https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html), [pandas sorting](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html), [Plotly bar charts](https://plotly.com/python/bar-charts/), [the prepared NBA endpoint](https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/leaguedashplayerstats.md).

## 4. Submit your script

Run your completed script and save terminal/chart evidence plus screenshots of healthy `docker compose ps` and `SELECT 1;` for your PR. You attach it on the GitHub website; it does not have to become another file in the repo. Save only `weekly/week0/your-handle_onboarding.py`; keep the common starter and backup unchanged. Generated charts and real downloaded data belong under ignored `data/`, not in your submission.

From the same member worktree root, run the commands below after replacing the example Issue number and username.

```sh
git status --short
git add weekly/week0/your-handle_onboarding.py
git diff --cached --stat
```

`git status` lists changed files. `git add` selects only your script for the next saved change. `git diff --cached --stat` lets you confirm what is selected: it should show only your script. **Check that result before running `git commit`.** Once the selected files are correct, save and upload your change:

```sh
git commit -m "Complete CourtIQ onboarding exercise"
git push -u origin issue-42/onboarding-your-handle
```

A commit saves locally; push uploads that commit to your GitHub feature branch. Neither command creates the PR.

If Git needs your identity, set `git config --local user.name "Your Name"` and `git config --local user.email "your-email@example.com"` with your details. HTTPS pushes require GitHub authentication, not your account password; see [GitHub's guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github).

On the GitHub repository page, select **Pull requests → New pull request**. Set **base** to `issue-42/integration` and **compare** to `issue-42/onboarding-your-handle`, replacing both examples. Base is the destination; compare is your work. Inspect the files, then create the PR with a title such as `Week 0: Your Name`.

In the description include `Related to #42` (actual number), your data source, Python verification result, Docker health/SQL result and the screenshot attachments. Select a teammate or PM in **Reviewers**; if that option is unavailable, comment on the Issue with your PR link and ask the PM to arrange review. Add your PR link to the shared Issue so the PM can track your submission.

Read review comments, edit the same local script, rerun it, commit and push fixes on the same branch; the existing PR updates automatically. Wait for approval before merging under CONTRIBUTING's rules. The [full PR walkthrough](../../CONTRIBUTING.md#open-a-pull-request-members) explains the website steps.

For problems: a missing integration branch means the PM must finish setup; permission denied on push means you should check your invitation/authentication with the PM; “nothing to commit” means Git sees no saved file changes. If confused, report the exact command and error in the Issue, with private credentials removed.

## Done when

- [ ] Local Python 3.12 environment verification and `pip check` pass.
- [ ] Docker Engine/Compose are installed and PostgreSQL becomes healthy with `docker compose up -d`.
- [ ] `SELECT 1;` succeeds; health/query evidence is attached to the PR.
- [ ] You can stop/restart PostgreSQL without deleting its named volume; no schema/ingestion work is required.
- [ ] Your script loads API or backup data and answers every TODO.
- [ ] Only players with at least 20 games appear in the descending top five.
- [ ] The interactive chart matches those five rows and clearly identifies the source.
- [ ] Two interpretation/limitation comments are present.
- [ ] Your individual script and evidence are submitted to the correct integration-base PR; no data, environments, `.env` credentials or database files are included.
