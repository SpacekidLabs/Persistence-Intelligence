"""
Persistence Intelligence - Experiment 01

Run:
    python experiments/01_signal_persistence.py

Optional:
    python experiments/01_signal_persistence.py --save experiments/01_signal_persistence.png
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from persistence.detectors import analyze_frames, normalize
from persistence.metrics import PersistenceMetrics, persistence_score
from persistence.trackers import peak_frequency_trace, spectral_centroid_trace
from persistence.visualizers import build_dashboard


SAMPLE_RATE = 44_100
DURATION_SECONDS = 5.0
BASE_FREQUENCY = 440.0
WINDOW_SIZE = 2048
HOP_SIZE = 512


@dataclass
class SignalResult:
    name: str
    signal: np.ndarray
    times: np.ndarray
    frame_times: np.ndarray
    frequencies: np.ndarray
    spectrum_db: np.ndarray
    energy_curve: np.ndarray
    peak_frequencies: np.ndarray
    centroids: np.ndarray
    metrics: PersistenceMetrics


def generate_signals() -> tuple[np.ndarray, dict[str, np.ndarray]]:
    times = np.arange(int(SAMPLE_RATE * DURATION_SECONDS)) / SAMPLE_RATE

    pure_sine = np.sin(2 * np.pi * BASE_FREQUENCY * times)

    decay_envelope = np.exp(-times / 1.15)
    decaying_sine = decay_envelope * np.sin(2 * np.pi * BASE_FREQUENCY * times)

    drift_hz = 10.0 * np.sin(2 * np.pi * 0.42 * times)
    instantaneous_frequency = BASE_FREQUENCY + drift_hz
    phase = 2 * np.pi * np.cumsum(instantaneous_frequency) / SAMPLE_RATE
    drifting_sine = np.sin(phase)

    rng = np.random.default_rng(7)
    burst_envelope = np.zeros_like(times)
    burst_length = int(0.85 * SAMPLE_RATE)
    burst_envelope[:burst_length] = np.hanning(burst_length)
    white_noise_burst = burst_envelope * rng.normal(0, 1, size=times.shape)

    signals = {
        "Pure sine 440 Hz": pure_sine,
        "Decaying sine 440 Hz": decaying_sine,
        "Frequency drift 440 Hz": drifting_sine,
        "White noise burst": white_noise_burst,
    }
    return times, {name: normalize(signal) for name, signal in signals.items()}


def analyze_signal(name: str, signal: np.ndarray, times: np.ndarray) -> SignalResult:
    frames = analyze_frames(
        signal=signal,
        sample_rate=SAMPLE_RATE,
        window_size=WINDOW_SIZE,
        hop_size=HOP_SIZE,
    )
    peak_frequencies = peak_frequency_trace(frames)
    centroids = spectral_centroid_trace(frames)
    metrics = persistence_score(frames, peak_frequencies, centroids)

    return SignalResult(
        name=name,
        signal=signal,
        times=times,
        frame_times=frames.frame_times,
        frequencies=frames.frequencies,
        spectrum_db=frames.spectrum_db,
        energy_curve=frames.energy,
        peak_frequencies=peak_frequencies,
        centroids=centroids,
        metrics=metrics,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Explore persistence in audio signals.")
    parser.add_argument("--save", help="Save the dashboard image instead of opening a window.")
    args = parser.parse_args()

    times, signals = generate_signals()
    results = [analyze_signal(name, signal, times) for name, signal in signals.items()]

    print("Persistence scores")
    for result in results:
        metrics = result.metrics
        print(
            f"{result.name:24s} "
            f"persistence={metrics.persistence:0.3f} "
            f"energy={metrics.energy_retention:0.3f} "
            f"stability={metrics.stability:0.3f} "
            f"continuity={metrics.continuity:0.3f}"
        )

    build_dashboard(results, duration_seconds=DURATION_SECONDS, save_path=args.save)


if __name__ == "__main__":
    main()
