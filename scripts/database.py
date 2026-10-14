"""Local PostgreSQL setup, fictional seed data, backups and safe recovery.

Uses Python's standard library and PostgreSQL tools already in the container.
Run with the local Python 3.12 venv. No host PostgreSQL client is required.
"""

import argparse
import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import io
import json
import os
from pathlib import Path
import plistlib
import re
import secrets
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BACKUPS = ROOT / "data/processed/backups"
FIXTURE = ROOT / "weekly/week0/player_stats_backup.csv"
VERSION = "synthetic-onboarding-v1"
FIELDS = ["PLAYER_ID", "PLAYER_NAME", "TEAM_ABBREVIATION", "SEASON", "GP",
          "PTS_TOTAL", "PTS_PER_GAME", "REB_PER_GAME", "AST_PER_GAME"]


def identifier(value):
    if not re.fullmatch(r"[a-z_][a-z0-9_]{0,62}", value):
        raise ValueError("Database/role names must be lowercase SQL identifiers (max 63 characters).")
    return '"' + value + '"'


def literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def settings(create=False):
    path = ROOT / ".env"
    if not path.exists():
        if not create:
            raise ValueError("Run: python scripts/database.py setup")
        with path.open("x", encoding="utf-8") as output:
            output.write((ROOT / ".env.example").read_text(encoding="utf-8"))
    text = path.read_text(encoding="utf-8")
    values = {}
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "=" not in line:
            raise ValueError("Invalid .env line; use KEY=value settings.")
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if key in values:
            raise ValueError(f"Duplicate .env setting: {key}")
        values[key] = value
    defaults = {"COMPOSE_PROJECT_NAME": "courtiq", "POSTGRES_USER": "courtiq",
                "POSTGRES_DB": "courtiq", "POSTGRES_PORT": "5432",
                "COURTIQ_APP_USER": "courtiq_app"}
    additions = []
    for key, default in defaults.items():
        if key not in values:
            values[key] = default
            additions.append(f"{key}={default}")
    for key in ("POSTGRES_PASSWORD", "COURTIQ_APP_PASSWORD"):
        if not values.get(key):
            if not create:
                raise ValueError(f"Missing {key}; run database.py setup.")
            values[key] = secrets.token_hex(32)
            if re.search(rf"^{key}=.*$", text, flags=re.M):
                text = re.sub(rf"^{key}=.*$", f"{key}={values[key]}", text, flags=re.M)
            else:
                additions.append(f"{key}={values[key]}")
        # Plain letters/digits avoid Compose interpolation and shell quoting surprises.
        if not re.fullmatch(r"[A-Za-z0-9_-]{16,}", values[key]):
            raise ValueError(f"{key} must contain at least 16 letters/digits/underscores/hyphens. "
                             "Do not change credentials on an existing volume without PM help.")
    for key in ("POSTGRES_USER", "POSTGRES_DB", "COURTIQ_APP_USER"):
        identifier(values[key])
    if values["POSTGRES_USER"] == values["COURTIQ_APP_USER"]:
        raise ValueError("The application role must differ from the administrator.")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,49}", values["COMPOSE_PROJECT_NAME"]):
        raise ValueError("Invalid COMPOSE_PROJECT_NAME.")
    if not values["POSTGRES_PORT"].isdigit() or not 1024 <= int(values["POSTGRES_PORT"]) <= 65535:
        raise ValueError("POSTGRES_PORT must be a nonprivileged port from 1024 to 65535.")
    if create:
        new_text = text.rstrip() + ("\n" + "\n".join(additions) if additions else "") + "\n"
        path.write_text(new_text, encoding="utf-8")
    path.chmod(0o600)
    return values


