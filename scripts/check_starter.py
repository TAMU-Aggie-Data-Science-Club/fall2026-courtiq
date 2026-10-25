"""Offline checks of supplied inputs/cache safety, not completion of student TODOs."""

import hashlib
import json
from contextlib import redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from src import data
from scripts import fetch_data, preview_component


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

    def test_malformed_parameters_give_actionable_error(self):
        with patch.object(fetch_data.leaguedashplayerstats, "LeagueDashPlayerStats") as endpoint:
            endpoint.return_value.get_json.return_value = self.mock_response()
            fetch_data.prepare("players")
        path = data.RAW / "players_2025-26.meta.json"
        metadata = json.loads(path.read_text())
        metadata["parameters"] = None
        path.write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "ask Cemal"):
            data.load_snapshot("players")

    def test_empty_response_gives_actionable_error(self):
        with patch.object(fetch_data.leaguedashplayerstats, "LeagueDashPlayerStats") as endpoint:
            endpoint.return_value.get_json.return_value = self.mock_response()
            fetch_data.prepare("players")
        path = data.RAW / "players_2025-26.json"
        raw_text = '{"resultSets": []}'
        path.write_text(raw_text, encoding="utf-8")
        meta_path = path.with_suffix(".meta.json")
        metadata = json.loads(meta_path.read_text())
        metadata["sha256"] = hashlib.sha256(raw_text.encode()).hexdigest()
        meta_path.write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Malformed players snapshot; ask Cemal"):
            data.load_snapshot("players")

    def test_unavailable_chart_does_not_claim_completion_or_overwrite_old_preview(self):
        root = Path(self.directory.name)
        previous = root / "data/processed/week1/player-chart.html"
        previous.parent.mkdir(parents=True)
        previous.write_text("previous preview", encoding="utf-8")
        output = io.StringIO()
        with patch.object(preview_component, "ROOT", root), redirect_stdout(output):
            preview_component.save_result(None, "player-chart", {})
        self.assertIn("NO OUTPUT", output.getvalue())
        self.assertIn("earlier preview file is unchanged", output.getvalue())
        self.assertEqual(previous.read_text(), "previous preview")
        self.assertFalse(previous.with_suffix(".meta.json").exists())

    def test_exported_chart_keeps_source_time_and_metadata(self):
        _, metadata = data.practice_data("players")
        with patch.object(preview_component, "ROOT", Path(self.directory.name)):
            preview_component.save_result(preview_component.Figure(), "player-chart", metadata)
        path = Path(self.directory.name) / "data/processed/week1/player-chart.html"
        html = path.read_text(encoding="utf-8")
        self.assertIn("SYNTHETIC", html)
        self.assertIn("Retrieved: not applicable (practice)", html)
        self.assertEqual(json.loads(path.with_suffix(".meta.json").read_text()), metadata)

    def test_chart_preview_defaults_to_an_eligible_player(self):
        raw, metadata = data.practice_data("players")
        raw = raw.iloc[[2, 0, 1, 3]].reset_index(drop=True)  # First player has only 19 games.
        with (patch("sys.argv", ["preview_component", "player-chart", "--demo"]),
              patch.object(data, "load_snapshot", return_value=(raw, metadata)),
              patch.object(preview_component.charts, "player_scoring_distribution", return_value=None) as chart):
            preview_component.main()
        selected = chart.call_args.args[1]
        self.assertEqual(selected, 101)


if __name__ == "__main__":
    print("OFFLINE starter-support checks only. Student TODOs and real NBA acceptance are separate.")
    unittest.main()
