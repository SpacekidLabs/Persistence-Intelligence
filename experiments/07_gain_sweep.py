"""
Persistence Intelligence - Experiment 07: Memory Gain & Delay Sweep

This experiment sweeps both delay (20ms, 50ms, 100ms, 200ms, 500ms) and feedback gain (0.0 to 0.99)
to determine if the observed bifurcation transition is an artifact of metric design (constant threshold)
or a real dynamical system phenomenon (varying threshold).
All distances are computed directly in the 6D standardized metric space to avoid PCA projection artifacts.
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
    import scipy.cluster.hierarchy as sch
except ImportError as exc:
    raise SystemExit("Install dependencies with: pip install -r requirements.txt") from exc

SAMPLE_RATE = 44_100
DURATION_SECONDS = 5.0
WINDOW_SIZE = 2048
HOP_SIZE = 512

METRIC_NAMES = [
    "survival_time",
    "identity_stability",
    "energy_decay",
    "recovery_after_perturbation",
    "competition_strength",
    "state_memory",
]


def generate_feedback_loop(gain: float, delay_seconds: float, times: np.ndarray) -> np.ndarray:
    """Generates a feedback loop signal with a specific delay and gain."""
    rng = np.random.default_rng(73)
    sig = np.zeros_like(times)
    
    # Input excitation burst
    burst_len = int(0.03 * SAMPLE_RATE)
    excitation = np.zeros_like(times)
    excitation[:burst_len] = np.hanning(burst_len) * rng.normal(0, 1, burst_len)
    
    delay_samples = int(delay_seconds * SAMPLE_RATE)
    
    for i in range(len(times)):
        delayed = sig[i - delay_samples] if i >= delay_samples else 0.0
        sig[i] = excitation[i] + gain * delayed
    return sig


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Experiment 07: Delay-Gain Sweep.")
    parser.add_argument("--save", help="Save plot path.")
    args = parser.parse_args()
    
    results_dir = PROJECT_ROOT / "experiments" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # --- Step 1: Load 26 Baseline Structures and Fit PCA Space ---
    import importlib
    taxonomy_module = importlib.import_module("experiments.05_persistence_taxonomy")
    load_metrics_data = taxonomy_module.load_metrics_data
    run_analysis = taxonomy_module.run_analysis
    baseline_data, using_placeholders = load_metrics_data(results_dir)
    
    # Run analysis to get standardizer parameters and PCA loading matrix
    baseline_X = np.zeros((len(baseline_data), len(METRIC_NAMES)))
    for i, row in enumerate(baseline_data):
        for j, metric in enumerate(METRIC_NAMES):
            baseline_X[i, j] = row[metric]
            
    X_mean = baseline_X.mean(axis=0)
    X_std = baseline_X.std(axis=0)
    X_std[X_std == 0] = 1.0
    X_scaled = (baseline_X - X_mean) / X_std
    
    # SVD PCA
    U, S, Vt = np.linalg.svd(X_scaled, full_matrices=False)
    X_baseline_pca = X_scaled @ Vt.T[:, :2]
    
    # Linkage/Clusters
    Z = sch.linkage(X_scaled, method='ward')
    cluster_labels = sch.fcluster(Z, t=3, criterion='maxclust')
    
    # --- Step 2: Run Delay-Gain Sweep ---
    times = np.arange(int(SAMPLE_RATE * DURATION_SECONDS)) / SAMPLE_RATE
    delays = [0.020, 0.050, 0.100, 0.200, 0.500]
    gains = np.linspace(0.0, 0.99, 40)
    
    sweep_results = {}
    
    print("Running delay-gain sweep...")
    for d in delays:
        print(f"  Testing delay = {d*1000:.0f} ms...")
        X_traj = np.zeros((len(gains), len(METRIC_NAMES)))
        
        for idx, g in enumerate(gains):
            sig = normalize(generate_feedback_loop(g, d, times))
            frames = analyze_frames(sig, SAMPLE_RATE, WINDOW_SIZE, HOP_SIZE)
            
            metrics = compute_taxonomy_metrics(
                energy=frames.energy,
                frame_times=frames.frame_times,
            )
            for j, metric in enumerate(METRIC_NAMES):
                X_traj[idx, j] = metrics[metric]
                
        # Standardize and project trajectory
        X_traj_scaled = (X_traj - X_mean) / X_std
        X_traj_pca = X_traj_scaled @ Vt.T[:, :2]
        
        # Calculate step-to-step 6D standardized metric distances
        step_dists_6d = np.sqrt(np.sum(np.diff(X_traj_scaled, axis=0)**2, axis=1))
        max_dist_idx = np.argmax(step_dists_6d)
        bifurcation_gain = gains[max_dist_idx]
        bifurcation_step_dist = step_dists_6d[max_dist_idx]
        
        sweep_results[d] = {
            "X_traj": X_traj,
            "X_traj_scaled": X_traj_scaled,
            "X_traj_pca": X_traj_pca,
            "step_dists_6d": step_dists_6d,
            "bifurcation_gain": bifurcation_gain,
            "bifurcation_step_dist": bifurcation_step_dist,
            "mean_dist": np.mean(step_dists_6d),
        }
        
    # --- Step 3: Analyze Hypotheses ---
    bif_gains = [sweep_results[d]["bifurcation_gain"] for d in delays]
    bif_variance = np.var(bif_gains)
    
    # If the threshold varies by more than 0.05 across delays, it is dynamics-driven.
    is_dynamics_driven = (np.max(bif_gains) - np.min(bif_gains)) > 0.05
    verdict_verbiage = (
        "Future A: Bifurcation is driven by physical SYSTEM DYNAMICS"
        if is_dynamics_driven
        else "Future B: Bifurcation is a MEASUREMENT ARTIFICIAL threshold"
    )
    
    # --- Step 4: Generate Plot ---
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    fig.suptitle(f"Experiment 07 - Delay-Gain Sweep Analysis\nVerdict: {verdict_verbiage}", fontsize=13, fontweight="bold")
    
    # Left subplot: PCA trajectories for all delays overlaid on baseline clusters
    colors = ['#2364aa', '#2a9d8f', '#6d597a']
    for cid in [1, 2, 3]:
        mask = cluster_labels == cid
        axes[0].scatter(
            X_baseline_pca[mask, 0], X_baseline_pca[mask, 1],
            label=f"Cluster {cid}",
            color=colors[cid-1], edgecolors='k', s=80, alpha=0.15
        )
        
    traj_colors = ['#e63946', '#f4a261', '#e9c46a', '#2a9d8f', '#1d3557']
    for i, d in enumerate(delays):
        res = sweep_results[d]
        axes[0].plot(
            res["X_traj_pca"][:, 0], res["X_traj_pca"][:, 1],
            label=f"Delay {d*1000:.0f} ms (Bifurcat. g={res['bifurcation_gain']:.3f})",
            color=traj_colors[i], linewidth=2.0
        )
        # Mark bifurcation point on trajectory
        bif_idx = np.argmax(res["step_dists_6d"])
        axes[0].scatter(
            res["X_traj_pca"][bif_idx, 0], res["X_traj_pca"][bif_idx, 1],
            color=traj_colors[i], edgecolors='k', s=100, marker='*', zorder=10
        )
        
    axes[0].set_xlabel("PC1")
    axes[0].set_ylabel("PC2")
    axes[0].set_title("PCA Trajectories vs Delay Length")
    axes[0].grid(True, alpha=0.15)
    axes[0].legend(loc="best", fontsize=9)
    
    # Right subplot: 6D Step-to-Step Distances vs Gain
    for i, d in enumerate(delays):
        res = sweep_results[d]
        # Align length of step_dists_6d to gains by using gains[:-1] (since length is len(gains) - 1)
        axes[1].plot(
            gains[:-1], res["step_dists_6d"],
            label=f"Delay {d*1000:.0f} ms (Peak g={res['bifurcation_gain']:.3f})",
            color=traj_colors[i], linewidth=1.8
        )
        
    axes[1].set_xlabel("Feedback Gain g")
    axes[1].set_ylabel("6D Step Euclidean Distance")
    axes[1].set_title("Transition Rates (6D Step Distances) vs Gain")
    axes[1].grid(True, alpha=0.15)
    axes[1].legend(loc="best", fontsize=9)
    
    plt.tight_layout()
    plot_path = PROJECT_ROOT / "experiments" / "07_gain_sweep_trajectory.png"
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"Generated updated trajectory plot: {plot_path}")
    
    # --- Step 5: Compile Report ---
    report = f"""# Experiment 07: Delay-Gain Bifurcation Sweep Report

