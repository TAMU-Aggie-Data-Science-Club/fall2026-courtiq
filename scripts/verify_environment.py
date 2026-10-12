"""Run from the repository root: python scripts/verify_environment.py."""

import importlib
import importlib.metadata
from pathlib import Path
import sys


def main():
    print(f"Python: {sys.version.split()[0]}\nInterpreter: {sys.executable}")
    failures = []
    if sys.version_info[:2] != (3, 12):
        failures.append("Use Python 3.12 to create the virtual environment.")
    if sys.prefix == sys.base_prefix:
        failures.append("Activate the repository's .venv before running this check.")

    root = Path(__file__).resolve().parents[1]
    for line in (root / "requirements.txt").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        package, expected = line.split("==")
        try:
            importlib.import_module(package)
            actual = importlib.metadata.version(package)
            print(f"{package}: {actual}")
            if actual != expected:
                failures.append(f"{package}: expected {expected}, found {actual}.")
        except (ImportError, importlib.metadata.PackageNotFoundError) as exc:
            failures.append(f"{package}: {exc}")

    try:
        import pandas as pd
        import plotly.express as px

        fixture = root / "tests/fixtures/synthetic_player_stats.csv"
        frame = pd.read_csv(fixture)
        # A smoke check only; the member's filtering/ranking exercise stays unanswered.
        fig = px.bar(frame.head(2), x="PLAYER_NAME", y="PTS_PER_GAME")
        assert len(fig.data[0].x) == 2
        print("Local synthetic fixture and Plotly figure creation: OK")
    except Exception as exc:
        failures.append(f"Fixture/Plotly check: {exc}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("PASS: environment imports and local smoke check (no live NBA requests).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
