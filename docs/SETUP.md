# CourtIQ development setup

Use **Python 3.12** and one repository-local `.venv` for scripts, notebooks and Streamlit. `.python-version` records the target; it does not install Python. Install Python 3.12 from [python.org](https://www.python.org/downloads/) first, and install [Git](https://git-scm.com/downloads). On Windows, enable the Python installer option to add Python to PATH. You do not need PostgreSQL, Docker, an NBA account or API access for onboarding.

## 1. Clone

Run in a terminal (PowerShell on Windows; Terminal on macOS/Linux):

```sh
git clone https://github.com/TAMU-Aggie-Data-Science-Club/fall2026-courtiq.git
cd fall2026-courtiq
```

These instructions describe the starter files after the PM makes them available. During local PM review, use the existing feature checkout instead of cloning; the files are not yet on GitHub.

## 2. Create and activate the environment

### Windows — PowerShell

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

### macOS — Terminal

```sh
python3.12 --version
python3.12 -m venv .venv
source .venv/bin/activate
```

### Linux — Terminal

```sh
python3.12 --version
python3.12 -m venv .venv
source .venv/bin/activate
```

Your distribution may require its Python 3.12 venv package (for example `python3.12-venv` on a distribution that provides it). If Python 3.12 is unavailable in your distribution's package manager, use your supported Python installation method or ask a PM; do not substitute another Python version silently.

## 3. Install and verify

All commands below work on the three platforms after activation. Run from the repository root:

```sh
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/verify_environment.py
python -m pip check
```

The verifier prints Python 3.12, the active interpreter path, each pinned package version and `PASS`. `pip check` should print `No broken requirements found.` It checks imports and makes a local Plotly figure; it does not fetch NBA data or complete the exercise.

Direct dependencies are pinned; transitive dependencies are resolved by pip, so this is not a fully locked environment. PostgreSQL drivers and stretch ML packages are deliberately deferred until their work is approved.

### Verification scope of this starter

The pinned environment was installed and verified on **macOS, Apple Silicon, Python 3.12.12**. Package imports, `pip check`, a Jupyter server and kernel, privately completed notebook execution/interactive chart HTML, Streamlit startup and all four navigation selections passed. Windows and Linux commands are documented but were not executed on those platforms. Browser interaction was not manually checked; members must confirm the notebook chart renders in their own browser. No live NBA connectivity or PostgreSQL functionality was tested or implemented.

## 4. Run Jupyter with the same environment

```sh
python -m ipykernel install --sys-prefix --name courtiq --display-name "CourtIQ (Python 3.12)"
python -m notebook
```

Registration stays inside `.venv`. Open `notebooks/00_onboarding.ipynb`, or your member copy described in [Deliverable 0](../weekly/week-00-onboarding.md). Choose **Kernel → Change Kernel → CourtIQ (Python 3.12)** if necessary. A notebook cell containing `import sys; print(sys.executable)` should point into this repository's `.venv`. The verification script alone does not prove that your browser/kernel works: run the notebook imports and confirm its chart appears.

The terminal prints a local browser URL. Treat its token as private; do not include it in screenshots or GitHub. Stop the notebook server with Ctrl+C (confirm shutdown if prompted).

## 5. Run the application

In a second terminal at the same repository root, activate the **existing** `.venv` using the command for your platform, then run:

```sh
python -m streamlit run app.py
```

Open `http://localhost:8501`. Select Players, Teams, Compare and Trends in the sidebar. Each page describes planned functionality and explicitly states that no statistics are loaded. Stop with Ctrl+C. To leave the environment, run `deactivate`.

## Troubleshooting

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
