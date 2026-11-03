"""Provided bounded classroom requests; run explicitly, never from Streamlit."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import time

import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats, leaguedashteamstats

from src.data import FIELDS, RAW, SEASON, load_snapshot


def prepare(kind, refresh=False):
    path = RAW / f"{kind}_{SEASON}.json"
    if path.exists() and not refresh:
        frame, metadata = load_snapshot(kind)
        print(f"Reused {kind}: {len(frame)} rows, retrieved {metadata['retrieved_at']}")
        return
    parameters = {"season": SEASON, "season_type_all_star": "Regular Season",
                  "per_mode_detailed": "PerGame", "timeout": 20,
                  "measure_type_detailed_defense": "Advanced" if kind == "ratings" else "Base"}
    endpoint = (leaguedashplayerstats.LeagueDashPlayerStats if kind == "players"
                else leaguedashteamstats.LeagueDashTeamStats)
    # One call per requested kind, no automatic retries. Library defaults are unchanged.
    response = endpoint(**parameters)
    raw_text = response.get_json()
    payload = json.loads(raw_text)
    results = payload["resultSets"]
    result = results[0] if isinstance(results, list) else results
    frame = pd.DataFrame(result["rowSet"], columns=result["headers"])
    missing = set(FIELDS[kind]) - set(frame.columns)
    if frame.empty or missing:
        raise ValueError(f"No usable {kind} response; missing fields: {sorted(missing)}")
    metadata = {"source": "NBA.com via nba_api", "kind": kind, "season": SEASON,
                "season_type": "Regular Season", "parameters": parameters,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "sha256": hashlib.sha256(raw_text.encode()).hexdigest()}
    RAW.mkdir(parents=True, exist_ok=True)
    # Validate the new response before replacing either file. A request failure writes nothing.
    temporary = path.with_suffix(".partial")
    temporary.write_text(raw_text, encoding="utf-8")
    meta_path = path.with_suffix(".meta.json")
    meta_temporary = meta_path.with_suffix(".partial")
    meta_temporary.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    temporary.replace(path)
    meta_temporary.replace(meta_path)
    print(f"Saved {kind}: {len(frame)} NBA rows → {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kinds", nargs="+", choices=list(FIELDS))
    parser.add_argument("--refresh", action="store_true", help="Deliberately replace matching snapshots")
    args = parser.parse_args()
    kinds = list(dict.fromkeys(args.kinds))
    for index, kind in enumerate(kinds):
        if index:
            time.sleep(3)  # Conservative spacing, not an official rate allowance.
        try:
            prepare(kind, args.refresh)
        except Exception as exc:
            parser.exit(1, f"{kind} collection failed ({type(exc).__name__}: {exc}). "
                        "Do not loop/retry or change sources; post the error to the Issue.\n")


if __name__ == "__main__":
    main()
