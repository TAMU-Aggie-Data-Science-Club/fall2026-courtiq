# CourtIQ development setup

Use this guide from your **member worktree root**, the folder containing `requirements.txt` and `compose.yaml`. [Week 0](../weekly/week0/week-00-onboarding.md#1-get-the-project-and-your-branch) explains how to get that worktree. Run commands one at a time in PowerShell on Windows or Terminal on macOS/Linux.

**Python scripts and Streamlit run locally in one `.venv`. Docker runs only PostgreSQL.** Jupyter, if used later, also stays in the local Python environment; this assignment uses a regular script and does not require Jupyter. The supplied database setup creates a small fictional teaching table and manages backups. Week 0 members verify it; they do not implement schemas, ingestion or an app/database connection.

For Week 0, complete sections 1–5 and check `python scripts/database.py status`. Sections 6–7 are reference for the app preview and later maintenance. Setup already creates a backup; manually restoring a database is not part of the assignment.

## 1. Local Python environment

Install [Python 3.12](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads/). On Windows, enable the Python launcher (`py`) and PATH options, then reopen the terminal.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
```

On all platforms, after activation:

```sh
python -m pip install -r requirements.txt
python scripts/verify_environment.py
python -m pip check
```

Expect `PASS` and `No broken requirements found.` Use this same `.venv` for all project Python commands. In each new terminal, activate the existing environment again rather than creating another one.

## 2. Install and start Docker

Docker runs a **container**, an isolated process containing PostgreSQL. Compose reads [compose.yaml](../compose.yaml) to start it with the same settings for everyone.

- **Windows:** follow [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/). Use its Linux-container/WSL 2 setup, complete any required restart, and launch Docker Desktop. If Windows asks for WSL or virtualization setup, follow the installer/documented steps; ask a PM if your machine is restricted.
- **macOS:** follow [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/). Choose Apple silicon or Intel to match your Mac (Apple menu → About This Mac), install the app and launch it.
- **Linux:** follow [Docker Desktop for Linux](https://docs.docker.com/desktop/setup/install/linux/) for your supported distribution. If you already use Docker Engine, ensure its service and the [Compose plugin](https://docs.docker.com/compose/install/linux/) are installed/running instead; an extra Desktop installation is unnecessary.

Wait until Docker Desktop reports its engine is running, then verify in a new terminal:

```sh
docker version
docker compose version
```

`docker version` must show both **Client** and **Server** sections. The Client alone means the engine is not running/reachable. Use the current `docker compose` command with a space, not the old standalone `docker-compose` command.

## 3. Create your private database settings

From the worktree root with `.venv` active and Docker running:

```sh
python scripts/database.py setup
```

This provided command creates a private `.env` from [.env.example](../.env.example), generates separate strong administrator/application passwords for empty password fields, starts PostgreSQL, loads the same version of the fictional fixture, creates a checked backup and installs automatic backup checks for your user account. Repeating setup preserves existing passwords and does not duplicate rows. No additional Python dependency or host PostgreSQL installation is required.

If you already copied `.env.example`, setup fills empty password fields without replacing nonempty passwords. Existing passwords must have at least 16 letters/digits/underscores/hyphens. If an existing database uses other credentials, ask a PM before changing them: changing `.env` does not change an initialized database's password. Setup never resets or deletes a volume to solve authentication failures.

The administrator is `POSTGRES_USER=courtiq`; the database is `POSTGRES_DB=courtiq`. `COURTIQ_APP_USER=courtiq_app` is a separate read-only account for future application reads. Use those application credentials when wiring up the application later; keep the administrator account for schema/loading/recovery maintenance. Passwords are stored only in local `.env`, not printed by the setup script. On macOS/Linux it restricts that file to your user; Windows uses your folder's existing access permissions.

`.env` is ignored by Git; `.env.example` contains no password and is shareable. Keep `.env` contents private; do not paste them into PRs or shared messages. The database port defaults to `127.0.0.1:5432`; if that port is occupied, set `POSTGRES_PORT=5433` in `.env`. Docker's PostgreSQL port inside the container remains 5432.

**One checkout per local database:** the sample `COMPOSE_PROJECT_NAME=courtiq` selects the same Docker resources on a given computer. If you have already set up CourtIQ in another checkout, keep using that checkout and its matching `.env`. For an independent PM/student test on the same computer, safely copy `.env.example` to `.env` **before** setup:

```sh
python -c "from pathlib import Path; Path('.env').open('x').write(Path('.env.example').read_text())"
```

Set a distinct project name such as `COMPOSE_PROJECT_NAME=courtiq-pm-test` and an unused host port such as `POSTGRES_PORT=55432`, then run setup. Leave the password fields blank so setup generates private credentials. If `.env` already exists, inspect it rather than overwrite it. Changing the project name selects another volume; it does not copy or delete the first database. Different members on different computers can all keep the default `courtiq` name.

## 4. Start PostgreSQL and verify it

From the same worktree root:

```sh
docker compose config -q
docker compose up -d
docker compose ps
```

`config -q` validates the configuration without printing your password. `up -d` downloads the PostgreSQL image on the first run and starts it in the background. Run `ps` again after a short wait until the `postgres` service shows **healthy**. First image download/initialization can take several minutes on a slow connection. Leave Docker Desktop running while you use the database.

Run a query using the `psql` client already inside the container:

```sh
docker compose exec postgres psql -U courtiq -d courtiq
```

You should see the `courtiq=#` SQL prompt. Type this SQL and press Enter:

```sql
SELECT 1;
```

Expect a result containing `1` and `(1 row)`. The semicolon ends the SQL statement. Exit this SQL prompt with:

```text
\q
```

You are now back at your normal terminal. For a one-command verification, this equivalent command also works:

```sh
docker compose exec -T postgres psql -U courtiq -d courtiq -c "SELECT 1;"
```

Report whether the health check and query passed in your PR description. Week 0 requires no screenshots or attachments. The supplied setup loads the data for you; there is no student database coding task. You can also inspect the read-only connection and starter-data count:

```sh
python scripts/database.py status
```

Expect 12 rows with source `synthetic` and version `synthetic-onboarding-v1` in `courtiq.player_season_stats`. Names and statistics are fictional. `gp` means games played; the `*_per_game` fields are already averages. The coding exercise still uses its provided CSV/API loader. Each member has an independent local database; local edits are not synchronized. Reloading the same supplied fixture gives everyone the same starting records.

Setting `USE_API=True` in your onboarding script changes that script's data source only; it does not load NBA results into PostgreSQL. Your onboarding PR submits your personal script and a brief text verification summary. Database files stay local. The Streamlit shell remains separate until later application integration.

## 5. Stop safely and understand persistence

When done:

```sh
docker compose stop
docker compose ps -a
```

The service should be stopped/exited. Start it again with `docker compose up -d`. Docker stores its database files in a **named volume** called `<project>_postgres_data` (`courtiq_postgres_data` with the sample project name), outside the Git working tree. Stopping or restarting preserves those files.

If you want to remove the stopped container/network while keeping the database:

```sh
docker compose down
```

Do **not** add `-v`/`--volumes`: that deletes the persistent database volume. Do not run a volume prune to troubleshoot. Changing user/database/password in `.env` after the first initialization does not change existing database credentials; ask a PM before altering credentials or resetting a volume. [PostgreSQL image behavior](https://hub.docker.com/_/postgres), [Compose shutdown reference](https://docs.docker.com/reference/cli/docker/compose/down/).

## 6. Run the local application

With `.venv` active:

```sh
python -m streamlit run app.py
```

Open `http://localhost:8501` to inspect Players, Teams, Compare and Trends. The shell still shows planned placeholders and is not connected to PostgreSQL. Stop Streamlit with Ctrl+C. Docker is only needed for the separate database setup check at this milestone.

## 7. Backups and recovery

A Docker volume provides persistence, but is not a backup. The database command saves compressed PostgreSQL archives and matching SHA-256 integrity manifests under ignored `data/processed/backups/`, outside the database volume. These contain the database schema and data, without role passwords. Both the `.dump` and matching `.json` are needed for recovery. Existing archives are retained; the script does not delete old backups automatically.

Create an immediate backup while PostgreSQL is running:

```sh
python scripts/database.py backup
```

`setup` also installs a per-user scheduled check once an hour. It creates a backup when there is no intact archive less than 24 hours old. macOS uses LaunchAgents, Windows uses Task Scheduler, and Linux uses the user's crontab (cron must be installed/running). macOS/Windows also check on login. Automatic jobs need the computer awake, the user session available as applicable, and Docker/PostgreSQL running. If the database is stopped when a backup is due, the check fails and tries again at the next scheduled run; it does not silently start/reset your database.

Check backup output with `python scripts/database.py status`. macOS/Linux scheduler output is in `data/processed/backups/scheduler.log`; Windows reports failures in Task Scheduler. A fresh timestamp and successful job result matter—registration alone does not prove a backup ran. Keep the checkout and `.venv` at their installed paths; moving them requires updating the scheduled job with PM help. To install scheduling separately, use `python scripts/database.py schedule`. For a disposable test that should not register a host job, use `python scripts/database.py setup --no-schedule`.

To recover, take the archive path printed by `backup`, replace `PATH_TO_YOUR_BACKUP.dump` below, and choose a **new** database name:

```sh
python scripts/database.py restore "PATH_TO_YOUR_BACKUP.dump" --database courtiq_recovery
```

The command checks the matching manifest and archive, restores into the new database in one transaction, reapplies read-only access and verifies a query. It refuses to overwrite the active database or any existing recovery database. Use only your own trusted archives. If restore fails, the new empty recovery database may remain; choose another name and ask a PM before deleting anything. The original database remains available. After checking recovered data, the PM can choose whether to point the project at that database; the script does not switch it automatically.

Before changing supplied data/schema, setup and `load-demo` create a backup if the teaching table already exists. To reload the provided starting data:

```sh
python scripts/database.py load-demo
```

Loading validates fields, units and duplicate keys, then applies changes in one transaction. It updates matching fixture rows and preserves unrelated rows. It does not erase extra records or resolve conflicting schemas automatically. Future real NBA schemas and source-approved ingestion are separate work.

**These are local backups.** They help recover from accidental changes or deletion of the Docker volume while the archive files survive. Losing this computer/disk would lose the database and these backups together; no off-device backup has been configured.

## Troubleshooting

| Problem | What to do |
| --- | --- |
| `docker` or `docker compose` not found | Finish Docker Desktop/Compose installation, reopen your terminal and repeat the version commands. |
| Cannot connect to Docker daemon / only Client shown | Launch Docker Desktop and wait for the engine. On Linux Engine, check the documented service/permission setup with a PM. |
| WSL 2 or virtualization error | Follow the Windows installer prerequisites; ask a PM if administrator or institution restrictions prevent setup. |
| No configuration file found | Enter the member worktree root containing `compose.yaml`; check `pwd` or PowerShell `Get-Location`. |
| `POSTGRES_PASSWORD` missing/empty | Open your local `.env` and set the password. Keep it private; do not edit `.env.example` to store it. |
| Port 5432 already allocated | Set `POSTGRES_PORT=5433` (or another free port) in `.env`, then rerun `python scripts/database.py setup` so loading/backups finish too. The container query command stays the same. |
| Service still starting or unhealthy | Wait briefly, rerun `docker compose ps`, then inspect `docker compose logs --tail=50 postgres`. Send relevant errors to the PM with secrets removed. |
| Image download fails | Check network/disk space and retry; avoid changing the PostgreSQL major version to work around a transient download failure. |
| Role/database does not exist after changing settings | Existing volumes retain their original initialization settings. Restore those settings or ask a PM; do not delete the volume. |
| Password authentication fails in a second checkout | A new `.env` may not match the existing `courtiq` volume. Use the original checkout/settings, or choose a distinct Compose project name and free port for an independent database. Never delete the existing volume to get past this. |
| Setup rejects a password | Existing values must be at least 16 letters/digits/underscores/hyphens. Ask a PM before changing a password on an initialized database. |
| Application writes are denied | Expected: `courtiq_app` is read-only. Approved maintenance uses the administrator through the provided scripts. |
| Backup scheduling fails | Check the OS scheduler's error and log. Linux needs cron; Windows needs permission to create a user task. On macOS, privacy restrictions may block jobs accessing Downloads—ask a PM before changing permissions or moving the checkout. Database setup may already have succeeded; check status and run a manual backup while resolving scheduling. |
| Backup restore refuses a file or destination | Keep its matching `.json`, choose a new database name, and use an intact trusted archive. Never overwrite the original to troubleshoot. |
| SQL prompt does not show a result | Include the semicolon in `SELECT 1;`; use `\q` to exit. |
| PowerShell blocks venv activation | Use Command Prompt with `.venv\Scripts\activate.bat`, or ask a PM. |
| Python imports fail | Activate `.venv`, check `python -c "import sys; print(sys.executable)"`, and reinstall the pinned requirements. |

If blocked, contact the PM in the assignment's Discord channel with your OS, command and relevant error; use the task's Issue once Issues are adopted. Keep passwords/tokens out of shared output.
