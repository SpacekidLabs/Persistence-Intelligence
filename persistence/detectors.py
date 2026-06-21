from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    from scipy.signal import get_window
except ImportError:
    get_window = None


@dataclass
class FrameAnalysis:
    frames: np.ndarray
    frame_times: np.ndarray
    frequencies: np.ndarray
    spectrum: np.ndarray
    spectrum_db: np.ndarray
    power: np.ndarray
    energy: np.ndarray
    active: np.ndarray


def normalize(signal: np.ndarray) -> np.ndarray:
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


def analysis_window(size: int) -> np.ndarray:
    if get_window is not None:
        return get_window("hann", size, fftbins=True)
    return np.hanning(size)


def frame_signal(signal: np.ndarray, window_size: int, hop_size: int) -> np.ndarray:
    frame_count = 1 + (len(signal) - window_size) // hop_size
    shape = (frame_count, window_size)
    strides = (signal.strides[0] * hop_size, signal.strides[0])
    return np.lib.stride_tricks.as_strided(signal, shape=shape, strides=strides).copy()


def analyze_frames(
    signal: np.ndarray,
    sample_rate: int,
    window_size: int,
    hop_size: int,
    active_floor_ratio: float = 0.01,
) -> FrameAnalysis:
    frames = frame_signal(signal, window_size, hop_size)
    windowed = frames * analysis_window(window_size)

    spectrum = np.abs(np.fft.rfft(windowed, axis=1))
    power = spectrum**2
    frequencies = np.fft.rfftfreq(window_size, d=1 / sample_rate)
    frame_times = (np.arange(len(frames)) * hop_size + window_size / 2) / sample_rate

    energy = np.mean(frames**2, axis=1)
    energy_floor = max(float(np.max(energy)) * active_floor_ratio, 1e-10)
    active = energy > energy_floor
    spectrum_db = 20 * np.log10(spectrum.T + 1e-8)

    return FrameAnalysis(
        frames=frames,
        frame_times=frame_times,
        frequencies=frequencies,
        spectrum=spectrum,
        spectrum_db=spectrum_db,
        power=power,
        energy=energy,
        active=active,
    )

