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

    def test_page_links_restore_navigation_in_new_session(self):
        from streamlit.testing.v1 import AppTest

        pages = {
            "scouting-lab": "Player Scouting Lab",
            "on-off-impact": "On/Off Impact",
            "team-forecasts": "Team Forecasts",
            "player-matchups": "Player Matchup Lab",
            "breakout-watch": "Breakout Watch",
        }
        for slug, title in pages.items():
            with self.subTest(page=slug):
                app = AppTest.from_file("app.py", default_timeout=40)
                app.query_params["page"] = slug
                app.run()
                self.assertFalse(app.exception)
                self.assertTrue(any(header.value == title for header in app.header))

        app = AppTest.from_file("app.py", default_timeout=40)
        app.query_params["page"] = "unknown"
        app.query_params["ref"] = "test"
        app.run()
        self.assertEqual(app.query_params["page"], ["scouting-lab"])
        app.radio(key="nav_player_tool").set_value("On/Off Impact").run()
        self.assertEqual(app.query_params["page"], ["on-off-impact"])
        app.sidebar.radio(key="nav_section").set_value("Compare").run()
        self.assertEqual(app.query_params["page"], ["player-matchups"])
        self.assertEqual(app.query_params["ref"], ["test"])

    def test_team_forecast_renders_automatically(self):
        from streamlit.testing.v1 import AppTest
        from src.dashboard import cached_team_forecast

        at=AppTest.from_file("app.py",default_timeout=60).run()
        cached_team_forecast.clear()
        with patch("src.models.team.predict", wraps=team.predict) as predict:
            at.sidebar.radio[0].set_value("Teams").run()
            self.assertEqual(at.radio(key="team_matchup_mode").value, "Upcoming games")
            if not any(picker.key == "team_upcoming_game" for picker in at.selectbox):
                at.radio(key="team_matchup_mode").set_value("Past games").run()
            predict.assert_called_once()
            _, home, away, date, spread, _ = predict.call_args.args
        self.assertEqual(len(at.exception),0,str(at.exception))
        self.assertFalse(at.button)
        if at.radio(key="team_matchup_mode").value == "Upcoming games":
            self.assertFalse(any("Actual final" in item.value for item in at.markdown))
        scoreboard = next(item.proto.body for item in at.get("html") if 'class="forecast-scoreboard"' in item.proto.body)
        expected = team.predict(self.t, home, away, date, spread)
        for side in ("home", "away"):
            self.assertIn(f"{expected[f'{side}_score']:.1f}", scoreboard)
            self.assertIn(f"{expected[f'{side}_win']:.1%} win chance", scoreboard)
        interval = json.loads(at.get("plotly_chart")[0].proto.spec)["data"][0]["x"]
        self.assertEqual(interval, [expected["distribution"]["low"], expected["distribution"]["high"]])

    def test_player_matchup_automatic_projections_and_both_meeting_lines(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file("app.py", default_timeout=40).run()
        app.sidebar.radio[0].set_value("Compare").run()
        self.assertEqual(app.radio(key="player_matchup_mode").value, "Upcoming games")
        app.session_state["player_past_game"] = 22500288
        app.radio(key="player_matchup_mode").set_value("Past games").run()
        self.assertFalse(app.exception)
        self.assertNotEqual(app.selectbox(key="player_past_game").value, 22500288)
        if (APP / "schedule.csv.gz").exists():
            app.session_state["player_upcoming_game"] = 22500288
            app.radio(key="player_matchup_mode").set_value("Upcoming games").run()
            self.assertFalse(app.exception)
            for picker in app.selectbox:
                if picker.key == "player_upcoming_game":
                    self.assertNotEqual(picker.value, 22500288)
        app.radio(key="player_matchup_mode").set_value("Custom matchup").run()

        roster = self.p.loc[self.p.played].sort_values(["date", "game_id"]).drop_duplicates("player_id", keep="last")
        away_name, home_name = "Luka Doncic", "Victor Wembanyama"
        away = roster.loc[roster.player_name.eq(away_name)].iloc[0]
        home = roster.loc[roster.player_name.eq(home_name)].iloc[0]
        app.selectbox(key="player_home").set_value(int(home.team_id)).run()
        app.selectbox(key="player_away").set_value(int(away.team_id)).run()
        app.selectbox(key="p_b").set_value(int(away.player_id)).run()
        app.selectbox(key="p_a").set_value(int(home.player_id)).run()
        self.assertFalse(app.exception)
        self.assertFalse(any("predict" in item.label.lower() for item in app.button))

        cards = next(item.proto.body for item in app.get("html") if "player-forecast-cards" in item.proto.body)
        selected_date = app.date_input(key="player_date").value
        forecast, _ = player.predict(self.p, self.t, away.player_id, home.team_id, selected_date, False)
        for stat in forecast.itertuples():
            self.assertIn(f"{stat.prediction:.1f}</strong>", cards)
            self.assertIn(f"80% range {stat.low:.1f}–{stat.high:.1f}", cards)
        self.assertEqual(cards.count("player-forecast-stat"), 6)
        self.assertIn(away_name, cards)
        self.assertIn(home_name, cards)
        figures = [json.loads(chart.proto.spec) for chart in app.get("plotly_chart")]
        self.assertEqual([figure["layout"]["title"]["text"] for figure in figures],
                         ["Points", "Rebounds", "Assists"])
        away_forecast = forecast.set_index("stat")
        for figure, stat in zip(figures, ("points", "rebounds", "assists")):
            projection, line, baseline = figure["data"][:3]
            row = away_forecast.loc[stat]
            self.assertEqual(line["x"], [row.low, row.high])
            self.assertEqual(projection["x"][0], row.prediction)
            self.assertEqual(projection["type"], "bar")
            self.assertEqual(projection["orientation"], "h")
            self.assertNotIn("text", projection)
            self.assertEqual(projection["hovertext"], [away_name, home_name])
            self.assertEqual(baseline["x"], [row.baseline])
            self.assertEqual(baseline["marker"]["symbol"], "circle-open")
            self.assertEqual(figure["layout"]["yaxis"]["ticktext"], [away_name, home_name])
        self.assertFalse(any(expander.label == "See forecast ranges on a chart" for expander in app.expander))

        meetings = player.encounters(self.p, away.player_id, home.player_id, selected_date)
        self.assertFalse(meetings.empty)
        detail = next(item.proto.body for item in app.get("html") if "player-meeting-table" in item.proto.body)
        self.assertIn(f'<th scope="col">{away_name}</th><th scope="col">{home_name}</th>', detail)
        rows = detail.split("<tbody>", 1)[1]
        self.assertEqual(rows.count("<tr>"), len(meetings))
        game = meetings.sort_values("date").iloc[-1]
        first = rows.split("</tr>", 1)[0]
        self.assertIn(f'datetime="{game.date:%Y-%m-%d}"', first)
        cells = first.split("<td>")[1:]
        self.assertEqual(len(cells), 2)
        box_scores = self.p.loc[self.p.game_id.eq(game.game_id)].set_index("player_id")
        for cell, who, opponent in zip(cells, (away, home), (home, away)):
            box = box_scores.loc[who.player_id]
            other = box_scores.loc[opponent.player_id]
            self.assertIn(f"<strong>{box.points:.0f}</strong><small>PTS</small>", cell)
            self.assertIn(f"<strong>{box.rebounds:.0f}</strong><small>REB</small>", cell)
            self.assertIn(f"<strong>{box.assists:.0f}</strong><small>AST</small>", cell)
            self.assertIn(f"<strong>{box.minutes:.0f}</strong><small>MIN</small>", cell)
            for stat in ("points", "rebounds", "assists"):
                self.assertEqual(f'title="Led in {stat}"' in cell, box[stat] > other[stat])
            self.assertNotIn('title="Led in minutes"', cell)

        with patch("src.models.player.predict", wraps=player.predict) as predict:
            app.run()
            predict.assert_not_called()

    def test_team_forecast_custom_spread_and_recent_window(self):
        from streamlit.testing.v1 import AppTest
        from src.dashboard import cached_team_forecast

        at = AppTest.from_file("app.py", default_timeout=40).run()
        at.sidebar.radio[0].set_value("Teams").run()
        at.radio(key="team_matchup_mode").set_value("Custom matchup").run()
        cutoff = max(pd.Timestamp(task["inference_available_after"]) for task in load("team")["tasks"].values())
        earliest = cutoff + pd.Timedelta(days=1)
        self.assertEqual(at.date_input(key="team_date").proto.min, f"{earliest:%Y/%m/%d}")
        self.assertTrue(any(f"Earliest forecast date: {earliest:%b} {earliest.day}, {earliest.year}" in item.value
                            for item in at.caption))
        cached_team_forecast.clear()
        with patch("src.models.team.predict", wraps=team.predict) as predict:
            next(widget for widget in at.checkbox if widget.label == "Include a home spread").check().run()
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
        self.assertTrue(any("-5.5" in item.value and "Home covers" in item.value
                            and "Away covers" in item.value for item in at.markdown))
        recent = json.loads(at.get("plotly_chart")[-1].proto.spec)
        self.assertTrue(all(len(trace["x"]) <= 10 for trace in recent["data"]))
        self.assertTrue(all("Opponent" in trace["hovertemplate"] and "Final score" in trace["hovertemplate"]
                            for trace in recent["data"]))
        self.assertTrue(all(result.startswith(("W ", "L ")) for trace in recent["data"]
                            for _, result in trace["customdata"]))
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

        at.radio(key="team_matchup_mode").set_value("Past games").run()
        self.assertEqual(at.selectbox(key="team_fixture_filter").value, team_id)
        if team_id:
            self.assertTrue(all(team_name in label for label in at.selectbox(key="team_past_game").options))
            at.radio(key="team_matchup_mode").set_value("Upcoming games").run()
            self.assertEqual(at.selectbox(key="team_fixture_filter").value, team_id)
            at.radio(key="team_matchup_mode").set_value("Past games").run()
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
        game = recorded.set_index("game_id").loc[at.selectbox(key="team_past_game").value]
        names = pd.read_csv(APP / "teams.csv.gz").set_index("team_id").team_name
        home, away = names[game.home_team_id], names[game.away_team_id]
        final = f"**Actual final** · {away} {game.away_points:.0f} · {home} {game.home_points:.0f}"
        self.assertTrue(any(item.value == final for item in at.markdown))
        forecast = team.predict(self.t, game.home_team_id, game.away_team_id, day)
        home_chance, away_chance = [round(100 * forecast[f"{side}_win"], 1) for side in ("home", "away")]
        if home_chance != away_chance:
            favorite = home if home_chance > away_chance else away
            winner = home if game.home_points > game.away_points else away
            verdict = (f"{favorite}, the forecast favorite, won." if winner == favorite
                       else f"{winner} won. The forecast favored {favorite}.")
            self.assertTrue(any(item.value == verdict for item in at.caption))

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
