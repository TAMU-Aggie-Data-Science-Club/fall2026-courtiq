"""Impact presentation helpers reuse the shared pipeline's values."""
import pandas as pd
from src.pipeline import reliability


def missed_message(row):
    if pd.isna(row.games_missed): return "DNP coverage unavailable"
    if row.games_missed==0: return "Played every recorded game; absent roster rows are not inferred as DNPs."
    if row.games_missed<5: return "Too few missed games to interpret."
    return "Based only on explicitly recorded DNP rows in this team stint."


def scatter(frame, selected_id):
    import plotly.graph_objects as go
    valid=frame.dropna(subset=["on_per48","off_per48"])
    fig=go.Figure(go.Scatter(x=valid.on_per48,y=valid.off_per48,mode="markers",
        text=valid.player_name,marker=dict(color="#9ca3af"),name="League peers"))
    chosen=valid[valid.player_id.eq(selected_id)]
    fig.add_trace(go.Scatter(x=chosen.on_per48,y=chosen.off_per48,text=chosen.player_name,
        mode="markers",marker=dict(color="#d58b20",size=14),name="Selected player"))
    if not valid.empty:
        lo=min(valid.on_per48.min(),valid.off_per48.min()); hi=max(valid.on_per48.max(),valid.off_per48.max())
        fig.add_trace(go.Scatter(x=[lo,hi],y=[lo,hi],mode="lines",line=dict(color="gray",dash="dot"),name="No difference"))
    fig.update_layout(xaxis_title="On: point margin per 48 minutes",yaxis_title="Off: point margin per 48 minutes")
    return fig
