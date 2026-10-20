"""Offline checks of supplied inputs/cache safety, not completion of student TODOs."""

import json
from contextlib import redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from src import data
from scripts import fetch_data


class StarterChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        quiet = redirect_stdout(io.StringIO())
        quiet.__enter__()
        self.addCleanup(quiet.__exit__, None, None, None)
        root = Path(self.directory.name)
        for module in (data, fetch_data):
            override = patch.object(module, "RAW", root)
            override.start()
            self.addCleanup(override.stop)

    def mock_response(self):
        frame, _ = data.practice_data("players")
        # Invented records in a disposable mock response, never a real NBA fixture.
        return json.dumps({"resultSets": [{"headers": frame.columns.tolist(),
                                          "rowSet": frame.astype(object).where(frame.notna(), None).values.tolist()}]})

    def test_practice_is_explicit_and_conversion_preserves_input(self):
        for kind in data.FIELDS:
            raw, metadata = data.load_snapshot(kind, demo=True)
            original = raw.copy(deep=True)
            table = data.component_table(raw, metadata)
            self.assertIn("SYNTHETIC", metadata["source"])
            self.assertIsNone(metadata["retrieved_at"])
            self.assertEqual(set(table.SEASON), {"SYNTHETIC-01"})
            pd.testing.assert_frame_equal(raw, original)

    def test_missing_real_input_never_fetches_or_falls_back(self):
        with patch.object(fetch_data.leaguedashplayerstats, "LeagueDashPlayerStats") as endpoint:
            with self.assertRaisesRegex(ValueError, "No players snapshot"):
                data.load_snapshot("players")
            endpoint.assert_not_called()

    def test_cache_replay_and_failed_refresh_preserve_snapshot(self):
        with patch.object(fetch_data.leaguedashplayerstats, "LeagueDashPlayerStats") as endpoint:
            endpoint.return_value.get_json.return_value = self.mock_response()
            fetch_data.prepare("players")
            endpoint.assert_called_once()
            parameters = endpoint.call_args.kwargs
            self.assertEqual(parameters["season"], "2025-26")
            self.assertEqual(parameters["per_mode_detailed"], "PerGame")
            path = data.RAW / "players_2025-26.json"
            original = path.read_bytes()
            fetch_data.prepare("players")
            endpoint.assert_called_once()  # Cache replay makes no second call.
            endpoint.side_effect = TimeoutError("simulated outage")
            with self.assertRaises(TimeoutError):
                fetch_data.prepare("players", refresh=True)
            self.assertEqual(path.read_bytes(), original)
            frame, _ = data.load_snapshot("players")
            self.assertEqual(len(frame), 4)

    def test_corrupt_response_does_not_replace_valid_cache(self):
        with patch.object(fetch_data.leaguedashplayerstats, "LeagueDashPlayerStats") as endpoint:
            endpoint.return_value.get_json.return_value = self.mock_response()
            fetch_data.prepare("players")
            path = data.RAW / "players_2025-26.json"
            original = path.read_bytes()
            endpoint.return_value.get_json.return_value = '{"resultSets": [{"headers": [], "rowSet": []}]}'
            with self.assertRaises(ValueError):
                fetch_data.prepare("players", refresh=True)
            self.assertEqual(path.read_bytes(), original)

    def test_modified_snapshot_is_rejected(self):
        with patch.object(fetch_data.leaguedashplayerstats, "LeagueDashPlayerStats") as endpoint:
            endpoint.return_value.get_json.return_value = self.mock_response()
            fetch_data.prepare("players")
        path = data.RAW / "players_2025-26.json"
        path.write_text(path.read_text() + " ", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "metadata"):
            data.load_snapshot("players")

    def test_wrong_units_in_metadata_are_rejected(self):
        with patch.object(fetch_data.leaguedashplayerstats, "LeagueDashPlayerStats") as endpoint:
            endpoint.return_value.get_json.return_value = self.mock_response()
            fetch_data.prepare("players")
        path = data.RAW / "players_2025-26.meta.json"
        metadata = json.loads(path.read_text())
        metadata["parameters"]["per_mode_detailed"] = "Totals"
        path.write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "parameters"):
            data.load_snapshot("players")


if __name__ == "__main__":
    print("OFFLINE starter-support checks only. Student TODOs and real NBA acceptance are separate.")
    unittest.main()
