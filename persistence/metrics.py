from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from persistence.detectors import FrameAnalysis


@dataclass
class PersistenceMetrics:
    persistence: float
    energy_retention: float
    frequency_stability: float
    centroid_stability: float
    stability: float
    continuity: float


def safe_mean(values: np.ndarray) -> float:
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return 0.0
    return float(np.mean(values))


def normalized_inverse_variation(values: np.ndarray, tolerance: float) -> float:
    active = values[np.isfinite(values)]
    if len(active) < 2:
        return 0.0
    return float(1.0 / (1.0 + (np.std(active) / tolerance)))


def energy_retention_score(energy: np.ndarray) -> float:
    early = energy[: max(3, len(energy) // 5)]
    late = energy[-max(3, len(energy) // 5) :]
    return float(np.clip(safe_mean(late) / (safe_mean(early) + 1e-12), 0, 1))


def continuity_score(frame_analysis: FrameAnalysis) -> float:
    continuity_values = []
    active_frames = frame_analysis.frames[frame_analysis.active]
    for left, right in zip(active_frames[:-1], active_frames[1:]):
        left_norm = np.linalg.norm(left)
        right_norm = np.linalg.norm(right)
        if left_norm == 0 or right_norm == 0:
            continue
        continuity_values.append(np.dot(left, right) / (left_norm * right_norm))
    return float(np.clip((safe_mean(np.array(continuity_values)) + 1.0) / 2.0, 0, 1))


def persistence_score(
    frame_analysis: FrameAnalysis,
    peak_frequencies: np.ndarray,
    centroids: np.ndarray,
    frequency_tolerance: float = 18.0,
    centroid_tolerance: float = 140.0,
) -> PersistenceMetrics:
    energy_retention = energy_retention_score(frame_analysis.energy)
    frequency_stability = normalized_inverse_variation(
        peak_frequencies,
        tolerance=frequency_tolerance,
    )
    centroid_stability = normalized_inverse_variation(
        centroids,
        tolerance=centroid_tolerance,
    )
    stability = float(np.sqrt(frequency_stability * centroid_stability))
    continuity = continuity_score(frame_analysis)
    persistence = float(energy_retention * stability * continuity)

    return PersistenceMetrics(
        persistence=persistence,
        energy_retention=energy_retention,
        frequency_stability=frequency_stability,
        centroid_stability=centroid_stability,
        stability=stability,
        continuity=continuity,
    )

