from __future__ import annotations

import streamlit as st

KEYS = ("signal_data", "sample_rate", "pipeline_steps", "active_tab")

DEFAULTS = {
    "signal_data": None,
    "sample_rate": 8_000.0,
    "pipeline_steps": [],
    "active_tab": "lab",
}

_ALIASES = {
    "signal": "signal_data",
    "spectrum": "spectrum_data",
    "analysis": "analysis_result",
    "events": "events_data",
    "anomalies": "anomalies_data",
    "pipeline_stages": "pipeline_steps",
    "pipeline_steps": "pipeline_steps",
}


def _canonical(key: str) -> str:
    return _ALIASES.get(key, key)


def init_state() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get(key: str):
    return st.session_state.get(_canonical(key), DEFAULTS.get(_canonical(key)))


def set(key: str, value) -> None:
    st.session_state[_canonical(key)] = value


def reset_signal() -> None:
    st.session_state["signal_data"] = None
    st.session_state["spectrum_data"] = None
    st.session_state["analysis_result"] = None
    st.session_state["events_data"] = []
    st.session_state["anomalies_data"] = []
