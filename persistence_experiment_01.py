"""
Persistence Intelligence - Experiment 01

Run:
    python persistence_experiment_01.py

Optional:
    python persistence_experiment_01.py --save persistence_experiment_01.png

This is intentionally a small exploratory application, not a framework.
It generates four test signals, measures a few provisional persistence
features, and displays waveform, spectrogram, and metric panels for visual
comparison.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np

try:
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit(
        "Matplotlib is required for this visual experiment.\n"
        "Install dependencies with: pip install -r requirements.txt"
    ) from exc

try:
    from scipy.signal import get_window
except ImportError:
    get_window = None


SAMPLE_RATE = 44_100
DURATION_SECONDS = 5.0
BASE_FREQUENCY = 440.0
WINDOW_SIZE = 2048
HOP_SIZE = 512


@dataclass
class SignalAnalysis:
    name: str
    signal: np.ndarray
    times: np.ndarray
    frame_times: np.ndarray
    frequencies: np.ndarray
    spectrum_db: np.ndarray
    energy_curve: np.ndarray
    peak_frequencies: np.ndarray
    centroids: np.ndarray
    persistence: float
    energy_retention: float
    frequency_stability: float
    centroid_stability: float
    stability: float
    continuity: float


def normalize(signal: np.ndarray) -> np.ndarray:
    peak = np.max(np.abs(signal))
    if peak == 0:
        return signal
    return signal / peak


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


def analysis_window(size: int) -> np.ndarray:
    if get_window is not None:
        return get_window("hann", size, fftbins=True)
    return np.hanning(size)


def frame_signal(signal: np.ndarray, window_size: int, hop_size: int) -> np.ndarray:
    frame_count = 1 + (len(signal) - window_size) // hop_size
    shape = (frame_count, window_size)
    strides = (signal.strides[0] * hop_size, signal.strides[0])
    return np.lib.stride_tricks.as_strided(signal, shape=shape, strides=strides).copy()


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


def analyze_signal(name: str, signal: np.ndarray, times: np.ndarray) -> SignalAnalysis:
    frames = frame_signal(signal, WINDOW_SIZE, HOP_SIZE)
    window = analysis_window(WINDOW_SIZE)
    windowed = frames * window

    spectrum = np.abs(np.fft.rfft(windowed, axis=1))
    power = spectrum**2
    frequencies = np.fft.rfftfreq(WINDOW_SIZE, d=1 / SAMPLE_RATE)
    frame_times = (np.arange(len(frames)) * HOP_SIZE + WINDOW_SIZE / 2) / SAMPLE_RATE

    energy = np.mean(frames**2, axis=1)
    energy_floor = max(float(np.max(energy)) * 0.01, 1e-10)
    active = energy > energy_floor

    spectrum_db = 20 * np.log10(spectrum.T + 1e-8)

    peak_bins = np.argmax(spectrum, axis=1)
    peak_frequencies = frequencies[peak_bins]
    peak_frequencies = np.where(active, peak_frequencies, np.nan)

    power_sum = np.sum(power, axis=1)
    centroids = np.divide(
        power @ frequencies,
        power_sum,
        out=np.zeros_like(power_sum),
        where=power_sum > 0,
    )
    centroids = np.where(active, centroids, np.nan)

    early = energy[: max(3, len(energy) // 5)]
    late = energy[-max(3, len(energy) // 5) :]
    energy_retention = np.clip(safe_mean(late) / (safe_mean(early) + 1e-12), 0, 1)

    frequency_stability = normalized_inverse_variation(peak_frequencies, tolerance=18.0)
    centroid_stability = normalized_inverse_variation(centroids, tolerance=140.0)
    stability = float(np.sqrt(frequency_stability * centroid_stability))

    continuity_values = []
    active_frames = frames[active]
    for left, right in zip(active_frames[:-1], active_frames[1:]):
        left_norm = np.linalg.norm(left)
        right_norm = np.linalg.norm(right)
        if left_norm == 0 or right_norm == 0:
            continue
        continuity_values.append(np.dot(left, right) / (left_norm * right_norm))
    continuity = np.clip((safe_mean(np.array(continuity_values)) + 1.0) / 2.0, 0, 1)

    persistence = float(energy_retention * stability * continuity)

    return SignalAnalysis(
        name=name,
        signal=signal,
        times=times,
        frame_times=frame_times,
        frequencies=frequencies,
        spectrum_db=spectrum_db,
        energy_curve=energy,
        peak_frequencies=peak_frequencies,
        centroids=centroids,
        persistence=persistence,
        energy_retention=float(energy_retention),
        frequency_stability=frequency_stability,
        centroid_stability=centroid_stability,
        stability=stability,
        continuity=float(continuity),
    )


def plot_waveform(axis, analysis: SignalAnalysis) -> None:
    axis.plot(analysis.times, analysis.signal, color="#2364aa", linewidth=0.8)
    axis.plot(
        analysis.frame_times,
        normalize(analysis.energy_curve) * 0.9,
        color="#d95d39",
        linewidth=1.1,
        label="energy",
    )
    axis.set_xlim(0, DURATION_SECONDS)
    axis.set_ylim(-1.1, 1.1)
    axis.set_ylabel(analysis.name, fontsize=10)
    axis.grid(True, alpha=0.18)


def plot_spectrogram(axis, analysis: SignalAnalysis) -> None:
    visible = analysis.frequencies <= 2_000
    image = axis.imshow(
        analysis.spectrum_db[visible],
        origin="lower",
        aspect="auto",
        extent=[0, DURATION_SECONDS, 0, 2_000],
        cmap="magma",
        vmin=-80,
        vmax=20,
    )
    axis.plot(
        analysis.frame_times,
        analysis.peak_frequencies,
        color="#73d2de",
        linewidth=1.0,
        alpha=0.9,
    )
    axis.plot(
        analysis.frame_times,
        analysis.centroids,
        color="#f9c74f",
        linewidth=1.0,
        alpha=0.8,
    )
    axis.set_ylim(0, 1_600)
    return image


def metric_bar(value: float, width: int = 22) -> str:
    filled = int(round(np.clip(value, 0, 1) * width))
    return "[" + "#" * filled + "-" * (width - filled) + f"] {value:0.3f}"


def plot_metrics(axis, analysis: SignalAnalysis) -> None:
    axis.axis("off")
    lines = [
        f"Persistence      {metric_bar(analysis.persistence)}",
        f"Energy retention {metric_bar(analysis.energy_retention)}",
        f"Freq stability   {metric_bar(analysis.frequency_stability)}",
        f"Centroid stable  {metric_bar(analysis.centroid_stability)}",
        f"Continuity       {metric_bar(analysis.continuity)}",
        "",
        f"Peak freq mean   {safe_mean(analysis.peak_frequencies):7.1f} Hz",
        f"Peak freq std    {np.nanstd(analysis.peak_frequencies):7.1f} Hz",
        f"Centroid mean    {safe_mean(analysis.centroids):7.1f} Hz",
    ]
    axis.text(
        0.0,
        0.98,
        "\n".join(lines),
        va="top",
        ha="left",
        family="monospace",
        fontsize=9.5,
        color="#1f2933",
    )


def build_dashboard(analyses: list[SignalAnalysis], save_path: str | None = None) -> None:
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 9,
            "figure.facecolor": "#f7f7f2",
            "axes.facecolor": "#ffffff",
        }
    )

    figure, axes = plt.subplots(
        nrows=len(analyses),
        ncols=3,
        figsize=(15, 9),
        gridspec_kw={"width_ratios": [1.2, 1.35, 1.25], "wspace": 0.24, "hspace": 0.34},
    )
    figure.suptitle(
        "Persistence Intelligence - Experiment 01: Audio Signal Persistence",
        fontsize=15,
        fontweight="bold",
        y=0.985,
    )

    spectrogram_image = None
    for row, analysis in enumerate(analyses):
        plot_waveform(axes[row, 0], analysis)
        spectrogram_image = plot_spectrogram(axes[row, 1], analysis)
        plot_metrics(axes[row, 2], analysis)

        if row == 0:
            axes[row, 0].set_title("Left Panel - Waveform + energy")
            axes[row, 1].set_title("Center Panel - Spectrogram + identity traces")
            axes[row, 2].set_title("Right Panel - Persistence metrics")

        if row == len(analyses) - 1:
            axes[row, 0].set_xlabel("Time (seconds)")
            axes[row, 1].set_xlabel("Time (seconds)")

        axes[row, 1].set_ylabel("Hz")

    if spectrogram_image is not None:
        colorbar = figure.colorbar(
            spectrogram_image,
            ax=axes[:, 1],
            fraction=0.02,
            pad=0.015,
        )
        colorbar.set_label("Magnitude (dB)")

    figure.text(
        0.015,
        0.012,
        "Formula: Persistence = EnergyRetention x Stability x Continuity. "
        "This prototype is meant to invite disagreement with the metric.",
        fontsize=9,
        color="#344054",
    )

    if save_path:
        figure.savefig(save_path, dpi=160, bbox_inches="tight")
        print(f"Saved dashboard to {save_path}")
    else:
        plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Explore persistence in audio signals.")
    parser.add_argument("--save", help="Save the dashboard image instead of opening a window.")
    args = parser.parse_args()

    times, signals = generate_signals()
    analyses = [analyze_signal(name, signal, times) for name, signal in signals.items()]

    print("Persistence scores")
    for analysis in analyses:
        print(
            f"{analysis.name:24s} "
            f"persistence={analysis.persistence:0.3f} "
            f"energy={analysis.energy_retention:0.3f} "
            f"stability={analysis.stability:0.3f} "
            f"continuity={analysis.continuity:0.3f}"
        )

    build_dashboard(analyses, save_path=args.save)


if __name__ == "__main__":
    main()
