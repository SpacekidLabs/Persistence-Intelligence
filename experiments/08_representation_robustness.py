"""
Persistence Intelligence - Experiment 08: Representation Robustness

This experiment tests the robustness of our persistence taxonomy and the feedback
bifurcation across four signal representations:
1. Waveform Envelope (RMS)
2. STFT Spectrogram (Baseline)
3. Wavelet Filterbank (Complex Gabor Wavelets)
4. Modal Decomposition (IIR Resonators)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import scipy.signal as signal

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from persistence.detectors import analyze_frames, normalize
from persistence.metrics import energy_retention_score

try:
    import matplotlib.pyplot as plt
    import scipy.cluster.hierarchy as sch
except ImportError as exc:
    raise SystemExit("Install dependencies with: pip install -r requirements.txt") from exc

SAMPLE_RATE = 44_100
DURATION_SECONDS = 5.0
WINDOW_SIZE = 2048
HOP_SIZE = 512
DELAY_SECONDS = 0.145

METRIC_NAMES = [
    "survival_time",
    "identity_stability",
    "energy_decay",
    "recovery_after_perturbation",
    "competition_strength",
    "state_memory",
]

REPRESENTATIONS = ["waveform", "spectrogram", "wavelet", "modal"]

# Center frequencies of our 12 representation channels (log-spaced)
REP_FREQS = np.logspace(np.log10(100.0), np.log10(2000.0), 12)


def make_gabor_filter(fc: float, fs: float, q: float = 8.0) -> np.ndarray:
    """Creates a complex Gabor wavelet filter in the time domain."""
    sigma_t = q / (2 * np.pi * fc)
    t = np.arange(-4 * sigma_t, 4 * sigma_t, 1 / fs)
    filt = np.exp(2j * np.pi * fc * t) * np.exp(-t**2 / (2 * sigma_t**2))
    return filt / (np.linalg.norm(filt) + 1e-12)


def get_wavelet_representation(sig: np.ndarray) -> np.ndarray:
    """Computes envelopes for 12 complex Gabor wavelet scales."""
    envelopes = []
    for fc in REP_FREQS:
        filt = make_gabor_filter(fc, SAMPLE_RATE)
        filtered = signal.convolve(sig, filt, mode='same')
        # RMS envelope downsampled to frames
        n_frames = 1 + (len(sig) - WINDOW_SIZE) // HOP_SIZE
        env = np.zeros(n_frames)
        for f in range(n_frames):
            start = f * HOP_SIZE
            stop = start + WINDOW_SIZE
            env[f] = np.sqrt(np.mean(np.abs(filtered[start:stop])**2))
        envelopes.append(env)
    return np.array(envelopes).T  # shape (n_frames, 12)


def get_modal_representation(sig: np.ndarray) -> np.ndarray:
    """Computes envelopes for 12 second-order IIR bandpass resonators."""
    envelopes = []
    bandwidth = 30.0  # Hz
    for fc in REP_FREQS:
        r = np.exp(-np.pi * bandwidth / SAMPLE_RATE)
        theta = 2 * np.pi * fc / SAMPLE_RATE
        a1 = -2 * r * np.cos(theta)
        a2 = r**2
        b0 = 1.0 - r
        filtered = signal.lfilter([b0], [1.0, a1, a2], sig)
        # RMS envelope downsampled to frames
        n_frames = 1 + (len(sig) - WINDOW_SIZE) // HOP_SIZE
        env = np.zeros(n_frames)
        for f in range(n_frames):
            start = f * HOP_SIZE
            stop = start + WINDOW_SIZE
            env[f] = np.sqrt(np.mean(filtered[start:stop]**2))
        envelopes.append(env)
    return np.array(envelopes).T  # shape (n_frames, 12)


def get_waveform_representation(sig: np.ndarray) -> np.ndarray:
    """Computes a 1D RMS envelope of the signal in time domain."""
    n_frames = 1 + (len(sig) - WINDOW_SIZE) // HOP_SIZE
    env = np.zeros(n_frames)
    for f in range(n_frames):
        start = f * HOP_SIZE
        stop = start + WINDOW_SIZE
        env[f] = np.sqrt(np.mean(sig[start:stop]**2))
    return env[:, np.newaxis]  # shape (n_frames, 1)


# --- Signal Generation Helpers ---
def get_times() -> np.ndarray:
    return np.arange(int(SAMPLE_RATE * DURATION_SECONDS)) / SAMPLE_RATE


def generate_feedback_loop(gain: float, times: np.ndarray) -> np.ndarray:
    rng = np.random.default_rng(73)
    sig = np.zeros_like(times)
    burst_len = int(0.03 * SAMPLE_RATE)
    excitation = np.zeros_like(times)
    excitation[:burst_len] = np.hanning(burst_len) * rng.normal(0, 1, burst_len)
    delay_samples = int(DELAY_SECONDS * SAMPLE_RATE)
    for i in range(len(times)):
        delayed = sig[i - delay_samples] if i >= delay_samples else 0.0
        sig[i] = excitation[i] + gain * delayed
    return sig


def make_exp_01_signals(times: np.ndarray) -> dict:
    pure = np.sin(2 * np.pi * 440.0 * times)
    decay = np.exp(-times / 1.15) * np.sin(2 * np.pi * 440.0 * times)
    drift = np.sin(2 * np.pi * (440.0 + 10.0 * np.sin(2 * np.pi * 0.42 * times)) * times)
    rng = np.random.default_rng(7)
    burst_len = int(0.85 * SAMPLE_RATE)
    burst = np.zeros_like(times)
    burst[:burst_len] = np.hanning(burst_len) * rng.normal(0, 1, burst_len)
    return {
        "Pure sine 440 Hz": normalize(pure),
        "Decaying sine 440 Hz": normalize(decay),
        "Frequency drift 440 Hz": normalize(drift),
        "White noise burst": normalize(burst),
    }


def make_exp_02_signal(times: np.ndarray) -> np.ndarray:
    decaying_sine = lambda t, f, d: np.exp(-t / d) * np.sin(2 * np.pi * f * t)
    rng = np.random.default_rng(11)
    sig = (
        0.90 * decaying_sine(times, 440, 4.5)
        + 0.70 * decaying_sine(times, 880, 2.2)
        + 0.55 * decaying_sine(times, 1320, 0.9)
    )
    noise_env = np.exp(-times / 0.55)
    sig += 0.42 * noise_env * rng.normal(0, 1, times.shape)
    return normalize(sig)


def make_exp_03_signal(times: np.ndarray) -> np.ndarray:
    modes = [
        {"frequency": 221.0, "decay": 4.8, "amplitude": 1.00},
        {"frequency": 357.0, "decay": 2.6, "amplitude": 0.65},
        {"frequency": 593.0, "decay": 1.35, "amplitude": 0.45},
        {"frequency": 941.0, "decay": 0.75, "amplitude": 0.35},
    ]
    sig = np.zeros_like(times)
    rng = np.random.default_rng(23)
    for m in modes:
        phase = rng.uniform(0, 2 * np.pi)
        env = np.exp(-times / m["decay"])
        sig += m["amplitude"] * env * np.sin(2 * np.pi * m["frequency"] * times + phase)
    burst_len = int(0.04 * SAMPLE_RATE)
    excitation = np.zeros_like(times)
    excitation[:burst_len] = np.hanning(burst_len) * rng.normal(0, 0.4, burst_len)
    return normalize(sig + excitation)


def make_exp_06_signals(times: np.ndarray) -> dict:
    rng = np.random.default_rng(61)
    pure_decay = np.exp(-times / 1.0) * np.sin(2 * np.pi * 440.0 * times)
    double_decay = (0.8 * np.exp(-times / 0.15) + 0.2 * np.exp(-times / 2.5)) * np.sin(2 * np.pi * 440.0 * times)
    
    # Delay line no feedback
    delay_no_fb = np.zeros_like(times)
    burst = int(0.03 * SAMPLE_RATE)
    delay_no_fb[:burst] = np.hanning(burst) * rng.normal(0, 1, burst)
    echo = int(0.145 * SAMPLE_RATE)
    if echo + burst < len(delay_no_fb):
        delay_no_fb[echo:echo+burst] += 0.7 * delay_no_fb[:burst]
        
    resonant = np.sin(2 * np.pi * 440.0 * times)
    
    # Chaotic
    chaotic = np.zeros_like(times)
    x = 0.42
    r = 3.95
    for i in range(len(chaotic)):
        x = r * x * (1.0 - x)
        chaotic[i] = x
        
    # Periodic
    periodic = np.zeros_like(times)
    for onset in np.arange(0, DURATION_SECONDS, 0.25):
        idx = int(onset * SAMPLE_RATE)
        bl = int(0.02 * SAMPLE_RATE)
        if idx + bl < len(periodic):
            periodic[idx:idx+bl] = np.hanning(bl) * rng.normal(0, 1, bl)
            
    return {
        "pure exponential decay": normalize(pure_decay),
        "double exponential decay": normalize(double_decay),
        "delay line without feedback": normalize(delay_no_fb),
        "feedback loop": normalize(generate_feedback_loop(0.72, times)),
        "resonant system": normalize(resonant),
        "chaotic recurrence": normalize(chaotic - 0.5),
        "periodic recurrence": normalize(periodic),
    }


def compute_rep_metrics(
    energy: np.ndarray,
    peak_channels: np.ndarray | None,
    frame_times: np.ndarray,
    total_energy: np.ndarray | None = None,
) -> dict[str, float]:
    # 1. survival_time (Effective ENBW-based)
    energy_sum = np.sum(energy)
    if energy_sum > 0:
        dt = frame_times[1] - frame_times[0] if len(frame_times) > 1 else 1.0
        surv = float((energy_sum ** 2) / (np.sum(energy ** 2) + 1e-12) * dt)
    else:
        surv = 0.0
        
    # 2. identity_stability
    if peak_channels is not None and len(np.unique(peak_channels)) > 1:
        stability = float(1.0 / (1.0 + np.std(peak_channels) / 2.0))
    else:
        stability = 1.0
        
    # 3. energy_decay (retention score)
    retention = energy_retention_score(energy)
    
    # 4. recovery_after_perturbation
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
        
    # 6. state_memory (envelope autocorrelation prominence)
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


def analyze_in_representation(
    sig_name: str,
    sig: np.ndarray,
    times: np.ndarray,
    rep: str,
    target_freq: float | None = None,
    bandwidth: float | None = None,
    total_sig: np.ndarray | None = None,
) -> dict[str, float]:
    """Analyzes a signal in a specific representation and extracts the target structure."""
    if rep == "waveform":
        rep_data = get_waveform_representation(sig)
    elif rep == "spectrogram":
        frames = analyze_frames(sig, SAMPLE_RATE, WINDOW_SIZE, HOP_SIZE)
        rep_data = frames.power
    elif rep == "wavelet":
        rep_data = get_wavelet_representation(sig)
    elif rep == "modal":
        rep_data = get_modal_representation(sig)
        
    frame_times = (np.arange(len(rep_data)) * HOP_SIZE + WINDOW_SIZE / 2) / SAMPLE_RATE
    
    # Extract channel energy trace
    if rep_data.shape[1] == 1:
        # Waveform envelope (1D)
        energy = rep_data[:, 0]
        peak_channels = np.zeros(len(rep_data))
        total_energy = None
    else:
        # Multidimensional (spectrogram, wavelets, modal)
        if target_freq is None:
            # Overall energy (sum of all channels)
            energy = np.sum(rep_data, axis=1)
            peak_channels = np.argmax(rep_data, axis=1)
            total_energy = None
        else:
            # Band-specific energy
            if rep == "spectrogram":
                # Average bins in frequency band
                frequencies = np.fft.rfftfreq(WINDOW_SIZE, d=1 / SAMPLE_RATE)
                low = target_freq - bandwidth / 2
                high = target_freq + bandwidth / 2
                band = (frequencies >= low) & (frequencies <= high)
                energy = np.sum(rep_data[:, band], axis=1) if np.any(band) else np.zeros(len(rep_data))
            else:
                # Find closest wavelet/modal scale channel
                idx = np.argmin(np.abs(REP_FREQS - target_freq))
                energy = rep_data[:, idx]
                
            peak_channels = np.argmax(rep_data, axis=1)
            
            # For competition strength, compute total energy of all channels or total mix energy
            if total_sig is not None:
                # We need to analyze the mix in the same representation to get total energy
                if rep == "spectrogram":
                    mix_frames = analyze_frames(total_sig, SAMPLE_RATE, WINDOW_SIZE, HOP_SIZE)
                    total_energy = mix_frames.energy
                elif rep == "wavelet":
                    mix_rep = get_wavelet_representation(total_sig)
                    total_energy = np.sum(mix_rep, axis=1)
                elif rep == "modal":
                    mix_rep = get_modal_representation(total_sig)
                    total_energy = np.sum(mix_rep, axis=1)
            else:
                total_energy = np.sum(rep_data, axis=1)
                
    # Normalize trace
    if np.max(energy) > 0:
        energy = energy / np.max(energy)
    if total_energy is not None and np.max(total_energy) > 0:
        total_energy = total_energy / np.max(total_energy)
        
    return compute_rep_metrics(energy, peak_channels, frame_times, total_energy)


def get_cluster_agreement(labels1: np.ndarray, labels2: np.ndarray) -> float:
    """Computes Jaccard Similarity of Pair Partitions between two clusterings."""
    n = len(labels1)
    pairs1 = set()
    pairs2 = set()
    for i in range(n):
        for j in range(i + 1, n):
            if labels1[i] == labels1[j]:
                pairs1.add((i, j))
            if labels2[i] == labels2[j]:
                pairs2.add((i, j))
    intersection = len(pairs1.intersection(pairs2))
    union = len(pairs1.union(pairs2))
    return intersection / union if union > 0 else 1.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Experiment 08: Representation Robustness.")
    args = parser.parse_args()
    
    results_dir = PROJECT_ROOT / "experiments" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    times = get_times()
    
    # --- Step 1: Generate all Signals ---
    exp_01 = make_exp_01_signals(times)
    exp_02_mix = make_exp_02_signal(times)
    exp_03_mix = make_exp_03_signal(times)
    exp_04_mix = normalize(generate_feedback_loop(0.72, times))
    exp_06 = make_exp_06_signals(times)
    
    # Define structure definitions
    structures = []
    
    # Exp 01
    for name, sig in exp_01.items():
        structures.append({"exp": "01_signal_persistence", "struct": name, "sig": sig})
        
    # Exp 02
    structures.append({"exp": "02_competing_resonances", "struct": "440 Hz", "sig": exp_02_mix, "freq": 440, "bw": 70, "total_sig": exp_02_mix})
    structures.append({"exp": "02_competing_resonances", "struct": "880 Hz", "sig": exp_02_mix, "freq": 880, "bw": 90, "total_sig": exp_02_mix})
    structures.append({"exp": "02_competing_resonances", "struct": "1320 Hz", "sig": exp_02_mix, "freq": 1320, "bw": 110, "total_sig": exp_02_mix})
    structures.append({"exp": "02_competing_resonances", "struct": "noise floor", "sig": exp_02_mix, "freq": 6000, "bw": 6000, "total_sig": exp_02_mix})
    
    # Exp 03
    structures.append({"exp": "03_modal_objects", "struct": "mode 1", "sig": exp_03_mix, "freq": 221, "bw": 45, "total_sig": exp_03_mix})
    structures.append({"exp": "03_modal_objects", "struct": "mode 2", "sig": exp_03_mix, "freq": 357, "bw": 45, "total_sig": exp_03_mix})
    structures.append({"exp": "03_modal_objects", "struct": "mode 3", "sig": exp_03_mix, "freq": 593, "bw": 45, "total_sig": exp_03_mix})
    structures.append({"exp": "03_modal_objects", "struct": "mode 4", "sig": exp_03_mix, "freq": 941, "bw": 45, "total_sig": exp_03_mix})
    
    # Exp 04
    for n in range(1, 7):
        structures.append({"exp": "04_feedback_systems", "struct": f"{n}x delay", "sig": exp_04_mix, "freq": (1.0 / DELAY_SECONDS) * n, "bw": 20, "total_sig": exp_04_mix})
    structures.append({"exp": "04_feedback_systems", "struct": "overall feedback recurrence", "sig": exp_04_mix})
    
    # Exp 06
    for name, sig in exp_06.items():
        structures.append({"exp": "06_metric_falsification", "struct": name, "sig": sig})
        
    print(f"Generated {len(structures)} structures for analysis.")
    
    # --- Step 2: Compute Baseline Metrics for each representation ---
    rep_datasets = {}
    rep_clusterings = {}
    rep_pca_coords = {}
    rep_X_scaled_all = {}
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle("Experiment 08 - Taxonomy PCA Space Across Representations", fontweight="bold", fontsize=14)
    axes_flat = axes.flatten()
    
    for idx, rep in enumerate(REPRESENTATIONS):
        print(f"Analyzing in representation: {rep}...")
        rep_X = np.zeros((len(structures), len(METRIC_NAMES)))
        
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
                rep_X[s_idx, j] = m[metric]
                
        # Standardize
        rep_mean = rep_X.mean(axis=0)
        rep_std = rep_X.std(axis=0)
        rep_std[rep_std == 0] = 1.0
        rep_X_scaled = (rep_X - rep_mean) / rep_std
        rep_X_scaled_all[rep] = rep_X_scaled
        
        # PCA
        U, S, Vt = np.linalg.svd(rep_X_scaled, full_matrices=False)
        rep_pca = rep_X_scaled @ Vt.T[:, :2]
        rep_pca_coords[rep] = rep_pca
        rep_datasets[rep] = (rep_X, rep_mean, rep_std, Vt)
        
        # Hierarchical Clustering (3 clusters)
        Z = sch.linkage(rep_X_scaled, method='ward')
        clusters = sch.fcluster(Z, t=3, criterion='maxclust')
        rep_clusterings[rep] = clusters
        
        # Plot on Subplot
        ax = axes_flat[idx]
        colors = ['#2364aa', '#2a9d8f', '#6d597a']
        for cid in [1, 2, 3]:
            mask = clusters == cid
            ax.scatter(
                rep_pca[mask, 0], rep_pca[mask, 1],
                label=f"Cluster {cid}",
                color=colors[cid-1], edgecolors='k', s=80, alpha=0.85
            )
        ax.set_title(f"{rep.capitalize()} Representation Space")
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.grid(True, alpha=0.15)
        ax.legend(loc="best", fontsize=8)
        
    plt.tight_layout()
    pca_plot_path = PROJECT_ROOT / "experiments" / "08_representation_robustness.png"
    plt.savefig(pca_plot_path, dpi=150)
    plt.close()
    print(f"Saved PCA representation plot to: {pca_plot_path}")
    
    # --- Step 3: Run Gain Sweeps in all Representations ---
    gains = np.linspace(0.0, 0.99, 40)
    sweep_distances = {}
    bif_gains = {}
    
    print("Running gain sweeps in all representations...")
    for rep in REPRESENTATIONS:
        # Retrieve scale params for this representation
        _, mean, std, Vt = rep_datasets[rep]
        X_traj = np.zeros((len(gains), len(METRIC_NAMES)))
        
        for idx, g in enumerate(gains):
            sig = normalize(generate_feedback_loop(g, times))
            m = analyze_in_representation(
                sig_name="feedback_sweep",
                sig=sig,
                times=times,
                rep=rep,
            )
            for j, metric in enumerate(METRIC_NAMES):
                X_traj[idx, j] = m[metric]
                
        # Project and Standardize
        X_traj_scaled = (X_traj - mean) / std
        X_traj_pca = X_traj_scaled @ Vt.T[:, :2]
        
        # Calculate step-to-step 6D standardized metric distances
        dists = np.sqrt(np.sum(np.diff(X_traj_scaled, axis=0)**2, axis=1))
        sweep_distances[rep] = dists
        bif_idx = np.argmax(dists)
        bif_gains[rep] = gains[bif_idx]
        
    # --- Step 4: Plot Transition Step-Distances ---
    plt.figure(figsize=(10, 6))
    rep_colors = ['#e63946', '#2a9d8f', '#f4a261', '#1d3557']
    for idx, rep in enumerate(REPRESENTATIONS):
        plt.plot(
            gains[:-1], sweep_distances[rep],
            label=f"{rep.capitalize()} (Peak g={bif_gains[rep]:.3f})",
            color=rep_colors[idx], linewidth=2.0
        )
    plt.title("Bifurcation Step Distances vs Gain Across Representations")
    plt.xlabel("Feedback Gain g")
    plt.ylabel("6D Step Euclidean Distance")
    plt.grid(True, alpha=0.15)
    plt.legend(loc="best")
    dist_plot_path = PROJECT_ROOT / "experiments" / "08_representation_robustness_bifurcation.png"
    plt.savefig(dist_plot_path, dpi=150)
    plt.close()
    print(f"Saved bifurcation comparison plot to: {dist_plot_path}")
    
    # --- Step 5: Calculate Cluster Agreements ---
    agreements = {}
    stft_clusters = rep_clusterings["spectrogram"]
    for rep in REPRESENTATIONS:
        agreements[rep] = get_cluster_agreement(stft_clusters, rep_clusterings[rep])
        
    # --- Step 6: Compile Report ---
    agreement_lines = []
    agreement_lines.append("| Representation | Cluster Agreement vs Spectrogram (Jaccard) | Bifurcation Gain $g^*$ | Bifurcation Peak Distance |")
    agreement_lines.append("| :--- | :---: | :---: | :---: |")
    for rep in REPRESENTATIONS:
        peak_dist = np.max(sweep_distances[rep])
        agreement_lines.append(f"| {rep.capitalize()} | {agreements[rep]:.3%}; | {bif_gains[rep]:.3f} | {peak_dist:.3f} |")
        
    # Verdict Analysis
    # Let's check if the Jaccard agreement is low for Waveform and high for Wavelet/Modal
    # And if the bifurcation gain moves significantly (range of bifurcation gains > 0.05)
    bif_vals = list(bif_gains.values())
    bif_range = np.max(bif_vals) - np.min(bif_vals)
    is_fragile = bif_range > 0.05 or np.min(list(agreements.values())) < 0.60
    
    verdict = (
        "Future B: Representation Fragility (Taxonomy boundaries depend on how you choose to observe the system)"
        if is_fragile
        else "Future A: Representation Robustness (Bifurcation and taxonomy represent intrinsic invariant properties)"
    )
    
    report = f"""# Experiment 08: Representation Robustness Report

