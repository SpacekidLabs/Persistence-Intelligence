"""
Experiment 03 - Modal Objects

Generate a struck modal resonator and track each mode after excitation.
This reconnects persistence with physical modeling: each mode is a decaying
oscillator with its own lifetime.
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
DURATION_SECONDS = 7.0
WINDOW_SIZE = 2048
HOP_SIZE = 512

MODES = [
    {"name": "mode 1", "frequency": 221.0, "amplitude": 1.00, "decay": 4.8},
    {"name": "mode 2", "frequency": 357.0, "amplitude": 0.65, "decay": 2.6},
    {"name": "mode 3", "frequency": 593.0, "amplitude": 0.45, "decay": 1.35},
    {"name": "mode 4", "frequency": 941.0, "amplitude": 0.35, "decay": 0.75},
]


def generate_modal_resonator() -> tuple[np.ndarray, np.ndarray]:
    times = np.arange(int(SAMPLE_RATE * DURATION_SECONDS)) / SAMPLE_RATE
    rng = np.random.default_rng(23)
    signal = np.zeros_like(times)

    for mode in MODES:
        phase = rng.uniform(0, 2 * np.pi)
        envelope = np.exp(-times / mode["decay"])
        signal += mode["amplitude"] * envelope * np.sin(
            2 * np.pi * mode["frequency"] * times + phase
        )

    excitation = np.zeros_like(times)
    burst_samples = int(0.04 * SAMPLE_RATE)
    excitation[:burst_samples] = np.hanning(burst_samples) * rng.normal(0, 0.4, burst_samples)
    return times, normalize(signal + excitation)


def main() -> None:
    import json
    parser = argparse.ArgumentParser(description="Track modes in a modal resonator.")
    parser.add_argument("--save", help="Save plot instead of opening a window.")
    args = parser.parse_args()

    times, signal = generate_modal_resonator()
    frames = analyze_frames(signal, SAMPLE_RATE, WINDOW_SIZE, HOP_SIZE)

    traces = {
        mode["name"]: band_energy_trace(frames, mode["frequency"], 45)
        for mode in MODES
    }

    # Compute and export taxonomy metrics
    taxonomy_metrics = {}
    sum_energy = sum(traces.values())
    for mode in MODES:
        name = mode["name"]
        energy = traces[name]
        from persistence.metrics import compute_taxonomy_metrics
        tax_met = compute_taxonomy_metrics(
            energy=energy,
            total_energy=sum_energy,
            frame_times=frames.frame_times,
        )
        taxonomy_metrics[name] = tax_met

    results_dir = PROJECT_ROOT / "experiments" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "03_modal_objects.json", "w") as f:
        json.dump(taxonomy_metrics, f, indent=4)
    print(f"Saved taxonomy metrics to {results_dir / '03_modal_objects.json'}")

    print("Modal object summary")
    print("mode    freq_hz  decay_s  survival_s  stability  late_energy")
    for mode in MODES:
        energy = traces[mode["name"]]
        late_energy = float(np.mean(energy[-max(3, len(energy) // 5) :]))
        print(
            f"{mode['name']:6s} {mode['frequency']:7.1f} {mode['decay']:8.2f} "
            f"{survival_time(frames.frame_times, energy):10.2f} "
            f"{band_stability_score(energy):9.3f} {late_energy:11.3f}"
        )

    figure, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    figure.suptitle("Experiment 03 - Modal Objects", fontweight="bold")

    axes[0].plot(times, signal, color="#2364aa", linewidth=0.75)
    axes[0].set_ylabel("signal")
    axes[0].set_title("Struck modal resonator")
    axes[0].grid(True, alpha=0.2)

    image = axes[1].imshow(
        frames.spectrum_db[frames.frequencies <= 1_400],
        origin="lower",
        aspect="auto",
        extent=[0, DURATION_SECONDS, 0, 1_400],
        cmap="magma",
        vmin=-85,
        vmax=20,
    )
    for mode in MODES:
        axes[1].axhline(mode["frequency"], color="#73d2de", linewidth=0.8, alpha=0.7)
    axes[1].set_ylabel("Hz")
    axes[1].set_title("Spectrogram with modal bands")
    figure.colorbar(image, ax=axes[1], label="dB")

    colors = ["#2364aa", "#d95d39", "#2a9d8f", "#6d597a"]
    for mode, color in zip(MODES, colors):
        axes[2].plot(
            frames.frame_times,
            traces[mode["name"]],
            label=f"{mode['name']} {mode['frequency']:.0f} Hz",
            color=color,
            linewidth=1.8,
        )
    axes[2].axhline(0.1, color="#222222", linewidth=0.8, linestyle="--", alpha=0.5)
    axes[2].set_ylim(-0.02, 1.05)
    axes[2].set_xlabel("Time after excitation (seconds)")
    axes[2].set_ylabel("normalized mode energy")
    axes[2].set_title("Mode persistence after excitation")
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