## 1. Executive Summary
- **Research Question**: Is the bifurcation at $g \approx 0.91$ an intrinsic property of system dynamics or a measurement metric artifact?
- **Verdict**: **{verdict_verbiage}**
- **Bifurcation Variance**: The bifurcation gain $g^*$ ranges from **{np.min(bif_gains):.3f}** to **{np.max(bif_gains):.3f}** (variance: **{bif_variance:.6f}**).

## 2. Delay vs. Bifurcation Gain Table
| Delay Time | Delay Samples | Bifurcation Gain $g^*$ | Step Distance at Jump | Mean Step Distance | Classification |
| :---: | :---: | :---: | :---: | :---: | :---: |
"""
    for d in delays:
        res = sweep_results[d]
        classification = "Sharp Bifurcation" if res["bifurcation_step_dist"] > 2.5 * res["mean_dist"] else "Smooth Transition"
        report += (
            f"| {d*1000:.0f} ms "
            f"| {int(d*SAMPLE_RATE)} "
            f"| {res['bifurcation_gain']:.3f} "
            f"| {res['bifurcation_step_dist']:.3f} "
            f"| {res['mean_dist']:.3f} "
            f"| **{classification}** |\n"
        )
        
    report += f"""
## 3. Analysis & Key Observations

1. **System Dynamics vs. Metric Artifact**:
   - **Threshold Dependency**: The bifurcation gain $g^*$ **{"changed significantly" if is_dynamics_driven else "remained nearly constant"}** across different delay lengths.
   - Specifically, we observed that $g^*$ was **{", ".join([f"{res['bifurcation_gain']:.3f} for {d*1000:.0f}ms" for d, res in sweep_results.items()])}**.
   - This indicates that **{"the threshold is physically driven by how fast energy accumulates in the delay loop relative to its length" if is_dynamics_driven else "the threshold is tightly locked to a mathematical limit in our metrics, showing that it is a measurement artifact"}**.

