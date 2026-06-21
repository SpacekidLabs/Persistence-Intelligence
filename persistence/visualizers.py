from __future__ import annotations

import numpy as np

try:
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit(
        "Matplotlib is required for this visual experiment.\n"
        "Install dependencies with: pip install -r requirements.txt"
    ) from exc

from persistence.detectors import normalize
from persistence.metrics import safe_mean


def plot_waveform(axis, result, duration_seconds: float) -> None:
    axis.plot(result.times, result.signal, color="#2364aa", linewidth=0.8)
    axis.plot(
        result.frame_times,
        normalize(result.energy_curve) * 0.9,
        color="#d95d39",
        linewidth=1.1,
        label="energy",
    )
    axis.set_xlim(0, duration_seconds)
    axis.set_ylim(-1.1, 1.1)
    axis.set_ylabel(result.name, fontsize=10)
    axis.grid(True, alpha=0.18)


def plot_spectrogram(axis, result, duration_seconds: float):
    visible = result.frequencies <= 2_000
    image = axis.imshow(
        result.spectrum_db[visible],
        origin="lower",
        aspect="auto",
        extent=[0, duration_seconds, 0, 2_000],
        cmap="magma",
        vmin=-80,
        vmax=20,
    )
    axis.plot(
        result.frame_times,
        result.peak_frequencies,
        color="#73d2de",
        linewidth=1.0,
        alpha=0.9,
    )
    axis.plot(
        result.frame_times,
        result.centroids,
        color="#f9c74f",
        linewidth=1.0,
        alpha=0.8,
    )
    axis.set_ylim(0, 1_600)
    return image


def metric_bar(value: float, width: int = 22) -> str:
    filled = int(round(np.clip(value, 0, 1) * width))
    return "[" + "#" * filled + "-" * (width - filled) + f"] {value:0.3f}"


def plot_metrics(axis, result) -> None:
    axis.axis("off")
    metrics = result.metrics
    lines = [
        f"Persistence      {metric_bar(metrics.persistence)}",
        f"Energy retention {metric_bar(metrics.energy_retention)}",
        f"Freq stability   {metric_bar(metrics.frequency_stability)}",
        f"Centroid stable  {metric_bar(metrics.centroid_stability)}",
        f"Continuity       {metric_bar(metrics.continuity)}",
        "",
        f"Peak freq mean   {safe_mean(result.peak_frequencies):7.1f} Hz",
        f"Peak freq std    {np.nanstd(result.peak_frequencies):7.1f} Hz",
        f"Centroid mean    {safe_mean(result.centroids):7.1f} Hz",
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


def build_dashboard(results, duration_seconds: float, save_path: str | None = None) -> None:
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
        nrows=len(results),
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
    for row, result in enumerate(results):
        plot_waveform(axes[row, 0], result, duration_seconds)
        spectrogram_image = plot_spectrogram(axes[row, 1], result, duration_seconds)
        plot_metrics(axes[row, 2], result)

        if row == 0:
            axes[row, 0].set_title("Left Panel - Waveform + energy")
            axes[row, 1].set_title("Center Panel - Spectrogram + identity traces")
            axes[row, 2].set_title("Right Panel - Persistence metrics")

        if row == len(results) - 1:
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
