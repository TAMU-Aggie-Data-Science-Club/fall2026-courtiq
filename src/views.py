"""Streamlit profile components; calculations and collection belong elsewhere."""

import streamlit as st


# Owner: June Hwang — edit only this function body.
def render_player_profile(frame, metadata):
    """Display only: canonical player table + provenance in, Streamlit elements out."""
    if frame.empty:
        st.info("No player records are available for this period.")
        return
    # TODO(June) 1: Select PLAYER_ID with a readable PLAYER_NAME label. Example:
    # labels = dict(zip(frame["PLAYER_ID"], frame["PLAYER_NAME"]))
    # selected = st.selectbox("Player", options=list(labels), format_func=labels.get,
    #                         key="profile_player")
    # TODO 2: Select that row; display GP and points/rebounds/assists per game.
    # Use st.columns and st.metric. For missing values display "Unavailable", not 0.
    # Example: st.metric("Example label", "12.3")
    # TODO 3: Caption source/season/type/retrieval time. No collection or formulas here.
    st.info("June: implement the player selector and season summary in render_player_profile().")


# Owner: Casey Hawkings — edit only this function body.
def render_team_profile(frame, metadata):
    """Canonical basic team table + provenance in; selected team display out."""
    if frame.empty:
        st.info("No team records are available for this period.")
        return
    # TODO(Casey) 1: st.selectbox with TEAM_ID as value and TEAM_NAME as readable label.
    # Example: labels = dict(zip(frame["TEAM_ID"], frame["TEAM_NAME"]))
    # st.selectbox("Team", list(labels), format_func=labels.get, key="profile_team")
    # TODO 2: st.metric for GP, wins, losses, and source W_PCT (format as a percent).
    # Display the three per-game averages too; handle missing values explicitly.
    # Example: f"{0.625:.1%}" → "62.5%". This formats, rather than recalculates, a value.
    # TODO 3: Display source, season/type and retrieval time. No analytics formulas here.
    st.info("Casey: implement team selection and the record summary in render_team_profile().")