class Database:
    def __init__(self, config):
        self.config = config
        self.env = os.environ.copy()
        for key in list(self.env):
            if key.startswith(("POSTGRES_", "COURTIQ_", "COMPOSE_")):
                self.env.pop(key)
        self.compose = [shutil.which("docker") or "docker", "compose", "--project-directory", str(ROOT),
                        "--env-file", str(ROOT / ".env"), "-f", str(ROOT / "compose.yaml")]

    def clean_error(self, message):
        for key in ("POSTGRES_PASSWORD", "COURTIQ_APP_PASSWORD"):
            message = message.replace(self.config[key], "[REDACTED]")
        return message.strip()[-1800:]

    def run(self, args, input=None, output=None, timeout=180):
        source = {"stdin": input} if hasattr(input, "read") else {"input": input}
        result = subprocess.run(self.compose + args, **source, stdout=output or subprocess.PIPE,
                                stderr=subprocess.PIPE, env=self.env, cwd=ROOT, timeout=timeout)
        if result.returncode:
            error = result.stderr.decode(errors="replace")
            raise RuntimeError(self.clean_error(error) or "Docker/PostgreSQL command failed.")
        if result.stderr:
            print(self.clean_error(result.stderr.decode(errors="replace")), file=sys.stderr)
        return result.stdout or b""

    def client(self, program, args, payload=b"", app=False, output=None):
        user = self.config["COURTIQ_APP_USER" if app else "POSTGRES_USER"]
        password = self.config["COURTIQ_APP_PASSWORD" if app else "POSTGRES_PASSWORD"]
        # Password enters through stdin, never through process arguments or logged commands.
        command = 'IFS= read -r PGPASSWORD; export PGPASSWORD; exec "$@"'
        arguments = ["exec", "-T", "postgres", "sh", "-c", command, "sh", program,
                     "--host=127.0.0.1", "--port=5432", "--username=" + user, "--no-password", *args]
        if isinstance(payload, Path):
            with tempfile.TemporaryFile() as source, payload.open("rb") as archive:
                source.write(password.encode() + b"\n")
                shutil.copyfileobj(archive, source)
                source.seek(0)
                return self.run(arguments, source, output)
        return self.run(arguments, password.encode() + b"\n" + payload, output)

    def sql(self, query, database=None, app=False):
        return self.client("psql", ["-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1",
                                   "--dbname=" + (database or self.config["POSTGRES_DB"])],
                           query.encode(), app=app).decode().strip()

    def start(self):
        self.run(["config", "-q"])
        config = json.loads(self.run(["config", "--format", "json"]))
        ports = config["services"]["postgres"]["ports"]
        if any(port.get("host_ip") != "127.0.0.1" for port in ports):
            raise ValueError("Refusing to start a database exposed beyond localhost.")
        self.run(["up", "-d"], timeout=300)
        container = self.run(["ps", "-q", "postgres"]).decode().strip()
        for _ in range(90):
            result = subprocess.run([self.compose[0], "inspect", "--format",
                                     "{{.State.Health.Status}}", container],
                                    capture_output=True, env=self.env)
            if result.returncode == 0 and result.stdout.strip() == b"healthy":
                self.sql("SELECT 1;")  # Validate the .env password, not just readiness.
                print("PostgreSQL healthy; administrator password authentication passed.")
                return
            time.sleep(1)
        raise RuntimeError("Database not healthy after 90 seconds; inspect docker compose logs.")

    def permissions(self, database=None):
        target = database or self.config["POSTGRES_DB"]
        role = identifier(self.config["COURTIQ_APP_USER"])
        exists = self.sql("SELECT 1 FROM pg_roles WHERE rolname = " + literal(self.config["COURTIQ_APP_USER"]) + ";")
        if exists:
            unsafe = self.sql("SELECT rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls "
                              "OR EXISTS (SELECT 1 FROM pg_auth_members WHERE member = r.oid) "
                              "OR EXISTS (SELECT 1 FROM pg_database WHERE datdba = r.oid) "
                              "OR EXISTS (SELECT 1 FROM pg_namespace WHERE nspowner = r.oid) "
                              "OR EXISTS (SELECT 1 FROM pg_class WHERE relowner = r.oid) "
                              "FROM pg_roles r WHERE rolname = " + literal(self.config["COURTIQ_APP_USER"]) + ";")
            if unsafe == "t":
                raise ValueError("Existing application role has elevated rights/ownership; ask a PM before changing it.")
        action = "ALTER" if exists else "CREATE"
        self.sql(f"{action} ROLE {role} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE "
                 f"NOINHERIT NOREPLICATION NOBYPASSRLS PASSWORD {literal(self.config['COURTIQ_APP_PASSWORD'])};\n"
                 f"ALTER ROLE {role} SET default_transaction_read_only = on;\n"
                 f"ALTER ROLE {role} SET statement_timeout = '15s';")
        self.sql(f"REVOKE ALL ON DATABASE {identifier(target)} FROM PUBLIC;\n"
                 f"GRANT CONNECT ON DATABASE {identifier(target)} TO {role};\n"
                 "REVOKE CREATE ON SCHEMA public FROM PUBLIC;\n"
                 f"REVOKE ALL ON SCHEMA public FROM {role};\n"
                 "REVOKE ALL ON SCHEMA courtiq FROM PUBLIC;\n"
                 f"REVOKE ALL ON ALL TABLES IN SCHEMA courtiq FROM PUBLIC, {role};\n"
                 f"GRANT USAGE ON SCHEMA courtiq TO {role};\n"
                 f"GRANT SELECT ON ALL TABLES IN SCHEMA courtiq TO {role};\n"
                 f"ALTER DEFAULT PRIVILEGES IN SCHEMA courtiq GRANT SELECT ON TABLES TO {role};",
                 database=target)


