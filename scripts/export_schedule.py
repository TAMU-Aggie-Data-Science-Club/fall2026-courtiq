"""Export the supplied league schedule for offline fixture selection."""
import csv
import gzip
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def export_schedule():
    fixtures = {}
    for path in sorted((ROOT / "data/raw/kaggle").glob("LeagueSchedule*.csv")):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                row = {key.lower(): value for key, value in row.items()}
                if row["gameid"].zfill(10).startswith("002") and row["hometeamid"] not in ("", "0") and row["awayteamid"] not in ("", "0"):
                    fixtures[row["gameid"]] = (row["gamedatetimeest"][:10], row["hometeamid"], row["awayteamid"])
    if fixtures:
        with gzip.open(ROOT / "app_data/schedule.csv.gz", "wt", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["game_id", "date", "home_team_id", "away_team_id"])
            writer.writerows((key, *fixtures[key]) for key in sorted(fixtures))


if __name__ == "__main__":
    export_schedule()

