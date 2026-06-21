"""
Persistence Intelligence - Experiment 06: Metric Falsification Sweep

This experiment generates 7 distinct test signals to stress-test and falsify
the taxonomy metrics, ensuring we can tell different kinds of persistence apart:
1. Pure exponential decay
2. Double exponential decay
3. Delay line without feedback (single echo)
4. Feedback loop (multiple echoes / comb resonance)
5. Resonant system (stable sine)
6. Chaotic recurrence (Logistic map)
7. Periodic recurrence (repeating pulse train)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from persistence.detectors import analyze_frames, normalize
from persistence.metrics import compute_taxonomy_metrics

try:
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit("Install dependencies with: pip install -r requirements.txt") from exc

SAMPLE_RATE = 44_100
DURATION_SECONDS = 5.0
WINDOW_SIZE = 2048
HOP_SIZE = 512


def generate_pure_decay(times: np.ndarray) -> np.ndarray:
    """1. Pure exponential decay (single decaying sine)."""
    return np.exp(-times / 1.0) * np.sin(2 * np.pi * 440.0 * times)


def generate_double_decay(times: np.ndarray) -> np.ndarray:
    """2. Double exponential decay (fast initial decay + slow long decay)."""
    env = 0.8 * np.exp(-times / 0.15) + 0.2 * np.exp(-times / 2.5)
    return env * np.sin(2 * np.pi * 440.0 * times)


def generate_delay_no_feedback(times: np.ndarray) -> np.ndarray:
    """3. Delay line without feedback (single echo delayed by 145ms)."""
    rng = np.random.default_rng(61)
    # Primary burst
    sig = np.zeros_like(times)
    burst_len = int(0.03 * SAMPLE_RATE)
    sig[:burst_len] = np.hanning(burst_len) * rng.normal(0, 1, burst_len)
    
    # Single Echo at 145ms
    echo_samples = int(0.145 * SAMPLE_RATE)
    if echo_samples + burst_len < len(sig):
        sig[echo_samples:echo_samples+burst_len] += 0.7 * sig[:burst_len]
    return sig


def generate_feedback_loop(times: np.ndarray) -> np.ndarray:
    """4. Feedback loop (recirculating delay line with feedback gain = 0.72)."""
    rng = np.random.default_rng(61)
    sig = np.zeros_like(times)
    
    # Input excitation burst
    burst_len = int(0.03 * SAMPLE_RATE)
    excitation = np.zeros_like(times)
    excitation[:burst_len] = np.hanning(burst_len) * rng.normal(0, 1, burst_len)
    
    delay_samples = int(0.145 * SAMPLE_RATE)
    feedback_gain = 0.72
    
    for i in range(len(times)):
        delayed = sig[i - delay_samples] if i >= delay_samples else 0.0
        sig[i] = excitation[i] + feedback_gain * delayed
    return sig


def generate_resonance(times: np.ndarray) -> np.ndarray:
    """5. Resonant system (stable sine wave, zero decay)."""
    return np.sin(2 * np.pi * 440.0 * times)


def generate_chaotic_recurrence(times: np.ndarray) -> np.ndarray:
    """6. Chaotic recurrence generated via the Logistic Map (r=3.95)."""
    sig = np.zeros_like(times)
    x = 0.42
    r = 3.95
    # Generate chaotic samples
    for i in range(len(sig)):
        x = r * x * (1.0 - x)
        sig[i] = x
    return sig - 0.5  # center it


def generate_periodic_recurrence(times: np.ndarray) -> np.ndarray:
    """7. Periodic recurrence (repeating train of impulse bursts every 250ms)."""
    sig = np.zeros_like(times)
    period = 0.25  # 4 Hz repeating pulses
    rng = np.random.default_rng(61)
    
    for onset in np.arange(0, DURATION_SECONDS, period):
        start_idx = int(onset * SAMPLE_RATE)
        burst_len = int(0.02 * SAMPLE_RATE)
        if start_idx + burst_len < len(sig):
            sig[start_idx:start_idx+burst_len] = np.hanning(burst_len) * rng.normal(0, 1, burst_len)
    return sig


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Experiment 06: Metric Falsification Sweep.")
    parser.add_argument("--save", help="Save dashboard image path.")
    args = parser.parse_args()
    
    times = np.arange(int(SAMPLE_RATE * DURATION_SECONDS)) / SAMPLE_RATE
    
    generators = {
        "pure exponential decay": generate_pure_decay,
        "double exponential decay": generate_double_decay,
        "delay line without feedback": generate_delay_no_feedback,
        "feedback loop": generate_feedback_loop,
        "resonant system": generate_resonance,
        "chaotic recurrence": generate_chaotic_recurrence,
        "periodic recurrence": generate_periodic_recurrence,
    }
    
    results = {}
    signals = {}
    
    print("Falsification Sweep - Calculating Corrected Metrics")
    print("=" * 80)
    print(f"{'Structure':30s} | {'Surv':5s} | {'Stab':5s} | {'Decay':5s} | {'Recov':5s} | {'Comp':5s} | {'Memory':5s}")
    print("-" * 80)
    
    for name, gen_func in generators.items():
        sig = normalize(gen_func(times))
        signals[name] = sig
        
        frames = analyze_frames(sig, SAMPLE_RATE, WINDOW_SIZE, HOP_SIZE)
        
        # Compute taxonomy metrics for the overall energy envelope
        metrics = compute_taxonomy_metrics(
            energy=frames.energy,
            frame_times=frames.frame_times,
        )
        results[name] = metrics
        
        print(
            f"{name:30s} | "
            f"{metrics['survival_time']:5.2f} | "
            f"{metrics['identity_stability']:5.2f} | "
            f"{metrics['energy_decay']:5.2f} | "
            f"{metrics['recovery_after_perturbation']:5.2f} | "
            f"{metrics['competition_strength']:5.2f} | "
            f"{metrics['state_memory']:5.2f}"
        )
        
    # Export metrics to JSON
    results_dir = PROJECT_ROOT / "experiments" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "06_metric_falsification.json", "w") as f:
        json.dump(results, f, indent=4)
    print(f"\nSaved metrics to {results_dir / '06_metric_falsification.json'}")
    
    # Generate Dashboard Plot
    fig, axes = plt.subplots(len(generators), 2, figsize=(14, 15), sharex='col')
    fig.suptitle("Experiment 06 - Metric Falsification Sweep", fontweight="bold", fontsize=14)
    
    for idx, (name, sig) in enumerate(signals.items()):
        frames = analyze_frames(sig, SAMPLE_RATE, WINDOW_SIZE, HOP_SIZE)
        
        # Plot waveform
        axes[idx, 0].plot(times, sig, color="#2364aa", linewidth=0.75)
        axes[idx, 0].set_ylabel(name.replace(" ", "\n"), fontsize=9, rotation=0, labelpad=25, va='center')
        axes[idx, 0].grid(True, alpha=0.15)
        
        # Plot spectrogram
        axes[idx, 1].imshow(
            frames.spectrum_db[frames.frequencies <= 2000],
            origin="lower",
            aspect="auto",
            extent=[0, DURATION_SECONDS, 0, 2000],
            cmap="magma",
            vmin=-80,
            vmax=20,
        )
        axes[idx, 1].grid(False)
        
    axes[-1, 0].set_xlabel("Time (seconds)")
    axes[-1, 1].set_xlabel("Time (seconds)")
    
    fig.tight_layout()
    if args.save:
        fig.savefig(args.save, dpi=150, bbox_inches="tight")
        print(f"Saved falsification plot to {args.save}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
