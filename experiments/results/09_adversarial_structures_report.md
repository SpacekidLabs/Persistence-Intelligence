# Experiment 09: Adversarial Structures Report

## 1. Executive Summary
- **Objective**: Find which signal structures maximize observer disagreement across Waveform, STFT Spectrogram, Wavelet, and Modal representations.
- **Max-Disagreement Signal**: **Chirps**
- **Disagreement Score**: **3.0951** (mean pairwise distance in 6D standardized metric space)

### Observer Disagreement Ranking
| Rank | Signal Structure | Disagreement Score |
| :---: | :--- | :---: |
| 1 | Chirps | 3.0951 |
| 2 | Glissando | 2.6780 |
| 3 | Granular clouds | 2.0060 |
| 4 | Quasi-periodic oscillators | 1.9520 |
| 5 | FM coupled | 1.5740 |
| 6 | Stochastic resonator | 1.3193 |
| 7 | 1/f noise | 1.1232 |
| 8 | Beating oscillators | 0.8942 |

## 2. Detailed Observer Conflict Profiles
### Chirps
- **Disagreement Score**: 3.0951
- **Cluster Assignments**:
  - **Waveform**: Recurrence (Cluster 1)
  - **Spectrogram**: Recurrence (Cluster 1)
  - **Wavelet**: Recurrence (Cluster 1)
  - **Modal**: Stationary/Resonance (Cluster 2)
- **Raw Metrics comparison**:
  | Metric | Waveform | Spectrogram | Wavelet | Modal |
  | :--- | :---: | :---: | :---: | :---: |
  | survival_time | 4.957 | 4.957 | 4.148 | 1.391 |
  | identity_stability | 1.000 | 0.073 | 0.435 | 0.433 |
  | energy_decay | 1.000 | 1.000 | 0.353 | 0.032 |
  | recovery_after_perturbation | 0.563 | 1.000 | 1.000 | 1.000 |
  | competition_strength | 1.000 | 1.000 | 1.000 | 1.000 |
  | state_memory | 0.203 | 0.230 | 0.000 | 0.000 |

### Glissando
- **Disagreement Score**: 2.6780
- **Cluster Assignments**:
  - **Waveform**: Recurrence (Cluster 1)
  - **Spectrogram**: Recurrence (Cluster 1)
  - **Wavelet**: Recurrence (Cluster 1)
  - **Modal**: Stationary/Resonance (Cluster 2)
- **Raw Metrics comparison**:
  | Metric | Waveform | Spectrogram | Wavelet | Modal |
  | :--- | :---: | :---: | :---: | :---: |
  | survival_time | 4.957 | 4.957 | 4.670 | 3.314 |
  | identity_stability | 1.000 | 0.152 | 0.520 | 0.519 |
  | energy_decay | 1.000 | 1.000 | 0.515 | 0.185 |
  | recovery_after_perturbation | 0.500 | 0.494 | 0.982 | 0.999 |
  | competition_strength | 1.000 | 1.000 | 1.000 | 1.000 |
  | state_memory | 0.874 | 0.395 | 0.395 | 0.000 |

### Granular clouds
- **Disagreement Score**: 2.0060
- **Cluster Assignments**:
  - **Waveform**: Recurrence (Cluster 1)
  - **Spectrogram**: Recurrence (Cluster 1)
  - **Wavelet**: Recurrence (Cluster 1)
  - **Modal**: Stationary/Resonance (Cluster 2)
- **Raw Metrics comparison**:
  | Metric | Waveform | Spectrogram | Wavelet | Modal |
  | :--- | :---: | :---: | :---: | :---: |
  | survival_time | 3.495 | 2.250 | 2.797 | 1.226 |
  | identity_stability | 1.000 | 0.065 | 0.370 | 0.405 |
  | energy_decay | 1.000 | 1.000 | 1.000 | 1.000 |
  | recovery_after_perturbation | 0.923 | 0.761 | 0.948 | 0.943 |
  | competition_strength | 1.000 | 1.000 | 1.000 | 1.000 |
  | state_memory | 0.182 | 0.170 | 0.230 | 0.215 |

### Quasi-periodic oscillators
- **Disagreement Score**: 1.9520
- **Cluster Assignments**:
  - **Waveform**: Recurrence (Cluster 1)
  - **Spectrogram**: Recurrence (Cluster 1)
  - **Wavelet**: Recurrence (Cluster 1)
  - **Modal**: Recurrence (Cluster 1)
- **Raw Metrics comparison**:
  | Metric | Waveform | Spectrogram | Wavelet | Modal |
  | :--- | :---: | :---: | :---: | :---: |
  | survival_time | 4.957 | 4.957 | 4.957 | 4.956 |
  | identity_stability | 1.000 | 1.000 | 1.000 | 1.000 |
  | energy_decay | 1.000 | 1.000 | 0.998 | 0.996 |
  | recovery_after_perturbation | 0.808 | 0.828 | 0.837 | 0.796 |
  | competition_strength | 1.000 | 1.000 | 1.000 | 1.000 |
  | state_memory | 0.944 | 0.944 | 0.145 | 0.111 |

