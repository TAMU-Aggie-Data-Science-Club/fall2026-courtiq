"""Real exported-data, model and Streamlit smoke checks (no network)."""
from datetime import datetime,timezone
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch,Mock
import pandas as pd
from src.pipeline import APP
from src.models import team,player
from src.models.common import load
from src.odds_api import refresh


class OddsTests(unittest.TestCase):
    def test_missing_key(self):
        with tempfile.TemporaryDirectory() as folder,patch("src.odds_api.APP",Path(folder)),patch.dict("os.environ",{},clear=True):
            with self.assertRaises(ValueError): refresh()

    def test_cache_and_empty(self):
        response=Mock(status_code=200,headers={"x-requests-remaining":"497"})
        response.json.return_value=[]
        session=Mock(); session.get.return_value=response
        with tempfile.TemporaryDirectory() as folder,patch("src.odds_api.APP",Path(folder)):
            table,msg=refresh("private-test-key",session=session)
            self.assertTrue(table.empty)
            refresh("private-test-key",session=session)
            self.assertEqual(session.get.call_count,1)
            self.assertNotIn("private-test-key",msg)

    def test_errors(self):
        with tempfile.TemporaryDirectory() as folder,patch("src.odds_api.APP",Path(folder)):
            for code in [401,429,500]:
                session=Mock(); session.get.return_value=Mock(status_code=code)
                with self.assertRaises(ValueError): refresh("secret",session=session)
            session=Mock(); session.get.return_value=Mock(status_code=200,headers={})
            session.get.return_value.json.return_value={"bad":True}
            with self.assertRaises(ValueError): refresh("secret",session=session)