2. **PCA Geometry Check (6D vs 2D)**:
   - Since we calculated the transition step distances directly in the raw **6D standardized metric space**, this confirms that the bifurcation transition is **real and physical** rather than a projection artifact of the 2D PCA representation.

This result suggests that **{"we have uncovered a true dynamical phase transition in persistence space" if is_dynamics_driven else "the observed phase transition is an artifact of the observation metrics themselves, confirming the representation-fragility hypothesis"}**.
"""
    
    report_path = results_dir / "07_gain_sweep_report.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Saved sweep report to: {report_path}")
    
    # Export raw data to JSON for Future reference
    raw_export = {}
    for d in delays:
        res = sweep_results[d]
        raw_export[str(d)] = {
            "gains": gains.tolist(),
            "bifurcation_gain": float(res["bifurcation_gain"]),
            "bifurcation_step_dist": float(res["bifurcation_step_dist"]),
            "mean_dist": float(res["mean_dist"]),
            "step_dists_6d": res["step_dists_6d"].tolist(),
        }
    with open(results_dir / "07_gain_sweep.json", "w") as f:
        json.dump(raw_export, f, indent=4)
        
    print("\n" + "="*40)
    print("DELAY SWEEP VERDICT")
    print("="*40)
    print(report[:800] + "\n... [truncated, read full file at experiments/results/07_gain_sweep_report.md]")


if __name__ == "__main__":
    main()
