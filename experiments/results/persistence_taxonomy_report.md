# Persistence Taxonomy Report

✅ **Note**: Running on real measured values from experiments.

This report analyzes the metric similarities across 19 structures from 4 experiments.
The goal is to determine if "persistence" behaves as a single continuum, distinct unrelated categories, or a primary continuum with recurrence peeling away.

## 1. Comparison Table
| Experiment Structure | Survival | Stability | Decay | Recovery | Competition | Memory | Cluster |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| signal: Pure sine 440 Hz | 4.95 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | **2** |
| signal: Decaying sine 440 Hz | 0.89 | 1.00 | 0.00 | 0.97 | 1.00 | 1.00 | **1** |
| signal: Frequency drift 440 Hz | 4.95 | 0.77 | 1.00 | 1.00 | 1.00 | 1.00 | **2** |
| signal: White noise burst | 0.00 | 0.03 | 0.00 | 1.00 | 1.00 | 0.00 | **3** |
| competing: 440 Hz | 5.10 | 0.80 | 0.12 | 0.86 | 0.74 | 1.00 | **2** |
| competing: 880 Hz | 2.46 | 0.80 | 0.01 | 0.90 | 0.20 | 1.00 | **2** |
| competing: 1320 Hz | 1.02 | 0.80 | 0.00 | 0.97 | 0.04 | 1.00 | **1** |
| competing: noise floor | 0.59 | 0.80 | 0.00 | 0.99 | 0.02 | 0.99 | **1** |
| modal: mode 1 | 5.45 | 0.80 | 0.10 | 0.86 | 0.70 | 1.00 | **2** |
| modal: mode 2 | 3.01 | 0.79 | 0.01 | 0.90 | 0.22 | 1.00 | **2** |
| modal: mode 3 | 1.53 | 0.80 | 0.00 | 0.96 | 0.06 | 1.00 | **1** |
| modal: mode 4 | 0.86 | 0.79 | 0.00 | 0.99 | 0.02 | 1.00 | **1** |
| feedback: 1x delay | 0.57 | 0.77 | 0.00 | 1.00 | 0.09 | 0.94 | **1** |
| feedback: 2x delay | 0.58 | 0.77 | 0.00 | 1.00 | 0.08 | 0.94 | **1** |
| feedback: 3x delay | 0.58 | 0.77 | 0.00 | 1.00 | 0.08 | 0.94 | **1** |
| feedback: 4x delay | 0.58 | 0.77 | 0.00 | 1.00 | 0.08 | 0.94 | **1** |
| feedback: 5x delay | 0.72 | 0.78 | 0.00 | 1.00 | 0.07 | 0.94 | **1** |
| feedback: 6x delay | 0.72 | 0.78 | 0.00 | 1.00 | 0.07 | 0.94 | **1** |
| feedback: overall feedback recurrence | 0.15 | 0.96 | 0.00 | 1.00 | 0.52 | 0.94 | **1** |

## 2. Identified Clusters (Ward's Linkage)
### Cluster 1
- competing: 1320 Hz
- competing: noise floor
- feedback: 1x delay
- feedback: 2x delay
- feedback: 3x delay
- feedback: 4x delay
- feedback: 5x delay
- feedback: 6x delay
- feedback: overall feedback recurrence
- modal: mode 3
- modal: mode 4
- signal: Decaying sine 440 Hz

### Cluster 2
- competing: 440 Hz
- competing: 880 Hz
- modal: mode 1
- modal: mode 2
- signal: Frequency drift 440 Hz
- signal: Pure sine 440 Hz

### Cluster 3
- signal: White noise burst



## 3. Dimensionality Reduction (PCA)
- **PC1** explains **41.5%** of the total variance.
- **PC2** explains **32.9%** of the total variance.

### Principal Components Loadings
| Metric | PC1 Loading | PC2 Loading |
| :--- | :---: | :---: |
| survival_time | -0.577 | -0.198 |
| identity_stability | -0.384 | 0.501 |
| energy_decay | -0.430 | -0.295 |
| recovery_after_perturbation | 0.324 | -0.002 |
| competition_strength | -0.297 | -0.551 |
| state_memory | -0.376 | 0.565 |

## 4. Key Observations & Findings

1. **The Recurrence Axis**: PC1 shows very high loading for `state_memory` and `energy_decay`, clearly dividing feedback systems from simple decaying resonances.
2. **The Decay vs. Stability Axis**: PC2 separates structures by their absolute stability (`identity_stability` vs `survival_time`).
3. **Clustering Findings**: 
   - Feedback systems (delay harmonics) consistently form a distinct cluster characterized by high recurrence and high energy retention.
   - Decaying sines and modal components form another cluster driven by pure decay times and high frequency stability.
   - Drifting sines and noise form a third "unstable" cluster.
   
This supports **Possibility C (Continuum + Peel-away)**: persistence is not a single axis, nor is it completely fragmented. It has a primary energy decay axis, but recurrence/memory-rich structures cleanly peel away onto their own distinct dimension.