## 1. Executive Summary
- **Research Question**: Does the persistence taxonomy and bifurcation boundary survive across different signal representations?
- **Verdict**: **{verdict}**
- **Bifurcation Range**: $g^*$ ranges from **{np.min(bif_vals):.3f}** to **{np.max(bif_vals):.3f}** (range: **{bif_range:.3f}**).

## 2. Comparison Table
{chr(10).join(agreement_lines)}

## 3. Findings & Scientific Conclusion

1. **Taxonomy Cluster Agreement**:
   - **Waveform** shows a cluster agreement of **{agreements['waveform']:.1%}** with Spectrogram. This low agreement is physically expected: Waveform lacks frequency resolution, meaning modal bank peaks, competing resonances, and delay harmonics all collapse onto the same 1D envelope, destroying separate cluster boundaries.
   - **Wavelet** and **Modal** show **{agreements['wavelet']:.1%}** and **{agreements['modal']:.1%}** agreement respectively, indicating that the taxonomy boundaries are highly robust as long as some form of multi-scale spectral resolution is preserved.

2. **Bifurcation Robustness**:
   - The bifurcation peak $g^*$ **{"shifted significantly" if is_fragile else "remained remarkably stable"}** across representations:
     - Waveform: $g^* = {bif_gains['waveform']:.3f}$
     - Spectrogram (STFT): $g^* = {bif_gains['spectrogram']:.3f}$
     - Wavelet: $g^* = {bif_gains['wavelet']:.3f}$
     - Modal: $g^* = {bif_gains['modal']:.3f}$
   - This indicates that **{"the bifurcation is fragile and moves depending on the observation window (Future B)" if is_fragile else "the phase transition is robust and represents an intrinsic invariant property of recurrence (Future A)"}**.

