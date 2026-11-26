"""Presentation helpers for team results during a player's season stint."""
import pandas as pd


def signed_margin(value, digits=1):
    if pd.isna(value):
        return "Unavailable"
    rounded = round(float(value), digits)
    return f"{rounded:+.{digits}f}" if rounded else f"{0:.{digits}f}"


def court_summary(row, team_name):
    if pd.isna(row.on_per48) or pd.isna(row.off_per48):
        return "A comparison needs usable scoring and playing-time data for both on-court and bench minutes."

    def result(margin, situation):
        margin = round(float(margin), 1)
        if not margin:
            return f"scored even with opponents {situation}"
        verb = "outscored opponents" if margin > 0 else "was outscored"
        return f"{verb} by {abs(margin):.1f} points per 48 minutes {situation}"

    on_court = result(row.on_per48, f"with {row.player_name} on the floor")
    on_bench = result(row.off_per48, f"with {row.player_name} on the bench")
    return f"In the games covered, the {team_name} {on_court} and {on_bench}."


TREND_WINDOW = 10
TREND_MIN_GAMES = 5


def rolling_margins(player_games, team_games):
    games = player_games.merge(
        team_games[["game_id", "team_id", "margin", "duration"]],
        on=["game_id", "team_id"],
        validate="one_to_one",
    )
    valid = (
        games.played & games.plus_minus.notna() & games.margin.notna()
        & games.minutes.gt(0) & games.minutes.le(games.duration + .05)
    )
    games = games.loc[valid].sort_values(["date", "game_id"])
    totals = pd.DataFrame({
        "on_points": games.plus_minus,
        "off_points": games.margin - games.plus_minus,
        "on_minutes": games.minutes,
        "off_minutes": (games.duration - games.minutes).clip(lower=0),
    }).rolling(TREND_WINDOW, min_periods=TREND_MIN_GAMES).sum()
    result = totals.assign(
        date=games.date,
        appearances=games.game_id.rolling(TREND_WINDOW, min_periods=TREND_MIN_GAMES).count(),
        on_margin=48 * totals.on_points / totals.on_minutes.where(totals.on_minutes.gt(0)),
        off_margin=48 * totals.off_points / totals.off_minutes.where(totals.off_minutes.gt(0)),
    )
    return result.dropna(subset=["on_margin", "off_margin"], how="all")


