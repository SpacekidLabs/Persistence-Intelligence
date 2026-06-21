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
    """Computes the 6 corrected taxonomy metrics, resolving the 4 identified flaws."""
    from persistence.trackers import band_stability_score
    
    # 1. survival_time (Effective Survival Time using ENBW of the energy curve)
    energy_sum = np.sum(energy)
    if energy_sum > 0:
        dt = frame_times[1] - frame_times[0] if (frame_times is not None and len(frame_times) > 1) else 1.0
        surv = float((energy_sum ** 2) / (np.sum(energy ** 2) + 1e-12) * dt)
    else:
        surv = 0.0
        
    # 2. identity_stability
    if peak_frequencies is not None and centroids is not None:
        frequency_stability = normalized_inverse_variation(peak_frequencies, tolerance=18.0)
        centroid_stability = normalized_inverse_variation(centroids, tolerance=140.0)
        stability = float(np.sqrt(frequency_stability * centroid_stability))
    else:
        stability = band_stability_score(energy)
        
    # 3. energy_decay (energy retention score)
    retention = energy_retention_score(energy)
    
    # 4. recovery_after_perturbation (smoothness of post-transient energy; returns 0 if decayed to silence)
    n = len(energy)
    if n < 10:
        recovery = 1.0
    else:
        post_transient = energy[int(n * 0.15):]
        if len(post_transient) < 5:
            recovery = 1.0
        else:
            post_mean = np.mean(post_transient)
            if post_mean < 1e-3:
                recovery = 0.0
            else:
                window = 5
                smoothed = np.convolve(post_transient, np.ones(window)/window, mode='valid')
                residuals = post_transient[window//2 : window//2 + len(smoothed)] - smoothed
                var_res = np.var(residuals)
                var_total = np.var(post_transient)
                if var_total == 0:
                    recovery = 1.0
                else:
                    recovery = float(1.0 / (1.0 + var_res / (var_total + 1e-12)))
            
    # 5. competition_strength
    if total_energy is not None:
        ratio = energy / (total_energy + 1e-12)
        comp_strength = float(np.clip(np.mean(ratio), 0, 1))
    else:
        comp_strength = 1.0
        
    # 6. state_memory (envelope autocorrelation peak prominence to separate decay from recurrence)
    if recurrence_values is not None:
        memory = float(np.mean(recurrence_values))
    else:
        if n >= 10:
            e_centered = energy - np.mean(energy)
            acorr = np.correlate(e_centered, e_centered, mode='full')[n-1:]
            if acorr[0] > 0:
                acorr = acorr / acorr[0]
                peaks = []
                for i in range(1, len(acorr) - 1):
                    if acorr[i] > acorr[i-1] and acorr[i] > acorr[i+1]:
                        peaks.append(acorr[i])
                if len(peaks) > 0:
                    memory = float(np.clip(np.max(peaks), 0, 1))
                else:
                    memory = 0.0
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