def fixture_rows():
    with FIXTURE.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != FIELDS:
            raise ValueError("The supplied fixture columns have changed; review before loading.")
        rows = list(reader)
    if not rows:
        raise ValueError("The supplied fixture is empty.")
    keys = set()
    for row in rows:
        if set(row) != set(FIELDS):
            raise ValueError("Fixture contains extra/missing columns.")
        if any(not row[field] or "\n" in row[field] or "\r" in row[field] for field in FIELDS):
            raise ValueError("Fixture contains missing/multiline fields.")
        key = (row["SEASON"], row["PLAYER_ID"])
        if key in keys or row["SEASON"] != "SYNTHETIC-01":
            raise ValueError("Fixture contains duplicate keys or unexpected provenance.")
        keys.add(key)
        try:
            for field in FIELDS[4:]:
                number = Decimal(row[field])
                if not number.is_finite() or number < 0:
                    raise ValueError("Fixture metrics must be finite and nonnegative.")
                if field in ("GP", "PTS_TOTAL") and number != number.to_integral_value():
                    raise ValueError("Games and total points must be integers.")
        except InvalidOperation as exc:
            raise ValueError("Fixture contains nonnumeric metrics.") from exc
    return rows


def load_demo(db):
    rows = fixture_rows()  # Validate before changing anything.
    if db.sql("SELECT to_regclass('courtiq.player_season_stats') IS NOT NULL;") == "t":
        backup(db)
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerows([VERSION, "synthetic", *[row[field] for field in FIELDS]] for row in rows)
    schema = (ROOT / "scripts/database.sql").read_text(encoding="utf-8")
    db.sql("BEGIN;\nSELECT pg_advisory_xact_lock(hashtext('courtiq-demo-loader'));\n" + schema + "\n"
           "CREATE TEMP TABLE fixture_load (LIKE courtiq.player_season_stats INCLUDING DEFAULTS);\n"
           "COPY fixture_load FROM STDIN WITH (FORMAT csv);\n" + buffer.getvalue() + "\\.\n"
           "INSERT INTO courtiq.player_season_stats SELECT * FROM fixture_load\n"
           "ON CONFLICT (dataset_version, season, player_id) DO UPDATE SET\n"
           "source=EXCLUDED.source, player_name=EXCLUDED.player_name,\n"
           "team_abbreviation=EXCLUDED.team_abbreviation, gp=EXCLUDED.gp, pts_total=EXCLUDED.pts_total,\n"
           "pts_per_game=EXCLUDED.pts_per_game, reb_per_game=EXCLUDED.reb_per_game,\n"
           "ast_per_game=EXCLUDED.ast_per_game;\nCOMMIT;")
    db.permissions()
    count = int(db.sql("SELECT count(*) FROM courtiq.player_season_stats WHERE dataset_version = " + literal(VERSION) + ";"))
    if count != len(rows):
        raise RuntimeError("Loaded dataset count differs from the fixture; existing rows were preserved.")
    print(f"Loaded {count} fictional rows ({VERSION}); repeated loads update matching keys, never delete rows.")


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def checked_manifest(archive, database):
    try:
        metadata = json.loads(archive.with_suffix(".json").read_text())
        if (not isinstance(metadata, dict) or metadata.get("format") != "postgres-custom"
                or metadata.get("database") != database
                or not isinstance(metadata.get("sha256"), str)
                or not re.fullmatch(r"[a-f0-9]{64}", metadata["sha256"])
                or not isinstance(metadata.get("bytes"), int)):
            raise ValueError("Invalid backup metadata.")
        created = datetime.fromisoformat(metadata["created_at"])
        if created.tzinfo is None:
            raise ValueError("Backup timestamp must include its timezone.")
        if digest(archive) != metadata["sha256"] or archive.stat().st_size != metadata["bytes"]:
            raise ValueError("Backup integrity check failed.")
        return metadata
    except (OSError, TypeError, KeyError, ValueError) as exc:
        raise ValueError("Backup/manifest is missing, malformed or corrupt; refusing to use it.") from exc


