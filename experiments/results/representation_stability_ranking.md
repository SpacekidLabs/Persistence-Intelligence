# Representation Stability Ranking

This document ranks the 26 baseline structures from the most representation-stable (least metric variance and cluster shifting across Waveform, STFT, Wavelet, and Modal representations) to the most representation-fragile.

| Rank | Structure | Experiment Source | Mean Metric Var | Unique Clusters | Cluster Assignments (W, S, Wl, M) |
| :---: | :--- | :--- | :---: | :---: | :---: |
| 1 | pure exponential decay | 06_metric_falsification | 0.0562 | 2 | (2, 3, 3, 3) |
| 2 | Decaying sine 440 Hz | 01_signal_persistence | 0.0565 | 2 | (2, 3, 3, 3) |
| 3 | double exponential decay | 06_metric_falsification | 0.0644 | 2 | (2, 3, 3, 3) |
| 4 | mode 1 | 03_modal_objects | 0.0650 | 2 | (2, 3, 3, 3) |
| 5 | periodic recurrence | 06_metric_falsification | 0.0983 | 3 | (3, 1, 2, 2) |
| 6 | overall feedback recurrence | 04_feedback_systems | 0.1254 | 1 | (1, 1, 1, 1) |
| 7 | feedback loop | 06_metric_falsification | 0.1254 | 1 | (1, 1, 1, 1) |
| 8 | mode 2 | 03_modal_objects | 0.1263 | 2 | (2, 3, 3, 3) |
| 9 | Frequency drift 440 Hz | 01_signal_persistence | 0.1410 | 2 | (3, 2, 2, 2) |
| 10 | delay line without feedback | 06_metric_falsification | 0.1711 | 1 | (1, 1, 1, 1) |
| 11 | 5x delay | 04_feedback_systems | 0.1773 | 1 | (1, 1, 1, 1) |
| 12 | 6x delay | 04_feedback_systems | 0.1773 | 1 | (1, 1, 1, 1) |
| 13 | 2x delay | 04_feedback_systems | 0.1776 | 1 | (1, 1, 1, 1) |
| 14 | 3x delay | 04_feedback_systems | 0.1776 | 1 | (1, 1, 1, 1) |
| 15 | 4x delay | 04_feedback_systems | 0.1776 | 1 | (1, 1, 1, 1) |
| 16 | mode 3 | 03_modal_objects | 0.1776 | 2 | (2, 3, 3, 3) |
| 17 | White noise burst | 01_signal_persistence | 0.1840 | 1 | (1, 1, 1, 1) |
| 18 | 880 Hz | 02_competing_resonances | 0.2001 | 2 | (2, 3, 3, 2) |
| 19 | 440 Hz | 02_competing_resonances | 0.2024 | 2 | (2, 3, 3, 2) |
| 20 | 1x delay | 04_feedback_systems | 0.2204 | 1 | (1, 1, 1, 1) |
| 21 | chaotic recurrence | 06_metric_falsification | 0.2735 | 2 | (3, 2, 2, 3) |
| 22 | 1320 Hz | 02_competing_resonances | 0.2980 | 2 | (2, 3, 3, 2) |
| 23 | mode 4 | 03_modal_objects | 0.3568 | 2 | (2, 3, 3, 3) |
| 24 | noise floor | 02_competing_resonances | 0.4444 | 2 | (2, 3, 3, 2) |
| 25 | Pure sine 440 Hz | 01_signal_persistence | 0.4861 | 2 | (3, 2, 2, 3) |
| 26 | resonant system | 06_metric_falsification | 0.4861 | 2 | (3, 2, 2, 3) |

## Analysis & Scientific Interpretation

### Stable Core (Top 5)
These structures retain consistent profiles and cluster membership across representations:
- **pure exponential decay** (06_metric_falsification): Mean Variance = 0.0562
- **Decaying sine 440 Hz** (01_signal_persistence): Mean Variance = 0.0565
- **double exponential decay** (06_metric_falsification): Mean Variance = 0.0644
- **mode 1** (03_modal_objects): Mean Variance = 0.0650
- **periodic recurrence** (06_metric_falsification): Mean Variance = 0.0983

### Fragile Boundary Structures (Bottom 5)
These structures change their behavior significantly depending on the representation window:
- **1320 Hz** (02_competing_resonances): Mean Variance = 0.2980, Unique Clusters = 2
- **mode 4** (03_modal_objects): Mean Variance = 0.3568, Unique Clusters = 2
- **noise floor** (02_competing_resonances): Mean Variance = 0.4444, Unique Clusters = 2
- **Pure sine 440 Hz** (01_signal_persistence): Mean Variance = 0.4861, Unique Clusters = 2
- **resonant system** (06_metric_falsification): Mean Variance = 0.4861, Unique Clusters = 2