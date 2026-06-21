"""
Experiment 04 - Feedback Systems

Put a delay inside a feedback loop and track recurring structures.
The question is whether persistence starts to look different from resonance:
not just a frequency surviving, but a pattern returning through time.
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
from persistence.trackers import band_energy_trace, survival_time

try:
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit("Install dependencies with: pip install -r requirements.txt") from exc


SAMPLE_RATE = 44_100
DURATION_SECONDS = 6.0
WINDOW_SIZE = 2048
HOP_SIZE = 512
DELAY_SECONDS = 0.145
FEEDBACK = 0.72


def generate_feedback_signal() -> tuple[np.ndarray, np.ndarray, int]:
    times = np.arange(int(SAMPLE_RATE * DURATION_SECONDS)) / SAMPLE_RATE
    delay_samples = int(DELAY_SECONDS * SAMPLE_RATE)
    rng = np.random.default_rng(41)

    excitation = np.zeros_like(times)
    burst_samples = int(0.035 * SAMPLE_RATE)
    excitation[:burst_samples] = np.hanning(burst_samples) * rng.normal(0, 1, burst_samples)

    signal = np.zeros_like(times)
    for index in range(len(times)):
        delayed = signal[index - delay_samples] if index >= delay_samples else 0.0
        signal[index] = excitation[index] + FEEDBACK * delayed

    # A tiny nonlinear loss keeps the loop lively without exploding.
    signal = np.tanh(1.4 * signal)
    return times, normalize(signal), delay_samples


def recurrence_trace(signal: np.ndarray, delay_samples: int) -> tuple[np.ndarray, np.ndarray]:
    max_lag_count = int((DURATION_SECONDS - DELAY_SECONDS) / DELAY_SECONDS)
    event_times = []
    recurrence = []
    template = signal[:delay_samples]
    template_norm = np.linalg.norm(template)

    for repeat in range(1, max_lag_count):
        start = repeat * delay_samples
        stop = start + delay_samples
        if stop > len(signal):
            break
        segment = signal[start:stop]
        denom = template_norm * np.linalg.norm(segment)
        score = 0.0 if denom == 0 else float(np.dot(template, segment) / denom)
        event_times.append(start / SAMPLE_RATE)
        recurrence.append(abs(score))

    return np.array(event_times), np.array(recurrence)


def main() -> None:
    parser = argparse.ArgumentParser(description="Track recurring structures in feedback.")
    parser.add_argument("--save", help="Save plot instead of opening a window.")
    args = parser.parse_args()

    times, signal, delay_samples = generate_feedback_signal()
    frames = analyze_frames(signal, SAMPLE_RATE, WINDOW_SIZE, HOP_SIZE)
    event_times, recurrence = recurrence_trace(signal, delay_samples)

    fundamental = 1.0 / DELAY_SECONDS
    delay_harmonics = {
        f"{n}x delay": band_energy_trace(frames, fundamental * n, 20)
        for n in range(1, 7)
    }

    print("Feedback system summary")
    print(f"delay={DELAY_SECONDS:.3f}s feedback={FEEDBACK:.2f} loop_frequency={fundamental:.2f}Hz")
    print(f"recurrence mean={np.mean(recurrence):.3f} max={np.max(recurrence):.3f}")
    for name, energy in delay_harmonics.items():
        print(f"{name:8s} survival={survival_time(frames.frame_times, energy):.2f}s")

    figure, axes = plt.subplots(4, 1, figsize=(12, 9), sharex=False)
    figure.suptitle("Experiment 04 - Feedback Systems", fontweight="bold")

    axes[0].plot(times, signal, color="#2364aa", linewidth=0.75)
    axes[0].set_xlim(0, DURATION_SECONDS)
    axes[0].set_ylabel("signal")
    axes[0].set_title("Delay feedback loop output")
    axes[0].grid(True, alpha=0.2)

    image = axes[1].imshow(
        frames.spectrum_db[frames.frequencies <= 500],
        origin="lower",
        aspect="auto",
        extent=[0, DURATION_SECONDS, 0, 500],
        cmap="magma",
        vmin=-85,
        vmax=15,
    )
    axes[1].set_ylabel("Hz")
    axes[1].set_title("Low-frequency comb created by recurrence")
    figure.colorbar(image, ax=axes[1], label="dB")

    axes[2].stem(event_times, recurrence, basefmt=" ", linefmt="#d95d39", markerfmt="o")
    axes[2].set_ylim(0, 1.05)
    axes[2].set_ylabel("similarity")
    axes[2].set_title("Pattern recurrence at delay intervals")
    axes[2].grid(True, alpha=0.2)

    for name, energy in delay_harmonics.items():
        axes[3].plot(frames.frame_times, energy, label=name, linewidth=1.4)
    axes[3].set_xlim(0, DURATION_SECONDS)
    axes[3].set_ylim(-0.02, 1.05)
    axes[3].set_xlabel("Time (seconds)")
    axes[3].set_ylabel("normalized energy")
    axes[3].set_title("Delay harmonic survival")
    axes[3].legend(ncol=3, loc="upper right")
    axes[3].grid(True, alpha=0.2)

    figure.tight_layout()
    if args.save:
        figure.savefig(args.save, dpi=160, bbox_inches="tight")
        print(f"Saved plot to {args.save}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