def backup(db, if_due=False):
    BACKUPS.mkdir(parents=True, exist_ok=True)
    BACKUPS.chmod(0o700)
    name = db.config["POSTGRES_DB"]
    if if_due:
        for manifest in sorted(BACKUPS.glob(name + "_*.json"), reverse=True):
            try:
                archive = manifest.with_suffix(".dump")
                metadata = checked_manifest(archive, name)
                created = datetime.fromisoformat(metadata["created_at"])
                if timedelta(0) <= datetime.now(timezone.utc) - created < timedelta(hours=24):
                    print("Verified local backup is less than 24 hours old; no new backup needed.")
                    return archive
            except ValueError:
                continue
    now = datetime.now(timezone.utc)
    stem = name + "_" + now.strftime("%Y%m%dT%H%M%S%fZ")
    archive = BACKUPS / (stem + ".dump")
    partial = BACKUPS / (stem + ".partial")
    try:
        with partial.open("xb") as output:
            db.client("pg_dump", ["--dbname=" + name, "--format=custom", "--no-owner", "--no-privileges"], output=output)
            output.flush()
            os.fsync(output.fileno())
        with partial.open("rb") as source:
            db.run(["exec", "-T", "postgres", "pg_restore", "--list"], input=source)
        partial.rename(archive)
        metadata = {"created_at": now.isoformat(), "database": name, "format": "postgres-custom",
                    "sha256": digest(archive), "bytes": archive.stat().st_size,
                    "credentials_included": False}
        with archive.with_suffix(".json").open("x", encoding="utf-8") as output:
            json.dump(metadata, output, indent=2)
        archive.chmod(0o600)
        print(f"Backup saved and archive checked: {archive}")
        return archive
    except Exception:
        partial.unlink(missing_ok=True)
        raise


def restore(db, archive, target):
    identifier(target)
    if target == db.config["POSTGRES_DB"]:
        raise ValueError("Restore requires a NEW recovery database; the active database is never overwritten.")
    archive = Path(archive).expanduser().resolve()
    checked_manifest(archive, db.config["POSTGRES_DB"])
    if db.sql("SELECT 1 FROM pg_database WHERE datname = " + literal(target) + ";"):
        raise ValueError("Recovery database already exists; choose a new name. Nothing was overwritten.")
    with archive.open("rb") as source:
        db.run(["exec", "-T", "postgres", "pg_restore", "--list"], input=source)
    db.sql(f"CREATE DATABASE {identifier(target)} TEMPLATE template0;")
    db.client("pg_restore", ["--dbname=" + target, "--no-owner", "--no-privileges",
                             "--exit-on-error", "--single-transaction"], archive)
    db.permissions(database=target)
    count = db.sql("SELECT count(*) FROM courtiq.player_season_stats;", database=target, app=True)
    print(f"Recovery database {target} restored; read-only application can read {count} rows. Original unchanged.")


