from __future__ import annotations

import numpy as np

from persistence.detectors import FrameAnalysis


def peak_frequency_trace(analysis: FrameAnalysis) -> np.ndarray:
    peak_bins = np.argmax(analysis.spectrum, axis=1)
    peaks = analysis.frequencies[peak_bins]
    return np.where(analysis.active, peaks, np.nan)


def spectral_centroid_trace(analysis: FrameAnalysis) -> np.ndarray:
    power_sum = np.sum(analysis.power, axis=1)
    centroids = np.divide(
        analysis.power @ analysis.frequencies,
        power_sum,
        out=np.zeros_like(power_sum),
        where=power_sum > 0,
    )
    return np.where(analysis.active, centroids, np.nan)


def band_energy_trace(
    analysis: FrameAnalysis,
    center_frequency: float,
    bandwidth: float,
    normalize: bool = True,
) -> np.ndarray:
    low = center_frequency - bandwidth / 2
    high = center_frequency + bandwidth / 2
    band = (analysis.frequencies >= low) & (analysis.frequencies <= high)
    if not np.any(band):
        return np.zeros_like(analysis.energy)

    energy = np.sum(analysis.power[:, band], axis=1)
    if normalize and np.max(energy) > 0:
        energy = energy / np.max(energy)
    return energy


def band_stability_score(energy: np.ndarray, active_threshold: float = 0.05) -> float:
    active = energy[energy > active_threshold]
    if len(active) < 2:
        return 0.0
    return float(1.0 / (1.0 + np.std(active)))


def survival_time(
    frame_times: np.ndarray,
    energy: np.ndarray,
    threshold: float = 0.1,
) -> float:
    active_times = frame_times[energy >= threshold]
    if len(active_times) == 0:
        return 0.0
    return float(active_times[-1] - active_times[0])
