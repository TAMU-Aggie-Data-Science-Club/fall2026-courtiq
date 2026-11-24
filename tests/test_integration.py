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
        self.assertIn("Sources and how to read the rankings", [item.label for item in at.expander])
        self.assertNotIn("Sources, definitions & limitations", [item.label for item in at.expander])
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

        at.button_group(key="scout_lens").set_value(["Playmaking"]).run()
        playmaking_labels = radar()["layout"]["polar"]["angularaxis"]["ticktext"]
        self.assertEqual(len(playmaking_labels), 4)
        self.assertTrue(any("Assists per turnover" in label for label in playmaking_labels))
        self.assertEqual(report_headings(), ["**Playmaking scouting report**"])

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

    def test_team_forecast_renders_automatically_and_player_button_still_works(self):
        from streamlit.testing.v1 import AppTest
        from src.dashboard import cached_team_forecast

        at=AppTest.from_file("app.py",default_timeout=60).run()
        cached_team_forecast.clear()
        with patch("src.models.team.predict", wraps=team.predict) as predict:
            at.sidebar.radio[0].set_value("Teams").run()
            self.assertEqual(at.radio(key="team_matchup_mode").value, "Upcoming Games")
            if not any(picker.key == "team_upcoming_game" for picker in at.selectbox):
                at.radio(key="team_matchup_mode").set_value("Past Games").run()
            predict.assert_called_once()
            _, home, away, date, spread, _ = predict.call_args.args
        self.assertEqual(len(at.exception),0,str(at.exception))
        self.assertFalse(at.button)
        if at.radio(key="team_matchup_mode").value == "Upcoming Games":
            self.assertFalse(any('class="forecast-final-heading"' in item.proto.body for item in at.get("html")))
        scoreboard = next(item.proto.body for item in at.get("html") if 'class="forecast-scoreboard"' in item.proto.body)
        expected = team.predict(self.t, home, away, date, spread)
        self.assertIn(f'Projected total · <b>{expected["total"]:.1f} points</b>', scoreboard)
        for side in ("home", "away"):
            self.assertIn(f"{expected[f'{side}_score']:.1f}", scoreboard)
            self.assertIn(f"{expected[f'{side}_win']:.1%} win chance", scoreboard)
        self.assertEqual(len(at.get("plotly_chart")), 2)
        key = next(item.proto.body for item in at.get("html") if 'aria-label="Point margin chart key"' in item.proto.body)
        self.assertIn("<b>Projected</b>", key)
        self.assertIn("80% range", key)
        self.assertNotIn("<b>Spread</b>", key)
        chart = json.loads(at.get("plotly_chart")[0].proto.spec)
        self.assertEqual(chart["data"][0]["x"], [expected["distribution"]["low"], expected["distribution"]["high"]])
        self.assertNotIn("Spread", chart["layout"]["yaxis"]["ticktext"])
        if at.radio(key="team_matchup_mode").value == "Upcoming Games":
            self.assertNotIn("Actual", chart["layout"]["yaxis"]["ticktext"])
        at.toggle(key="team_use_spread").set_value(True).run()
        self.assertFalse(at.exception)
        key = next(item.proto.body for item in at.get("html") if 'aria-label="Point margin chart key"' in item.proto.body)
        self.assertIn("<b>Spread</b>", key)
        chart = json.loads(at.get("plotly_chart")[0].proto.spec)
        with_spread = team.predict(self.t, home, away, date, -4.5)
        self.assertEqual(chart["data"][0]["x"], [with_spread["distribution"]["low"], with_spread["distribution"]["high"]])
        spread_marker = next(trace for trace in chart["data"] if trace.get("name") == "Spread")
        self.assertEqual(spread_marker["x"], [4.5])
        self.assertIn(spread_marker["y"][0], (0, .25))
        self.assertNotIn("Spread", chart["layout"]["yaxis"]["ticktext"])
        at.sidebar.radio[0].set_value("Compare").run()
        self.assertEqual(len(at.exception),0,str(at.exception))
        self.assertFalse(at.button)
        cards = next(item.proto.body for item in at.get("html") if 'class="ciq-cards"' in item.proto.body)
        self.assertEqual(cards.count('class="ciq-card"'), 2)
        for label in ("PTS", "REB", "AST"):
            self.assertEqual(cards.count(f"<b>{label}</b>"), 2)
        self.assertTrue(any(item.value == "Past meetings" for item in at.subheader))

    def test_team_forecast_custom_spread_and_recent_window(self):
        from streamlit.testing.v1 import AppTest
        from src.dashboard import cached_team_forecast

        at = AppTest.from_file("app.py", default_timeout=40).run()
        at.sidebar.radio[0].set_value("Teams").run()
        at.radio(key="team_matchup_mode").set_value("Custom Matchup").run()
        cutoff = max(pd.Timestamp(task["inference_available_after"]) for task in load("team")["tasks"].values())
        earliest = cutoff + pd.Timedelta(days=1)
        self.assertEqual(at.date_input(key="team_date").proto.min, f"{earliest:%Y/%m/%d}")
        self.assertTrue(any(f"Earliest forecast date: {earliest:%b} {earliest.day}, {earliest.year}" in item.value
                            for item in at.caption))
        cached_team_forecast.clear()
        with patch("src.models.team.predict", wraps=team.predict) as predict:
            at.toggle(key="team_use_spread").set_value(True).run()
            at.number_input[0].set_value(-5.5).run()
            self.assertEqual(predict.call_count, 2)
            self.assertEqual(predict.call_args.args[4], -5.5)
            at.radio(key="team_recent_window").set_value(10).run()
            self.assertEqual(predict.call_count, 2)
            home = at.selectbox(key="team_home").value
            away = at.selectbox(key="team_away").value
            day = at.date_input(key="team_date").value
            at.button(key="team_swap_sides").click().run()
            self.assertEqual(at.selectbox(key="team_home").value, away)
            self.assertEqual(at.selectbox(key="team_away").value, home)
            self.assertEqual(predict.call_args.args[1:4], (away, home, day))
        self.assertFalse(at.exception)
        key = next(item.proto.body for item in at.get("html") if 'aria-label="Point margin chart key"' in item.proto.body)
        self.assertIn("-5.5", key)
        self.assertTrue(any("Home covers" in item.value and "Away covers" in item.value for item in at.markdown))
        recent = json.loads(at.get("plotly_chart")[-1].proto.spec)
        self.assertTrue(all(len(trace["x"]) <= 10 for trace in recent["data"]))
        self.assertTrue(all("%{customdata[0]} %{customdata[1]}" in trace["hovertemplate"]
                            and "%{customdata[2]} · Margin %{y:+.0f} pts<extra></extra>" in trace["hovertemplate"]
                            for trace in recent["data"]))
        self.assertTrue(all(result.startswith(("W ", "L ")) for trace in recent["data"]
                            for _, _, result in trace["customdata"]))
        self.assertEqual(at.radio(key="team_recent_window").label, "Recent games per team")
        cards = next(item.proto.body for item in at.get("html") if 'class="forecast-form-cards"' in item.proto.body)
        self.assertEqual(cards.count("forecast-form-record"), 2)
        self.assertIn("10 games", cards)

    def test_team_forecast_matchup_finder(self):
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file("app.py", default_timeout=40).run()
        at.sidebar.radio[0].set_value("Teams").run()
        upcoming = [picker for picker in at.selectbox if picker.key == "team_upcoming_game"]
        team_id = 0
        if upcoming:
            dates = {label.split(" · ", 1)[0] for label in upcoming[0].options}
            self.assertLessEqual(len(dates), 3)
            at.selectbox(key="team_upcoming_limit").set_value(7).run()
            expanded = {label.split(" · ", 1)[0] for label in at.selectbox(key="team_upcoming_game").options}
            self.assertTrue(dates.issubset(expanded))
            self.assertLessEqual(len(expanded), 7)
            team_filter = at.selectbox(key="team_fixture_filter")
            team_name = team_filter.options[1]
            lookup = pd.read_csv(APP / "teams.csv.gz").set_index("team_name").team_id
            team_id = int(lookup[team_name])
            team_filter.set_value(team_id).run()
            self.assertTrue(all(team_name in label for label in at.selectbox(key="team_upcoming_game").options))
        else:
            self.assertTrue(any("no upcoming games" in item.value for item in at.info))

        at.radio(key="team_matchup_mode").set_value("Past Games").run()
        self.assertEqual(at.selectbox(key="team_fixture_filter").value, team_id)
        if team_id:
            self.assertTrue(all(team_name in label for label in at.selectbox(key="team_past_game").options))
            at.radio(key="team_matchup_mode").set_value("Upcoming Games").run()
            self.assertEqual(at.selectbox(key="team_fixture_filter").value, team_id)
            at.radio(key="team_matchup_mode").set_value("Past Games").run()
            at.selectbox(key="team_fixture_filter").set_value(0).run()
        day = self.t.date.max().date()
        at.selectbox(key="team_past_month").set_value(str(day)[:7]).run()
        self.assertFalse(any(picker.label == "Opponent" for picker in at.selectbox))
        at.selectbox(key="team_past_date").set_value(day).run()
        recorded = pd.read_csv(APP / "games.csv.gz", parse_dates=["date"])
        dates_in_month = recorded.loc[
            recorded.date.dt.strftime("%Y-%m").eq(str(day)[:7]) & recorded.date.le(pd.Timestamp(day))
        ]
        expected_days = dates_in_month.groupby(dates_in_month.date.dt.date).game_id.nunique()
        self.assertCountEqual(at.selectbox(key="team_past_date").options, [
            f"{date:%b} {date.day} · {count} {'game' if count == 1 else 'games'}"
            for date, count in expected_days.items()
        ])
        self.assertTrue(at.selectbox(key="team_past_game").options)
        self.assertFalse(at.exception)
        self.assertTrue(any(item.value == "Historical forecast" for item in at.subheader))
        self.assertTrue(any(
            item.value == f"This forecast uses only box scores from games played before {day:%b} {day.day}, {day.year}."
            for item in at.caption
        ))
        game = recorded.set_index("game_id").loc[at.selectbox(key="team_past_game").value]
        names = pd.read_csv(APP / "teams.csv.gz").set_index("team_id").team_name
        home, away = names[game.home_team_id], names[game.away_team_id]
        winner = home if game.home_points > game.away_points else away
        final = next(item.proto.body for item in at.get("html") if 'class="forecast-result-scores"' in item.proto.body)
        self.assertIn('<div class="forecast-final-heading"><h4>Final score</h4>', final)
        self.assertEqual(final.count('class="forecast-winner"'), 1)
        self.assertIn(f'<strong class="forecast-winner">{winner} {max(game.away_points, game.home_points):.0f}', final)
        for name, score in ((away, game.away_points), (home, game.home_points)):
            self.assertIn(f'{name} {score:.0f}', final)
        forecast = team.predict(self.t, game.home_team_id, game.away_team_id, day)
        home_chance, away_chance = forecast["home_win"], forecast["away_win"]
        if home_chance != away_chance:
            favorite = home if home_chance > away_chance else away
            verdict = "Model correctly picked the winner" if winner == favorite else "Model picked the wrong winner"
            self.assertIn(f'{verdict}</span></div>', final)
        actual_margin = game.home_points - game.away_points
        chart = json.loads(at.get("plotly_chart")[0].proto.spec)
        self.assertEqual(next(trace["x"] for trace in chart["data"] if trace.get("name") == "Actual"), [actual_margin])
        at.toggle(key="team_use_spread").set_value(True)
        at.toggle(key="dark_mode").set_value(True).run()
        self.assertFalse(at.exception)
        chart = json.loads(at.get("plotly_chart")[0].proto.spec)
        markers = {trace.get("name"): trace["x"] for trace in chart["data"]}
        self.assertEqual(markers["Actual"], [actual_margin])
        self.assertEqual(markers["Spread"], [4.5])
        self.assertEqual(chart["layout"]["paper_bgcolor"], "#121b22")

        self.assertNotIn("August 2025", at.selectbox(key="team_past_month").options)
        old_day = recorded.loc[recorded.date.ge("2025-10-22"), "date"].min()
        at.selectbox(key="team_past_month").set_value(old_day.strftime("%Y-%m")).run()
        at.selectbox(key="team_past_date").set_value(old_day.date()).run()
        slate = recorded.loc[recorded.date.eq(old_day)]
        active = set(slate.home_team_id) | set(slate.away_team_id)
        other_team = next(int(tid) for tid in recorded.home_team_id.unique() if tid not in active)
        at.selectbox(key="team_fixture_filter").set_value(other_team).run()
        last_team_game = recorded.loc[
            recorded.home_team_id.eq(other_team) | recorded.away_team_id.eq(other_team), "date"
        ].max()
        self.assertEqual(at.selectbox(key="team_past_month").value, last_team_game.strftime("%Y-%m"))
        self.assertEqual(at.selectbox(key="team_past_date").value, last_team_game.date())

        home = recorded.loc[recorded.home_team_id.eq(other_team) & recorded.date.ge("2025-10-22")]
        away = recorded.loc[recorded.away_team_id.eq(other_team) & recorded.date.ge("2025-10-22")]
        opponent = int(sorted(set(home.away_team_id) & set(away.home_team_id))[0])
        opponent_picker = at.selectbox(key=f"team_past_opponent_{other_team}")
        self.assertEqual(opponent_picker.value, 0)
        opponent_picker.set_value(opponent).run()
        names = pd.read_csv(APP / "teams.csv.gz").set_index("team_id").team_name
        meetings = pd.concat([home.loc[home.away_team_id.eq(opponent)],
                              away.loc[away.home_team_id.eq(opponent)]])
        for game in meetings.itertuples():
            at.selectbox(key="team_past_month").set_value(game.date.strftime("%Y-%m")).run()
            at.selectbox(key="team_past_date").set_value(game.date.date()).run()
            self.assertEqual(at.selectbox(key="team_past_game").options,
                             [f"{names[game.away_team_id]} at {names[game.home_team_id]}"])

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
        self.assertTrue(any('class="ciq-table"' in item.proto.body for item in app.get("html")))

        app.slider(key="impact_peer_minutes").set_value(2500).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("reaches this minutes cutoff" in item.value for item in app.info))
        self.assertFalse(any('class="ciq-table"' in item.proto.body for item in app.get("html")))

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