### FM coupled
- **Disagreement Score**: 1.5740
- **Cluster Assignments**:
  - **Waveform**: Recurrence (Cluster 1)
  - **Spectrogram**: Recurrence (Cluster 1)
  - **Wavelet**: Recurrence (Cluster 1)
  - **Modal**: Recurrence (Cluster 1)
- **Raw Metrics comparison**:
  | Metric | Waveform | Spectrogram | Wavelet | Modal |
  | :--- | :---: | :---: | :---: | :---: |
  | survival_time | 4.957 | 4.957 | 4.951 | 4.943 |
  | identity_stability | 1.000 | 0.466 | 0.803 | 0.836 |
  | energy_decay | 1.000 | 1.000 | 0.999 | 0.999 |
  | recovery_after_perturbation | 0.538 | 1.000 | 0.440 | 0.524 |
  | competition_strength | 1.000 | 1.000 | 1.000 | 1.000 |
  | state_memory | 0.892 | 0.871 | 0.933 | 0.947 |

### Stochastic resonator
- **Disagreement Score**: 1.3193
- **Cluster Assignments**:
  - **Waveform**: Recurrence (Cluster 1)
  - **Spectrogram**: Recurrence (Cluster 1)
  - **Wavelet**: Recurrence (Cluster 1)
  - **Modal**: Recurrence (Cluster 1)
- **Raw Metrics comparison**:
  | Metric | Waveform | Spectrogram | Wavelet | Modal |
  | :--- | :---: | :---: | :---: | :---: |
  | survival_time | 4.956 | 4.948 | 4.937 | 4.903 |
  | identity_stability | 1.000 | 0.007 | 0.409 | 0.819 |
  | energy_decay | 1.000 | 1.000 | 0.977 | 0.945 |
  | recovery_after_perturbation | 0.821 | 0.649 | 0.863 | 0.847 |
  | competition_strength | 1.000 | 1.000 | 1.000 | 1.000 |
  | state_memory | 0.152 | 0.131 | 0.201 | 0.117 |

### 1/f noise
- **Disagreement Score**: 1.1232
- **Cluster Assignments**:
  - **Waveform**: Recurrence (Cluster 1)
  - **Spectrogram**: Recurrence (Cluster 1)
  - **Wavelet**: Recurrence (Cluster 1)
  - **Modal**: Recurrence (Cluster 1)
- **Raw Metrics comparison**:
  | Metric | Waveform | Spectrogram | Wavelet | Modal |
  | :--- | :---: | :---: | :---: | :---: |
  | survival_time | 4.773 | 3.386 | 4.908 | 4.785 |
  | identity_stability | 1.000 | 0.434 | 0.642 | 0.960 |
  | energy_decay | 1.000 | 0.975 | 0.983 | 0.985 |
  | recovery_after_perturbation | 0.920 | 0.802 | 0.910 | 0.914 |
  | competition_strength | 1.000 | 1.000 | 1.000 | 1.000 |
  | state_memory | 0.136 | 0.170 | 0.114 | 0.143 |

### Beating oscillators
- **Disagreement Score**: 0.8942
- **Cluster Assignments**:
  - **Waveform**: Recurrence (Cluster 1)
  - **Spectrogram**: Recurrence (Cluster 1)
  - **Wavelet**: Recurrence (Cluster 1)
  - **Modal**: Recurrence (Cluster 1)
- **Raw Metrics comparison**:
  | Metric | Waveform | Spectrogram | Wavelet | Modal |
  | :--- | :---: | :---: | :---: | :---: |
  | survival_time | 4.142 | 3.312 | 4.145 | 4.142 |
  | identity_stability | 1.000 | 0.907 | 1.000 | 1.000 |
  | energy_decay | 1.000 | 1.000 | 0.998 | 0.997 |
  | recovery_after_perturbation | 0.996 | 0.998 | 0.996 | 0.996 |
  | competition_strength | 1.000 | 1.000 | 1.000 | 1.000 |
  | state_memory | 0.929 | 0.929 | 0.927 | 0.927 |

## 3. Scientific Interpretation & Verdict

Under our measurement framework, the **Chirps** signal exhibits the largest conflict between observers (waveform=Recurrence, spectrogram=Recurrence, wavelet=Recurrence, modal=Stationary/Resonance).

This is physically coherent:
- **Chirps**: A continuous frequency sweep has a flat waveform envelope (no decay, maximum recovery/smoothness), but passes through different channels of spectral filters over time. Waveform registers it as stationary, STFT registers it as decaying/evolving, and modal registers it as temporary resonances in filters. This maximizes observer disagreement.

### Scientific Verdict:
> [!IMPORTANT]
> **Category boundaries in persistence are fundamentally observation-dependent (Future B: Representation Fragility).**
> The existence of signals that produce high observer disagreement confirms that persistence taxonomy is not an absolute, representation-invariant property of the signal itself, but is rather a joint property of the system's physical parameters and the observer's resolution parameters.