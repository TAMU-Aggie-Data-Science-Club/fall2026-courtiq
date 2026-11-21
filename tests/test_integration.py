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


if __name__=="__main__": unittest.main()