class FeedbackTests(unittest.TestCase):
    """Checks for the UI feedback pass: accuracy tables, readable tables, colors and dark mode."""
    setUp = RealTests.setUp

    def test_team_market_record_matches_saved_evaluation(self):
        from src.dashboard import team_market_record

        record = team_market_record(json.loads((APP / "manifest.json").read_text())["version"])
        saved = load("team")["tasks"]["home_win"]
        test = next(r for r in saved["results"] if r["period"] == "test")
        self.assertEqual(record["n"], test["n"])
        self.assertAlmostEqual(record["winner"], test["accuracy"])
        margin = next(r for r in load("team")["tasks"]["margin"]["results"] if r["period"] == "test")
        self.assertAlmostEqual(record["margin_mae"], margin["mae"])
        for key in ("ats", "ou", "market_winner"):
            self.assertTrue(0 < record[key] < 1, key)
        self.assertGreater(record["ats_n"], 1000)
        self.assertGreater(record["ou_n"], 1000)

    def test_prop_stand_in_line_uses_only_earlier_games(self):
        from src.dashboard import player_prop_record

        version = json.loads((APP / "manifest.json").read_text())["version"]
        record = player_prop_record(version)
        self.assertEqual(set(record), {"points", "rebounds", "assists"})
        for result in record.values():
            self.assertTrue(.3 < result["rate"] < .8)
            self.assertGreater(result["n"], 10000)

    def test_stand_in_line_hand_computed(self):
        from src.dashboard import stand_in_lines

        games = pd.DataFrame({
            "player_id": [1] * 12 + [1] * 6 + [2] * 6,
            "season_start": [2025] * 12 + [2026] * 6 + [2025] * 6,
            "points": list(range(1, 13)) + [50] * 6 + [7] * 6,
        })
        line = stand_in_lines(games, "points")
        self.assertTrue(line.iloc[:5].isna().all())          # fewer than 5 earlier games
        self.assertAlmostEqual(line.iloc[5], 3.0)            # mean of games 1-5, never game 6 itself
        self.assertAlmostEqual(line.iloc[11], 6.5)           # mean of games 2-11 (last 10 only)
        self.assertTrue(line.iloc[12:17].isna().all())       # new season starts over
        self.assertAlmostEqual(line.iloc[17], 50.0)
        self.assertAlmostEqual(line.iloc[23], 7.0)           # other player kept separate

    def test_pair_colors_separate_similar_teams(self):
        from src.dashboard import color_distance, pair_colors

        teams = pd.read_csv(APP / "teams.csv.gz")
        ids = teams.set_index("team_code").team_id
        home, away = pair_colors(teams, ids["ATL"], ids["DET"])
        self.assertGreaterEqual(color_distance(home, away), 12)
        self.assertEqual(pair_colors(teams, ids["BOS"], ids["LAL"]), pair_colors(teams, ids["BOS"], ids["LAL"]))

    def test_percentile_colors_are_distinct_for_color_blind_viewers(self):
        from src.dashboard import color_distance
        from src.features.scouting import percentile_color

        steps = [percentile_color(value) for value in (90, 60, 40, 10)]
        for first, second in zip(steps, steps[1:]):
            self.assertGreaterEqual(color_distance(first, second), 12)

    def test_every_page_renders_in_dark_mode(self):
        from streamlit.testing.v1 import AppTest

        for page in ["Players", "Teams", "Compare", "Trends"]:
            at = AppTest.from_file("app.py", default_timeout=60).run()
            at.sidebar.toggle(key="dark_mode").set_value(True).run()
            at.sidebar.radio[0].set_value(page).run()
            self.assertFalse(at.exception, page)
            self.assertTrue(any("#121b22" in item.proto.body for item in at.get("html")), page)
            for chart in at.get("plotly_chart"):
                spec = json.loads(chart.proto.spec)
                self.assertEqual(spec["layout"].get("paper_bgcolor"), "#121b22", page)
        labels = [option for option in at.sidebar.radio[0].options]
        self.assertTrue(any("Player Scouting & Impact" in label for label in labels))

    def test_player_matchups_meeting_table_lists_both_players(self):
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file("app.py", default_timeout=60).run()
        at.sidebar.radio[0].set_value("Compare").run()
        self.assertFalse(at.exception)
        tables = [item.proto.body for item in at.get("html") if 'class="ciq-table"' in item.proto.body]
        meetings = next((body for body in tables if '<th class="group"' in body and ">PTS<" in body), None)
        if meetings is not None:
            away = at.selectbox(key="p_b").format_func(at.selectbox(key="p_b").value)
            home = at.selectbox(key="p_a").format_func(at.selectbox(key="p_a").value)
            self.assertIn(away, meetings)
            self.assertIn(home, meetings)
            self.assertEqual(meetings.count(">PTS<"), 2)
