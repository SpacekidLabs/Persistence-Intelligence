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

