import numpy as np

from signal_processing.generators import composite, sine, white_noise
from signal_processing.transforms import (
    dft,
    fft,
    fft_radix2_educational,
    ifft,
    stft,
)

tone = sine(
    frequency=440,
    amplitude=1.0,
    duration=2.0,
    sampling_rate=4_000,
)

noise = white_noise(
    duration=2.0,
    sampling_rate=4_000,
    amplitude=0.05,
    seed=42,
)

signal = composite(tone, noise)

spectrum = fft(signal, one_sided=True)
reconstructed = ifft(spectrum)

educational_fft = fft_radix2_educational(signal.samples[:1024])
educational_dft = dft(signal.samples[:128])

spectrogram = stft(
    signal,
    nperseg=256,
    hop_length=128,
    window="hann",
)
