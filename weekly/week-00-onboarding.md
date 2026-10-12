# Week 00 · Deliverable 0 — Technical Onboarding & Product Exploration

**CourtIQ · ADSC Fall 2026 · Individual assignment for all nine members**

**Time:** approximately 1–2 hours (about 105 minutes: setup 25, notebook 45, proposal 20, submission 15). Installation/network problems may take longer; ask a PM if blocked. **Due:** before the first team meeting; the PM will place the exact date/time in the shared GitHub Issue. Each member submits their own work even when discussing ideas with teammates.

> **Issue authority:** The linked GitHub Issue is authoritative for owners, task status, deadlines and approved changes. This file contains the assignment instructions. Until publication, the [onboarding issue draft](../docs/ONBOARDING_ISSUE.md) is preparation material only.

## Learning objectives

By the end, you can use one Python environment, inspect and filter a pandas table, distinguish season totals from per-game averages, create an interactive Plotly chart, explain a result's limitations, and submit work through the team's feature-to-integration PR workflow.

## Part A — Development environment (25 minutes)

Use **Python 3.12** and one repository-local `.venv` for scripts, notebooks and Streamlit. `.python-version` records the target; it does not install Python. Install Python 3.12 from [python.org](https://www.python.org/downloads/) first, and install [Git](https://git-scm.com/downloads). On Windows, enable the Python installer option to add Python to PATH. You do not need PostgreSQL, Docker, an NBA account or API access for onboarding.

### 1. Clone

Run in a terminal (PowerShell on Windows; Terminal on macOS/Linux):

```sh
git clone https://github.com/TAMU-Aggie-Data-Science-Club/fall2026-courtiq.git
cd fall2026-courtiq
```

These instructions describe the starter files after the PM makes them available. During local PM review, use the existing feature checkout instead of cloning; the files are not yet on GitHub.

After cloning, complete [submission steps 1–2](#github-submission-15-minutes) to create your member feature worktree. Run the environment commands below from that worktree root so you install dependencies only once.

### 2. Create and activate the environment

#### Windows — PowerShell

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, allow scripts **for this terminal only**, then retry:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Alternatively use Command Prompt: `.venv\Scripts\activate.bat`.

#### macOS — Terminal

```sh
python3.12 --version
python3.12 -m venv .venv
source .venv/bin/activate
```

#### Linux — Terminal

```sh
python3.12 --version
python3.12 -m venv .venv
source .venv/bin/activate
```

Your distribution may require its Python 3.12 venv package (for example `python3.12-venv` on a distribution that provides it). If Python 3.12 is unavailable in your distribution's package manager, use your supported Python installation method or ask a PM; do not substitute another Python version silently.

### 3. Install and verify

All commands below work on the three platforms after activation. Run from the repository root:

```sh
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/verify_environment.py
python -m pip check
```

The verifier prints Python 3.12, the active interpreter path, each pinned package version and `PASS`. `pip check` should print `No broken requirements found.` It checks imports and makes a local Plotly figure; it does not fetch NBA data or complete the exercise.

Direct dependencies are pinned; transitive dependencies are resolved by pip, so this is not a fully locked environment. PostgreSQL drivers and stretch ML packages are deliberately deferred until their work is approved.

#### Verification scope of this starter

The pinned environment was installed and verified on **macOS, Apple Silicon, Python 3.12.12**. Package imports, `pip check`, a Jupyter server and kernel, privately completed notebook execution/interactive chart HTML, Streamlit startup and all four navigation selections passed. Windows and Linux commands are documented but were not executed on those platforms. Browser interaction was not manually checked; members must confirm the notebook chart renders in their own browser. No live NBA connectivity or PostgreSQL functionality was tested or implemented.

### 4. Run Jupyter with the same environment

```sh
python -m ipykernel install --sys-prefix --name courtiq --display-name "CourtIQ (Python 3.12)"
python -m notebook
```

Registration stays inside `.venv`. Open `notebooks/00_onboarding.ipynb`, or your member copy described in [the submission instructions below](#github-submission-15-minutes). Choose **Kernel → Change Kernel → CourtIQ (Python 3.12)** if necessary. A notebook cell containing `import sys; print(sys.executable)` should point into this repository's `.venv`. The verification script alone does not prove that your browser/kernel works: run the notebook imports and confirm its chart appears.

The terminal prints a local browser URL. Treat its token as private; do not include it in screenshots or GitHub. Stop the notebook server with Ctrl+C (confirm shutdown if prompted).

### 5. Run the application

In a second terminal at the same repository root, activate the **existing** `.venv` using the command for your platform, then run:

```sh
python -m streamlit run app.py
```

Open `http://localhost:8501`. Select Players, Teams, Compare and Trends in the sidebar. Each page describes planned functionality and explicitly states that no statistics are loaded. Stop with Ctrl+C. To leave the environment, run `deactivate`.

### Troubleshooting

| Symptom | Action |
| --- | --- |
| `python3.12` or `py -3.12` not found | Install Python 3.12, reopen the terminal, and check the version before creating `.venv`. |
| Wrong Python version in verifier | Create the environment with Python 3.12; ask a PM before replacing an existing environment if unsure. |
| `ModuleNotFoundError` or wrong package version | Activate `.venv`, check `python -c "import sys; print(sys.executable)"`, then repeat `python -m pip install -r requirements.txt`. |
| Notebook imports fail but terminal works | Select the CourtIQ kernel; compare `sys.executable` in both places. Restart the kernel after installing packages. |
| Fixture not found | Keep the notebook inside this checkout, including `notebooks/submissions/`; do not move it to Downloads. |
| Chart does not appear | Run imports first; use `fig.show(renderer="notebook")`. Trust your own notebook via File → Trust Notebook if needed, then rerun the cell. |
| Port 8501 in use | Stop the earlier server or run `python -m streamlit run app.py --server.port 8502` and use port 8502. |
| Install times out or fails | Retry on a stable network. Save the error text and ask a PM; avoid randomly changing pins. |
| Live NBA request times out | Use the supplied offline fixture; live API access is optional and not assessed. |

Do not commit `.venv/`, `.env` files, tokens, notebook checkpoint folders, downloaded NBA data or caches. See [DATA.md](../DATA.md) and [CONTRIBUTING.md](../CONTRIBUTING.md).


Select the CourtIQ kernel and run the starter imports/data-loading cell. Capture the verifier PASS and successful notebook/figure execution for your PR. Tell a PM the command, error message, OS and Python version if blocked; hide tokens and private details in evidence.

## Part B — Guided NBA-style data exploration (45 minutes)

First create your individual notebook copy using the submission instructions below. Open it in Jupyter. The supplied [synthetic fixture](../tests/fixtures/synthetic_player_stats.csv) contains **12 fictional NBA-style player rows, not real NBA results**. Names, teams and seasons are invented. The [fixture dictionary](../tests/fixtures/README.md) explains every column.

Work through the clearly labeled notebook TODOs:

1. Load the fixture using the supplied code and inspect its first rows, dimensions, types and columns.
2. Explain `GP`, `PTS_TOTAL` and `PTS_PER_GAME`. Totals accumulate across games; per-game values are already averaged. **Do not divide `PTS_PER_GAME` by `GP` again.** For a separate example, 120 total points over 10 games means 12 points per game; a stored average of 12 remains 12.
3. Keep players with **at least 20 games**, including exactly 20. Investigate how low-game players could distort a ranking.
4. Rank the eligible rows by **points per game descending**, and keep the top five. Preserve that order for the chart. Use averages, not total points.
5. Create a Plotly bar chart: player name on x, points per game on y, highest to lowest left to right. Label the title as **synthetic** and the axes with readable names/units. Show the chart interactively in the notebook.
6. Write 3–5 sentences interpreting the ranking, the impact of the 20-game rule and at least one limitation. Do not generalize fictional data to the actual NBA or infer overall ability from scoring alone.

Hints: look up pandas boolean indexing, `sort_values`, `head`, and Plotly Express `bar`. For an unrelated example of filtering, `practice[practice["AGE"] >= 18]` keeps adults. The exercise's actual filtering/ranking/chart code is yours to write. Starter `None` values let unanswered cells show reminders; replace them, then restart the kernel and **Run All**. Unanswered TODOs are not completed work even if Run All has no errors.

Check yourself: every ranked player has at least 20 games; there are five distinct rows; their averages descend; the chart uses those same rows and values. You can use `PTS_TOTAL / GP` to confirm the stored average, but do not replace an average with an average divided again.

**Optional extension (not required or graded):** Read the [nba_api endpoint documentation](https://github.com/swar/nba_api/tree/master/docs/nba_api/stats/endpoints) and identify a potential endpoint such as `LeagueDashPlayerStats` or `PlayerGameLog`. Discuss its fields and per-mode parameters. Actual retrieval requires PM confirmation of source permission per [DATA.md](../DATA.md); requests may time out or be blocked. Keep any approved downloads under ignored `data/`, never in a PR. This assignment works entirely offline after package installation.

## Part C — Product brainstorming (20 minutes)

Copy the [proposal template](../docs/FEATURE_PROPOSAL_TEMPLATE.md) to your individual path below. Write about 150–250 words and optionally include a linked example or sketch. Answer all five questions: what you propose, the fan's question, required data, how it might work in CourtIQ, and a relevant example/sketch/visualization (or describe an original sketch in words).

| Permanent team | Members | Initial research focus |
| --- | --- | --- |
| A — Data and Architecture | Aiden Jackson, Ignacio Wijatno, Andrew Mok | NBA data availability, useful endpoints, necessary fields and data organization |
| B — Application and Visualization | June Hwang, Jason Q. Koffi, Sri Abhinav Thatavarthi | Player/team layouts, Streamlit interactions and effective basketball charts |
| C — Statistics and Analytics | Michael Du, Casey Hawkings, Jack Dunlap | Useful statistics, comparisons, percentiles and recent-performance methods |

These are temporary research responsibilities. Teams remain together but rotate technical responsibilities during the semester. Discuss with teammates, but each member submits one useful proposal. Proposals support our first meeting's design discussion; they do not automatically expand scope. See [the application plan](../ARCHITECTURE.md) for the four planned sections.

## GitHub submission (15 minutes)

Follow the established [contribution workflow](../CONTRIBUTING.md). The commands below are for **members submitting their assignment**, not authorization for an agent to publish this starter.

### 1. Find the issue and integration branch

Open the repository's GitHub **Issues** tab and find **Deliverable 0 — Technical Onboarding & Product Exploration**. Read its deadline/checklist, then comment with your GitHub username and permanent team to claim your individual slice. This is one shared issue with nine submissions; do not claim the entire issue exclusively. The PM creates/publishes `issue-<n>/integration` with the starter files before members begin. If it does not exist or the issue is missing, ask a PM rather than inventing a number or targeting `main`.

### 2. Create your feature worktree

From your clean clone's root, run `git fetch origin`. In the following example, **replace `42` with the actual issue number** and **replace `your-handle` with your lowercase GitHub username** everywhere. Do not type the placeholder strings unchanged.

```sh
git fetch origin
git worktree add -b issue-42/onboarding-your-handle ../courtiq-onboarding-your-handle origin/issue-42/integration
cd ../courtiq-onboarding-your-handle
```

This follows the flat `issue-<n>/<slice>` naming rule. In the new worktree create/activate `.venv` and install dependencies using [Part A above](#part-a--development-environment-25-minutes); use that same environment for all tools in this checkout. If you already did Part A in the initial clone, repeat environment setup here before notebook work. To avoid duplicate installation, create this worktree immediately after cloning and do Part A there.

### 3. Copy your individual files

From the activated terminal at your worktree root, run `python` to open the Python prompt. Replace `your-handle` in the snippet, then paste these lines (without typing the `>>>` prompt):

```python
from pathlib import Path
handle = "your-handle"
nb = Path("notebooks/submissions") / f"{handle}_00_onboarding.ipynb"
proposal = Path("docs/proposals") / f"{handle}.md"
nb.parent.mkdir(parents=True, exist_ok=True)
proposal.parent.mkdir(parents=True, exist_ok=True)
with nb.open("xb") as output:
    output.write(Path("notebooks/00_onboarding.ipynb").read_bytes())

with proposal.open("xb") as output:
    output.write(Path("docs/FEATURE_PROPOSAL_TEMPLATE.md").read_bytes())

exit()
```

Keep the blank lines after each indented block when pasting. Exclusive `"xb"` mode prevents overwriting existing copies. If you see `FileExistsError`, open your existing files instead of copying again.

Replace `your-handle` first. Complete `notebooks/submissions/your-handle_00_onboarding.ipynb` and `docs/proposals/your-handle.md`. **Do not edit the shared starter notebook or fixture.** Keep the notebook inside the checkout so its relative fixture lookup works. In a proposal copy, resource links should use full URLs or paths relative to `docs/proposals/`. Screenshots can be attached directly to the PR; they do not require shared tracked filenames.

### 4. Save, check and commit your own work

Restart the notebook kernel and Run All; confirm imports, filtering, top five and the interactive chart work. Save with useful outputs visible; inspect them for private paths/tokens. From the worktree root:

```sh
git status --short
git diff --check
git add notebooks/submissions/your-handle_00_onboarding.ipynb docs/proposals/your-handle.md
git diff --cached --stat
git commit -m "Complete individual CourtIQ onboarding exercise and proposal"
git push -u origin issue-42/onboarding-your-handle
```

Stage only your two files. Do not commit datasets downloaded from NBA sources, `.venv`, credentials or caches. Our synthetic fixture is already supplied; it should not appear as your change.

### 5. Open the correct pull request and request review

On GitHub choose **Pull requests → New pull request**, set **base** to `issue-42/integration` and **compare** to `issue-42/onboarding-your-handle`. Confirm your PR changes only your files. Title: `Deliverable 0: Your Name`. Describe:

- Your name, username and team; `Related to #42` (use the actual number).
- OS, Python version, verifier result and kernel confirmation.
- Notebook/chart screenshot and a short account of what you learned.
- Link to your proposal; any installation issue or remaining question.

Use **Related to**, rather than **Closes**, so one member's submission does not close the shared issue. Request a teammate's or PM's review in GitHub's Reviewers control. Wait for any configured automated review and human review. Read all feedback, edit your two files, rerun affected cells, save, commit and push follow-up changes, then re-request review. Merge only after approval following CONTRIBUTING. The PM owns the eventual integration-to-`main` review.

## Acceptance checklist for each member

- [ ] Python 3.12 and one `.venv`; verifier PASS and `pip check` successful.
- [ ] Notebook uses the CourtIQ kernel and loads the supplied fixture without live API access.
- [ ] All TODOs answered, including inspection and explanation of totals versus averages.
- [ ] Filter includes exactly 20 games and excludes every row below 20.
- [ ] Five eligible players ranked by points per game descending.
- [ ] Interactive Plotly chart uses the same five rows, columns and order, with synthetic labeling.
- [ ] 3–5 sentence interpretation discusses the threshold and a limitation.
- [ ] Complete feature proposal with all questions answered and team research focus.
- [ ] Unique notebook/proposal paths, execution evidence, correct integration-base PR and requested review.
- [ ] No secrets, real downloaded data, virtual environments or cache artifacts submitted.

## Useful resources

- [Python venv documentation](https://docs.python.org/3.12/library/venv.html)
- [pandas getting started](https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html)
- [Plotly bar charts](https://plotly.com/python/bar-charts/)
- [Jupyter Notebook documentation](https://jupyter-notebook.readthedocs.io/en/stable/)
- [Streamlit getting started](https://docs.streamlit.io/get-started)
- [GitHub pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request)

The [initial onboarding PDF](../docs/DELIVERABLE_0.pdf) is a static snapshot from the original setup. Use this weekly assignment for current instructions and the linked GitHub Issue for owners, status, deadlines and approved changes.
