"""Keeps the chosen crop and season in sync across views."""
import streamlit as st


def init_state(cal_df):
    if "master_crop" not in st.session_state:
        crops = sorted(cal_df["crop"].unique())
        st.session_state.master_crop = "Irish potato" if "Irish potato" in crops else crops[0]
    if "master_season" not in st.session_state:
        seasons = sorted(cal_df.loc[cal_df["crop"] == st.session_state.master_crop, "season"].unique())
        st.session_state.master_season = "Season A" if "Season A" in seasons else seasons[0]


def sync_crop(widget_key):
    st.session_state.master_crop = st.session_state[widget_key]


def sync_season(widget_key):
    st.session_state.master_season = st.session_state[widget_key]


def get_active_index(options, master_key):
    val = st.session_state.get(master_key)
    return options.index(val) if val in options else 0
