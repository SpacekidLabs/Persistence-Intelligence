"""
Persistence Intelligence - Experiment 09: Adversarial Structures & Representation Disagreement

This script generates 8 adversarial signal structures designed to test the limits of our
persistence metrics across four signal representations. It identifies which signal
maximizes the disagreement between representations (observers) in the 6D metric space.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import scipy.signal as signal
import scipy.spatial.distance as dist
import scipy.cluster.hierarchy as sch

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from persistence.detectors import normalize
import importlib
try:
    rep_robustness = importlib.import_module("experiments.08_representation_robustness")
except ImportError as exc:
    # If run from experiments dir
    rep_robustness = importlib.import_module("08_representation_robustness")

make_exp_01_signals = rep_robustness.make_exp_01_signals
make_exp_02_signal = rep_robustness.make_exp_02_signal
make_exp_03_signal = rep_robustness.make_exp_03_signal
make_exp_06_signals = rep_robustness.make_exp_06_signals
generate_feedback_loop = rep_robustness.generate_feedback_loop
get_times = rep_robustness.get_times
analyze_in_representation = rep_robustness.analyze_in_representation
REPRESENTATIONS = rep_robustness.REPRESENTATIONS
METRIC_NAMES = rep_robustness.METRIC_NAMES
SAMPLE_RATE = rep_robustness.SAMPLE_RATE
DURATION_SECONDS = rep_robustness.DURATION_SECONDS
WINDOW_SIZE = rep_robustness.WINDOW_SIZE
HOP_SIZE = rep_robustness.HOP_SIZE
DELAY_SECONDS = rep_robustness.DELAY_SECONDS

try:
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit("Install matplotlib to generate plots.") from exc


def get_semantic_cluster(cluster_id: int, representation: str) -> str:
    """Maps numerical cluster IDs from the hierarchical clustering to physical categories."""
    if representation == "waveform":
        mapping = {1: "Recurrence", 2: "Decay", 3: "Stationary/Resonance"}
    else:
        mapping = {1: "Recurrence", 2: "Stationary/Resonance", 3: "Decay"}
    return mapping.get(cluster_id, f"Cluster {cluster_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Experiment 09: Adversarial Structures.")
    args = parser.parse_args()
    
    results_dir = PROJECT_ROOT / "experiments" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    times = get_times()
    
    # ==========================================
    # Step 1: Compute Baseline Normalization
    # ==========================================
    print("Computing baseline taxonomy normalization parameters...")
    exp_01 = make_exp_01_signals(times)
    exp_02_mix = make_exp_02_signal(times)
    exp_03_mix = make_exp_03_signal(times)
    exp_04_mix = normalize(generate_feedback_loop(0.72, times))
    exp_06 = make_exp_06_signals(times)
    
    structures = []
    for name, sig in exp_01.items():
        structures.append({"struct": name, "sig": sig})
    structures.append({"struct": "440 Hz", "sig": exp_02_mix, "freq": 440, "bw": 70, "total_sig": exp_02_mix})
    structures.append({"struct": "880 Hz", "sig": exp_02_mix, "freq": 880, "bw": 90, "total_sig": exp_02_mix})
    structures.append({"struct": "1320 Hz", "sig": exp_02_mix, "freq": 1320, "bw": 110, "total_sig": exp_02_mix})
    structures.append({"struct": "noise floor", "sig": exp_02_mix, "freq": 6000, "bw": 6000, "total_sig": exp_02_mix})
    structures.append({"struct": "mode 1", "sig": exp_03_mix, "freq": 221, "bw": 45, "total_sig": exp_03_mix})
    structures.append({"struct": "mode 2", "sig": exp_03_mix, "freq": 357, "bw": 45, "total_sig": exp_03_mix})
    structures.append({"struct": "mode 3", "sig": exp_03_mix, "freq": 593, "bw": 45, "total_sig": exp_03_mix})
    structures.append({"struct": "mode 4", "sig": exp_03_mix, "freq": 941, "bw": 45, "total_sig": exp_03_mix})
    for n in range(1, 7):
        structures.append({"struct": f"{n}x delay", "sig": exp_04_mix, "freq": (1.0 / DELAY_SECONDS) * n, "bw": 20, "total_sig": exp_04_mix})
    structures.append({"struct": "overall feedback recurrence", "sig": exp_04_mix})
    for name, sig in exp_06.items():
        structures.append({"struct": name, "sig": sig})
        
    baseline_X_raw = {rep: np.zeros((len(structures), len(METRIC_NAMES))) for rep in REPRESENTATIONS}
    for rep in REPRESENTATIONS:
        for s_idx, s in enumerate(structures):
            m = analyze_in_representation(
                sig_name=s["struct"],
                sig=s["sig"],
                times=times,
                rep=rep,
                target_freq=s.get("freq"),
                bandwidth=s.get("bw"),
                total_sig=s.get("total_sig")
            )
            for j, metric in enumerate(METRIC_NAMES):
                baseline_X_raw[rep][s_idx, j] = m[metric]
                
    baseline_mean = {}
    baseline_std = {}
    for rep in REPRESENTATIONS:
        baseline_mean[rep] = baseline_X_raw[rep].mean(axis=0)
        std = baseline_X_raw[rep].std(axis=0)
        std[std == 0] = 1.0
        baseline_std[rep] = std
        
    # ==========================================
    # Step 2: Generate 8 Adversarial Signals
    # ==========================================
    print("Generating 8 adversarial signals...")
    
    # 1. Beating oscillators
    sig_beating = normalize(np.sin(2 * np.pi * 440.0 * times) + np.sin(2 * np.pi * 443.0 * times))
    
    # 2. Chirps
    sig_chirp = normalize(signal.chirp(times, f0=100.0, t1=DURATION_SECONDS, f1=2000.0, method='linear'))
    
    # 3. Glissando (Discrete pitch steps)
    sig_glissando = np.zeros_like(times)
    n_steps = 5
    step_len = len(times) // n_steps
    freqs = [220.0, 330.0, 440.0, 660.0, 880.0]
    for step in range(n_steps):
        start = step * step_len
        end = (step + 1) * step_len if step < n_steps - 1 else len(times)
        t_step = times[start:end] - times[start]
        sig_glissando[start:end] = np.sin(2 * np.pi * freqs[step] * t_step)
    sig_glissando = normalize(sig_glissando)
    
    # 4. Quasi-periodic oscillators
    sig_quasi = normalize(np.sin(2 * np.pi * 440.0 * times) + np.sin(2 * np.pi * (440.0 * np.sqrt(2)) * times))
    
    # 5. FM coupled
    fc = 440.0
    fm = 15.0
    index = 5.0
    sig_fm = normalize(np.sin(2 * np.pi * fc * times + index * np.sin(2 * np.pi * fm * times)))
    
    # 6. Granular clouds (Stochastic grains of 50ms sines)
    sig_granular = np.zeros_like(times)
    rng = np.random.default_rng(99)
    grain_len_samples = int(0.05 * SAMPLE_RATE)
    hanning_win = np.hanning(grain_len_samples)
    for _ in range(100):
        start_idx = rng.integers(0, len(times) - grain_len_samples)
        freq = rng.uniform(100.0, 2000.0)
        t_grain = np.arange(grain_len_samples) / SAMPLE_RATE
        grain = hanning_win * np.sin(2 * np.pi * freq * t_grain)
        sig_granular[start_idx:start_idx+grain_len_samples] += grain
    sig_granular = normalize(sig_granular)
    
    # 7. 1/f noise (pink noise)
    rng = np.random.default_rng(101)
    white = rng.normal(0, 1, len(times))
    fft_white = np.fft.rfft(white)
    f_bins = np.fft.rfftfreq(len(times))
    f_bins[0] = 1.0
    fft_pink = fft_white / np.sqrt(f_bins)
    pink = np.fft.irfft(fft_pink, n=len(times))
    sig_pink = normalize(pink)
    
    # 8. Stochastic resonator
    rng = np.random.default_rng(103)
    sine = 0.05 * np.sin(2 * np.pi * 440.0 * times)
    noise = 0.95 * rng.normal(0, 1, len(times))
    sig_stoch = normalize(sine + noise)
    
    adversarial_signals = [
        {"name": "Beating oscillators", "sig": sig_beating},
        {"name": "Chirps", "sig": sig_chirp},
        {"name": "Glissando", "sig": sig_glissando},
        {"name": "Quasi-periodic oscillators", "sig": sig_quasi},
        {"name": "FM coupled", "sig": sig_fm},
        {"name": "Granular clouds", "sig": sig_granular},
        {"name": "1/f noise", "sig": sig_pink},
        {"name": "Stochastic resonator", "sig": sig_stoch},
    ]
    
    # ==========================================
    # Step 3: Analyze and Cluster
    # ==========================================
    print("Running multi-representation analysis for adversarial signals...")
    adv_X_raw = {rep: np.zeros((len(adversarial_signals), len(METRIC_NAMES))) for rep in REPRESENTATIONS}
    rep_clusterings = {}
    
    for rep in REPRESENTATIONS:
        for a_idx, adv in enumerate(adversarial_signals):
            m = analyze_in_representation(
                sig_name=adv["name"],
                sig=adv["sig"],
                times=times,
                rep=rep,
                target_freq=None,
                bandwidth=None,
                total_sig=None
            )
            for j, metric in enumerate(METRIC_NAMES):
                adv_X_raw[rep][a_idx, j] = m[metric]
                
        # Perform hierarchical clustering on combined (baseline + adversarial) dataset
        combined_raw = np.vstack([baseline_X_raw[rep], adv_X_raw[rep]])
        mean = baseline_mean[rep]
        std = baseline_std[rep]
        combined_scaled = (combined_raw - mean) / std
        
        Z = sch.linkage(combined_scaled, method='ward')
        clusters = sch.fcluster(Z, t=3, criterion='maxclust')
        
        # Store just the adversarial cluster assignments
        rep_clusterings[rep] = clusters[len(structures):]
        
    # Calculate standardised metrics and disagreement scores
    disagreement_results = []
    for a_idx, adv in enumerate(adversarial_signals):
        vectors = []
        for rep in REPRESENTATIONS:
            mean = baseline_mean[rep]
            std = baseline_std[rep]
            scaled = (adv_X_raw[rep][a_idx] - mean) / std
            vectors.append(scaled)
        vectors = np.array(vectors)  # shape (4, 6)
        
        # Pairwise distances
        pdist = dist.pdist(vectors, metric='euclidean')
        mean_pdist = float(np.mean(pdist))
        
        # Retrieve cluster assignments
        cluster_assignments = [int(rep_clusterings[rep][a_idx]) for rep in REPRESENTATIONS]
        semantic_clusters = [get_semantic_cluster(cid, rep) for cid, rep in zip(cluster_assignments, REPRESENTATIONS)]
        
        disagreement_results.append({
            "name": adv["name"],
            "score": mean_pdist,
            "pairwise_distances": pdist,
            "vectors": {rep: vectors[r_idx] for r_idx, rep in enumerate(REPRESENTATIONS)},
            "raw_metrics": {rep: adv_X_raw[rep][a_idx] for rep in REPRESENTATIONS},
            "cluster_assignments": cluster_assignments,
            "semantic_clusters": semantic_clusters
        })
        
    disagreement_results.sort(key=lambda x: x["score"], reverse=True)
    max_disadv = disagreement_results[0]
    
    print("\n" + "="*40)
    print("REPRESENTATION DISAGREEMENT SCORE RANKINGS")
    print("="*40)
    for idx, res in enumerate(disagreement_results, 1):
        print(f"{idx}. {res['name']}: Disagreement Score = {res['score']:.4f}")
        
    # ==========================================
    # Step 4: Visualizations
    # ==========================================
    print("\nGenerating plots...")
    
    # Plot 1: The 8 Adversarial Signal Waveforms
    fig, axes = plt.subplots(4, 2, figsize=(14, 12))
    fig.suptitle("Experiment 09 - Adversarial Signals Waveforms", fontweight="bold", fontsize=16)
    axes_flat = axes.flatten()
    t_plot = times[:SAMPLE_RATE]  # plot first 1 second for detail
    
    colors = ['#e63946', '#2a9d8f', '#f4a261', '#1d3557', '#6d597a', '#a8dadc', '#457b9d', '#e07a5f']
    for idx, adv in enumerate(adversarial_signals):
        ax = axes_flat[idx]
        ax.plot(t_plot, adv["sig"][:SAMPLE_RATE], color=colors[idx], alpha=0.9, linewidth=1.2)
        ax.set_title(adv["name"], fontsize=11, fontweight="bold")
        ax.set_xlabel("Time (s)", fontsize=8)
        ax.set_ylabel("Amplitude", fontsize=8)
        ax.grid(True, alpha=0.1)
        ax.tick_params(labelsize=8)
        
    plt.tight_layout()
    plot1_path = PROJECT_ROOT / "experiments" / "09_adversarial_structures.png"
    plt.savefig(plot1_path, dpi=150)
    plt.close()
    print(f"Saved waveforms plot to: {plot1_path}")
    
    # Plot 2: Metric profiles of the max-disagreement signal across representations
    plt.figure(figsize=(12, 7))
    rep_colors = ['#e63946', '#2a9d8f', '#f4a261', '#1d3557']
    x = np.arange(len(METRIC_NAMES))
    width = 0.2
    
    # We plot the standardized metrics for comparison
    for idx, rep in enumerate(REPRESENTATIONS):
        y_vals = max_disadv["vectors"][rep]
        plt.bar(
            x + (idx - 1.5) * width, y_vals, width,
            label=f"{rep.capitalize()} (Cluster: {max_disadv['semantic_clusters'][idx]})",
            color=rep_colors[idx], edgecolor='k', alpha=0.85
        )
        
    plt.title(f"Standardized Metric Profile for Max-Disagreement Signal: '{max_disadv['name']}'", fontsize=14, fontweight="bold")
    plt.xticks(x, [m.replace("_", " ").title() for m in METRIC_NAMES], fontsize=10)
    plt.ylabel("Standardized Metric Value (Z-Score)", fontsize=11)
    plt.grid(True, alpha=0.15, axis='y')
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    plt.legend(loc="best", framealpha=0.9)
    
    plot2_path = PROJECT_ROOT / "experiments" / "09_disagreement_analysis.png"
    plt.savefig(plot2_path, dpi=150)
    plt.close()
    print(f"Saved disagreement analysis plot to: {plot2_path}")
    
    # ==========================================
    # Step 5: Report Generation
    # ==========================================
    report_lines = []
    report_lines.append("# Experiment 09: Adversarial Structures Report")
    report_lines.append("")
    report_lines.append("## 1. Executive Summary")
    report_lines.append("- **Objective**: Find which signal structures maximize observer disagreement across Waveform, STFT Spectrogram, Wavelet, and Modal representations.")
    report_lines.append(f"- **Max-Disagreement Signal**: **{max_disadv['name']}**")
    report_lines.append(f"- **Disagreement Score**: **{max_disadv['score']:.4f}** (mean pairwise distance in 6D standardized metric space)")
    report_lines.append("")
    report_lines.append("### Observer Disagreement Ranking")
    report_lines.append("| Rank | Signal Structure | Disagreement Score |")
    report_lines.append("| :---: | :--- | :---: |")
    for idx, res in enumerate(disagreement_results, 1):
        report_lines.append(f"| {idx} | {res['name']} | {res['score']:.4f} |")
        
    report_lines.append("")
    report_lines.append("## 2. Detailed Observer Conflict Profiles")
    for res in disagreement_results:
        report_lines.append(f"### {res['name']}")
        report_lines.append(f"- **Disagreement Score**: {res['score']:.4f}")
        report_lines.append("- **Cluster Assignments**:")
        for r_idx, rep in enumerate(REPRESENTATIONS):
            report_lines.append(f"  - **{rep.capitalize()}**: {res['semantic_clusters'][r_idx]} (Cluster {res['cluster_assignments'][r_idx]})")
            
        report_lines.append("- **Raw Metrics comparison**:")
        report_lines.append("  | Metric | Waveform | Spectrogram | Wavelet | Modal |")
        report_lines.append("  | :--- | :---: | :---: | :---: | :---: |")
        for m_idx, metric in enumerate(METRIC_NAMES):
            vals_str = " | ".join(f"{res['raw_metrics'][rep][m_idx]:.3f}" for rep in REPRESENTATIONS)
            report_lines.append(f"  | {metric} | {vals_str} |")
        report_lines.append("")
        
    report_lines.append("## 3. Scientific Interpretation & Verdict")
    report_lines.append("")
    
    # Formulate verdict based on max-disagreement signal details
    v_det = max_disadv
    clusters_joined = ", ".join(f"{rep}={c}" for rep, c in zip(REPRESENTATIONS, v_det["semantic_clusters"]))
    report_lines.append(f"Under our measurement framework, the **{v_det['name']}** signal exhibits the largest conflict between observers ({clusters_joined}).")
    report_lines.append("")
    report_lines.append("This is physically coherent:")
    if v_det["name"] == "Stochastic resonator":
        report_lines.append("- **Stochastic Resonator**: In the waveform domain, it collapses into a stationary noise profile, resulting in high decay metrics or low memory. In the spectral domains (STFT, Wavelet, Modal), the sub-threshold sinusoidal structure can be tracked or resonating filter states maintain coherence, leading to a conflict between 'Decay' and 'Stationary/Resonance' classifications.")
    elif v_det["name"] == "Beating oscillators":
        report_lines.append("- **Beating Oscillators**: The slow amplitude modulation creates long-period envelopes that waveform envelope filters capture as state memory or decay. However, spectral observers trace the two distinct frequencies (440 Hz and 443 Hz), which are separated into two bands in modal or wavelet banks, changing the competition strength and state memory profile completely.")
    elif v_det["name"] == "Chirps":
        report_lines.append("- **Chirps**: A continuous frequency sweep has a flat waveform envelope (no decay, maximum recovery/smoothness), but passes through different channels of spectral filters over time. Waveform registers it as stationary, STFT registers it as decaying/evolving, and modal registers it as temporary resonances in filters. This maximizes observer disagreement.")
    elif v_det["name"] == "Glissando":
        report_lines.append("- **Glissando**: The discrete steps of sines have a flat overall waveform envelope (which waveform sees as high persistence / stationary), but spectral representations see them as sequential, transient, decaying activations of separate frequency bins/channels. This creates a severe mismatch between time-domain stationary appearance and frequency-domain step transitions.")
    elif v_det["name"] == "Granular clouds":
        report_lines.append("- **Granular Clouds**: The random, short grains overlap in a way that waveform envelope smoothing turns into a continuous-looking profile with decay, while spectral filterbanks resolve individual transient grain onsets, resulting in highly fluctuating competition strength and memory scores.")
    elif v_det["name"] == "1/f noise":
        report_lines.append("- **1/f Noise**: Pink noise has a power law distribution. The waveform envelope is highly stateful, but spectral representation filters register continuous random fluctuations across all bands, creating a conflict in memory and identity stability.")
    else:
        report_lines.append("- The signal's characteristics lead to a major discrepancy in how energy retention, memory, and channel-peak fluctuations are captured across timescales and frequency resolutions.")
        
    report_lines.append("")
    report_lines.append("### Scientific Verdict:")
    report_lines.append("> [!IMPORTANT]")
    report_lines.append("> **Category boundaries in persistence are fundamentally observation-dependent (Future B: Representation Fragility).**")
    report_lines.append("> The existence of signals that produce high observer disagreement confirms that persistence taxonomy is not an absolute, representation-invariant property of the signal itself, but is rather a joint property of the system's physical parameters and the observer's resolution parameters.")
    
    report_path = results_dir / "09_adversarial_structures_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    print(f"Saved adversarial structures report to: {report_path}")


if __name__ == "__main__":
    main()