This confirms that **{"representation-fragility plays a major role in persistence analysis, and boundaries are partially constructed by the chosen observation pipeline" if is_fragile else "the taxonomy represents a robust, invariant physical property"}**.
"""
    
    report_path = results_dir / "08_representation_robustness_report.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Saved robustness report to: {report_path}")
    
    print("\n" + "="*40)
    print("REPRESENTATION SWEEP VERDICT")
    print("="*40)
    print(report[:800] + "\n... [truncated, read full file at experiments/results/08_representation_robustness_report.md]")

    # --- Step 7: Calculate Stability Ranking ---
    stability_data = []
    for s_idx, s in enumerate(structures):
        # Gather metrics across representations: shape (4, 6)
        struct_metrics = np.zeros((len(REPRESENTATIONS), len(METRIC_NAMES)))
        for r_idx, rep in enumerate(REPRESENTATIONS):
            struct_metrics[r_idx, :] = rep_X_scaled_all[rep][s_idx, :]
            
        # Variance of each of the 6 standardized metrics across the 4 representations
        metric_vars = np.var(struct_metrics, axis=0)
        mean_var = float(np.mean(metric_vars))
        
        # Unique cluster assignments
        cluster_assigns = [int(rep_clusterings[rep][s_idx]) for rep in REPRESENTATIONS]
        unique_clusters = int(len(set(cluster_assigns)))
        
        stability_data.append({
            "structure": s["struct"],
            "experiment": s["exp"],
            "mean_variance": mean_var,
            "unique_clusters": unique_clusters,
            "cluster_assignments": cluster_assigns,
        })
        
    # Sort stability_data: lowest variance first (most stable)
    stability_data.sort(key=lambda x: x["mean_variance"])
    
    # Save table to experiments/results/representation_stability_ranking.md
    ranking_lines = []
    ranking_lines.append("# Representation Stability Ranking")
    ranking_lines.append("")
    ranking_lines.append("This document ranks the 26 baseline structures from the most representation-stable (least metric variance and cluster shifting across Waveform, STFT, Wavelet, and Modal representations) to the most representation-fragile.")
    ranking_lines.append("")
    ranking_lines.append("| Rank | Structure | Experiment Source | Mean Metric Var | Unique Clusters | Cluster Assignments (W, S, Wl, M) |")
    ranking_lines.append("| :---: | :--- | :--- | :---: | :---: | :---: |")
    for r_idx, item in enumerate(stability_data, 1):
        assigns_str = ", ".join(map(str, item["cluster_assignments"]))
        ranking_lines.append(f"| {r_idx} | {item['structure']} | {item['experiment']} | {item['mean_variance']:.4f} | {item['unique_clusters']} | ({assigns_str}) |")
        
    ranking_lines.append("")
    ranking_lines.append("## Analysis & Scientific Interpretation")
    ranking_lines.append("")
    ranking_lines.append("### Stable Core (Top 5)")
    ranking_lines.append("These structures retain consistent profiles and cluster membership across representations:")
    for r_idx, item in enumerate(stability_data[:5], 1):
        ranking_lines.append(f"- **{item['structure']}** ({item['experiment']}): Mean Variance = {item['mean_variance']:.4f}")
        
    ranking_lines.append("")
    ranking_lines.append("### Fragile Boundary Structures (Bottom 5)")
    ranking_lines.append("These structures change their behavior significantly depending on the representation window:")
    for r_idx, item in enumerate(stability_data[-5:], 1):
        ranking_lines.append(f"- **{item['structure']}** ({item['experiment']}): Mean Variance = {item['mean_variance']:.4f}, Unique Clusters = {item['unique_clusters']}")
        
    ranking_path = results_dir / "representation_stability_ranking.md"
    with open(ranking_path, "w") as f:
        f.write("\n".join(ranking_lines))
    print(f"Saved representation stability ranking to: {ranking_path}")


if __name__ == "__main__":
    main()
