"""CLI smoke tests: subcommands run and produce real files."""

from __future__ import annotations

from signal_processing.cli.main import main
from signal_processing.io import read_wav


def test_cli_generate_creates_wav(tmp_path):
    out = tmp_path / "tone.wav"
    rc = main(["generate", "--waveform", "sine", "--frequency", "440",
               "--duration", "0.1", "--sampling-rate", "8000",
               "-o", str(out)])
    assert rc == 0
    assert out.is_file()
    sig = read_wav(out)
    assert sig.sampling_rate == 8_000
    assert sig.n_samples == 800


def test_cli_fft_reports_dominant_frequency(tmp_path, capsys):
    out = tmp_path / "tone.wav"
    main(["generate", "--waveform", "sine", "--frequency", "100",
          "--duration", "1.0", "--sampling-rate", "2000", "-o", str(out)])
    rc = main(["fft", str(out), "--peaks", "3"])
    captured = capsys.readouterr().out
    assert rc == 0
    assert "Dominant frequency" in captured
    assert "100" in captured


def test_cli_demo_writes_artifacts(tmp_path):
    out_dir = tmp_path / "demo"
    rc = main(["demo", "-o", str(out_dir)])
    assert rc == 0
    assert (out_dir / "01_raw.wav").is_file()
    assert (out_dir / "02_filtered.wav").is_file()
    assert (out_dir / "03_analysis.json").is_file()
    assert (out_dir / "05_dashboard.png").is_file()
