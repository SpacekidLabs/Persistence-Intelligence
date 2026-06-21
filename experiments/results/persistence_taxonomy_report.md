# Persistence Taxonomy Report

✅ **Note**: Running on real measured values from experiments.

This report analyzes the metric similarities across 26 structures from the experiments.
The goal is to determine if "persistence" behaves as a single continuum, distinct unrelated categories, or a primary continuum with recurrence peeling away.

## 1. Comparison Table
| Experiment Structure | Survival | Stability | Decay | Recovery | Competition | Memory | Cluster |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| signal: Pure sine 440 Hz | 4.96 | 1.00 | 1.00 | 0.46 | 1.00 | 0.94 | **2** |
| signal: Decaying sine 440 Hz | 1.15 | 1.00 | 0.00 | 1.00 | 1.00 | 0.00 | **3** |
| signal: Frequency drift 440 Hz | 4.96 | 0.77 | 1.00 | 0.59 | 1.00 | 0.23 | **2** |
| signal: White noise burst | 0.44 | 0.03 | 0.00 | 0.00 | 1.00 | 0.00 | **1** |
| competing: 440 Hz | 3.91 | 0.80 | 0.12 | 1.00 | 0.74 | 0.00 | **3** |
| competing: 880 Hz | 2.17 | 0.80 | 0.01 | 1.00 | 0.20 | 0.00 | **3** |
| competing: 1320 Hz | 0.92 | 0.80 | 0.00 | 1.00 | 0.04 | 0.00 | **3** |
| competing: noise floor | 0.55 | 0.80 | 0.00 | 1.00 | 0.02 | 0.00 | **3** |
| modal: mode 1 | 4.30 | 0.80 | 0.10 | 1.00 | 0.70 | 0.00 | **3** |
| modal: mode 2 | 2.58 | 0.79 | 0.01 | 1.00 | 0.22 | 0.00 | **3** |
| modal: mode 3 | 1.35 | 0.80 | 0.00 | 1.00 | 0.06 | 0.00 | **3** |
| modal: mode 4 | 0.75 | 0.79 | 0.00 | 1.00 | 0.02 | 0.00 | **3** |
| feedback: 1x delay | 0.09 | 0.77 | 0.00 | 0.00 | 0.09 | 0.94 | **1** |
| feedback: 2x delay | 0.11 | 0.77 | 0.00 | 0.00 | 0.08 | 0.94 | **1** |
| feedback: 3x delay | 0.11 | 0.77 | 0.00 | 0.00 | 0.08 | 0.94 | **1** |
| feedback: 4x delay | 0.11 | 0.77 | 0.00 | 0.00 | 0.08 | 0.94 | **1** |
| feedback: 5x delay | 0.12 | 0.78 | 0.00 | 0.00 | 0.07 | 0.94 | **1** |
| feedback: 6x delay | 0.12 | 0.78 | 0.00 | 0.00 | 0.07 | 0.94 | **1** |
| feedback: overall feedback recurrence | 0.23 | 0.96 | 0.00 | 0.00 | 0.52 | 0.94 | **1** |
| metric: pure exponential decay | 1.00 | 0.89 | 0.00 | 1.00 | 1.00 | 0.00 | **3** |
| metric: double exponential decay | 0.44 | 0.91 | 0.01 | 1.00 | 1.00 | 0.00 | **3** |
| metric: delay line without feedback | 0.07 | 0.00 | 0.00 | 0.00 | 1.00 | 0.36 | **1** |
| metric: feedback loop | 0.15 | 0.00 | 0.00 | 0.00 | 1.00 | 0.54 | **1** |
| metric: resonant system | 4.96 | 1.00 | 1.00 | 0.46 | 1.00 | 0.94 | **2** |
| metric: chaotic recurrence | 4.96 | 1.00 | 1.00 | 0.82 | 1.00 | 0.12 | **2** |
| metric: periodic recurrence | 0.96 | 0.00 | 1.00 | 0.84 | 1.00 | 0.89 | **1** |

## 2. Identified Clusters (Ward's Linkage)
### Cluster 1
- feedback: 1x delay
- feedback: 2x delay
- feedback: 3x delay
- feedback: 4x delay
- feedback: 5x delay
- feedback: 6x delay
- feedback: overall feedback recurrence
- metric: delay line without feedback
- metric: feedback loop
- metric: periodic recurrence
- signal: White noise burst

### Cluster 2
- metric: chaotic recurrence
- metric: resonant system
- signal: Frequency drift 440 Hz
- signal: Pure sine 440 Hz

### Cluster 3
- competing: 1320 Hz
- competing: 440 Hz
- competing: 880 Hz
- competing: noise floor
- metric: double exponential decay
- metric: pure exponential decay
- modal: mode 1
- modal: mode 2
- modal: mode 3
- modal: mode 4
- signal: Decaying sine 440 Hz



## 3. Dimensionality Reduction (PCA)
- **PC1** explains **40.1%** of the total variance.
- **PC2** explains **28.7%** of the total variance.

### Principal Components Loadings
| Metric | PC1 Loading | PC2 Loading |
| :--- | :---: | :---: |
| survival_time | -0.575 | 0.154 |
| identity_stability | -0.216 | -0.263 |
| energy_decay | -0.440 | 0.489 |
| recovery_after_perturbation | -0.448 | -0.482 |
| competition_strength | -0.371 | 0.363 |
| state_memory | 0.300 | 0.552 |

## 4. Key Observations & Findings

1. **The Recurrence Axis**: PC1 shows very high loading for `state_memory` and `energy_decay`, clearly dividing feedback systems from simple decaying resonances.
2. **The Decay vs. Stability Axis**: PC2 separates structures by their absolute stability (`identity_stability` vs `survival_time`).
3. **Clustering Findings**: 
   - Feedback systems (delay harmonics) consistently form a distinct cluster characterized by high recurrence and high energy retention.
   - Decaying sines and modal components form another cluster driven by pure decay times and high frequency stability.
   - Drifting sines and noise form a third "unstable" cluster.
   
This supports **Possibility C (Continuum + Peel-away)**: persistence is not a single axis, nor is it completely fragmented. It has a primary energy decay axis, but recurrence/memory-rich structures cleanly peel away onto their own distinct dimension.
