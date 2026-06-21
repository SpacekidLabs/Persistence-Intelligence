"""
Experiment 02 - Competing Resonances

Four structures are mixed together:
    440 Hz, 880 Hz, 1320 Hz, and noise.

The experiment tracks band energy through time and asks which structures
survive longest and which are most stable.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from persistence.detectors import analyze_frames, normalize
from persistence.trackers import band_energy_trace, band_stability_score, survival_time

try:
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit("Install dependencies with: pip install -r requirements.txt") from exc


SAMPLE_RATE = 44_100
DURATION_SECONDS = 6.0
WINDOW_SIZE = 2048
HOP_SIZE = 512


def decaying_sine(times: np.ndarray, frequency: float, decay_seconds: float) -> np.ndarray:
    return np.exp(-times / decay_seconds) * np.sin(2 * np.pi * frequency * times)


def generate_signal() -> tuple[np.ndarray, np.ndarray]:
    times = np.arange(int(SAMPLE_RATE * DURATION_SECONDS)) / SAMPLE_RATE
    rng = np.random.default_rng(11)

    signal = (
        0.90 * decaying_sine(times, 440, 4.5)
        + 0.70 * decaying_sine(times, 880, 2.2)
        + 0.55 * decaying_sine(times, 1320, 0.9)
    )

    noise_envelope = np.exp(-times / 0.55)
    signal += 0.42 * noise_envelope * rng.normal(0, 1, size=times.shape)
    return times, normalize(signal)


def main() -> None:
    import json
    parser = argparse.ArgumentParser(description="Track competing resonances.")
    parser.add_argument("--save", help="Save plot instead of opening a window.")
    args = parser.parse_args()

    times, signal = generate_signal()
    frames = analyze_frames(signal, SAMPLE_RATE, WINDOW_SIZE, HOP_SIZE)

    structures = {
        "440 Hz": band_energy_trace(frames, 440, 70),
        "880 Hz": band_energy_trace(frames, 880, 90),
        "1320 Hz": band_energy_trace(frames, 1320, 110),
        "noise floor": band_energy_trace(frames, 6_000, 6_000),
    }

    rows = []
    for name, energy in structures.items():
        rows.append(
            (
                name,
                survival_time(frames.frame_times, energy, threshold=0.1),
                band_stability_score(energy),
                float(np.mean(energy[-max(3, len(energy) // 5) :])),
            )
        )

    # Compute and export taxonomy metrics
    taxonomy_metrics = {}
    sum_energy = sum(structures.values())
    for name, energy in structures.items():
        from persistence.metrics import compute_taxonomy_metrics
        tax_met = compute_taxonomy_metrics(
            energy=energy,
            total_energy=sum_energy,
            frame_times=frames.frame_times,
        )
        taxonomy_metrics[name] = tax_met

    results_dir = PROJECT_ROOT / "experiments" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "02_competing_resonances.json", "w") as f:
        json.dump(taxonomy_metrics, f, indent=4)
    print(f"Saved taxonomy metrics to {results_dir / '02_competing_resonances.json'}")

    print("Competing resonance summary")
    print("structure       survival_s  stability  late_energy")
    for name, survive, stable, late in rows:
        print(f"{name:12s} {survive:10.2f}  {stable:9.3f}  {late:11.3f}")

    figure, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    figure.suptitle("Experiment 02 - Competing Resonances", fontweight="bold")

    axes[0].plot(times, signal, color="#2364aa", linewidth=0.75)
    axes[0].set_ylabel("signal")
    axes[0].set_title("Mixture: 440 Hz, 880 Hz, 1320 Hz, noise")
    axes[0].grid(True, alpha=0.2)

    image = axes[1].imshow(
        frames.spectrum_db[frames.frequencies <= 2_000],
        origin="lower",
        aspect="auto",
        extent=[0, DURATION_SECONDS, 0, 2_000],
        cmap="magma",
        vmin=-80,
        vmax=20,
    )
    axes[1].set_ylabel("Hz")
    axes[1].set_title("Spectrogram")
    figure.colorbar(image, ax=axes[1], label="dB")

    colors = {
        "440 Hz": "#2364aa",
        "880 Hz": "#d95d39",
        "1320 Hz": "#2a9d8f",
        "noise floor": "#6d597a",
    }
    for name, energy in structures.items():
        axes[2].plot(frames.frame_times, energy, label=name, color=colors[name], linewidth=1.8)
    axes[2].axhline(0.1, color="#222222", linewidth=0.8, linestyle="--", alpha=0.5)
    axes[2].set_ylim(-0.02, 1.05)
    axes[2].set_xlabel("Time (seconds)")
    axes[2].set_ylabel("normalized band energy")
    axes[2].set_title("Energy survival by structure")
    axes[2].legend(loc="upper right")
    axes[2].grid(True, alpha=0.2)

    figure.tight_layout()
    if args.save:
        figure.savefig(args.save, dpi=160, bbox_inches="tight")
        print(f"Saved plot to {args.save}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
