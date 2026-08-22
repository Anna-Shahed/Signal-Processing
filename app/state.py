"""Session-state store — one place where the instrument's state lives."""

from __future__ import annotations

import streamlit as st

DEFAULTS = {
    "route": "lab",
    "signal": None,
    "spectrum": None,
    "pipeline_stages": [],
    "analysis": None,
    "events": [],
    "anomalies": [],
    "project": None,
}


def init_state() -> None:
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)


def get(key: str):
    return st.session_state.get(key)


def set(key: str, value) -> None:
    st.session_state[key] = value
