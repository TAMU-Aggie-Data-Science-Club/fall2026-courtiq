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
    def setUp(self):
        from streamlit.testing.v1.element_tree import ButtonGroup

        # Streamlit 1.50 AppTest iterates a single-selection string character by character.
        original_indices = ButtonGroup.indices

        def indices(widget):
            if widget.proto.label != "Scouting lens":
                return original_indices.fget(widget)
            value = widget.value
            selections = [value] if isinstance(value, str) else value or []
            options = [option.content for option in widget.options]
            return [options.index(selection) for selection in selections]

        self.enterContext(patch.object(ButtonGroup, "indices", property(indices)))

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

    def test_scouting_filters_and_lenses(self):
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file("app.py", default_timeout=40).run()
        seasons = pd.read_csv(APP / "player_season.csv.gz")
        season = at.selectbox(key="scout_season").value
        stints = seasons.query("season == @season and team_id != 0")
        counts = stints.groupby("player_id").team_id.nunique()
        player_id = int(counts[counts > 1].index[0])

        def radar():
            self.assertFalse(at.exception)
            return json.loads(at.get("plotly_chart")[0].proto.spec)

        def report_headings():
            return [item.value for item in at.markdown if item.value.endswith("scouting report**")]

        self.assertEqual(report_headings(), ["**All-around scouting report**"])
        latest = self.p.loc[self.p.played & self.p.season.eq(season), "date"].max()
        expected_date = f"Games included through {latest:%b} {latest.day}, {latest.year}"
        self.assertTrue(any(expected_date in item.value and "snapshot prepared" in item.value
                            for item in at.caption))
        profiles = []
        teams = pd.read_csv(APP / "teams.csv.gz").set_index("team_id").team_name
        player_stints = stints.loc[stints.player_id.eq(player_id)]
        for team_id in player_stints.team_id:
            at.selectbox(key="scout_team").set_value(int(team_id)).run()
            at.selectbox(key="scout_player").set_value(player_id).run()
            profiles.append(radar()["data"])
            self.assertEqual(profiles[-1][1]["name"], player_stints.player_name.iloc[0])
            header = next(item.proto.body for item in at.get("html")
                          if 'class="scout-identity"' in item.proto.body)
            self.assertEqual(header.count('class="scout-team-dot"'), len(player_stints))
            self.assertTrue(all(teams[tid] in header for tid in player_stints.team_id))
            self.assertIn("</span> / <span", header)
            self.assertTrue(any(player_stints.player_name.iloc[0] in item.value
                                and "League comparison" in item.value for item in at.subheader))
        self.assertTrue(all(profile == profiles[0] for profile in profiles))

        at.button_group(key="scout_lens").set_value(["Shooting"]).run()
        labels = radar()["layout"]["polar"]["angularaxis"]["ticktext"]
        self.assertEqual(len(labels), 8)
        self.assertTrue(any("3PA per game" in label for label in labels))
        self.assertEqual(report_headings(), ["**Shooting scouting report**"])

        at.selectbox(key="scout_team").set_value(0).run()
        ratings = pd.read_csv(APP / "scouting_ratings.csv.gz")
        qualified = seasons.query("season == @season and team_id == 0 and games >= 20 and mpg >= 15")
        ranked = ratings.loc[ratings.season_start.eq(int(season[:4]))].dropna(
            subset=["drtg", "netrtg", "team_dreb_share"]
        )
        ranked = ranked[ranked[["guard_starts", "forward_starts", "center_starts"]].sum(axis=1).gt(0)]
        ranked_player = qualified.loc[qualified.player_id.isin(ranked.player_id)]
        at.selectbox(key="scout_player").set_value(int(ranked_player.iloc[0].player_id)).run()
        at.button_group(key="scout_lens").set_value(["Defense & Rebounding"]).run()
        defense_labels = radar()["layout"]["polar"]["angularaxis"]["ticktext"]
        self.assertEqual(len(defense_labels), 8)
        self.assertTrue(any("Defensive Rating" in label and "pctile" in label for label in defense_labels))
        self.assertTrue(any("Net Rating" in label and "pctile" in label for label in defense_labels))
        self.assertTrue(any("Team DREB share" in label and "pctile" in label for label in defense_labels))
        self.assertTrue(any("Foul Avoidance" in label and "pctile" in label for label in defense_labels))
        position_details = next(item for item in at.expander if item.label == "Position details")
        self.assertTrue(any("Recorded starting positions" in item.value for item in position_details.markdown))
        self.assertFalse(any("Recorded starting positions" in item.proto.body for item in at.get("html")))
        self.assertFalse(any("Foul frequency" in item.proto.body for item in at.get("html")))
        self.assertTrue(any("of minutes covered" in item.proto.body for item in at.get("html")))
        self.assertEqual(report_headings(), ["**Defensive scouting report**"])

        short_season = seasons.query("season == @season and team_id == 0 and games < 20")
        at.selectbox(key="scout_player").set_value(int(short_season.iloc[0].player_id)).run()
        labels = radar()["layout"]["polar"]["angularaxis"]["ticktext"]
        self.assertTrue(all("Unranked" in label for label in labels))
        self.assertTrue(any("Needs 20 games and 15 minutes per game" in item.proto.body
                            for item in at.get("html")))

        at.selectbox(key="scout_season").set_value("2026-27").run()
        early = seasons.query("season == '2026-27' and team_id == 0 and games >= 5 and mpg >= 15")
        leading_scorer = early.loc[early.points_pg.idxmax()]
        at.selectbox(key="scout_player").set_value(int(leading_scorer.player_id)).run()
        at.button_group(key="scout_lens").set_value(["All-Around"]).run()
        labels = radar()["layout"]["polar"]["angularaxis"]["ticktext"]
        self.assertTrue(any("Points per game<br><b>100th pctile" in label for label in labels))
        self.assertFalse(any("👑" in label for label in labels))
        self.assertTrue(any("drops from 20 games played to 5" in item.value and "misleading" in item.value
                            for item in at.warning))
        self.assertFalse(any('class="scout-crown"' in item.proto.body or "Elite Scorer" in item.proto.body
                             for item in at.get("html")))

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


if __name__=="__main__": unittest.main()