@unittest.skipUnless((APP/"manifest.json").exists(),"Real exports not built")
class RealTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t=pd.read_csv(APP/"team_games.csv.gz",parse_dates=["date"])
        cls.p=pd.read_csv(APP/"player_games.csv.gz",parse_dates=["date"],low_memory=False)

    def test_team_predictions(self):
        ids=self.t.team_id.unique()
        when=self.t.date.max()+pd.Timedelta(days=1)
        r=team.predict(self.t,ids[0],ids[1],when,-4.5)
        self.assertAlmostEqual(r["home_win"]+r["away_win"],1)
        self.assertAlmostEqual(r["home_score"]-r["away_score"],r["margin"])
        self.assertAlmostEqual(r["home_score"]+r["away_score"],r["total"])
        self.assertEqual(r["distribution"]["push"],0)
        with self.assertRaises(ValueError): team.predict(self.t,ids[0],ids[0],when)
        with self.assertRaises(ValueError): team.predict(self.t,ids[0],ids[1],"2020-01-01")

    def test_player_predictions(self):
        who=self.p[self.p.played].iloc[-1]
        result,bundle=player.predict(self.p,self.t,who.player_id,who.opponent_id,self.p.date.max()+pd.Timedelta(days=1),False)
        self.assertEqual(result.stat.tolist(),["points","rebounds","assists"])
        self.assertTrue(result.prediction.ge(0).all())
        self.assertTrue(result.high.ge(result.low).all())

    def test_app_pages(self):
        from streamlit.testing.v1 import AppTest
        for page in ["Players","Teams","Compare","Trends"]:
            at=AppTest.from_file("app.py",default_timeout=40).run()
            at.sidebar.radio[0].set_value(page).run()
            self.assertEqual(len(at.exception),0,str(at.exception))
        at=AppTest.from_file("app.py",default_timeout=40).run()
        next(widget for widget in at.radio if widget.label=="Player tools").set_value("On/Off Impact").run()
        self.assertEqual(len(at.exception),0,str(at.exception))

    def test_prediction_buttons(self):
        from streamlit.testing.v1 import AppTest
        at=AppTest.from_file("app.py",default_timeout=60).run()
        at.sidebar.radio[0].set_value("Teams").run()
        at.button[0].click().run()
        self.assertEqual(len(at.exception),0,str(at.exception))
        self.assertEqual(len(at.metric),4,"Prediction must actually render, not only show an error message")
        at.sidebar.radio[0].set_value("Compare").run()
        at.button[0].click().run()
        self.assertEqual(len(at.exception),0,str(at.exception))
        self.assertTrue(any("Recorded opposing-player encounters" in str(item.value) for item in at.markdown))

    def test_impact_uses_selected_team_stint(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file("app.py", default_timeout=40).run()
        next(widget for widget in app.radio if widget.label == "Player tools").set_value("On/Off Impact").run()
        season = app.selectbox(key="impact_season").value
        rows = pd.read_csv(APP / "on_off.csv.gz").query("season == @season")
        complete = rows.dropna(subset=["on_per48", "off_per48"])
        qualifying = complete.query("games >= 20 and minutes_on >= 500")
        stint_counts = qualifying.groupby("player_id").team_id.nunique()
        player_id = int(stint_counts[stint_counts > 1].index[0])
        stints = qualifying.loc[qualifying.player_id.eq(player_id)]
        teams = pd.read_csv(APP / "teams.csv.gz").set_index("team_id").team_name

        for expected in stints.itertuples():
            app.selectbox(key="impact_team_filter").set_value(int(expected.team_id)).run()
            app.selectbox(key="impact_player").set_value(player_id).run()
            self.assertFalse(app.exception)
            identity = next(item.proto.body for item in app.get("html") if 'class="impact-identity"' in item.proto.body)
            self.assertIn(teams[expected.team_id], identity)
            chart = json.loads(app.get("plotly_chart")[0].proto.spec)
            self.assertEqual(chart["data"][0]["y"], ["On court", "On bench"])
            self.assertAlmostEqual(chart["data"][0]["x"][0], expected.on_per48)
            self.assertAlmostEqual(chart["data"][0]["x"][1], expected.off_per48)
            scatter = json.loads(app.get("plotly_chart")[-1].proto.spec)
            traces = {trace["name"]: trace for trace in scatter["data"]}
            team_names = sorted(stints.team_id.map(teams))
            number = str(team_names.index(teams[expected.team_id]) + 1)
            self.assertEqual(traces["Stint shown above"]["text"], [number])
            self.assertFalse(traces["Stint shown above"]["showlegend"])
            self.assertFalse(traces["Other stints for this player"]["showlegend"])
            self.assertCountEqual(traces["Other stints for this player"]["text"],
                                  [str(i + 1) for i, name in enumerate(team_names)
                                   if name != teams[expected.team_id]])
            self.assertFalse(scatter["layout"].get("annotations"))
            key = next(item.proto.body for item in app.get("html") if 'class="impact-stint-key"' in item.proto.body)
            self.assertIn(f">{number}</b>{teams[expected.team_id]}<small>· Shown above</small>", key)

        no_missed = complete.loc[complete.games_missed.eq(0) & complete.valid_on_games.ge(10)].iloc[0]
        app.selectbox(key="impact_team_filter").set_value(int(no_missed.team_id)).run()
        app.selectbox(key="impact_player").set_value(int(no_missed.player_id)).run()
        self.assertFalse(app.exception)
        headings = [item.value for item in app.subheader]
        self.assertIn("On/Off over time", headings)
        self.assertNotIn("Games played vs. missed", headings)
        charts = app.get("plotly_chart")
        self.assertEqual(len(charts), 3)
        trend = json.loads(charts[1].proto.spec)
        self.assertEqual([trace["name"] for trace in trend["data"]], ["On court", "On bench"])
        scatter = json.loads(charts[-1].proto.spec)
        self.assertIn("On bench", scatter["layout"]["xaxis"]["title"]["text"])
        self.assertIn("On court", scatter["layout"]["yaxis"]["title"]["text"])
        self.assertEqual(scatter["data"][-1]["name"], "Same margin")
        self.assertFalse(any(item.label == "Explore on-court and bench results" for item in app.expander))
        self.assertTrue(any("needs 20 games played" in item.value for item in app.caption))

        small_sample = complete.loc[complete.reliability.eq("Low")].iloc[0]
        app.selectbox(key="impact_team_filter").set_value(int(small_sample.team_id)).run()
        app.selectbox(key="impact_player").set_value(int(small_sample.player_id)).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Sample size: Limited" in item.value for item in app.info))

        app.selectbox(key="impact_season").set_value("2026-27").run()
        app.selectbox(key="impact_team_filter").set_value(0).run()
        app.slider(key="impact_peer_minutes").set_value(0).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("needs 5 games played" in item.value for item in app.caption))
        self.assertTrue(any("Early-season comparisons" in item.value for item in app.warning))
        scatter = json.loads(app.get("plotly_chart")[-1].proto.spec)
        self.assertEqual(scatter["data"][-1]["name"], "Same margin")
        self.assertEqual(len(app.dataframe), 1)

        app.slider(key="impact_peer_minutes").set_value(2500).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("reaches this minutes cutoff" in item.value for item in app.info))
        self.assertFalse(app.dataframe)

    def test_impact_trend_weights_by_minutes_and_rolls_off_old_games(self):
        from src.features.impact import rolling_margins

        players = pd.DataFrame({
            "game_id": range(11), "team_id": 1, "date": pd.date_range("2025-01-01", periods=11),
            "played": True, "minutes": [10] + [20] * 10, "plus_minus": [10] + [2] * 10,
        })
        teams = pd.DataFrame({"game_id": range(11), "team_id": 1, "margin": 3, "duration": 48})
        trend = rolling_margins(players, teams)
        self.assertEqual(trend.appearances.tolist(), [5, 6, 7, 8, 9, 10, 10])
        self.assertAlmostEqual(trend.iloc[0].on_margin, 48 * 18 / 90)
        self.assertAlmostEqual(trend.iloc[-1].on_margin, 48 * 20 / 200)
        self.assertAlmostEqual(trend.iloc[-1].off_margin, 48 * 10 / 280)


if __name__=="__main__": unittest.main()
