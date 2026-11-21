"""Explicit daily odds refresh. UI imports never trigger network requests."""
from datetime import datetime, timezone
import json
import os
import pandas as pd
import requests
from src.pipeline import APP


def refresh(key=None, now=None, session=None):
    now=now or datetime.now(timezone.utc)
    path=APP/"odds_today.csv"
    meta=APP/"odds_today.meta.json"
    if path.exists() and meta.exists() and json.loads(meta.read_text())["date"]==now.date().isoformat():
        return pd.read_csv(path), "Reused today's cached odds; no request made."
    key=key or os.environ.get("ODDS_API_KEY")
    if not key: raise ValueError("ODDS_API_KEY is missing. Manual matchup mode remains available.")
    client=session or requests
    try:
        response=client.get("https://api.the-odds-api.com/v4/sports/basketball_nba/odds",
            params=dict(apiKey=key,regions="us",markets="h2h,spreads,totals",oddsFormat="american",dateFormat="iso"),timeout=20)
    except requests.RequestException:
        raise ValueError("Odds request failed or timed out. Cached/manual mode remains available.") from None
    if response.status_code!=200:
        raise ValueError(f"Odds service returned HTTP {response.status_code}; no automatic retry. Check credentials/quota privately.")
    try:
        payload=response.json()
        if not isinstance(payload,list): raise ValueError()
        rows=[]
        for event in payload:
            for book in event.get("bookmakers",[]):
                row={"event_id":event["id"],"commence_time":event["commence_time"],
                     "home_team":event["home_team"],"away_team":event["away_team"],"bookmaker":book["key"],
                     "updated":book.get("last_update"),"retrieved_at":now.isoformat()}
                for market in book.get("markets",[]):
                    for outcome in market.get("outcomes",[]):
                        if market["key"]=="totals": row["total"]=outcome.get("point")
                        else:
                            side="home" if outcome["name"]==event["home_team"] else "away"
                            row[f"{market['key']}_{side}"]=outcome.get("price")
                            if market["key"]=="spreads": row[f"spread_{side}"]=outcome.get("point")
                rows.append(row)
        columns=["event_id","commence_time","home_team","away_team","bookmaker","updated","retrieved_at"]
        table=pd.DataFrame(rows) if rows else pd.DataFrame(columns=columns)
    except (ValueError,TypeError,KeyError):
        raise ValueError("Malformed odds response; existing cache preserved.") from None
    APP.mkdir(exist_ok=True)
    table.to_csv(path,index=False)
    log=APP/"odds_log.csv"
    if log.exists():
        previous=pd.read_csv(log)
        pd.concat([previous,table],ignore_index=True).to_csv(log,index=False)
    else: table.to_csv(log,index=False)
    remaining=response.headers.get("x-requests-remaining","unknown")
    meta.write_text(json.dumps({"date":now.date().isoformat(),"remaining":remaining,"retrieved_at":now.isoformat()}),encoding="utf-8")
    return table,f"Saved {len(table)} bookmaker records. Credits remaining: {remaining}."
