# Signal Processing Laboratory

A research-oriented digital signal-processing laboratory and Python toolkit, implemented from first principles and exposed through multiple interfaces.

[![Python](https://img.shields.io/badge/python-3.11+-black?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache--2.0-black)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-pytest%20%2B%20Hypothesis-black?logo=pytest&logoColor=white)](tests/)
[![UI](https://img.shields.io/badge/UI-midnight%20black-black)](#design-language)

> One computational core, multiple interfaces: a **Python library**, **CLI**, **interactive web laboratory**, **REST API**, and **MCP server**.

---

## Overview

Signal Processing Laboratory is a Python-based digital signal-processing system designed to make the underlying mathematics inspectable while remaining practical for real analysis workflows.

The project combines educational implementations of fundamental algorithms with NumPy/SciPy-backed production paths. Educational implementations are explicitly tested against mathematical properties and reference implementations where appropriate.

Core capabilities include:

- Discrete Fourier Transform (DFT)
- Inverse DFT (IDFT)
- Radix-2 Cooley–Tukey FFT
- Short-Time Fourier Transform (STFT)
- Inverse STFT (ISTFT)
- Discrete Wavelet Transform (DWT)
- Inverse DWT (IDWT)
- FIR filter design
- IIR filter design
- Direct convolution
- FFT-based convolution
- Welch power spectral density estimation
- Peak detection
- Event detection
- Anomaly detection
- Feature extraction
- Kalman filtering
- Signal resampling
- Composable processing pipelines
- Signal visualization
- CSV / WAV / JSON input and output

The design principle is simple:

> **Make the computation inspectable, make the numerical behavior testable, and make the resulting signal understandable.**

---

# Architecture

The system is organized around a shared computational layer. Interfaces should not implement their own versions of signal-processing algorithms; they should call the same underlying operations exposed by the library.

```text
                         SIGNAL PROCESSING LABORATORY
                                      │
                                      ▼
                           ┌────────────────────┐
                           │    Signal Model    │
                           │                    │
                           │ samples            │
                           │ sampling rate      │
                           │ metadata            │
                           └─────────┬──────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │  Operation Layer   │
                           │                    │
                           │ DFT / FFT          │
                           │ STFT / DWT         │
                           │ Filters            │
                           │ Convolution        │
                           │ Resampling          │
                           │ Detection           │
                           │ Kalman filtering   │
                           └─────────┬──────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │ Analysis / Results │
                           │                    │
                           │ Spectrum           │
                           │ Features           │
                           │ Events             │
                           │ Anomalies          │
                           │ AnalysisResult     │
                           └─────────┬──────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
                 Library            CLI          Pipeline
                    │                │                │
                    └────────────────┼────────────────┘
                                     │
                         ┌───────────┴───────────┐
                         ▼                       ▼
                  Web Laboratory          REST / MCP
````

---

# Interfaces

| Interface          | Entry point                            | Purpose                                 |
| ------------------ | -------------------------------------- | --------------------------------------- |
| **Python library** | `from signal_processing import Signal` | Programmatic use, scripts, notebooks    |
| **CLI**            | `signal-process`                       | Terminal workflows and automation       |
| **Web laboratory** | `signal-process lab`                   | Interactive signal exploration          |
| **REST API**       | `signal-process-api`                   | HTTP-based integration                  |
| **MCP server**     | `signal-process-mcp`                   | Tool access from MCP-compatible clients |

All interfaces are intended to use the same underlying operation layer.

---

# Quick Start

## Requirements

* Python 3.11+
* `pip`
* `make` for development shortcuts
* Docker for the containerized stack

## Clone

```bash
git clone <repository-url>
cd signal-processing
```

## Create an environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

## Install

```bash
pip install -e ".[all,api,mcp]"
```

If the project does not define the optional dependency groups above, install the dependencies specified in `pyproject.toml` instead.

---

# Run the Tests

```bash
pytest
```

The test suite is organized into:

```text
tests/
├── unit/
├── property/
└── integration/
```

### Unit tests

Test individual models, algorithms and utilities.

### Property-based tests

Hypothesis is used to test mathematical and behavioral properties across a wide range of generated inputs.

Examples include:

```text
DFT → IDFT → original signal
```

and:

```text
direct convolution ≈ FFT convolution
```

### Integration tests

Integration tests verify that multiple components work together as a complete processing workflow.

---

# Example

A minimal signal-processing workflow:

```python
import numpy as np

from signal_processing import Signal

samples = np.sin(
    2 * np.pi * 440 * np.arange(0, 2, 1 / 44100)
)

signal = Signal(
    samples=samples,
    sampling_rate=44100,
)

print("Mean:", signal.mean())
print("RMS:", signal.rms())

normalized = signal.normalize()
```

The exact public API is defined by the implementation and documented API reference.

---

# Processing Workflow

The intended workflow is:

```text
Input
  │
  ▼
Signal
  │
  ▼
Preprocessing
  │
  ├── Normalize
  ├── Resample
  └── Filter
  │
  ▼
Transformation
  │
  ├── DFT
  ├── FFT
  ├── STFT
  └── DWT
  │
  ▼
Analysis
  │
  ├── Spectrum
  ├── PSD
  ├── Features
  ├── Peaks
  └── Events
  │
  ▼
Detection
  │
  ├── Anomalies
  └── State estimation
  │
  ▼
AnalysisResult
```

The goal is for each stage to preserve the information required by downstream analysis.

---

# Core Algorithms

## Discrete Fourier Transform

The project includes an explicit direct DFT implementation.

The direct implementation exists primarily for educational transparency and verification.

Complexity:

```text
O(N²)
```

It provides a reference point for understanding the Fourier transform before moving to FFT implementations.

---

## Radix-2 FFT

A hand-written radix-2 Cooley–Tukey FFT is included to expose the algorithmic structure of the fast Fourier transform.

Complexity:

```text
O(N log N)
```

The educational implementation should be validated against a trusted numerical reference.

---

## STFT

Short-Time Fourier Transform provides localized time-frequency analysis.

The implementation includes:

* windowing
* configurable hop size
* configurable window
* frequency representation
* time representation
* inverse reconstruction where supported

---

## Wavelets

The project includes discrete wavelet transforms for localized multi-resolution analysis.

```text
Signal
  │
  ▼
Wavelet decomposition
  │
  ├── Approximation
  ├── Detail level 1
  ├── Detail level 2
  └── ...
  │
  ▼
Reconstruction
```

---

## Filters

Supported filter functionality includes FIR and IIR designs.

The filter layer should expose:

* design parameters
* coefficients
* frequency response
* application to signals

---

## Convolution

Both direct and FFT-based convolution paths are provided.

The two implementations can be compared numerically to validate the optimized path.

```text
x(t) ─────┐
          ├── Convolution ──► y(t)
h(t) ─────┘
```

---

## Spectral Analysis

The analysis layer includes tools such as:

* FFT spectra
* power spectral density
* Welch PSD
* spectral peaks
* frequency-domain features

---

## Event and Anomaly Detection

The detection layer converts signal behavior into structured events.

Conceptually:

```text
Signal
  │
  ▼
Features
  │
  ▼
Detection
  │
  ▼
Event / Anomaly
  │
  ▼
AnalysisResult
```

Detected events should retain relevant timing, measurements and metadata so that the result can be traced back to the source signal.

---

## Kalman Filtering

The project includes a Kalman filter implementation for state estimation from noisy measurements.

The implementation separates:

```text
Prediction
     ↓
Measurement
     ↓
Update
     ↓
Estimated state
```

---

# Pipelines

Operations can be composed into reusable processing pipelines.

Conceptually:

```python
pipeline = (
    Pipeline()
    .add(...)
    .add(...)
    .add(...)
)

result = pipeline.run(signal)
```

A pipeline should make processing steps explicit and reproducible.

Example:

```text
Raw signal
    ↓
Normalize
    ↓
Low-pass filter
    ↓
FFT
    ↓
Feature extraction
    ↓
Anomaly detection
    ↓
Analysis result
```

---

# Interactive Web Laboratory

The web laboratory provides a visual environment for exploring signals and processing operations.

Launch it with:

```bash
make lab
```

or:

```bash
streamlit run app/main.py
```

The laboratory is designed around the idea that the **signal itself should be the primary visual object**.

A typical experiment should expose:

```text
INPUT
  ↓
SIGNAL
  ↓
PROCESSING
  ↓
TRANSFORMATION
  ↓
ANALYSIS
  ↓
RESULT
```

The interface should make it possible to see how an operation changes the signal rather than only displaying a final number.

---

# REST API

The REST API exposes the computational system over HTTP.

Example development command:

```bash
signal-process-api
```

or:

```bash
uvicorn signal_processing.api:app --reload
```

If FastAPI is used, interactive API documentation is available through the standard FastAPI documentation endpoints when the server is running.

The API should expose the same underlying operations as the Python library wherever practical.

---

# MCP Server

The project optionally exposes signal-processing capabilities through an MCP server.

Launch:

```bash
signal-process-mcp
```

The MCP layer is intended to provide structured access to operations such as:

```text
load signal
inspect signal
transform signal
filter signal
analyze spectrum
detect events
detect anomalies
run pipeline
```

The MCP implementation should remain a thin integration layer over the core processing engine rather than becoming a second computational implementation.

---

# Numerical Validation

Scientific software requires more than tests that merely confirm that functions execute.

The project therefore separates:

```text
Implementation
     │
     ▼
Mathematical properties
     │
     ▼
Reference implementations
     │
     ▼
Numerical tolerances
     │
     ▼
Integration behavior
```

Examples of validation targets include:

### Fourier transforms

```text
DFT ↔ IDFT reconstruction
Educational DFT ↔ reference FFT
Educational FFT ↔ reference FFT
Frequency-axis correctness
```

### Convolution

```text
Direct convolution ≈ FFT convolution
```

### Wavelets

```text
DWT → IDWT ≈ original signal
```

### Filtering

```text
Frequency response
Passband behavior
Stopband behavior
Coefficient validity
```

### Resampling

```text
Expected output length
Sampling-rate metadata
Signal integrity
```

### Kalman filtering

```text
State propagation
Measurement update
Noise handling
Numerical stability
```

Numerical comparisons should use explicit tolerances rather than exact floating-point equality.

---

# Project Structure

```text
signal-processing/
│
├── src/
│   └── signal_processing/
│       ├── models/
│       ├── transforms/
│       ├── filters/
│       ├── analysis/
│       ├── detection/
│       ├── pipelines/
│       ├── io/
│       ├── utils/
│       └── ...
│
├── tests/
│   ├── unit/
│   ├── property/
│   └── integration/
│
├── examples/
│
├── benchmarks/
│
├── docs/
│   ├── architecture.md
│   ├── algorithms.md
│   ├── validation.md
│   └── api.md
│
├── app/
│
├── pyproject.toml
├── Dockerfile
├── Makefile
├── README.md
└── LICENSE
```

The exact structure may vary as the project evolves.

---

# Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

Run formatting:

```bash
ruff format .
```

Run static type checking if configured:

```bash
mypy src
```

Build the package:

```bash
python -m build
```

---

# Benchmarks

Performance-sensitive operations should be benchmarked separately from correctness tests.

The project can compare:

```text
Direct DFT
     vs
Radix-2 FFT
     vs
NumPy FFT
```

and:

```text
Direct convolution
     vs
FFT convolution
     vs
SciPy reference
```

Benchmarks should report:

* input size
* execution time
* memory behavior where relevant
* numerical error
* implementation used
* Python/environment information

Correctness and performance should be evaluated separately.

---

# Design Language

The laboratory uses a deliberately restrained visual language.

### Principles

* Midnight-black foundation
* Soft white typography
* Hairline dividers
* Minimal borders
* Generous negative space
* System-style typography
* Monospace numerical readouts
* Precise alignment
* Sparse scientific annotations
* Minimal animation
* Data-first visualization

The visual language is inspired by modern scientific instruments, contemporary information design and the restraint of modern desktop operating systems.

It intentionally avoids:

* generic SaaS dashboards
* excessive cards
* neon cyberpunk styling
* unnecessary gradients
* excessive shadows
* decorative AI imagery
* visual noise

The objective is to make the interface feel like a **scientific instrument**, not a dashboard.

---

# Design Philosophy

The project has two complementary goals.

### 1. Computational transparency

Core algorithms should be understandable.

Where an educational implementation exists, the code should expose the underlying computation rather than hiding it behind a high-level dependency.

### 2. Practical usability

Production workflows should not require users to manually understand every implementation detail.

Where appropriate, NumPy/SciPy-backed operations provide efficient production paths.

The distinction is intentional:

```text
                    SIGNAL
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
        EDUCATIONAL         PRODUCTION
        IMPLEMENTATION        BACKEND
              │                 │
              └────────┬────────┘
                       ▼
                  SAME RESULT
                       │
                       ▼
                 VALIDATION
```

---

# Examples

The `examples/` directory contains runnable demonstrations of individual capabilities and complete workflows.

Examples should remain:

* small
* reproducible
* executable
* focused on one concept
* consistent with the public API

Example categories include:

```text
examples/
├── signal_generation
├── fft_analysis
├── filtering
├── stft
├── wavelets
├── convolution
├── anomaly_detection
├── kalman_filter
└── end_to_end_pipeline
```

---

# Reproducibility

Scientific results should be reproducible wherever randomness is involved.

Experiments should document:

* sampling rate
* signal duration
* signal parameters
* random seeds where applicable
* algorithm configuration
* numerical tolerance
* software environment

---

# Documentation

The repository keeps documentation focused on information that helps users understand, validate and extend the system.

Recommended documentation:

```text
docs/
├── architecture.md
├── algorithms.md
├── validation.md
└── api.md
```

### `architecture.md`

Explains how the system is organized and how the interfaces interact with the core.

### `algorithms.md`

Explains the mathematical and computational principles behind major algorithms.

### `validation.md`

Documents numerical validation methodology, tolerances and reference comparisons.

### `api.md`

Documents the public Python API and supported interfaces.

---

# Engineering Standards

The project aims to maintain:

* explicit public APIs
* deterministic behavior where possible
* numerical validation
* type annotations
* meaningful exceptions
* reproducible examples
* automated testing
* continuous integration
* documented algorithms
* separation between core computation and interfaces

---

# Validation Checklist

Before considering a release, verify:

```text
[ ] Package installs from a clean environment
[ ] Public imports work
[ ] Unit tests pass
[ ] Property-based tests pass
[ ] Integration tests pass
[ ] Examples execute successfully
[ ] Educational algorithms match reference implementations
[ ] Numerical tolerances are documented
[ ] Pipeline execution works end-to-end
[ ] Web laboratory launches
[ ] REST API launches
[ ] MCP server launches
[ ] Docker build succeeds
[ ] CI succeeds
[ ] Documentation matches the current API
[ ] README claims are supported by the implementation
```

The final item is particularly important:

> **Documentation should describe what the repository actually does, not what it is intended to do.**

---

# Roadmap

Potential future work includes:

* additional wavelet families
* improved streaming processing
* GPU acceleration
* richer spectral analysis
* real-time signal acquisition
* additional anomaly-detection methods
* expanded benchmark suite
* hardware-in-the-loop experiments
* richer experiment provenance
* additional visualization modes

Roadmap items are exploratory unless implemented and tested.

---

# License

This project is licensed under the Apache License 2.0.

See [`LICENSE`](LICENSE) for the full license text.

---

# Status

This project is under active development.

Capabilities described above should be considered supported only when they are implemented, tested and runnable in the current repository.

The repository prioritizes **correctness, reproducibility and inspectability over feature count**.

```
