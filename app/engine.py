from __future__ import annotations

from typing import Any, Callable

import streamlit as st


def run_task(label: str, fn: Callable[[], Any]) -> Any:
    """Run ``fn`` inside a collapsible status block; errors become callouts."""
    try:
        with st.status(label, expanded=False) as status:
            result = fn()
            status.update(label=f"✓ {label}", state="complete")
        return result
    except ZeroDivisionError:
        st.error("Division by zero — check signal amplitude or threshold values.")
    except FloatingPointError:
        st.error("Numerical instability detected — check for NaN or infinite inputs.")
    except (ValueError, IndexError, KeyError) as exc:
        st.warning(f"Shape or value error: {exc}")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Processing failed: {exc}")
    return None