def trend_chart(trend, color, neutral="#637783"):
    import plotly.graph_objects as go

    fig = go.Figure()
    for label, margin, minutes, accent, dash in (
        ("On court", "on_margin", "on_minutes", color, "solid"),
        ("On bench", "off_margin", "off_minutes", neutral, "dash"),
    ):
        fig.add_trace(go.Scatter(
            x=trend.date, y=trend[margin], name=label, mode="lines+markers",
            line=dict(color=accent, dash=dash, width=2.5),
            text=trend[margin].map(signed_margin),
            customdata=trend[[minutes, "appearances"]],
            hovertemplate=(
                "%{text} points per 48<br>%{customdata[0]:,.0f} minutes"
                " across %{customdata[1]:.0f} appearances<extra>%{fullData.name}</extra>"
            ),
        ))
    fig.add_hline(y=0, line_color="#697681", line_width=1)
    fig.update_yaxes(tickformat=".1f", hoverformat=".1f")
    fig.update_layout(
        xaxis_title="Game date", yaxis_title="Team point margin per 48",
        hovermode="x unified", height=325, margin=dict(l=45, r=15, t=36, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    return fig


def margin_bars(row, color, neutral="#637783"):
    import plotly.graph_objects as go

    values = [row.on_per48, row.off_per48]
    labels = ["On court", "On bench"]
    colors = [color, neutral]
    minutes = [row.minutes_on, row.minutes_off]
    valid = [i for i, value in enumerate(values) if pd.notna(value)]
    fig = go.Figure()
    if valid:
        fig.add_trace(go.Bar(
            x=[values[i] for i in valid],
            y=[labels[i] for i in valid],
            orientation="h",
            marker_color=[colors[i] for i in valid],
            text=[signed_margin(values[i]) for i in valid],
            textposition="outside",
            cliponaxis=False,
            customdata=[minutes[i] for i in valid],
            hovertemplate="%{y}<br>%{text} points per 48<br>%{customdata:,.0f} minutes<extra></extra>",
        ))
        extent = max(5, *(abs(values[i]) for i in valid)) * 1.22
        fig.update_xaxes(range=[-extent, extent], title_text="Team point margin per 48 minutes")
    for i, label in enumerate(labels):
        if i not in valid:
            fig.add_annotation(x=0, y=label, text="Unavailable", showarrow=False, xshift=8, xanchor="left")
    fig.update_yaxes(categoryorder="array", categoryarray=list(reversed(labels)), fixedrange=True)
    fig.add_vline(x=0, line_color="#697681", line_width=1)
    fig.update_layout(height=230, margin=dict(l=80, r=35, t=12, b=54), showlegend=False)
    return fig


def scout_peers(frame, min_minutes, selected_id, selected_team, min_games=20):
    eligible = frame.loc[frame.games.ge(min_games) & frame.minutes_on.ge(min_minutes)]
    eligible = eligible.dropna(subset=["on_per48", "off_per48", "on_off_diff"]).copy()
    eligible["rank"] = eligible.on_off_diff.rank(method="min", ascending=False).astype(int)
    eligible["tied"] = eligible.on_off_diff.duplicated(keep=False)
    eligible["selected"] = eligible.player_id.eq(selected_id) & eligible.team_id.eq(selected_team)
    return eligible.sort_values(["rank", "player_name", "team_id"])


def _stint_tooltip_background(accent):
    navy = (37, 55, 70)
    team = bytes.fromhex(accent.lstrip("#"))
    # Keep the fill dark enough for light text, even for bright team colors.
    return "#" + bytes(round(.7 * base + .3 * color) for base, color in zip(navy, team)).hex()


def scatter(frame, selected_id, selected_team):
    import plotly.graph_objects as go

    player = frame.player_id.eq(selected_id)
    current = player & frame.team_id.eq(selected_team)
    fig = go.Figure()
    for mask, name, highlighted, primary in (
        (~player, "League peers", False, False),
        (player & ~current, "Other stints for this player", True, False),
        (current, "Stint shown above", True, True),
    ):
        rows = frame.loc[mask]
        if rows.empty:
            continue
        numbers = rows.stint_number.astype(str).tolist() if highlighted else None
        marker = (
            dict(color="#fffdf8", size=21 if primary else 18,
                 line=dict(color=rows.team_accent, width=3 if primary else 2))
            if highlighted else dict(color="#8997a0", size=7, opacity=.5)
        )
        custom = rows[["on_per48", "off_per48"]].map(signed_margin).assign(stint=rows.stint_label)
        hover_label = None
        heading = "%{customdata[2]}"
        if highlighted:
            hover_label = dict(
                bgcolor=rows.team_accent.map(_stint_tooltip_background).tolist(),
                bordercolor=rows.team_accent.tolist(),
                font=dict(color="#fff7ed"),
            )
            heading = f"<b>{heading}</b>"
            if primary:
                heading += "<br>Selected team stint"
        fig.add_trace(go.Scatter(
            x=rows.off_per48, y=rows.on_per48,
            mode="markers+text" if highlighted else "markers", text=numbers,
            textposition="middle center", textfont=dict(color="#202c36", size=11, weight=700),
            name=name, marker=marker, showlegend=not highlighted, zorder=1 if highlighted else 0,
            customdata=custom, hoverlabel=hover_label,
            hovertemplate=(
                heading + "<br>On court: %{customdata[0]}<br>On bench: %{customdata[1]}<extra></extra>"
            ),
        ))
    if not frame.empty:
        lo = min(frame.on_per48.min(), frame.off_per48.min())
        hi = max(frame.on_per48.max(), frame.off_per48.max())
        pad = max(1, (hi - lo) * .08)
        bounds = [lo - pad, hi + pad]
        fig.add_trace(go.Scatter(
            x=bounds, y=bounds, mode="lines", name="Same margin",
            line=dict(color="#697681", dash="dot"), hoverinfo="skip",
        ))
        fig.update_xaxes(range=bounds)
        fig.update_yaxes(range=bounds)
    fig.update_xaxes(tickformat=".1f", hoverformat=".1f")
    fig.update_yaxes(tickformat=".1f", hoverformat=".1f")
    fig.update_layout(
        xaxis_title="On bench · point margin per 48",
        yaxis_title="On court · point margin per 48",
        height=390,
        margin=dict(l=45, r=20, t=14, b=55),
        legend=dict(orientation="h", y=1.09),
    )
    return fig
