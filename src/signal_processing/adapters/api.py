"""REST API — same operation layer, served over HTTP, readable by any agent.

Run locally:   uvicorn signal_processing.api:app --reload --port 8000
Public docs:   /docs          (Swagger UI)
Agent entry:   /openapi.json  (OpenAPI 3.1 — point any LLM/agent at this)
Remote MCP:    /mcp           (streamable-http transport)
"""

from __future__ import annotations

import asyncio

import numpy as np
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from . import __version__
from .adapters.operations import (
    analyze_signal,
    convolve_op,
    detect_anomalies_op,
    detect_events_op,
    fft_spectrum,
    filter_signal,
    generate_signal,
    kalman_op,
    pipeline_run,
    resample_op,
    stft_op,
)

app = FastAPI(
    title="Signal Processing Laboratory API",
    version=__version__,
    description="Generate, transform, filter, and analyze signals. "
                "Consumable by any agent via OpenAPI or MCP (/mcp).",
)


@app.get("/health")
def health() -> dict:
    """Liveness probe for container orchestration."""
    return {"status": "ok", "version": __version__}


@app.post("/generate", tags=["signals"])
def generate(payload: dict) -> dict:
    return generate_signal(**payload)


@app.post("/fft", tags=["transforms"])
def fft(payload: dict) -> dict:
    return fft_spectrum(**payload)


@app.post("/filter", tags=["transforms"])
def filt(payload: dict) -> dict:
    return filter_signal(**payload)


@app.post("/analyze", tags=["analysis"])
def analyze(payload: dict) -> dict:
    return analyze_signal(**payload)


@app.post("/events", tags=["analysis"])
def events(payload: dict) -> dict:
    return detect_events_op(**payload)


@app.post("/anomalies", tags=["analysis"])
def anomalies(payload: dict) -> dict:
    return detect_anomalies_op(**payload)


@app.post("/stft", tags=["transforms"])
def stft(payload: dict) -> dict:
    return stft_op(**payload)


@app.post("/resample", tags=["transforms"])
def resample(payload: dict) -> dict:
    return resample_op(**payload)


@app.post("/convolve", tags=["transforms"])
def conv(payload: dict) -> dict:
    return convolve_op(**payload)


@app.post("/kalman", tags=["analysis"])
def kalman(payload: dict) -> dict:
    return kalman_op(**payload)


@app.post("/pipeline", tags=["pipelines"])
def pipe(payload: dict) -> dict:
    return pipeline_run(**payload)


@app.websocket("/ws/stream")
async def ws_stream(websocket: WebSocket) -> None:
    """Real-time streaming: emits live sine chunks with a running spectrum.

    Connect from any WebSocket client:
        ws://localhost:8000/ws/stream
    """
    await websocket.accept()
    fs, freq = 8_000.0, 440.0
    t = 0.0
    try:
        while True:
            block = np.sin(2 * np.pi * freq * np.arange(256) / fs + t)
            t += 256 / fs
            await websocket.send_json({
                "t": round(t, 4),
                "samples": block.tolist(),
                "rms": float(np.sqrt(np.mean(block ** 2))),
            })
            await asyncio.sleep(1 / 30)
    except WebSocketDisconnect:
        return


# Mount the MCP server (streamable-http) for remote agents — optional dep.
try:  # pragma: no cover
    from .mcp_server import mcp_asgi
    app.mount("/mcp", mcp_asgi())
except Exception:  # mcp not installed
    pass


def main() -> None:
    uvicorn.run("signal_processing.api:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
