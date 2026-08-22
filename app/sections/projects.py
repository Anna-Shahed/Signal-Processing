from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from app import components as ui
from app.state import get, set as set_state
from signal_processing import Signal, SignalValidationError

PROJECTS_DIR = Path("projects")


def _slug(name: str) -> str:
    cleaned = "".join(c if c.isalnum() or c in "-_." else "_"
                      for c in name.strip().lower())
    return cleaned or "untitled"


def _list_projects() -> list[Path]:
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(PROJECTS_DIR.glob("*.json"),
                  key=lambda p: p.stat().st_mtime, reverse=True)


def _save_project(name: str) -> None:
    signal = get("signal")
    if signal is None:
        st.warning("No signal in the workspace to save.")
        return
    payload = {
        "version": "0.1.0",
        "created": datetime.now(timezone.utc).isoformat(),
        "signal": signal.to_dict(),
        "pipeline_stages": get("pipeline_stages") or [],
        "metrics": (get("analysis").metrics if get("analysis") else {}),
    }
    path = PROJECTS_DIR / f"{_slug(name)}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    ui.metadata_row(f"saved -> {path}")


def _open_project(path: Path) -> None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        signal = Signal.from_dict(payload["signal"])
    except (KeyError, SignalValidationError, json.JSONDecodeError) as exc:
        st.error(f"Could not open {path.name}: {exc}")
        return
    set_state("signal", signal)
    set_state("pipeline_stages", payload.get("pipeline_stages", []))
    set_state("project", path.name)
    ui.metadata_row(f"opened -> {path.name}")

def render() -> None:
    ui.section_header("New Project")
    name = st.text_input("Project name", value="untitled",
                         label_visibility="collapsed")
    if st.button("Save current signal", type="primary"):
        _save_project(name)

    ui.section_header("Projects")
    projects = _list_projects()
    if not projects:
        st.caption("No saved projects yet.")
        return

    for path in projects:
        stamp = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        size = f"{path.stat().st_size / 1024:.1f} KB"
        c1, c2, c3 = st.columns([4, 1, 1])
        with c1:
            ui.metadata_row(f"{path.stem}  ·  {stamp}  ·  {size}")
        with c2:
            if st.button("Open", key=f"open_{path.stem}"):
                _open_project(path)
        with c3:
            if st.button("Delete", key=f"del_{path.stem}"):
                path.unlink(missing_ok=True)
                st.rerun()