def status(db):
    print(db.run(["ps"]).decode().strip())
    result = db.sql("SELECT json_build_object('database', current_database(), 'role', current_user,\n"
                    "'rows', count(*), 'dataset_versions', array_agg(DISTINCT dataset_version),\n"
                    "'sources', array_agg(DISTINCT source)) FROM courtiq.player_season_stats;", app=True)
    print("Read-only application connection:", result)
    print("Backups directory:", BACKUPS)
    archives = sorted(BACKUPS.glob(db.config["POSTGRES_DB"] + "_*.dump"))
    valid = []
    for archive in archives:
        try:
            metadata = checked_manifest(archive, db.config["POSTGRES_DB"])
            valid.append((archive.name, metadata["created_at"]))
        except ValueError:
            print("WARNING: incomplete/corrupt backup:", archive.name)
    print("Latest verified backup:", valid[-1] if valid else "NONE — run database.py backup")


def schedule(db):
    """Install a per-user hourly check; create a backup when the last is 24h old."""
    if sys.prefix == sys.base_prefix:
        raise ValueError("Activate the project .venv before installing automatic backups.")
    logs = BACKUPS / "scheduler.log"
    BACKUPS.mkdir(parents=True, exist_ok=True)
    program = [sys.executable, str(ROOT / "scripts/database.py"), "backup", "--if-due"]
    project = db.config["COMPOSE_PROJECT_NAME"]
    if sys.platform == "darwin":
        label = "org.courtiq.backup." + project
        path = Path.home() / "Library/LaunchAgents" / (label + ".plist")
        content = plistlib.dumps({"Label": label, "ProgramArguments": program,
                                 "WorkingDirectory": str(ROOT), "RunAtLoad": True,
                                 "StartInterval": 3600, "EnvironmentVariables": {
                                     "PATH": os.pathsep.join(dict.fromkeys([
                                         str(Path(shutil.which("docker") or "/usr/local/bin/docker").parent),
                                         str(Path(sys.executable).parent), "/opt/homebrew/bin", "/usr/local/bin", "/usr/bin", "/bin"]))},
                                 "StandardOutPath": str(logs), "StandardErrorPath": str(logs)})
        path.parent.mkdir(parents=True, exist_ok=True)
        changed = path.exists() and path.read_bytes() != content
        if changed:
            existing = plistlib.loads(path.read_bytes())
            if (existing.get("Label") != label or existing.get("ProgramArguments") != program
                    or existing.get("WorkingDirectory") != str(ROOT)):
                raise ValueError(f"Existing backup job belongs to another checkout: {path}. Ask the PM before replacing it.")
        path.write_bytes(content)
        path.chmod(0o600)
        domain = f"gui/{os.getuid()}"
        loaded = subprocess.run(["launchctl", "print", domain + "/" + label], capture_output=True)
        if changed and loaded.returncode == 0:
            subprocess.run(["launchctl", "bootout", domain + "/" + label], check=True, capture_output=True)
        if loaded.returncode or changed:
            subprocess.run(["launchctl", "bootstrap", domain, str(path)], check=True, capture_output=True)
        print("Automatic backup check installed:", label)
    elif sys.platform == "win32":
        task = "CourtIQBackup-" + project
        existing = subprocess.run(["schtasks", "/Query", "/TN", task, "/XML"], capture_output=True)
        if existing.returncode == 0:
            parsed = ET.fromstring(existing.stdout)
            ns = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}
            action = parsed.find("t:Actions/t:Exec", ns)
            if (action is not None and action.findtext("t:Command", namespaces=ns) == program[0]
                    and action.findtext("t:Arguments", namespaces=ns) == subprocess.list2cmdline(program[1:])
                    and action.findtext("t:WorkingDirectory", namespaces=ns) == str(ROOT)
                    and parsed.findtext("t:Triggers/t:TimeTrigger/t:Repetition/t:Interval", namespaces=ns) == "PT1H"):
                print("Automatic backup check already installed:", task)
                return
            raise ValueError(f"Task {task} has different settings; inspect it rather than overwrite it.")
        ns = "http://schemas.microsoft.com/windows/2004/02/mit/task"
        ET.register_namespace("", ns)
        def element(parent, tag, text=None, **attrs):
            child = ET.SubElement(parent, "{" + ns + "}" + tag, attrs)
            child.text = text
            return child
        task_xml = ET.Element("{" + ns + "}Task", {"version": "1.2"})
        username = subprocess.check_output(["whoami"], text=True).strip()
        triggers = element(task_xml, "Triggers")
        trigger = element(triggers, "TimeTrigger")
        element(trigger, "StartBoundary", datetime.now().replace(microsecond=0).isoformat())
        repetition = element(trigger, "Repetition")
        element(repetition, "Interval", "PT1H")
        element(repetition, "StopAtDurationEnd", "false")
        element(element(triggers, "LogonTrigger"), "UserId", username)
        principal = element(element(task_xml, "Principals"), "Principal", id="Author")
        element(principal, "UserId", username)
        element(principal, "LogonType", "InteractiveToken")
        element(principal, "RunLevel", "LeastPrivilege")
        options = element(task_xml, "Settings")
        element(options, "MultipleInstancesPolicy", "IgnoreNew")
        element(options, "StartWhenAvailable", "true")
        element(options, "ExecutionTimeLimit", "PT10M")
        action = element(element(task_xml, "Actions", Context="Author"), "Exec")
        element(action, "Command", program[0])
        element(action, "Arguments", subprocess.list2cmdline(program[1:]))
        element(action, "WorkingDirectory", str(ROOT))
        with tempfile.TemporaryDirectory(prefix="courtiq-task-") as folder:
            path = Path(folder) / "task.xml"
            ET.ElementTree(task_xml).write(path, encoding="utf-16", xml_declaration=True)
            subprocess.run(["schtasks", "/Create", "/TN", task, "/XML", str(path)], check=True, capture_output=True)
        print("Automatic backup check installed:", task, "(inspect failures in Task Scheduler)")
    elif sys.platform.startswith("linux"):
        if not shutil.which("crontab"):
            raise ValueError("Install/enable your distribution's cron service, then run database.py schedule.")
        existing = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if existing.returncode not in (0, 1):
            raise RuntimeError("Cannot read the current user's crontab.")
        marker = "# CourtIQ backup " + project
        command = " ".join(shlex.quote(part) for part in program) + " >> " + shlex.quote(str(logs)) + " 2>&1"
        line = "0 * * * * " + command.replace("%", "\\%") + " " + marker
        matches = [item for item in existing.stdout.splitlines() if marker in item]
        if matches and matches != [line]:
            raise ValueError("A different CourtIQ cron job already exists; ask the PM before replacing it.")
        if not matches:
            subprocess.run(["crontab", "-"], input=existing.stdout.rstrip() + "\n" + line + "\n",
                           text=True, check=True, capture_output=True)
        print("Automatic backup check installed in your crontab.")
    else:
        raise ValueError("Automatic scheduling is supported on macOS, Windows and Linux.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("setup", help="Generate private settings, start, seed, back up and schedule")
    setup.add_argument("--no-schedule", action="store_true", help="Skip host job installation (e.g. disposable tests)")
    commands.add_parser("load-demo", help="Back up, then reload the fictional fixture without deleting other rows")
    commands.add_parser("status", help="Verify read-only access, starter row counts and backup location")
    backups = commands.add_parser("backup", help="Create a checked local pg_dump archive")
    backups.add_argument("--if-due", action="store_true", help="Skip if a verified backup is under 24 hours old")
    recovery = commands.add_parser("restore", help="Restore our archive into a NEW recovery database")
    recovery.add_argument("archive", help="Path to .dump (matching .json manifest required)")
    recovery.add_argument("--database", required=True, help="New recovery database name; existing databases are refused")
    commands.add_parser("schedule", help="Install per-user automatic daily backup checks")
    args = parser.parse_args()
    if os.name != "nt":
        os.umask(0o077)
    db = Database(settings(create=args.command == "setup"))
    try:
        if args.command == "setup":
            db.start()
            load_demo(db)
            backup(db)
            status(db)
            if not args.no_schedule:
                schedule(db)
        elif args.command == "load-demo":
            load_demo(db)
            backup(db)
        elif args.command == "status":
            status(db)
        elif args.command == "backup":
            backup(db, args.if_due)
        elif args.command == "restore":
            restore(db, args.archive, args.database)
        elif args.command == "schedule":
            schedule(db)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        raise RuntimeError(db.clean_error(str(exc))) from None


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print("ERROR:", str(exc), file=sys.stderr)
        sys.exit(1)
