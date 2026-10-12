# CourtIQ development setup

Use this guide from your **member worktree root**, the folder containing `requirements.txt` and `compose.yaml`. [Week 0](../weekly/week0/week-00-onboarding.md#1-get-the-project-and-your-branch) explains how to get that worktree. Run commands one at a time in PowerShell on Windows or Terminal on macOS/Linux.

**Python scripts and Streamlit run locally in one `.venv`. Docker runs only PostgreSQL.** Jupyter, if used later, also stays in the local Python environment; this assignment uses a regular script and does not require Jupyter. Week 0 requires a healthy database and `SELECT 1;`, not tables, a schema, ingestion or an app/database connection.

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

From the worktree root with `.venv` active, copy [.env.example](../.env.example) safely:

```sh
python -c "from pathlib import Path; Path('.env').open('x').write(Path('.env.example').read_text())"
```

If this reports `FileExistsError`, keep your existing `.env` and open it instead. Edit the `.env` file in a text editor and set `POSTGRES_PASSWORD` to a new local-only password (letters/digits are easiest for this exercise). Keep `POSTGRES_USER=courtiq` and `POSTGRES_DB=courtiq` for the commands below. This is a development database password, not your GitHub or university password.

`.env` is ignored by Git; `.env.example` contains no password and is shareable. Do not paste the `.env` contents into PRs or screenshots. The database port defaults to `127.0.0.1:5432`; if that port is occupied, set `POSTGRES_PORT=5433` in `.env`. Docker's PostgreSQL port inside the container remains 5432.

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

Take screenshots of the healthy `docker compose ps` result and the successful query for your onboarding PR. There is no database coding or data loading task yet.

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

## Troubleshooting

| Problem | What to do |
| --- | --- |
| `docker` or `docker compose` not found | Finish Docker Desktop/Compose installation, reopen your terminal and repeat the version commands. |
| Cannot connect to Docker daemon / only Client shown | Launch Docker Desktop and wait for the engine. On Linux Engine, check the documented service/permission setup with a PM. |
| WSL 2 or virtualization error | Follow the Windows installer prerequisites; ask a PM if administrator or institution restrictions prevent setup. |
| No configuration file found | Enter the member worktree root containing `compose.yaml`; check `pwd` or PowerShell `Get-Location`. |
| `POSTGRES_PASSWORD` missing/empty | Open your local `.env` and set the password. Keep it private; do not edit `.env.example` to store it. |
| Port 5432 already allocated | Set `POSTGRES_PORT=5433` in `.env`, then rerun `docker compose up -d`. The container query command stays the same. |
| Service still starting or unhealthy | Wait briefly, rerun `docker compose ps`, then inspect `docker compose logs --tail=50 postgres`. Send relevant errors to the PM with secrets removed. |
| Image download fails | Check network/disk space and retry; avoid changing the PostgreSQL major version to work around a transient download failure. |
| Role/database does not exist after changing settings | Existing volumes retain their original initialization settings. Restore those settings or ask a PM; do not delete the volume. |
| SQL prompt does not show a result | Include the semicolon in `SELECT 1;`; use `\q` to exit. |
| PowerShell blocks venv activation | Use Command Prompt with `.venv\Scripts\activate.bat`, or ask a PM. |
| Python imports fail | Activate `.venv`, check `python -c "import sys; print(sys.executable)"`, and reinstall the pinned requirements. |

If blocked, comment on the assignment Issue with your OS, command and relevant error. Keep passwords/tokens out of shared output.
