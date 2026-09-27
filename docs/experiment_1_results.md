# Experiment 1 — Production Result Summary

## Status

**COMPLETE — local production sweep validated.**

Experiment 1 evaluated 6,000 matched Raw/ZNE conditions (12,000 CSV rows) over:

- qubits: 2, 4, 6, 8
- nominal depths: 5, 10, 20, 40, 80
- depolarizing probabilities: 1e-4, 3e-4, 1e-3, 3e-3, 1e-2
- nominal shots: 1,024; 4,096; 16,384
- 20 seeded circuit instances
- ZNE scales: 1, 3, 5

The production run used commit `49e03f0fe1c15706f38b6fce6367cba52dc9bc2f`,
Python 3.11.5, Qiskit 2.5.2, Qiskit Aer 0.17.2, and NumPy 2.4.6 on
ARM64 macOS. The run completed in approximately 71.57 minutes.

## Aggregate reliability result

Across all 6,000 matched conditions:

- Raw mean absolute error: **0.296512**
- ZNE mean absolute error: **0.252623**
- Mean absolute improvement: **0.043890**
- Relative reduction in mean absolute error: **14.8%**
- Individual conditions improved: **97.83%**
- Individual conditions tied: **2.17%**
- Individual conditions worse: **0%**

After aggregating over seeds, 295 of 300 width/depth/noise/shot cells improved and 5 tied.
The seed-aggregated mean improvement is approximately 0.04389 with a 95% CI of
approximately **[0.0401, 0.0477]**.

These statistics characterize this experimental grid only and should not be interpreted as
a universal performance guarantee for ZNE.

## Principal finding: a finite mitigation operating window

ZNE benefit is strongly non-monotonic in the interaction between physical noise and
circuit depth.

Mean absolute-error improvement by depth/noise:

| Depth | 1e-4 | 3e-4 | 1e-3 | 3e-3 | 1e-2 |
|---:|---:|---:|---:|---:|---:|
| 5 | 0.0040 | 0.0118 | 0.0356 | 0.0734 | 0.0793 |
| 10 | 0.0085 | 0.0242 | 0.0615 | 0.0875 | 0.0466 |
| 20 | 0.0175 | 0.0450 | 0.0846 | 0.0685 | 0.0166 |
| 40 | 0.0333 | 0.0710 | 0.0821 | 0.0344 | 0.0035 |
| 80 | 0.0569 | 0.0877 | 0.0525 | 0.0110 | 0.0004 |

The noise level associated with maximum mitigation benefit shifts downward as circuit
depth increases. At sufficiently high noise and depth, ZNE benefit collapses toward zero.
This motivates treating QEM as having a finite resource-dependent operating regime rather
than assuming mitigation benefit grows monotonically with noise.

## Resource cost

The three-scale ZNE protocol incurs approximately:

- **3x sampling**
- **9x aggregate two-qubit gate work**
- approximately **8.9x aggregate depth work**
- approximately **8.9x measured simulator execution time** in this production run

Therefore, positive error reduction alone is insufficient to establish resource efficiency.

## Shot-budget result

Mean mitigation improvement is nearly unchanged across the tested nominal shot budgets:

- 1,024: **0.04375**
- 4,096: **0.04392**
- 16,384: **0.04400**

Within this benchmark, increasing nominal shots by 16x changes mean mitigation benefit
far less than changing circuit depth or physical noise. This result should be interpreted
for the present deterministic mirror-style workload and not generalized to arbitrary
quantum workloads.

## Extrapolation/clipping diagnostic

474 of 6,000 ZNE estimates (**7.9%**) required clipping to [0,1]. All clipping events were
upper-bound overshoots; no negative extrapolations were observed. Clipping is concentrated
in low-noise/high-success regimes and should be reported explicitly alongside unclipped
estimates.

## Reproducibility

The 32-row checkpoint smoke dataset matches the corresponding production subset exactly
for success probability and absolute error under the same seeded conditions.

## Paper interpretation

Experiment 1 supports the QEM portion of RQ1/RQ2/RQ3:

1. ZNE substantially improves reliability over a broad but finite operating region.
2. The improvement is purchased with substantial sampling and circuit-work overhead.
3. The useful mitigation region depends strongly on the interaction of noise and circuit depth.
4. Once circuits become sufficiently degraded, additional QEM resources yield diminishing or
   effectively zero reliability gain.

Experiment 1 does **not** yet establish a NISQ-to-FTQC crossover. That requires comparison
against error detection and/or error-corrected logical execution under a common resource
accounting framework.

## Next experiment

Experiment 2 should introduce quantum error detection/postselection under the same workload
and resource schema. The immediate comparison becomes:

**Raw -> ZNE -> QED -> QED+ZNE**

before moving to fully encoded QEC and decoder-cost benchmarking.
