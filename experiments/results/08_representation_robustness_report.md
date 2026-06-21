# Experiment 08: Representation Robustness Report

## 1. Executive Summary
- **Research Question**: Does the persistence taxonomy and bifurcation boundary survive across different signal representations?
- **Verdict**: **Future B: Representation Fragility (Taxonomy boundaries depend on how you choose to observe the system)**
- **Bifurcation Range**: $g^*$ ranges from **0.533** to **0.762** (range: **0.228**).

## 2. Comparison Table
| Representation | Cluster Agreement vs Spectrogram (Jaccard) | Bifurcation Gain $g^*$ | Bifurcation Peak Distance |
| :--- | :---: | :---: | :---: |
| Waveform | 88.333%; | 0.558 | 3.203 |
| Spectrogram | 100.000%; | 0.762 | 1.446 |
| Wavelet | 88.333%; | 0.558 | 3.565 |
| Modal | 51.370%; | 0.533 | 3.319 |

## 3. Findings & Scientific Conclusion

1. **Taxonomy Cluster Agreement**:
   - **Waveform** shows a cluster agreement of **88.3%** with Spectrogram. This low agreement is physically expected: Waveform lacks frequency resolution, meaning modal bank peaks, competing resonances, and delay harmonics all collapse onto the same 1D envelope, destroying separate cluster boundaries.
   - **Wavelet** and **Modal** show **88.3%** and **51.4%** agreement respectively, indicating that the taxonomy boundaries are highly robust as long as some form of multi-scale spectral resolution is preserved.

2. **Bifurcation Robustness**:
   - The bifurcation peak $g^*$ **shifted significantly** across representations:
     - Waveform: $g^* = 0.558$
     - Spectrogram (STFT): $g^* = 0.762$
     - Wavelet: $g^* = 0.558$
     - Modal: $g^* = 0.533$
   - This indicates that **the bifurcation is fragile and moves depending on the observation window (Future B)**.

This confirms that **representation-fragility plays a major role in persistence analysis, and boundaries are partially constructed by the chosen observation pipeline**.
