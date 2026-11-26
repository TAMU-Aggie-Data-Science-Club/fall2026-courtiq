"""Export older cleaned game logs for the On/Off Impact trend chart."""
import pandas as pd

from src.pipeline import APP, PROCESSED


def export_impact_history():
    columns = {
        "player_games": ["game_id", "player_id", "team_id", "season", "date", "played", "minutes", "plus_minus"],
        "team_games": ["game_id", "team_id", "season", "date", "margin", "duration"],
    }
    exports = {}
    for name, fields in columns.items():
        source = pd.read_csv(PROCESSED / f"{name}.csv.gz", usecols=["season_start", *fields])
        bundled = pd.read_csv(APP / f"{name}.csv.gz", usecols=["season_start"])
        older = source.season_start.lt(bundled.season_start.min())
        exports[name] = source.loc[older, fields]

    for name, frame in exports.items():
        frame.to_csv(APP / f"impact_history_{name}.csv.gz", index=False,
                     compression={"method": "gzip", "mtime": 0})
        print(f"{name}: {len(frame):,} older rows exported")


if __name__ == "__main__":
    export_impact_history()
