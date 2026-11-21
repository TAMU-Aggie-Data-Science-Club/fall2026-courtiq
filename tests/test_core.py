"""Known-answer tests for shared formulas, chronology and feature boundaries."""
import unittest
import numpy as np
import pandas as pd
from src.pipeline import season_fields,shooting,pregame,reliability,game_score,impact_table
from src.features.scouting import canonical,rankings,report,radar
from src.features.breakout import target,season_features,training_transitions
from src.models.common import cover_distribution


class PipelineTests(unittest.TestCase):
    def test_seasons_and_type(self):
        frame=pd.DataFrame({"gameId":[22300001,22400617,42300001,62300001,29900001],
            "gameDateTimeEst":["2023-10-01","2024-10-01","2024-04-01","2024-12-01","1999-11-01"]})
        actual=season_fields(frame,start=1990)
        self.assertEqual(actual.season.tolist(),["1999-00","2023-24","2024-25"])

    def test_formulas(self):
        f=pd.DataFrame(dict(points=[30],fgm=[10],fga=[20],fg3m=[4],fg3a=[10],ftm=[4],fta=[5],
            rebounds=[8],oreb=[2],dreb=[6],assists=[7],turnovers=[2],steals=[1],blocks=[1],fouls=[3]))
        row=shooting(f).iloc[0]
        self.assertAlmostEqual(row.ts_pct,30/(2*(20+.44*5)))
        self.assertAlmostEqual(row.efg_pct,.6)
        self.assertAlmostEqual(row.fg2_pct,.6)
        self.assertAlmostEqual(row.ftr,.25)
        self.assertAlmostEqual(game_score(f).iloc[0],30+4-14-.4+1.4+1.8+1+4.9+.7-1.2-2)
        f[["fga","fg3a","fta","turnovers"]]=0
        self.assertTrue(shooting(f)[["ts_pct","fg3_pct","ft_pct","ast_tov"]].isna().all().all())

    def test_future_mutation(self):
        f=pd.DataFrame(dict(player_id=[1]*4,season_start=[2025]*4,game_id=[1,2,3,4],
            date=pd.date_range("2025-01-01",periods=4),points=[10,20,30,40]))
        before=pregame(f,"player_id",["points"],windows=[2])
        self.assertEqual(before.iloc[3].pre_points_2,25)
        self.assertTrue(pd.isna(before.iloc[0].pre_points_2))
        f.loc[3,"points"]=999
        after=pregame(f,"player_id",["points"],windows=[2])
        pd.testing.assert_series_equal(before.pre_points_2,after.pre_points_2)

    def test_same_date_rejected(self):
        f=pd.DataFrame(dict(player_id=[1,1],season_start=[2025,2025],game_id=[1,2],date=pd.to_datetime(["2025-01-01"]*2),points=[10,20]))
        with self.assertRaises(ValueError): pregame(f,"player_id",["points"])

    def test_impact(self):
        p=pd.DataFrame(dict(game_id=[1],player_id=[7],team_id=[2],season_start=[2025],season=["2025-26"],
            player_name=["Example"],played=[True],minutes=[30.],plus_minus=[10.],points=[20.],game_score=[15.]))
        t=pd.DataFrame(dict(game_id=[1],team_id=[2],margin=[4.],duration=[48.],win=[1],points=[104.],opp_points=[100.],possessions=[100.]))
        row=impact_table(p,t).iloc[0]
        self.assertEqual(row.on_per48,16)
        self.assertEqual(row.off_per48,-16)
        self.assertEqual(row.on_off_diff,32)
        self.assertEqual(row.games_missed,0)
        self.assertTrue(pd.isna(row.without_win_pct))

    def test_reliability_boundaries(self):
        for a,b,expected in [(499,300,"Low"),(500,249,"Low"),(500,250,"Medium"),
            (1499,500,"Medium"),(1500,499,"Medium"),(1500,500,"High")]:
            self.assertEqual(reliability(a,b),expected)

    def test_spreads(self):
        r=cover_distribution(5,[-1,0,1],-5)
        self.assertAlmostEqual(sum(r[k] for k in ["home_cover","away_cover","push"]),1)
        self.assertAlmostEqual(r["push"],1/3)
        self.assertEqual(cover_distribution(5,[-1,0,1],-4.5)["push"],0)


