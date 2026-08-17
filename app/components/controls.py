"""Reusable Streamlit controls: signal export buttons."""

from __future__ import annotations

import io as _io

import numpy as np
import soundfile as sf
import streamlit as st

from signal_processing import Signal
from signal_processing.io.json import to_json_string


def _wav_bytes(signal: Signal, subtype: str = "PCM_16") -> bytes:
    buf = _io.BytesIO()
    samples = np.asarray(signal.samples, dtype=float)
    if samples.ndim > 1:
        samples = samples[:, 0]
    sf.write(buf, samples, int(round(signal.sampling_rate)), subtype=subtype, format="WAV")
    return buf.getvalue()


def _csv_bytes(signal: Signal) -> bytes:
    buf = _io.StringIO()
    data = np.column_stack((np.asarray(signal.time, dtype=float),
                            np.asarray(signal.samples, dtype=float)))
    np.savetxt(buf, data, delimiter=",", header="time,value", comments="")
    return buf.getvalue().encode("utf-8")


def export_buttons(signal: Signal, *, key: str = "export") -> None:
    """Render WAV / CSV / JSON download buttons for a signal."""
    stem = (signal.name or "signal").replace(" ", "_")
    st.markdown("**Export signal**")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("WAV", _wav_bytes(signal), file_name=f"{stem}.wav",
                           mime="audio/wav", key=f"{key}_wav", use_container_width=True)
    with c2:
        st.download_button("CSV", _csv_bytes(signal), file_name=f"{stem}.csv",
                           mime="text/csv", key=f"{key}_csv", use_container_width=True)
    with c3:
        st.download_button("JSON", to_json_string(signal), file_name=f"{stem}.json",
                           mime="application/json", key=f"{key}_json",
                           use_container_width=True)
