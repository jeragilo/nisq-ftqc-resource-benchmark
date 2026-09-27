# Experiment 1 Protocol — QEM Resource Sweep

## Purpose

Experiment 1 moves from pipeline validation to the first substantive Paper 2 QEM study.

It asks:

> How does the reliability benefit of zero-noise extrapolation change with physical noise, circuit complexity, and sampling budget, and when does the additional mitigation cost cease to provide a favorable tradeoff?

This experiment primarily informs RQ1 (reliability), RQ2 (resource efficiency), and the QEM side of RQ3 (crossover).

## Design principles inherited from Experiment 0

- preserve seeded, reproducible workloads
- preserve raw/noisy and mitigated matched conditions
- explicitly account for all folded-circuit sampling and gate/depth work
- preserve raw data as workflow artifacts
- do not treat individual rows as independent scientific replicates
- do not interpret simulator wall time as QPU time

## Planned expansion

### Circuit widths
2, 4, 6, and 8 qubits.

### Nominal mirror-body depths
5, 10, 20, 40, and 80.

### Depolarizing-noise probabilities
1e-4, 3e-4, 1e-3, 3e-3, and 1e-2.

### Nominal shot budgets
1,024; 4,096; and 16,384.

### Seeds
20 seeded circuit instances per configuration.

### ZNE configurations
Compare at least:
- raw execution
- linear ZNE using scales (1, 3, 5)

A second extrapolation/scaling configuration should only be added after the baseline sweep is computationally validated.

## New diagnostics

Experiment 1 must record, in addition to Experiment 0 metrics:

- un-clipped ZNE estimate
- whether clipping to [0,1] occurred
- values observed at each noise scale
- mitigation improvement relative to matched raw execution
- sampling overhead ratio
- aggregate gate-work ratio
- aggregate depth-work ratio
- runtime ratio

## Analysis

Primary analyses:

1. absolute error vs physical noise
2. absolute error vs nominal depth
3. mitigation improvement vs noise/depth
4. mitigation improvement vs shot budget
5. reliability improvement per additional shot
6. reliability improvement per aggregate two-qubit gate execution
7. Pareto dominance of raw vs ZNE in selected two-resource projections
8. identification of high-noise/depth regions where ZNE benefit saturates or collapses

## Computational strategy

Experiment 0 revealed that rebuilding/transpiling each circuit repeatedly is expensive. Experiment 1 should cache or reuse transpiled/folded circuits wherever the noise model and simulator basis allow it. Fast unit tests remain separate from full scientific sweeps.

## Interpretation guardrail

Experiment 1 can characterize QEM resource-efficiency regimes. It cannot establish the full NISQ-to-FTQC crossover because QED and QEC are not yet included.
