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


def compute_taxonomy_metrics(
    energy: np.ndarray,
    peak_frequencies: np.ndarray | None = None,
    centroids: np.ndarray | None = None,
    recurrence_values: np.ndarray | None = None,
    total_energy: np.ndarray | None = None,
    frame_times: np.ndarray | None = None,
) -> dict[str, float]:
    """Computes the 6 harmonized metrics for the taxonomy analysis."""
    from persistence.trackers import band_stability_score, survival_time
    
    # 1. survival_time
    if frame_times is not None:
        surv = survival_time(frame_times, energy, threshold=0.1)
    else:
        surv = 0.0
        
    # 2. identity_stability
    if peak_frequencies is not None and centroids is not None:
        frequency_stability = normalized_inverse_variation(peak_frequencies, tolerance=18.0)
        centroid_stability = normalized_inverse_variation(centroids, tolerance=140.0)
        stability = float(np.sqrt(frequency_stability * centroid_stability))
    else:
        stability = band_stability_score(energy)
        
    # 3. energy_decay (measured as energy retention score)
    retention = energy_retention_score(energy)
    
    # 4. recovery_after_perturbation
    n = len(energy)
    if n < 10:
        recovery = 1.0
    else:
        post_transient = energy[int(n * 0.15):]
        if len(post_transient) < 2:
            recovery = 1.0
        else:
            recovery = float(1.0 / (1.0 + np.std(post_transient)))
            
    # 5. competition_strength
    if total_energy is not None:
        ratio = energy / (total_energy + 1e-12)
        comp_strength = float(np.clip(np.mean(ratio), 0, 1))
    else:
        comp_strength = 1.0  # Default to 1.0 for single isolated signals
        
    # 6. state_memory
    if recurrence_values is not None:
        memory = float(np.mean(recurrence_values))
    else:
        # Compute autocorrelation-based self-similarity
        if n >= 4:
            half = n // 2
            first_half = energy[:half]
            second_half = energy[half:2*half]
            denom = np.linalg.norm(first_half) * np.linalg.norm(second_half)
            if denom > 0:
                memory = float(np.clip(np.dot(first_half, second_half) / denom, 0, 1))
            else:
                memory = 0.0
        else:
            memory = 0.0
            
    return {
        "survival_time": surv,
        "identity_stability": stability,
        "energy_decay": retention,
        "recovery_after_perturbation": recovery,
        "competition_strength": comp_strength,
        "state_memory": memory,
    }


