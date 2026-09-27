# Experiment 2 Production Design v1

## Objective

Freeze a production-scale repeated-QED/QEM benchmark only after Phase D validation.

## Core comparison

Raw / ZNE / repeated QED(L) / repeated QED(L)+ZNE

## Default grid

- qubits: 2, 4, 6, 8
- total body depth: 8, 16, 32, 64
- depolarizing p: 1e-4, 3e-4, 1e-3, 3e-3, 1e-2
- nominal shots: 1,024; 4,096; 16,384
- seeds: 0..19
- check intervals: 2, 8
- ZNE scales: 1, 3, 5

Matched interval-conditions: 9,600
Method rows: 38,400

## Required engineering before launch

1. checkpoint after each matched four-method condition,
2. --resume support,
3. provenance JSON with commit/software/machine/config,
4. explicit scale-wise hybrid acceptance and estimates,
5. no silent clipping; preserve unclipped estimate,
6. progress and ETA,
7. smoke CI only; production locally,
8. post-run integrity audit before interpretation.

## Analysis priorities

- reliability by method over depth/noise/width
- acceptance collapse surfaces for repeated QED
- hybrid clipping frequency and overshoot magnitude
- error versus executed-shot cost
- error versus accepted-shot cost
- error versus physical-qubit cost
- error versus 2Q work and aggregate depth
- Pareto frontiers by physical condition
- QEM-to-QED/hybrid crossover regions

## Guardrail

Do not launch this grid until the production runner has checkpoint/resume and the estimated
runtime has been profiled on a reduced subset.