class ScoutingTests(unittest.TestCase):
    def frame(self):
        f=pd.DataFrame(dict(player_id=[1,2,3],team_id=[0]*3,season=["2025-26"]*3,
            games=[20,20,19],mpg=[15,20,30],fg3a=[50,49,100],fta=[50,50,50],
            points_pg=[10,10,30],assists_pg=[2,np.nan,7],rebounds_pg=[4,5,6],steals_pg=[1,2,3],
            blocks_pg=[.5,1,2],ts_pct=[.5,.6,.7],fg3_pct=[.3,.4,.5],ft_pct=[.8,.9,1]))
        return f

    def test_ties_qualification_missing(self):
        f=self.frame(); before=f.copy(deep=True)
        r=rankings(f,"2025-26")
        pts=r[r.metric.eq("points_pg")].set_index("player_id")
        self.assertEqual(pts.loc[1,"percentile"],75)
        self.assertEqual(pts.loc[2,"percentile"],75)
        self.assertTrue(pd.isna(pts.loc[3,"percentile"]))
        three=r[r.metric.eq("fg3_pct")].set_index("player_id")
        self.assertEqual(three.loc[1,"percentile"],100)
        self.assertTrue(pd.isna(three.loc[2,"percentile"]))
        self.assertEqual(r.query("metric == 'assists_pg'").population.iloc[0],1)
        pd.testing.assert_frame_equal(f,before)

    def test_tot(self):
        f=self.frame(); extra=f.iloc[[0]].copy(); extra.team_id=7
        combined=canonical(pd.concat([f,extra]))
        self.assertEqual(len(combined),3)
        self.assertEqual(combined.player_id.value_counts().max(),1)
        bad=pd.concat([extra,extra.assign(team_id=8)])
        with self.assertRaises(ValueError): canonical(bad)

    def test_chart_missing_not_imputed(self):
        r=rankings(self.frame(),"2025-26").query("player_id == 2")
        fig=radar(r)
        self.assertEqual(fig.data[1].fill,"none")
        self.assertFalse(fig.data[1].connectgaps)
        badges,text=report(r)
        self.assertLessEqual(len(badges),3)
        self.assertIn("Rankings",text)

    def test_breakout_thresholds(self):
        self.assertTrue(target(20,5,15))
        for args in [(19.9,5,15),(20,4.9,15),(20,5,14.9)]: self.assertFalse(target(*args))

    def test_lower_direction(self):
        f=self.frame(); f.loc[0,"points_pg"]=5
        r=rankings(f,"2025-26",directions={"points_pg":False})
        row=r.query("player_id == 1 and metric == 'points_pg'").iloc[0]
        self.assertEqual(row.percentile,100)
        self.assertEqual(row["rank"],1)

    def test_breakout_future_features(self):
        f=pd.DataFrame(dict(player_id=[1,1],team_id=[0,0],season=["2024-25","2025-26"],season_start=[2024,2025],
            games=[30,30],mpg=[20,25],pra_per36=[25,35],age=[23,24]))
        before=season_features(f)
        f.loc[1,["mpg","pra_per36"]]=[99,999]
        after=season_features(f)
        pd.testing.assert_series_equal(before.iloc[0],after.iloc[0])

    def test_reproducible_model(self):
        from src.models.common import estimator
        x=pd.DataFrame({"feature":[0,1,2,3,4,5]}); y=np.array([0,0,0,1,1,1])
        first=estimator(True).fit(x,y).predict_proba(x)
        second=estimator(True).fit(x,y).predict_proba(x)
        np.testing.assert_allclose(first,second)


if __name__=="__main__": unittest.main()
